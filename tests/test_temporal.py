import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
import torch

from conftest import training_fixture
from lsc5 import budget
from lsc5.data import make_splits
from lsc5.io import atomic_json, producer_hash, read_json, sha256
from lsc5.opaque_features import frame_scaler, prepare_sequences, transform
from lsc5.temporal import OpaqueTCN, collate
from lsc5.temporal_training import fit_temporal
from lsc5.training import configure_cpu


def test_temporal_padding_batch_invariance_and_real_zero_frames():
    configure_cpu()
    torch.manual_seed(17)
    rng = np.random.default_rng(9)
    short = rng.normal(size=(7, 1662)).astype(np.float32)
    long = rng.normal(size=(19, 1662)).astype(np.float32)
    model = OpaqueTCN().eval()
    with torch.inference_mode():
        alone = model(*collate([short]))
        together = model(*collate([short, long]))[:1]
        x, mask = collate([short])
        padded = model(torch.cat([x, torch.zeros(1, 31, 1662)], 1),
                       torch.cat([mask, torch.zeros(1, 31, dtype=torch.bool)], 1))
    torch.testing.assert_close(alone, together, atol=1e-6, rtol=0)
    torch.testing.assert_close(alone, padded, atol=1e-6, rtol=0)
    zero = np.zeros((1, 1662), dtype=np.float64)
    ones = np.ones((3, 1662), dtype=np.float64)
    scaler = frame_scaler([zero, ones], ['zero', 'ones'])
    np.testing.assert_array_equal(scaler['mean'], np.full(1662, .75, dtype=np.float32))
    np.testing.assert_allclose(scaler['scale'], np.sqrt(.1875), atol=1e-7)
    real_zero = transform(zero, scaler)
    assert np.any(real_zero != 0)
    _, mask = collate([real_zero, transform(ones, scaler)])
    assert mask[0].tolist() == [True, False, False]


