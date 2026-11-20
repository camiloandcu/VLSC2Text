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
