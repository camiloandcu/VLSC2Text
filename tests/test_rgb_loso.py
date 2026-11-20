"""Synthetic contract checks; these never establish real RGB accuracy or GPU speed."""
from pathlib import Path
import hashlib
import os

import numpy as np
import pytest

from conftest import training_fixture
from lsc5 import budget, rgb_loso_budget as rb
from lsc5.data import make_splits
from lsc5.io import atomic_json, digest, producer_hash, read_json, sha256
from lsc5.rgb_frames import decode, indices


def test_channel_scaler_pyramid_and_heldout_immutability():
    from lsc5.rgb_head import fit_scaler, pyramid
    x = np.random.default_rng(5).normal(size=(4, 16, 384)).astype(np.float32)
    x[:, :, 0] = 3
    state = fit_scaler(x[:3], ["a", "b", "c"])
    np.testing.assert_allclose(state["mean"], x[:3].astype(np.float64).mean((0, 1)), atol=2e-8)
    assert state["scale"][0] == 1
    before = {k:v.copy() for k, v in state.items()}
    features = pyramid(x[3:], state)
    reverse = pyramid(x[3:], state, reverse=True)
    assert features.shape == (1, 1152) and features.dtype == np.float32
    np.testing.assert_array_equal(features[:, :384], reverse[:, :384])
    np.testing.assert_array_equal(features[:, 384:768], reverse[:, 768:])
    scaled = (x[3:]-state["mean"])/state["scale"]
    np.testing.assert_array_equal(features[:, :384], scaled.mean(1, dtype=np.float64).astype(np.float32))
    for k in state:
        np.testing.assert_array_equal(state[k], before[k])


@pytest.fixture
def full_cache(tmp_path, monkeypatch):
    from lsc5 import rgb_pilot
    from lsc5.rgb_encoder import COMMIT, SOURCE_INVENTORY_HASH, WEIGHT_SHA256
    train, manifest = training_fixture(tmp_path/"dataset", per_class=75)
    ledger = tmp_path/"budget.json"
    budget.initialize(ledger)
    rb.enable(ledger, manifest)
    rb.reserve(ledger, "extract", "extract", manifest)
    claim = rb.claim_gpu(ledger, "extract", str(tmp_path/"execution"), rb.machine_identity())
    class SyntheticEncoder:
        def __init__(self, _):
            self.identity = {"commit": COMMIT, "source_inventory_hash": SOURCE_INVENTORY_HASH,
                "weight_sha256": WEIGHT_SHA256, "architecture": "dinov2_vits14_no_registers", "eval": True,
                "frozen": True, "weight_url": "https://dl.fbaipublicfiles.com/dinov2/dinov2_vits14/dinov2_vits14_pretrain.pth"}
            self.versions = {"torch": "2.4.1+cu121", "torchvision": "0.19.1+cu121", "pillow": "11.3.0"}
            self.parameter_count = 1
        def extract(self, pixels, batch_size=4):
            v = np.random.default_rng(int(pixels[0, 0, 0, 0])).normal(size=(len(pixels), 384)).astype(np.float32)
            return v, [{"forward_seconds": 0.} for _ in range(0, len(pixels), 4)]
        def memory_stats(self):
            return {"torch_peak_allocated_bytes": 0, "torch_peak_reserved_bytes": 0}
    def synthetic_decode(_, sample):
        pixels = np.full((16, 224, 224, 3), sum(map(ord, sample["id"])) % 255, dtype=np.uint8)
        return pixels, {"id": sample["id"], "video_sha256": sample["video_sha256"], "video_frames": 3,
            "indices": indices(3).tolist(), "pixels_sha256": hashlib.sha256(pixels.tobytes()).hexdigest()}
    monkeypatch.setattr(rgb_pilot, "Encoder", SyntheticEncoder)
    monkeypatch.setattr(rgb_pilot, "decode", synthetic_decode)
    monkeypatch.setattr(rgb_pilot, "require_supervisor", lambda: None)
    root = tmp_path/"full"
    rgb_pilot.run_pilot(train, manifest, None, claim, root, coverage="full1125")
    rb.settle_gpu(ledger, {"attempt_id": "extract", "reservation_hash": claim["reservation_hash"],
        "producer_hash": producer_hash(), "terminal_state": "COMPLETED", "actual_seconds": 5,
        "stages": [{"name": "extract", "returncode": 0}], "full_result_sha256": sha256(root/"run.json")})
    return manifest, ledger, root/"cache"


