import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from conftest import training_fixture
from lsc5 import budget
from lsc5.data import make_splits
from lsc5.features import prepare_stats
from lsc5.io import atomic_json, read_json
from lsc5.restore import predict_train
from lsc5.training import balanced_batches, learning_rate, run_pilot


def test_balanced_epoch_covers_every_id_once_including_remainder():
    labels = np.tile(np.repeat(np.arange(5), 75), 2)
    signers = np.repeat(["M03", "M04"], 375)
    batches = list(balanced_batches(labels, signers, 17, 0))
    assert [len(b) for b in batches] == [40] * 18 + [30]
    assert sorted(np.concatenate(batches).tolist()) == list(range(750))
    for batch in batches:
        counts = [sum((signers[batch] == s) & (labels[batch] == c)) for s in set(signers) for c in range(5)]
        assert len(set(counts)) == 1
    again = list(balanced_batches(labels, signers, 17, 0))
    assert all(np.array_equal(a, b) for a, b in zip(batches, again))
    assert learning_rate(0) == pytest.approx(.0002)
    assert learning_rate(79) == pytest.approx(.00001)


def test_pilot_requires_allocated_slurm_and_restores_from_originals(tmp_path, monkeypatch):
    train, manifest = training_fixture(tmp_path / "source", per_class=40)
    cache = tmp_path / "stats"
    prepare_stats(train, manifest, cache)
    split = make_splits(manifest)[0]
    ledger = tmp_path / "budget.json"
    budget.initialize(ledger)
    budget.reserve(ledger, "fixture")
    budget.bind_job(ledger, "fixture", "123")
    output = tmp_path / "run"
    monkeypatch.delenv("SLURM_JOB_ID", raising=False)
    with pytest.raises(ValueError, match="Slurm"):
        run_pilot(manifest, split, cache, ledger, "fixture", output)
    monkeypatch.setenv("SLURM_JOB_ID", "123")
    monkeypatch.setenv("SLURM_CPUS_PER_TASK", "4")
    metrics = run_pilot(manifest, split, cache, ledger, "fixture", output)
    assert metrics["metric_scope"] == "two_epoch_diagnostic_not_candidate"
    assert metrics["measured_step_count"] >= 10
    assert metrics["batch60_probe"]["backward_optimizer_step"]
    assert metrics["train_clips"] == 400 and metrics["validation_clips"] == 200
    manifest_path = tmp_path / "manifest.json"
    atomic_json(manifest_path, manifest)
    # Removing the cache proves the separate process reconstructs R0 from originals.
    (cache / "stats.npz").unlink()
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"))
    command = [sys.executable, "-m", "lsc5.cli", "predict-train", "--data-root", str(train.parent),
               "--manifest", str(manifest_path), "--run", str(output), "--out", str(tmp_path / "restored.npz")]
    result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stderr
    assert '"cache_required": false' in result.stdout
    with np.load(tmp_path / "restored.npz", allow_pickle=False) as restored:
        assert restored["probabilities"].shape == (200, 5)
        np.testing.assert_allclose(restored["probabilities"].sum(1), 1, atol=1e-6)
    assert read_json(ledger)["attempts"][0]["state"] == "committed"
    assert read_json(output / "run.json")["status"] == "complete"
    with pytest.raises(ValueError, match="already claimed"):
        run_pilot(manifest, split, cache, ledger, "fixture", tmp_path / "other_run")
    complete = read_json(output / "run.json")
    for changes in [{"files": {}}, {"feature_schema_id": "wrong"}, {"recipe": "wrong"}]:
        atomic_json(output / "run.json", dict(complete, **changes))
        target = tmp_path / "must_not_publish.npz"
        with pytest.raises(ValueError):
            predict_train(train, manifest, output, target)
        assert not target.exists()
    atomic_json(output / "run.json", complete)
