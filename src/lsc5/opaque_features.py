"""Opaque native-length sequences, verified train-only cache and frame scaler."""
from pathlib import Path
import hashlib
import io
import os
import shutil
import tempfile
import zipfile

import numpy as np

from .data import read_sequence, validate_baseline_manifest
from .io import atomic_json, producer_hash, read_json, sha256, train_path


def originals(train_root, samples):
    for sample in samples:
        path = train_path(train_root, sample['landmarks_path'])
        if sha256(path) != sample['landmarks_sha256']:
            raise ValueError('Original sequence hash mismatch')
        x = read_sequence(path)
        if len(x) != sample['frames']:
            raise ValueError('Original length mismatch')
        yield x


def prepare_sequences(manifest, output, train_root=None, train_zip=None):
    validate_baseline_manifest(manifest)
    if (train_root is None) == (train_zip is None):
        raise ValueError('Choose exactly one train source')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = output.parent / ('.'+output.name+'.lock')
    with lock.open('x'):
        stage = Path(tempfile.mkdtemp(prefix='.'+output.name, dir=output.parent))
        archive = None
        try:
            if output.exists():
                raise FileExistsError(output)
            samples = manifest['samples']
            if train_zip is not None:
                if Path(train_zip).name != 'Train.zip':
                    raise ValueError('Only explicit Train.zip accepted')
                archive = zipfile.ZipFile(train_zip)
                names = archive.namelist()
                if len(names) != len(set(names)):
                    raise ValueError('Duplicate archive members')
                def source():
                    for s in samples:
                        suffix = '/'+s['landmarks_path']
                        matches = [n for n in names if n.endswith(suffix)]
                        if len(matches) != 1:
                            raise ValueError('Ambiguous/missing train archive sequence')
                        payload = archive.read(matches[0])
                        if hashlib.sha256(payload).hexdigest() != s['landmarks_sha256']:
                            raise ValueError('Server train payload differs from manifest')
                        yield np.load(io.BytesIO(payload), allow_pickle=False)
                sequences = source()
            else:
                sequences = originals(train_root, samples)
            offsets = np.cumsum([0]+[s['frames'] for s in samples], dtype=np.int64)
            values = np.lib.format.open_memmap(stage/'values.npy', mode='w+', dtype=np.float64,
                                               shape=(int(offsets[-1]), 1662))
            for i, x in enumerate(sequences):
                if (x.shape != (samples[i]['frames'], 1662) or x.dtype != np.float64
                        or not np.isfinite(x).all()):
                    raise ValueError('Invalid original sequence')
                values[offsets[i]:offsets[i+1]] = x
            values.flush()
            del values
            meta = {'schema': 'opaque_sequence_v1', 'data_role': 'train', 'complete': True,
                    'producer_hash': producer_hash(), 'manifest_hash': manifest['manifest_hash'],
                    'ids': [s['id'] for s in samples], 'offsets': offsets.tolist(),
                    'dtype': 'float64', 'values_sha256': sha256(stage/'values.npy')}
            atomic_json(stage/'metadata.json', meta)
            load_sequences(stage, manifest)
            os.rename(stage, output)
        finally:
            if archive is not None:
                archive.close()
            shutil.rmtree(stage, ignore_errors=True)
            lock.unlink()


def load_sequences(directory, manifest):
    validate_baseline_manifest(manifest)
    root = Path(directory)
    m = read_json(root/'metadata.json')
    offsets = np.cumsum([0]+[s['frames'] for s in manifest['samples']], dtype=np.int64)
    expected = {'schema': 'opaque_sequence_v1', 'data_role': 'train', 'complete': True,
                'producer_hash': producer_hash(), 'manifest_hash': manifest['manifest_hash'],
                'ids': [s['id'] for s in manifest['samples']], 'offsets': offsets.tolist(), 'dtype': 'float64'}
    if any(m.get(k) != v for k, v in expected.items()) or sha256(root/'values.npy') != m['values_sha256']:
        raise ValueError('Sequence cache identity/hash mismatch')
    values = np.load(root/'values.npy', mmap_mode='r', allow_pickle=False)
    if values.shape != (offsets[-1], 1662) or values.dtype != np.float64:
        raise ValueError('Invalid sequence cache shape/dtype')
    result = [values[offsets[i]:offsets[i+1]] for i in range(len(offsets)-1)]
    if any(not np.isfinite(x).all() for x in result):
        raise ValueError('Nonfinite cache values')
    return result


def frame_scaler(sequences, ids):
    if len(sequences) != len(ids) or not ids or len(set(ids)) != len(ids):
        raise ValueError('Invalid scaler coverage')
    count, mean, m2 = 0, np.zeros(1662), np.zeros(1662)
    for x in sequences:
        n = len(x)
        avg = x.mean(0, dtype=np.float64)
        delta = avg-mean
        m2 += x.var(0, dtype=np.float64)*n + delta*delta*count*n/(count+n)
        mean += delta*n/(count+n)
        count += n
    scale = np.sqrt(m2/count).astype(np.float32)
    scale[scale < 1e-6] = 1
    return {'mean': mean.astype(np.float32), 'scale': scale, 'fit_ids': np.asarray(ids)}


def transform(x, scaler):
    y = ((x-scaler['mean'])/scaler['scale']).astype(np.float32)
    if not np.isfinite(y).all():
        raise ValueError('Nonfinite transformed sequence')
    return y
