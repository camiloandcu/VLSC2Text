import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from conftest import training_fixture
from lsc5 import budget
from lsc5.data import make_splits
from lsc5.evaluation import aggregate_oof, classification_metrics
from lsc5.features import prepare_stats
from lsc5.io import atomic_json, read_json, sha256
from lsc5.training import run_baseline


def test_baseline_scope_preserves_history_and_rejects_cross_profile(tmp_path):
    ledger = tmp_path / "budget.json"
    budget.initialize(ledger)
    budget.reserve(ledger, "prior")
    budget.bind_job(ledger, "prior", "1")
    budget.settle(ledger, "prior", 3, "1", "COMPLETED")
    before = read_json(ledger)
    with pytest.raises(ValueError, match="authorized"):
        budget.reserve(ledger, "not_yet", scope=budget.BASELINE_SCOPE)
    budget.enable_baseline(ledger)
    budget.enable_baseline(ledger)
    after = read_json(ledger)
    assert after["attempts"] == before["attempts"]
    assert after["final_reserve_seconds"] == 43200
    assert after["scope_limits_seconds"][budget.BASELINE_SCOPE] == 3600
    budget.reserve(ledger, "new", scope=budget.BASELINE_SCOPE)
    budget.bind_job(ledger, "new", "2")
    with pytest.raises(ValueError, match="scope"):
        budget.claim_attempt(ledger, "new", "2", tmp_path / "bad")
    assert not read_json(ledger)["attempts"][-1]["claimed"]
    # An interrupted job can end before claim; it still consumes its measured time.
    budget.settle(ledger, "new", 7, "2", "PREEMPTED")
    assert budget.totals(read_json(ledger)) == (10, 0)
    changed = read_json(ledger)
    changed["scope_limits_seconds"][budget.BASELINE_SCOPE] = 1
    atomic_json(ledger, changed)
    with pytest.raises(ValueError, match="cannot be changed"):
        budget.enable_baseline(ledger)


def test_complete_baseline_restore_oof_and_invalid_artifacts(tmp_path, monkeypatch):
    train, manifest = training_fixture(tmp_path / "data", per_class=75)
    cache = tmp_path / "stats"
    prepare_stats(train, manifest, cache)
    ledger = tmp_path / "budget.json"
    budget.initialize(ledger)
    budget.enable_baseline(ledger)
    runs = []
    for i, split in enumerate(make_splits(manifest)):
        attempt = f"baseline-{i}"
        job_id = str(200 + i)
        budget.reserve(ledger, attempt, scope=budget.BASELINE_SCOPE)
        budget.bind_job(ledger, attempt, job_id)
        monkeypatch.setenv("SLURM_JOB_ID", job_id)
        monkeypatch.setenv("SLURM_CPUS_PER_TASK", "4")
        output = tmp_path / attempt
        metrics = run_baseline(manifest, split, cache, ledger, attempt, output)
        assert len(metrics["training_losses"]) == 80
        assert len(metrics["batch_sizes"]) == 1520
        assert metrics["batch60_probe"] is None
        assert metrics["metric_scope"] == "fixed_80_epoch_outer_fold"
        assert read_json(output / "run.json")["epochs"] == 80
        with np.load(output / "preprocessor.npz") as scaler:
            assert scaler["fit_ids"].tolist() == split["train_ids"]
        runs.append(output)
    manifest_path = tmp_path / "manifest.json"
    atomic_json(manifest_path, manifest)
    (cache / "stats.npz").unlink()
    result = subprocess.run([sys.executable, "-m", "lsc5.cli", "predict-train",
                             "--data-root", str(train.parent), "--manifest", str(manifest_path),
                             "--run", str(runs[0]), "--out", str(tmp_path / "restored.npz")],
                            env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src")),
                            capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stderr
    report = aggregate_oof(manifest, runs, tmp_path / "oof")
    assert report["complete"] and report["overall"]["clips"] == 1125
    with np.load(tmp_path / "oof/oof.npz") as oof:
        assert len(set(oof["ids"].tolist())) == 1125
        assert oof["logits"].shape == (1125, 5)
        assert report["overall"] == classification_metrics(oof["labels"], oof["predictions"])
    for invalid in [runs[:2], [runs[0], runs[0], runs[2]]]:
        with pytest.raises(ValueError):
            aggregate_oof(manifest, invalid, tmp_path / "must_not_publish")
    run_path = runs[0] / "run.json"
    original = read_json(run_path)
    atomic_json(run_path, dict(original, phase="diagnostic_pilot", epochs=2))
    with pytest.raises(ValueError, match="Diagnostic"):
        aggregate_oof(manifest, runs, tmp_path / "must_not_publish")
    atomic_json(run_path, dict(original, hyperparameters=dict(original["hyperparameters"], lr=.5)))
    with pytest.raises(ValueError, match="recipe"):
        aggregate_oof(manifest, runs, tmp_path / "must_not_publish")
    atomic_json(run_path, original)
    validation = runs[0] / "validation.npz"
    original_bytes = validation.read_bytes()
    with np.load(validation) as archive:
        arrays = {k: archive[k] for k in archive.files}
    changes = [dict(probabilities=np.zeros_like(arrays["probabilities"])),
               dict(probabilities=np.full_like(arrays["probabilities"], .2)),
               dict(logits=np.zeros((375, 4), dtype=np.float32)),
               dict(labels=(arrays["labels"] + 1) % 5),
               dict(ids=arrays["ids"][::-1])]
    for change in changes:
        np.savez_compressed(validation, **dict(arrays, **change))
        altered = dict(original, files=dict(original["files"], **{"validation.npz": sha256(validation)}))
        atomic_json(run_path, altered)
        with pytest.raises(ValueError):
            aggregate_oof(manifest, runs, tmp_path / "must_not_publish")
        assert not (tmp_path / "must_not_publish").exists()
    validation.write_bytes(original_bytes)
    atomic_json(run_path, original)


def test_incomplete_cohort_cannot_claim_attempt_or_publish_oof(tmp_path):
    _, manifest = training_fixture(tmp_path / "small", per_class=6)
    with pytest.raises(ValueError, match="1125"):
        run_baseline(manifest, make_splits(manifest)[0], tmp_path / "cache",
                     tmp_path / "ledger", "attempt", tmp_path / "run")
    with pytest.raises(ValueError, match="1125"):
        aggregate_oof(manifest, [], tmp_path / "oof")
    assert not (tmp_path / "oof").exists() and not (tmp_path / "ledger").exists()
