"""Opaque per-clip R0 statistics and complete atomic caches."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile

import numpy as np

from .data import read_sequence, validate_manifest
from .io import atomic_json, producer_hash, read_json, sha256, train_path


def raw_stats(values):
    result = np.concatenate((values.mean(axis=0, dtype=np.float64),
                             values.std(axis=0, dtype=np.float64, ddof=0))).astype(np.float32)
    if result.shape != (3324,) or not np.isfinite(result).all():
        raise ValueError("Invalid R0 statistics")
    return result


def from_originals(train_root, samples):
    rows = []
    for sample in samples:
        path = train_path(train_root, sample["landmarks_path"])
        if sha256(path) != sample["landmarks_sha256"]:
            raise ValueError("Original landmarks hash mismatch")
        values = read_sequence(path)
        if len(values) != sample["frames"]:
            raise ValueError("Original length mismatch")
        rows.append(raw_stats(values))
    return np.stack(rows)


def prepare_stats(train_root, manifest, output):
    validate_manifest(manifest)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = output.parent / ("." + output.name + ".lock")
    with lock.open("x"):
        staging = Path(tempfile.mkdtemp(prefix="." + output.name, dir=output.parent))
        try:
            if output.exists():
                raise FileExistsError(output)
            values = from_originals(train_root, manifest["samples"])
            ids = [s["id"] for s in manifest["samples"]]
            np.savez_compressed(staging / "stats.npz", values=values, ids=np.asarray(ids))
            atomic_json(staging / "metadata.json", {
                "revision": "raw_stats_cache_v1", "cache_kind": "raw_stats", "data_role": "train",
                "feature_schema_id": "raw_stats_v2", "dtype": "float32", "shape": list(values.shape),
                "manifest_hash": manifest["manifest_hash"], "ids": ids,
                "input_hashes": [s["landmarks_sha256"] for s in manifest["samples"]],
                "producer_hash": producer_hash(), "values_sha256": sha256(staging / "stats.npz"),
                "complete": True})
            load_stats(staging, manifest)
            os.rename(staging, output)
        finally:
            shutil.rmtree(staging, ignore_errors=True)
            lock.unlink()


def load_stats(directory, manifest):
    validate_manifest(manifest)
    directory = Path(directory)
    meta = read_json(directory / "metadata.json")
    ids = [s["id"] for s in manifest["samples"]]
    expected = {"revision": "raw_stats_cache_v1", "cache_kind": "raw_stats", "data_role": "train",
                "feature_schema_id": "raw_stats_v2", "dtype": "float32", "shape": [len(ids), 3324],
                "manifest_hash": manifest["manifest_hash"], "ids": ids,
                "input_hashes": [s["landmarks_sha256"] for s in manifest["samples"]],
                "producer_hash": producer_hash(), "complete": True}
    if any(meta.get(k) != v for k, v in expected.items()):
        raise ValueError("Incomplete or incompatible statistics cache")
    if sha256(directory / "stats.npz") != meta["values_sha256"]:
        raise ValueError("Statistics cache hash mismatch")
    with np.load(directory / "stats.npz", allow_pickle=False) as cache:
        values = cache["values"]
        if cache["ids"].tolist() != ids or values.shape != (len(ids), 3324):
            raise ValueError("Statistics coverage/order mismatch")
        if values.dtype != np.float32 or not np.isfinite(values).all():
            raise ValueError("Invalid feature values")
    return values


def fit_scaler(values, ids):
    if len(ids) != len(values) or len(set(ids)) != len(ids) or not len(ids):
        raise ValueError("Invalid scaler fit IDs")
    mean = values.mean(axis=0, dtype=np.float64).astype(np.float32)
    scale = values.std(axis=0, ddof=0, dtype=np.float64).astype(np.float32)
    scale[scale < 1e-6] = 1
    return {"mean": mean, "scale": scale, "fit_ids": np.asarray(ids)}


def scale_values(values, scaler):
    result = (values - scaler["mean"]) / scaler["scale"]
    if not np.isfinite(result).all():
        raise ValueError("Nonfinite scaled features")
    return result.astype(np.float32)
