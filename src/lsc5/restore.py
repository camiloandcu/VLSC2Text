"""Verify closed outer-run contracts and restore from original train NPY."""
import os
from pathlib import Path
import tempfile

import numpy as np
import torch

from .data import CLASSES, validate_baseline_manifest, validate_manifest, validate_split
from .features import from_originals, scale_values
from .io import digest, producer_hash, read_json, sha256
from .models import RawStatsMLP, probabilities
from .training import HYPERPARAMETERS, configure_cpu


def load_run(manifest, run_directory):
    validate_manifest(manifest)
    root = Path(run_directory)
    run = read_json(root / "run.json")
    split = read_json(root / "split.json")
    validate_split(manifest, split)
    if run.get("status") != "complete" or run.get("fit_role") != "outer":
        raise ValueError("Only complete outer artifacts are supported")
    required = {"model.pt", "preprocessor.npz", "validation.npz", "split.json", "metrics.json"}
    if set(run.get("files", {})) != required:
        raise ValueError("Incomplete artifact hash inventory")
    expected = {"recipe": "raw_stats_mlp_v2", "feature_schema_id": "raw_stats_v2",
                "protocol_revision": "R2.1",
                "nominal_recipe_epochs": 80, "seed": 17, "hyperparameters": HYPERPARAMETERS}
    profiles = {"diagnostic_pilot": 2, "outer_baseline": 80}
    if run.get("phase") not in profiles or run.get("epochs") != profiles[run["phase"]]:
        raise ValueError("Incompatible declared execution profile")
    if run["phase"] == "outer_baseline":
        validate_baseline_manifest(manifest)
    if any(run.get(k) != v for k, v in expected.items()):
        raise ValueError("Incompatible declared recipe or feature schema")
    if run.get("producer_hash") != producer_hash() or run.get("manifest_hash") != manifest["manifest_hash"]:
        raise ValueError("Producer/manifest mismatch")
    if (run.get("split_hash") != split["split_hash"] or run.get("fit_ids_hash") != digest(split["train_ids"])
            or run.get("validation_ids_hash") != digest(split["validation_ids"]) or run.get("classes") != CLASSES):
        raise ValueError("Split/class/fit provenance mismatch")
    for name, expected in run["files"].items():
        if Path(name).name != name or sha256(root / name) != expected:
            raise ValueError("Artifact hash mismatch")
    with np.load(root / "preprocessor.npz", allow_pickle=False) as archive:
        scaler = {k: archive[k] for k in ["mean", "scale", "fit_ids"]}
    if scaler["fit_ids"].tolist() != split["train_ids"]:
        raise ValueError("Scaler was fitted on different IDs")
    if (any(scaler[k].shape != (3324,) or scaler[k].dtype != np.float32
            or not np.isfinite(scaler[k]).all() for k in ["mean", "scale"])
            or np.any(scaler["scale"] <= 0)):
        raise ValueError("Invalid scaler state")
    return run, split, scaler


def predict_train(train_root, manifest, run_directory, output):
    run, split, scaler = load_run(manifest, run_directory)
    root = Path(run_directory)
    by_id = {s["id"]: s for s in manifest["samples"]}
    raw = from_originals(train_root, [by_id[i] for i in split["validation_ids"]])
    configure_cpu()
    model = RawStatsMLP()
    model.load_state_dict(torch.load(root / "model.pt", map_location="cpu", weights_only=True))
    probs = probabilities(model, scale_values(raw, scaler))
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with np.load(root / "validation.npz", allow_pickle=False) as reference:
        if reference["ids"].tolist() != split["validation_ids"]:
            raise ValueError("Validation ID order mismatch")
        difference = float(np.max(np.abs(reference["probabilities"] - probs)))
        if not np.allclose(reference["probabilities"], probs, atol=1e-6, rtol=0):
            raise ValueError(f"Restoration probabilities disagree: max_abs={difference}")
    fd, temporary = tempfile.mkstemp(prefix="." + output.name, dir=output.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            np.savez_compressed(handle, ids=np.asarray(split["validation_ids"]), probabilities=probs)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {"validation_clips": len(probs), "source": "original_train_npy", "max_abs_difference": difference,
            "atol": 1e-6, "rtol": 0, "cache_required": False}
