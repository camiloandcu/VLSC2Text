"""Strict head artifacts and restoration using independently supplied embeddings."""
from pathlib import Path
import math

import numpy as np
import torch

from .data import CLASSES, validate_baseline_manifest, validate_split
from .io import atomic_json, digest, producer_hash, read_json, sha256
from .rgb_head import HYPERPARAMETERS, RGBPyramidMLP, infer, load_embeddings, pyramid
from .rgb_loso_budget import BASELINE_SHA
from .training import configure_cpu


def load_run(manifest, directory):
    validate_baseline_manifest(manifest)
    root = Path(directory)
    run, split = read_json(root/"run.json"), read_json(root/"split.json")
    validate_split(manifest, split)
    expected = {"recipe": "rgb_pyramid_mlp_v2", "feature_schema_id": "dinov2s14_cls_v2",
                "protocol_revision": "R2.1", "fit_role": "outer", "status": "complete", "seed": 17,
                "nominal_recipe_epochs": 80, "classes": CLASSES, "hyperparameters": HYPERPARAMETERS,
                "producer_hash": producer_hash(), "manifest_hash": manifest["manifest_hash"],
                "split_hash": split["split_hash"], "fit_ids_hash": digest(split["train_ids"]),
                "validation_ids_hash": digest(split["validation_ids"]), "baseline_report_sha256": BASELINE_SHA}
    phases = {"rgb_head_pilot": 2, "outer_rgb": 80}
    if (any(run.get(k) != v for k, v in expected.items()) or run.get("phase") not in phases
            or run.get("epochs") != phases[run["phase"]] or len(run.get("cache_metadata_sha256", "")) != 64):
        raise ValueError("Incompatible RGB head run identity")
    required = {"model.pt", "preprocessor.npz", "validation.npz", "split.json", "metrics.json"}
    if set(run.get("files", {})) != required or any(sha256(root/n) != v for n, v in run["files"].items()):
        raise ValueError("RGB head artifact hash/inventory mismatch")
    with np.load(root/"preprocessor.npz", allow_pickle=False) as archive:
        state = {k: archive[k] for k in ["mean", "scale", "fit_ids"]}
    if (state["fit_ids"].tolist() != split["train_ids"]
            or any(state[k].shape != (384,) or state[k].dtype != np.float32 or not np.isfinite(state[k]).all()
                   for k in ["mean", "scale"]) or np.any(state["scale"] <= 0)):
        raise ValueError("Invalid RGB fit-only channel scaler")
    return run, split, state


def restore_embeddings(manifest, directory, values, output, source):
    root = Path(directory)
    run, split, state = load_run(manifest, root)
    if source not in {"immutable_full_train_cache", "original_train_videos_and_pinned_weight"}:
        raise ValueError("Unknown RGB restoration source")
    lookup = {s["id"]: i for i, s in enumerate(manifest["samples"])}
    if values.shape != (1125, 16, 384):
        raise ValueError("Full original/restored embedding coverage required")
    configure_cpu()
    model = RGBPyramidMLP()
    model.load_state_dict(torch.load(root/"model.pt", weights_only=True, map_location="cpu"))
    _, probs = infer(model, pyramid(values[[lookup[i] for i in split["validation_ids"]]], state))
    with np.load(root/"validation.npz", allow_pickle=False) as reference:
        if reference["ids"].tolist() != split["validation_ids"] or reference["probabilities"].shape != probs.shape:
            raise ValueError("RGB validation reference coverage mismatch")
        difference = float(np.max(np.abs(reference["probabilities"]-probs)))
        if not np.allclose(reference["probabilities"], probs, atol=1e-6, rtol=0):
            raise ValueError(f"RGB restoration disagrees: {difference}")
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with output.open("xb") as file:
        np.savez_compressed(file, ids=np.asarray(split["validation_ids"]), probabilities=probs)
    return {"validation_clips": 375, "source": source, "cache_required": source == "immutable_full_train_cache",
            "max_abs_difference": difference, "atol": 1e-6, "rtol": 0, "outer_signer": split["outer_signer"],
            "run_sha256": sha256(root/"run.json"), "manifest_hash": manifest["manifest_hash"],
            "producer_hash": producer_hash(), "restored_file": output.name, "restored_sha256": sha256(output)}


def restore_cache(manifest, directory, cache, output):
    run, _, _ = load_run(manifest, directory)
    if sha256(Path(cache)/"metadata.json") != run["cache_metadata_sha256"]:
        raise ValueError("Immutable training cache identity changed")
    values, _ = load_embeddings(cache, manifest)
    result = restore_embeddings(manifest, directory, values, Path(output).with_suffix(".npz"), "immutable_full_train_cache")
    if Path(output).exists():
        raise FileExistsError(output)
    atomic_json(output, result)
    return result


def verify_restoration(directory, manifest, receipt, receipt_directory, source):
    run, split, _ = load_run(manifest, directory)
    expected = {"validation_clips": 375, "source": source, "cache_required": source == "immutable_full_train_cache",
                "atol": 1e-6, "rtol": 0, "manifest_hash": manifest["manifest_hash"],
                "producer_hash": producer_hash(), "run_sha256": sha256(Path(directory)/"run.json"),
                "outer_signer": split["outer_signer"]}
    difference = receipt.get("max_abs_difference", math.inf)
    name = receipt.get("restored_file", "")
    if (any(receipt.get(k) != v for k, v in expected.items()) or not math.isfinite(difference)
            or not 0 <= difference <= 1e-6 or not name or Path(name).name != name):
        raise ValueError("Incompatible RGB restoration receipt")
    file = Path(receipt_directory)/name
    if sha256(file) != receipt.get("restored_sha256"):
        raise ValueError("Restored RGB probabilities hash mismatch")
    with np.load(file, allow_pickle=False) as actual, np.load(Path(directory)/"validation.npz", allow_pickle=False) as ref:
        if (actual["ids"].tolist() != split["validation_ids"] or actual["probabilities"].shape != (375, 5)
                or not np.isfinite(actual["probabilities"]).all()
                or not np.allclose(actual["probabilities"], ref["probabilities"], atol=1e-6, rtol=0)):
            raise ValueError("RGB restored predictions mismatch")
    return run