def test_temporal_pilot_original_restore_and_budget_gate(tmp_path, monkeypatch):
    train, manifest = training_fixture(tmp_path/'source', per_class=75)
    cache = tmp_path/'sequences'
    prepare_sequences(manifest, cache, train_root=train)
    split = make_splits(manifest)[0]
    ledger = tmp_path/'budget.json'
    budget.initialize(ledger)
    budget.enable_temporal(ledger)
    budget.enable_temporal(ledger)
    with pytest.raises(ValueError, match='pilot gate'):
        budget.reserve_temporal(ledger, 'forbidden', 30)
    with pytest.raises(ValueError, match='grace'):
        budget.reserve_temporal(ledger, 'too_much_grace', 61, pilot=True)
    budget.reserve_temporal(ledger, 'pilot', 30, pilot=True)
    budget.bind_job(ledger, 'pilot', '123')
    monkeypatch.setenv('SLURM_JOB_ID', '123')
    monkeypatch.setenv('SLURM_CPUS_PER_TASK', '4')
    run = tmp_path/'run'
    metrics = fit_temporal(manifest, split, cache, ledger, 'pilot', run, pilot=True)
    assert len(metrics['training_losses']) == 2
    assert metrics['measured_step_count'] == 33
    assert metrics['batch_sizes'] == ([40]*18+[30])*2
    assert metrics['batch60_probe']['discarded_copy']
    with pytest.raises(ValueError, match='reconciled'):
        budget.admit_temporal(ledger, manifest, run)
    budget.settle(ledger, 'pilot', 5, '123', 'COMPLETED')
    with pytest.raises(ValueError, match='restoration receipt'):
        budget.admit_temporal(ledger, manifest, run)
    manifest_path = tmp_path/'manifest.json'
    atomic_json(manifest_path, manifest)
    # Remove training cache: replay must use original NPY, in another process.
    (cache/'values.npy').rename(cache/'hidden.npy')
    restored = tmp_path/'restored.npz'
    result = subprocess.run([sys.executable, '-m', 'lsc5.cli', 'predict-train',
                             '--data-root', str(train.parent), '--manifest', str(manifest_path),
                             '--run', str(run), '--out', str(restored)], capture_output=True,
                            text=True, env=dict(os.environ, PYTHONPATH=str(Path.cwd()/'src')), timeout=60)
    assert result.returncode == 0, result.stderr
    receipt = json.loads(result.stdout)
    assert receipt['validation_clips'] == 375 and receipt['max_abs_difference'] <= 1e-6
    assert not receipt['cache_required']
    receipt_path = tmp_path/'restoration.json'
    atomic_json(receipt_path, receipt)
    gate = budget.admit_temporal(ledger, manifest, run, receipt_path)
    assert gate['projected_fold_seconds_with_margin'] < 900
    assert gate['restored_sha256'] == sha256(restored)
    with pytest.raises(ValueError, match='manifest'):
        budget.check_temporal_gate(ledger, producer_hash(), 'wrong')
    (cache/'hidden.npy').rename(cache/'values.npy')
    runs = []
    for i, outer in enumerate(make_splits(manifest)):
        attempt, job = 'full'+str(i), str(124+i)
        budget.reserve_temporal(ledger, attempt, 30)
        budget.bind_job(ledger, attempt, job)
        monkeypatch.setenv('SLURM_JOB_ID', job)
        target = tmp_path/attempt
        full = fit_temporal(manifest, outer, cache, ledger, attempt, target)
        assert len(full['training_losses']) == 80 and len(full['batch_sizes']) == 1520
        runs.append(target)
    with pytest.raises(ValueError, match='count'):
        budget.reserve_temporal(ledger, 'full4', 30)
    from lsc5.evaluation import aggregate_oof, compare_oof
    report = aggregate_oof(manifest, runs, tmp_path/'candidate')
    assert report['experiment_id'] == 'R2-E02O' and report['overall']['clips'] == 1125
    # Isolate comparison boundary from the baseline trainer, already covered elsewhere.
    baseline = tmp_path/'baseline'
    baseline.mkdir()
    (baseline/'oof.npz').write_bytes((tmp_path/'candidate/oof.npz').read_bytes())
    prior = dict(report, recipe='raw_stats_mlp_v2', experiment_id='R2-E01', protocol_revision='R2.1')
    atomic_json(baseline/'report.json', prior)
    anchor = sha256(baseline/'report.json')
    paired = compare_oof(manifest, tmp_path/'candidate', baseline, tmp_path/'paired.json', anchor)
    assert paired['delta_correct'] == 0 and not paired['accuracy_promotion']
    with pytest.raises(ValueError, match='Frozen baseline'):
        compare_oof(manifest, tmp_path/'candidate', baseline, tmp_path/'bad.json', '0'*64)
    atomic_json(tmp_path/'candidate/report.json', dict(report, sources=[]))
    with pytest.raises(ValueError, match='sources'):
        compare_oof(manifest, tmp_path/'candidate', baseline, tmp_path/'bad.json', anchor)
    atomic_json(tmp_path/'candidate/report.json', dict(report, experiment_id='diagnostic'))
    with pytest.raises(ValueError, match='identity'):
        compare_oof(manifest, tmp_path/'candidate', baseline, tmp_path/'bad.json', anchor)
    with pytest.raises(ValueError, match='Diagnostic'):
        aggregate_oof(manifest, [run, run, run], tmp_path/'oof')
    original = read_json(run/'run.json')
    atomic_json(run/'run.json', dict(original, files={}))
    from lsc5.temporal_restore import load_temporal_run
    with pytest.raises(ValueError, match='inventory'):
        load_temporal_run(manifest, run)


def test_retained_values_do_not_change_temporal_fit(tmp_path, monkeypatch):
    from lsc5.temporal_training import _fit
    train, manifest = training_fixture(tmp_path/'source', per_class=75)
    split = make_splits(manifest)[0]
    rng = np.random.default_rng(98)
    values = [rng.normal(size=(3, 1662)) for _ in manifest['samples']]
    monkeypatch.setattr('lsc5.temporal_training.load_sequences', lambda *_: values)
    first, second = tmp_path/'a', tmp_path/'b'
    first.mkdir(); second.mkdir()
    a = _fit(manifest, split, None, first, 2)
    ids = set(split['validation_ids'])
    values = [v+100 if s['id'] in ids else v for s, v in zip(manifest['samples'], values)]
    b = _fit(manifest, split, None, second, 2)
    assert a['training_losses'] == b['training_losses']
    aw = torch.load(first/'model.pt', weights_only=True)
    bw = torch.load(second/'model.pt', weights_only=True)
    assert all(torch.equal(aw[k], bw[k]) for k in aw)
    with np.load(first/'preprocessor.npz') as sa, np.load(second/'preprocessor.npz') as sb:
        assert all(np.array_equal(sa[k], sb[k]) for k in sa.files)
    with np.load(first/'validation.npz') as va, np.load(second/'validation.npz') as vb:
        assert not np.array_equal(va['logits'], vb['logits'])
