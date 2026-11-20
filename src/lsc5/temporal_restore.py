"""Strict opaque TCN artifacts and independent replay from original train NPY."""
from pathlib import Path
import os
import tempfile

import numpy as np
import torch

from .data import CLASSES, validate_baseline_manifest, validate_split
from .io import digest, producer_hash, read_json, sha256
from .opaque_features import originals, transform
from .temporal import HYPERPARAMETERS, OpaqueTCN, infer
from .training import configure_cpu


def load_temporal_run(manifest, directory):
    validate_baseline_manifest(manifest)
    root = Path(directory)
    run, split = read_json(root/'run.json'), read_json(root/'split.json')
    validate_split(manifest, split)
    expected = {'recipe': 'opaque_tcn_v1', 'feature_schema_id': 'opaque_sequence_v1',
                'protocol_revision': 'R2.2', 'fit_role': 'outer', 'status': 'complete',
                'seed': 17, 'nominal_recipe_epochs': 80, 'classes': CLASSES,
                'hyperparameters': HYPERPARAMETERS, 'producer_hash': producer_hash(),
                'manifest_hash': manifest['manifest_hash'], 'split_hash': split['split_hash'],
                'fit_ids_hash': digest(split['train_ids']), 'validation_ids_hash': digest(split['validation_ids'])}
    phases = {'temporal_pilot': 2, 'outer_temporal': 80}
    if (any(run.get(k) != v for k, v in expected.items()) or run.get('phase') not in phases
            or run.get('epochs') != phases[run['phase']]):
        raise ValueError('Incompatible temporal run identity')
    required = {'model.pt', 'preprocessor.npz', 'validation.npz', 'split.json', 'metrics.json'}
    if set(run.get('files', {})) != required:
        raise ValueError('Incomplete temporal inventory')
    for n, value in run['files'].items():
        if sha256(root/n) != value:
            raise ValueError('Temporal artifact hash mismatch')
    with np.load(root/'preprocessor.npz', allow_pickle=False) as state:
        scaler = {k: state[k] for k in ['mean', 'scale', 'fit_ids']}
    if (scaler['fit_ids'].tolist() != split['train_ids']
            or any(scaler[k].shape != (1662,) or scaler[k].dtype != np.float32
                   or not np.isfinite(scaler[k]).all() for k in ['mean', 'scale'])
            or np.any(scaler['scale'] <= 0)):
        raise ValueError('Invalid temporal scaler')
    return run, split, scaler


def predict_temporal(train_root, manifest, directory, output):
    _, split, scaler = load_temporal_run(manifest, directory)
    by_id = {s['id']: s for s in manifest['samples']}
    x = [transform(v, scaler) for v in originals(train_root, [by_id[i] for i in split['validation_ids']])]
    configure_cpu()
    model = OpaqueTCN()
    model.load_state_dict(torch.load(Path(directory)/'model.pt', weights_only=True, map_location='cpu'))
    _, probs = infer(model, x)
    with np.load(Path(directory)/'validation.npz', allow_pickle=False) as reference:
        if reference['ids'].tolist() != split['validation_ids'] or reference['probabilities'].shape != probs.shape:
            raise ValueError('Temporal reference coverage mismatch')
        difference = float(np.max(np.abs(reference['probabilities']-probs)))
        if not np.allclose(reference['probabilities'], probs, atol=1e-6, rtol=0):
            raise ValueError('Temporal restoration disagrees')
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, tmp = tempfile.mkstemp(dir=output.parent, prefix='.'+output.name)
    try:
        with os.fdopen(fd, 'wb') as f:
            np.savez_compressed(f, ids=np.asarray(split['validation_ids']), probabilities=probs)
        os.replace(tmp, output)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return {'validation_clips': len(probs), 'max_abs_difference': difference,
            'source': 'original_train_npy', 'cache_required': False, 'atol': 1e-6, 'rtol': 0,
            'run_sha256': sha256(Path(directory)/'run.json'),
            'manifest_hash': manifest['manifest_hash'], 'producer_hash': producer_hash(),
            'restored_file': output.name, 'restored_sha256': sha256(output)}
