import numpy as np
import pytest
import torch

from lsc5 import wave


def _clip(t=20, left=False, seed=0):
    rng = np.random.default_rng(seed)
    pose = np.zeros((t, 33, 4))
    pose[..., :2] = 0.5 + rng.normal(0, 0.01, (t, 33, 2))
    pose[..., 3] = 0.99
    pose[:, 11, 0], pose[:, 12, 0] = 0.55, 0.45      # left shoulder appears on image right
    pose[:, 11, 1] = pose[:, 12, 1] = 0.4
    pose[:, 15, :2], pose[:, 16, :2] = [0.6, 0.8], [0.4, 0.8]
    active = 15 if left else 16
    pose[5:15, active, 1] = 0.3                       # raise one wrist mid-clip
    face = rng.uniform(0.45, 0.55, (t, 468, 3))
    lh = np.zeros((t, 21, 3)); rh = np.zeros((t, 21, 3))
    hand = lh if left else rh
    hand[5:15, :, :2] = pose[5:15, active, None, :2] + rng.normal(0, 0.01, (10, 21, 2))
    return wave.join_blocks(pose, face, lh, rh)


def test_left_dominance_is_label_free_and_detected():
    assert wave.left_dominant(_clip(left=True))
    assert not wave.left_dominant(_clip(left=False))


def test_mirror_swaps_hands_and_pose_pairs_and_is_involutive_on_body():
    perm = np.arange(468)
    x = _clip(left=True)
    m = wave.mirror(x, perm)
    p0, _, lh0, rh0 = wave.split_blocks(x)
    p1, _, lh1, rh1 = wave.split_blocks(m)
    assert np.allclose(rh1[..., 0][rh1[..., 0] != 0], 1 - lh0[..., 0][lh0[..., 0] != 0])
    assert not lh1.any()
    assert np.allclose(p1[:, 15, 0], 1 - p0[:, 16, 0])
    back = wave.mirror(m, perm)
    assert np.allclose(back[:, wave.POSE], x[:, wave.POSE]) and np.allclose(back[:, wave.LH], x[:, wave.LH])
    assert not wave.left_dominant(wave.canonical(x, perm))


def test_body_features_invariant_to_translation_and_scale():
    x = _clip()
    y = x.copy()
    for block in (wave.POSE, wave.LH, wave.RH):
        k = 4 if block == wave.POSE else 3
        b = y[:, block].reshape(len(y), -1, k)
        nz = (b[..., :2] != 0).any(-1, keepdims=True)
        b[..., :2] = np.where(nz, b[..., :2] * 0.8 + 0.05, 0)
        y[:, block] = b.reshape(len(y), -1)
    assert wave.body_sequence(x).shape == (20, 191)
    assert np.allclose(wave.body_sequence(x), wave.body_sequence(y), atol=1e-5)


def test_tcn_ignores_padding():
    torch.manual_seed(0)
    model = wave.TCN(191).eval()
    seq = torch.randn(1, 12, 191)
    padded = torch.cat([seq, torch.randn(1, 30, 191)], 1)
    mask = torch.zeros(1, 42, dtype=torch.bool); mask[:, :12] = True
    with torch.inference_mode():
        a = model(seq, torch.ones(1, 12, dtype=torch.bool))
        b = model(padded, mask)
    assert torch.allclose(a, b, atol=1e-5)


def test_bundle_refuses_test_paths(tmp_path):
    p = tmp_path / "test" / "x.npy"
    p.parent.mkdir()
    np.save(p, _clip())
    with pytest.raises(ValueError, match="reserved"):
        wave.predict_bundle(tmp_path / "missing", [p])


def test_predict_csv_end_to_end_on_synthetic_train(tmp_path):
    from lsc5 import delivery
    from lsc5.data import CLASSES
    root = tmp_path / "train"
    samples = []
    for c, label in enumerate(CLASSES):
        (root / "landmarks" / label).mkdir(parents=True)
        for s in ("M02", "M03"):
            for k in range(4):
                i = f"S0{c+1}_{s}_V01_C01_Clip{c}{k}{s}"
                x = _clip(left=(k % 2 == 0), seed=c * 10 + k)
                x[:, wave.RH] += 0.0
                np.save(root / "landmarks" / label / f"{i}.npy", x)
                samples.append({"id": i, "label": label, "signer": s, "view": "V01",
                                "landmarks_path": f"landmarks/{label}/{i}.npy"})
    manifest = {"samples": samples, "manifest_hash": "synthetic"}
    wave.finalfit(root, manifest, tmp_path / "bundle", seeds=(17,))
    ids = [s["id"] for s in samples[:6]]
    paths = [root / s["landmarks_path"] for s in samples[:6]]
    template = tmp_path / "template.csv"
    template.write_text("video_id,predicted_sign\n" + "".join(f"{i},\n" for i in ids), encoding="utf-8")
    probs = wave.predict_bundle(tmp_path / "bundle", paths)
    ref = np.load(tmp_path / "bundle" / "train_reference.npz")["probabilities"][:6]
    assert np.abs(probs - ref).max() <= 1e-6
    assert delivery.write_submission(template, ids, probs, tmp_path / "submission.csv")["rows"] == 6
