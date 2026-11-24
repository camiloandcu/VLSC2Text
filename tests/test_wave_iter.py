import numpy as np
import pytest

from lsc5 import wave, wave_iter
from test_wave import _clip


def test_feature_shapes_and_missing_hands_stay_neutral():
    c = _clip(t=24)
    s = wave_iter.sequence(c, handshape=True)
    assert s.shape == (24, 191 + 18)
    v = wave_iter.velocity_features(s)
    assert v.shape == (24, 98) and not v[0].any()
    xy = s[:, :98].reshape(24, 49, 2)
    missing = ~(xy != 0).any(-1)
    vv = v.reshape(24, 49, 2)
    assert not vv[1:][missing[1:] | missing[:-1]].any()
    assert wave_iter.candidate_features(c).shape == ((191 + 18 + 98) * 5,)


def test_view_augment_keeps_missing_points_zero_and_is_seeded():
    c = _clip(t=24)
    a = wave_iter.view_augment(c, np.random.default_rng(1))
    b = wave_iter.view_augment(c, np.random.default_rng(1))
    assert np.array_equal(a, b)
    lh0, lh1 = c[:, wave.LH], a[:, wave.LH]
    assert np.array_equal(lh0 == 0, lh1 == 0)


def test_iter2_bundle_refuses_test_paths(tmp_path):
    p = tmp_path / "test" / "x.npy"
    p.parent.mkdir()
    np.save(p, _clip())
    with pytest.raises(ValueError, match="reserved"):
        wave_iter.predict_bundle(tmp_path / "missing", [p])


def test_rest_gate_removes_low_static_hand_but_keeps_moving_one():
    c = _clip(t=30)                                   # right hand raised and jittering at shoulder height
    pose, face, lh, rh = (b.copy() for b in wave.split_blocks(c))
    lh[:, :, :2] = [0.6, 0.95]                       # left hand static far below the shoulders (lap/table)
    lh[:, :, 2] = 0.01
    c = wave.join_blocks(pose, face, lh, rh)
    g = wave_iter.rest_gate(c, low=1.3)
    assert not g[:, wave.LH].any()
    assert np.array_equal(g[:, wave.RH] != 0, c[:, wave.RH] != 0)


def test_iter3_bundle_refuses_test_paths(tmp_path):
    p = tmp_path / "test" / "x.npy"
    p.parent.mkdir()
    np.save(p, _clip())
    with pytest.raises(ValueError, match="reserved"):
        wave_iter.predict_bundle_v3(tmp_path / "missing", [p])


def test_contact_and_bimanual_features_are_finite_and_label_free():
    for left in (False, True):
        c = _clip(t=30, left=left)
        f = wave_iter.features(c, wave_iter.CANDIDATE_V4)
        assert np.isfinite(f).all()
        assert f.shape[0] == wave_iter.features(c, wave_iter.CANDIDATE_V3).shape[0] + 4 + 6
    empty = _clip(t=30)
    empty[:, wave.LH] = 0
    b = wave_iter.bimanual_features(empty)
    assert b[0] == 0 and b[1] == 0 and np.isfinite(b).all()


def _synthetic_train(root, signers=("M02", "M03"), per_class=4):
    from lsc5.data import CLASSES
    samples = []
    for c, label in enumerate(CLASSES):
        (root / "landmarks" / label).mkdir(parents=True, exist_ok=True)
        for s in signers:
            for k in range(per_class):
                i = f"S0{c+1}_{s}_V01_C01_Clip{c}{k}{s}"
                x = _clip(t=30, left=(k % 2 == 0), seed=c * 10 + k)
                np.save(root / "landmarks" / label / f"{i}.npy", x)
                samples.append({"id": i, "label": label, "signer": s, "view": "V01",
                                "landmarks_path": f"landmarks/{label}/{i}.npy"})
    return {"samples": samples, "manifest_hash": "synthetic"}


@pytest.mark.parametrize("candidate", ["v4_contact_bimanual", "v6_pose_robust"])
def test_iter3_bundle_round_trip_and_csv(tmp_path, candidate):
    """finalfit_v3 -> bundle on disk -> new predict_bundle_v3 call -> CSV, per-sample and order invariant."""
    from lsc5 import delivery
    root = tmp_path / "train"
    manifest = _synthetic_train(root)
    bundle = wave_iter.finalfit_v3(root, manifest, tmp_path / "bundle", cfg=wave_iter.CANDIDATES[candidate], seeds=(17,))
    assert bundle["members"][0]["dim"] == (191 + 18 + 98) * 5 + 4 + 6 == 1545
    assert bundle["cfg"] == {k: (list(v) if isinstance(v, tuple) else v) for k, v in wave_iter.CANDIDATES[candidate].items()}
    paths = [root / s["landmarks_path"] for s in manifest["samples"]]
    ref = np.load(tmp_path / "bundle" / "train_reference.npz")["probabilities"]
    probs = wave_iter.predict_bundle_v3(tmp_path / "bundle", paths)
    assert np.abs(probs - ref).max() <= 1e-6
    single = wave_iter.predict_bundle_v3(tmp_path / "bundle", paths[3:4])
    assert np.abs(single[0] - probs[3]).max() <= 1e-6
    ids = [s["id"] for s in manifest["samples"]]
    template = tmp_path / "template.csv"
    template.write_text("video_id,predicted_sign\n" + "".join(f"{i},\n" for i in ids), encoding="utf-8")
    assert delivery.write_submission(template, ids, probs, tmp_path / "submission.csv")["rows"] == len(ids)
    (tmp_path / "bundle" / "mlp_s17_norm.npz").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="hash mismatch"):
        wave_iter.predict_bundle_v3(tmp_path / "bundle", paths[:1])


def test_frozen_iter4_cfg_does_not_use_pose_robust_path():
    assert "pose_robust" not in wave_iter.CANDIDATE_V4
    c = _clip(t=30, left=True)
    assert np.array_equal(wave_iter.canonical_cfg(c, np.arange(468), wave_iter.CANDIDATE_V4), wave.canonical(c, np.arange(468)))


def test_pose_robust_matches_frozen_without_dropouts_and_survives_them():
    perm = np.arange(468)
    for left in (False, True):
        c = _clip(t=30, left=left)
        assert wave_iter.wrist_lift_robust(c) == wave.wrist_lift(c)
        assert wave_iter.active_segment_robust(c) == wave.active_segment(c)
        holes = c.copy()
        holes[::3, wave.POSE] = 0                     # MediaPipe pose dropouts are serialised as zeros
        l, r = wave_iter.wrist_lift_robust(wave_iter.canonical_robust(holes, perm))
        assert r > l                                  # dominant hand ends on the right despite dropouts
        seg = wave_iter.active_segment_robust(holes)
        assert seg.start >= 1 and seg.stop <= 19          # raised frames are 5..14, margin 3
    blank = np.zeros((10, 1662))
    assert wave_iter.active_segment_robust(blank) == slice(0, 10) and wave_iter.wrist_lift_robust(blank) == [0.0, 0.0]


def test_augmentation_is_train_only():
    """Without augment=True the feature builder is deterministic and ignores the rng."""
    c = _clip(t=30)
    a = wave_iter.features(c, wave_iter.CANDIDATE_V4, np.random.default_rng(1))
    b = wave_iter.features(c, wave_iter.CANDIDATE_V4, np.random.default_rng(2))
    assert np.array_equal(a, b)
    aug = wave_iter.features(c, wave_iter.CANDIDATE_V4, np.random.default_rng(1), augment=True)
    assert not np.array_equal(a, aug)