def test_full_coverage_head_pilot_restore_and_measured_gate(full_cache, tmp_path, monkeypatch):
    from lsc5.rgb_pilot import load_cache
    from lsc5.rgb_head_training import fit
    from lsc5.rgb_head_restore import load_run, restore_cache
    from lsc5.evaluation import aggregate_oof
    manifest, ledger, cache = full_cache
    meta = load_cache(cache, manifest, coverage="full1125")
    assert len(meta["ids"]) == 1125
    with pytest.raises(ValueError, match="coverage"):
        load_cache(cache, manifest)
    with pytest.raises(ValueError, match="gate"):
        rb.reserve(ledger, "earlyfull", "M02", manifest)
    with pytest.raises(ValueError, match="Three completed"):
        rb.reserve(ledger, "earlyrestore", "restore", manifest)
    rb.reserve(ledger, "pilot", "pilot", manifest)
    budget.bind_job(ledger, "pilot", "123")
    monkeypatch.setenv("SLURM_JOB_ID", "123")
    monkeypatch.setenv("SLURM_CPUS_PER_TASK", "4")
    split = make_splits(manifest)[0]
    root = tmp_path/"head"
    metrics = fit(manifest, split, cache, ledger, "pilot", root, pilot=True)
    run, _, state = load_run(manifest, root)
    assert metrics["train_clips"] == 750 and state["fit_ids"].tolist() == split["train_ids"]
    assert metrics["measured_step_count"] == 33 and len(metrics["training_losses"]) == 2
    assert metrics["batch60_probe"]["discarded_copy"]
    receipt = restore_cache(manifest, root, cache, root/"cache_restoration.json")
    assert receipt["max_abs_difference"] == 0 and receipt["source"] == "immutable_full_train_cache"
    budget.settle(ledger, "pilot", 10, "123", "COMPLETED")
    with pytest.raises(FileNotFoundError):
        rb.admit(ledger, manifest, root, tmp_path/"missing.json")
    gate = rb.admit(ledger, manifest, root, root/"cache_restoration.json")
    assert gate["projected_fold_seconds_with_margin"] <= 900
    rb.reserve(ledger, "fold02", "M02", manifest)
    with pytest.raises(ValueError, match="One attempt"):
        rb.reserve(ledger, "repeat02", "M02", manifest)
    with pytest.raises(ValueError, match="original-video"):
        aggregate_oof(manifest, [root]*3, tmp_path/"forbidden_oof")
    # A correctly rehashed artifact with validation IDs as fit IDs must still fail.
    saved = {k:v.copy() for k, v in state.items()}
    saved["fit_ids"] = np.asarray(split["validation_ids"])
    np.savez_compressed(root/"preprocessor.npz", **saved)
    run["files"]["preprocessor.npz"] = sha256(root/"preprocessor.npz")
    atomic_json(root/"run.json", run)
    with pytest.raises(ValueError, match="scaler"):
        load_run(manifest, root)
    original = read_json(cache/"metadata.json")
    atomic_json(cache/"metadata.json", dict(original, coverage="pilot30"))
    with pytest.raises(ValueError, match="coverage"):
        load_cache(cache, manifest, coverage="full1125")


def test_new_gpu_claim_guards_history_and_deadline(tmp_path):
    _, manifest = training_fixture(tmp_path/"source", per_class=75)
    path = tmp_path/"ledger.json"
    budget.initialize(path)
    prior = read_json(path)
    rb.enable(path, manifest)
    row = rb.reserve(path, "full", "extract", manifest)
    assert row["reserved_seconds"] == 18060 and prior["final_reserve_seconds"] == read_json(path)["final_reserve_seconds"]
    with pytest.raises(ValueError):
        budget.bind_job(path, "full", "23")
    claim = rb.claim_gpu(path, "full", str(tmp_path/"run"), rb.machine_identity())
    rb.validate_gpu_reservation(claim, manifest)
    with pytest.raises(ValueError, match="Invalid"):
        rb.validate_gpu_reservation(dict(claim, time_limit_seconds=600), manifest)
    with pytest.raises(ValueError, match="unclaimed"):
        rb.claim_gpu(path, "full", str(tmp_path/"run"), rb.machine_identity())
    failure = {"attempt_id": "full", "reservation_hash": claim["reservation_hash"],
               "producer_hash": producer_hash(), "terminal_state": "FAILED", "actual_seconds": 3}
    rb.settle_gpu(path, failure)
    with pytest.raises(ValueError):
        rb.settle_gpu(path, failure)
    assert budget.totals(read_json(path)) == (3, 0)


def test_delayed_claim_and_rehashed_baseline_cannot_bypass_gates(tmp_path, monkeypatch):
    from lsc5.evaluation import compare_oof
    _, manifest = training_fixture(tmp_path/"source", per_class=75)
    path = tmp_path/"ledger.json"
    budget.initialize(path)
    monkeypatch.setattr(rb.time, "time", lambda: rb.CUTOFF-100000)
    rb.enable(path, manifest)
    rb.reserve(path, "extract", "extract", manifest)
    monkeypatch.setattr(rb.time, "time", lambda: rb.CUTOFF-600)
    with pytest.raises(ValueError, match="calendar"):
        rb.claim_gpu(path, "extract", str(tmp_path/"out"), rb.machine_identity())
    assert not read_json(path)["attempts"][0]["claimed"]
    baseline, candidate = tmp_path/"baseline", tmp_path/"candidate"
    baseline.mkdir(); candidate.mkdir()
    atomic_json(baseline/"report.json", {"recipe": "raw_stats_mlp_v2"})
    atomic_json(candidate/"report.json", {"recipe": "rgb_pyramid_mlp_v2"})
    with pytest.raises(ValueError, match="original frozen baseline"):
        compare_oof(manifest, candidate, baseline, tmp_path/"no_comparison.json", sha256(baseline/"report.json"))
