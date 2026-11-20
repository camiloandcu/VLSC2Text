"""Closed temporal pilot/full fits. Held-out predictions are made only at the end."""
import copy
import os
from pathlib import Path
import random
import resource
import time

import numpy as np
import torch
from torch import nn

from . import budget
from .data import CLASSES, validate_baseline_manifest, validate_split
from .io import atomic_json, digest, producer_hash, sha256
from .opaque_features import frame_scaler, load_sequences, prepare_sequences, transform
from .temporal import HYPERPARAMETERS, OpaqueTCN, collate, infer
from .training import balanced_batches, configure_cpu, learning_rate


def fit_temporal(manifest, split, cache, ledger, attempt, output, pilot=False, train_zip=None):
    validate_baseline_manifest(manifest)
    validate_split(manifest, split)
    if pilot and split['outer_signer'] != 'M02':
        raise ValueError('Temporal pilot is fixed to M02')
    job = os.environ.get('SLURM_JOB_ID')
    if not job or os.environ.get('SLURM_CPUS_PER_TASK') != '4':
        raise ValueError('Four allocated Slurm CPUs required')
    reservation = budget.claim_attempt(ledger, attempt, job, output, expected_scope=budget.TEMPORAL_SCOPE)
    expected_limit = 300 if pilot else 900
    if reservation['time_limit_seconds'] != expected_limit:
        raise ValueError('Reservation time limit disagrees with profile')
    if not pilot:
        budget.check_temporal_gate(ledger, producer_hash(), manifest["manifest_hash"])
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    started = time.perf_counter()
    epochs = 2 if pilot else 80
    run = {'phase': 'temporal_pilot' if pilot else 'outer_temporal', 'epochs': epochs,
           'nominal_recipe_epochs': 80, 'seed': 17, 'recipe': 'opaque_tcn_v1',
           'feature_schema_id': 'opaque_sequence_v1', 'protocol_revision': 'R2.2',
           'fit_role': 'outer', 'classes': CLASSES, 'hyperparameters': HYPERPARAMETERS,
           'producer_hash': producer_hash(), 'manifest_hash': manifest['manifest_hash'],
           'split_hash': split['split_hash'], 'fit_ids_hash': digest(split['train_ids']),
           'validation_ids_hash': digest(split['validation_ids']), 'job_id': job,
           'attempt_id': attempt, 'budget_scope': budget.TEMPORAL_SCOPE, 'status': 'running'}
    atomic_json(output/'run.json', run)
    atomic_json(output/'split.json', split)
    try:
        prep = time.perf_counter()
        if not Path(cache).exists():
            if not pilot or train_zip is None:
                raise ValueError('Only pilot can prepare cache from explicit train archive')
            prepare_sequences(manifest, cache, train_zip=train_zip)
        prep_seconds = time.perf_counter()-prep
        metrics = _fit(manifest, split, cache, output, epochs)
        metrics.update(cache_preparation_seconds=prep_seconds,
                       process_seconds_before_final_metadata=time.perf_counter()-started,
                       peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        atomic_json(output/'metrics.json', metrics)
        run.update(status='complete', files={n: sha256(output/n) for n in
                   ['model.pt', 'preprocessor.npz', 'validation.npz', 'split.json', 'metrics.json']})
        atomic_json(output/'run.json', run)
        return metrics
    except BaseException as e:
        run.update(status='failed', error_type=type(e).__name__, error=str(e))
        atomic_json(output/'run.json', run)
        raise


def _fit(manifest, split, cache, output, epochs):
    configure_cpu()
    random.seed(17)
    np.random.seed(17)
    torch.manual_seed(17)
    torch.use_deterministic_algorithms(True)
    t = time.perf_counter()
    sequences = load_sequences(cache, manifest)
    lookup = {s['id']: i for i, s in enumerate(manifest['samples'])}
    fit = [lookup[i] for i in split['train_ids']]
    val = [lookup[i] for i in split['validation_ids']]
    scaler = frame_scaler([sequences[i] for i in fit], split['train_ids'])
    train_x = [transform(sequences[i], scaler) for i in fit]
    labels = np.asarray([CLASSES.index(s['label']) for s in manifest['samples']], dtype=np.int64)
    y = torch.from_numpy(labels[fit])
    signers = [manifest['samples'][i]['signer'] for i in fit]
    io_seconds = time.perf_counter()-t
    model = OpaqueTCN()
    opt = torch.optim.AdamW(model.parameters(), lr=.001, weight_decay=.001)
    ce = nn.CrossEntropyLoss()
    steps, losses, sizes, epoch_seconds = [], [], [], []
    for epoch in range(epochs):
        t = time.perf_counter()
        model.train()
        for group in opt.param_groups:
            group['lr'] = learning_rate(epoch)
        total = 0.
        for batch in balanced_batches(y.numpy(), signers, 17, epoch):
            tick = time.perf_counter()
            opt.zero_grad(set_to_none=True)
            loss = ce(model(*collate([train_x[i] for i in batch])), y[batch.copy()])
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1)
            opt.step()
            total += float(loss.detach())*len(batch)
            steps.append(time.perf_counter()-tick)
            sizes.append(len(batch))
        losses.append(total/len(fit))
        epoch_seconds.append(time.perf_counter()-t)
    if len(steps[5:]) < 10:
        raise ValueError('Insufficient timing steps')
    t = time.perf_counter()
    logits, probs = infer(model, [transform(sequences[i], scaler) for i in val])
    eval_seconds = time.perf_counter()-t
    probe = None
    if epochs == 2:
        clone = copy.deepcopy(model).train()
        optimizer = torch.optim.AdamW(clone.parameters(), lr=.001, weight_decay=.001)
        tick = time.perf_counter()
        loss = ce(clone(*collate(train_x[:60])), y[:60])
        loss.backward()
        nn.utils.clip_grad_norm_(clone.parameters(), 1)
        optimizer.step()
        probe = {'size': 60, 'fit_only': True, 'discarded_copy': True,
                 'backward_optimizer_step': True, 'seconds': time.perf_counter()-tick}
        del clone, optimizer
    tick = time.perf_counter()
    torch.save(model.state_dict(), output/'model.pt')
    np.savez_compressed(output/'preprocessor.npz', **scaler)
    np.savez_compressed(output/'validation.npz', ids=np.asarray(split['validation_ids']),
                        labels=labels[val], logits=logits, probabilities=probs)
    write_seconds = time.perf_counter()-tick
    return {'metric_scope': 'two_epoch_diagnostic_not_candidate' if epochs == 2 else 'fixed_80_epoch_outer_fold',
            'train_clips': len(fit), 'validation_clips': len(val), 'training_losses': losses,
            'validation_accuracy': float((probs.argmax(1) == labels[val]).mean()),
            'batch_sizes': sizes, 'epoch_seconds': epoch_seconds,
            'warmup_measurement_steps': 5, 'measured_step_count': len(steps[5:]),
            'post_warmup_step_max_seconds': max(steps[5:]),
            'post_warmup_step_median_seconds': float(np.median(steps[5:])),
            'io_and_scaling_seconds': io_seconds, 'evaluation_seconds': eval_seconds,
            'artifact_write_seconds': write_seconds, 'batch60_probe': probe,
            'projected_fold_seconds_with_margin': 1.5*(80*19*max(steps[5:])+io_seconds+eval_seconds+write_seconds),
            'parameter_count': sum(p.numel() for p in model.parameters())}
