import copy

import numpy as np
import pytest

from lsc5.data import build_manifest, make_splits, validate_manifest, validate_split
from lsc5.features import fit_scaler, from_originals, load_stats, prepare_stats, raw_stats
from lsc5.io import atomic_json, digest, read_json, train_path


def test_inventory_excludes_test_and_raw_features_ignore_metadata(small_train, tmp_path):
    train, manifest = small_train
    test = tmp_path / "test"
    test.mkdir()
    (test / "must_not_open.npy").write_bytes(b"invalid numpy payload")
    assert len(build_manifest(train)["samples"]) == 15
    with pytest.raises(ValueError):
        train_path(train, "../test/must_not_open.npy")
    (train / "escape.npy").symlink_to(test / "must_not_open.npy")
    with pytest.raises(ValueError):
        train_path(train, "escape.npy")
    with pytest.raises(ValueError):
        build_manifest(test)
    sample = manifest["samples"][0]
    altered = dict(sample, label="sign_05", signer="M99", camera="C99", view="V99")
    np.testing.assert_array_equal(from_originals(train, [sample]), from_originals(train, [altered]))


def test_loso_and_cross_subject_duplicates(small_train):
    _, manifest = small_train
    for split in make_splits(manifest):
        validate_split(manifest, split)
        assert not set(split["train_ids"]) & set(split["validation_ids"])
        assert len(split["train_ids"]) == 10 and len(split["validation_ids"]) == 5
        broken = copy.deepcopy(split)
        broken["train_ids"].append(split["validation_ids"][0])
        with pytest.raises(ValueError):
            validate_split(manifest, broken)
    broken = copy.deepcopy(manifest)
    a = broken["samples"][0]
    b = next(s for s in broken["samples"] if s["signer"] != a["signer"])
    b["landmarks_sha256"] = a["landmarks_sha256"]
    broken["manifest_hash"] = digest({k: v for k, v in broken.items() if k != "manifest_hash"})
    with pytest.raises(ValueError, match="across signers"):
        validate_manifest(broken)


def test_opaque_statistics_and_fold_scaling():
    x = np.zeros((3, 1662), dtype=np.float64)
    x[:, 0] = [0, 3, 6]
    r = raw_stats(x)
    assert r.shape == (3324,) and r[0] == 3
    assert r[1662] == pytest.approx(np.std([0, 3, 6]))
    fit = np.asarray([[1, 4], [3, 4]], dtype=np.float32)
    scaler = fit_scaler(fit, ["a", "b"])
    np.testing.assert_array_equal(scaler["mean"], [2, 4])
    np.testing.assert_array_equal(scaler["scale"], [1, 1])
    # A distant validation distribution cannot change the training scaler.
    validation = np.full((2, 2), 1e6, dtype=np.float32)
    assert not np.array_equal(scaler["mean"], np.vstack([fit, validation]).mean(0))


def test_cache_rejects_partial_corrupt_and_wrong_role(small_train, tmp_path):
    train, manifest = small_train
    path = tmp_path / "stats"
    prepare_stats(train, manifest, path)
    assert load_stats(path, manifest).shape == (15, 3324)
    meta = read_json(path / "metadata.json")
    for key, value in [("complete", False), ("data_role", "test"), ("ids", meta["ids"][:-1]),
                        ("producer_hash", "wrong")]:
        atomic_json(path / "metadata.json", dict(meta, **{key: value}))
        with pytest.raises(ValueError):
            load_stats(path, manifest)
    atomic_json(path / "metadata.json", meta)
    with (path / "stats.npz").open("ab") as handle:
        handle.write(b"corrupt")
    with pytest.raises(ValueError, match="hash"):
        load_stats(path, manifest)
