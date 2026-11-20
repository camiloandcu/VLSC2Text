import json
from pathlib import Path

import numpy as np
import pytest

from lsc5 import delivery
from lsc5.data import CLASSES


def _dataset(tmp_path, signers=("M02", "M03"), per=4, frames=6):
    root = tmp_path / "train"
    rng = np.random.default_rng(0)
    samples = []
    for c, label in enumerate(CLASSES):
        (root / "landmarks" / label).mkdir(parents=True, exist_ok=True)
        for s in signers:
            for k in range(per):
                i = f"S0{c+1}_{s}_V01_C01_Clip{k:03d}"
                x = rng.normal(size=(frames, 1662)) + c
                np.save(root / "landmarks" / label / f"{i}.npy", x)
                samples.append({"id": i, "label": label, "signer": s,
                                "landmarks_path": f"landmarks/{label}/{i}.npy"})
    return root, {"samples": samples, "manifest_hash": "synthetic"}


def test_seed_outside_closed_set_rejected():
    with pytest.raises(ValueError):
        delivery.check_seed(7)


def test_test_paths_refused(tmp_path):
    p = tmp_path / "test" / "a.npy"
    p.parent.mkdir()
    np.save(p, np.zeros((3, 1662)))
    with pytest.raises(ValueError):
        delivery.r0_from_paths([p])


def test_bundle_roundtrip_order_and_tamper(tmp_path):
    root, manifest = _dataset(tmp_path)
    bundle = delivery.finalfit(root, manifest, (17, 29), tmp_path / "bundle")
    assert [m["seed"] for m in bundle["members"]] == [17, 29]
    paths = [root / s["landmarks_path"] for s in manifest["samples"]]
    ref = np.load(tmp_path / "bundle" / "train_reference.npz")["probabilities"]
    p = delivery.predict_bundle(tmp_path / "bundle", paths)
    assert np.abs(p - ref).max() <= 1e-6
    perm = np.random.default_rng(1).permutation(len(paths))
    assert np.abs(delivery.predict_bundle(tmp_path / "bundle", [paths[k] for k in perm]) - p[perm]).max() <= 1e-6
    single = delivery.predict_bundle(tmp_path / "bundle", paths[:1])
    assert np.abs(single - p[:1]).max() <= 1e-6
    model = tmp_path / "bundle" / "model_s17.pt"
    model.write_bytes(model.read_bytes() + b"x")
    with pytest.raises(ValueError):
        delivery.load_bundle(tmp_path / "bundle")


def _template(tmp_path, ids):
    t = tmp_path / "template.csv"
    t.write_text("video_id,predicted_sign\n" + "".join(f"{i},\n" for i in ids), encoding="utf-8")
    return t


@pytest.mark.parametrize("body,header", [
    ("a,sign_01\n", "video_id,predicted_sign"),                       # missing row
    ("a,sign_01\nb,sign_02\nb,sign_02\n", "video_id,predicted_sign"),  # duplicate
    ("a,sign_01\nb,sign_02\nc,sign_03\n", "video_id,predicted_sign"),  # extra
    ("a,sign_01\nb,sign_09\n", "video_id,predicted_sign"),            # bad code
    ("a,sign_01\nb,sign_02\n", "id,predicted_sign"),                  # header
    ("a,sign_01,x\nb,sign_02\n", "video_id,predicted_sign"),          # columns
])
def test_invalid_submissions(tmp_path, body, header):
    t = _template(tmp_path, ["a", "b"])
    s = tmp_path / "s.csv"
    s.write_text(header + "\n" + body, encoding="utf-8")
    with pytest.raises(ValueError):
        delivery.validate_submission(t, s)


def test_write_submission_valid_and_no_overwrite(tmp_path):
    t = _template(tmp_path, ["b", "a"])
    out = tmp_path / "submission.csv"
    r = delivery.write_submission(t, ["a", "b"], np.eye(5)[[1, 4]], out)
    assert r["rows"] == 2
    assert out.read_text().splitlines() == ["video_id,predicted_sign", "b,sign_05", "a,sign_02"]
    with pytest.raises(FileExistsError):
        delivery.write_submission(t, ["a", "b"], np.eye(5)[[1, 4]], out)
