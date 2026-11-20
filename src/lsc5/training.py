"""Closed two-epoch diagnostic and eighty-epoch outer baseline profiles."""
from __future__ import annotations

import copy
import math
import os
from pathlib import Path
import random
import resource
import time

import numpy as np
import torch
from torch import nn

from . import budget
from .data import CLASSES, validate_baseline_manifest, validate_manifest, validate_split
from .features import fit_scaler, load_stats, scale_values
from .io import atomic_json, digest, producer_hash, sha256
from .models import RawStatsMLP


HYPERPARAMETERS = {"hidden_dim": 128, "dropout": 0.3, "optimizer": "AdamW",
                                  "lr": 0.001, "weight_decay": 0.001, "loss": "cross_entropy",
                                  "batch_per_signer_class": 4, "scheduler": "cosine",
                                  "warmup_epochs": 5, "end_lr_fraction": 0.01}


def configure_cpu():
    torch.set_num_threads(4)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)


def balanced_batches(labels, signers, seed, epoch):
    rng = np.random.default_rng(np.random.SeedSequence([seed, epoch]))
    groups = {}
    for i, (label, signer) in enumerate(zip(labels, signers)):
        groups.setdefault((str(signer), int(label)), []).append(i)
    if not groups or len({len(v) for v in groups.values()}) != 1:
        raise ValueError("Balanced sampler requires equally populated signer/class strata")
    expected = {(str(s), c) for s in set(signers) for c in range(5)}
    if set(groups) != expected:
        raise ValueError("Every fit signer must have all five classes")
    shuffled = [rng.permutation(groups[k]) for k in sorted(groups)]
    for start in range(0, len(shuffled[0]), 4):
        yield rng.permutation(np.concatenate([g[start:start + 4] for g in shuffled]))


def learning_rate(epoch):
    if epoch < 5:
        return 1e-3 * (epoch + 1) / 5
    ratio = 0.01 + 0.99 * (1 + math.cos(math.pi * (epoch - 4) / 75)) / 2
    return 1e-3 * ratio


def run_pilot(manifest, split, cache_dir, budget_path, attempt_id, output):
    return _run(manifest, split, cache_dir, budget_path, attempt_id, output, "diagnostic_pilot")


def run_baseline(manifest, split, cache_dir, budget_path, attempt_id, output):
    validate_baseline_manifest(manifest)
    return _run(manifest, split, cache_dir, budget_path, attempt_id, output, "outer_baseline")


def _run(manifest, split, cache_dir, budget_path, attempt_id, output, phase):
    epochs = 2 if phase == "diagnostic_pilot" else 80
    scope = budget.SCOPE if phase == "diagnostic_pilot" else budget.BASELINE_SCOPE
    started = time.perf_counter()
    validate_manifest(manifest)
    validate_split(manifest, split)
    job_id = os.environ.get("SLURM_JOB_ID")
    if not job_id:
        raise ValueError("Real pilot requires the authorized Slurm execution path")
    if int(os.environ.get("SLURM_CPUS_PER_TASK", "0")) != 4:
        raise ValueError("Pilot requires exactly four allocated CPUs")
    output = Path(output)
    reservation = budget.claim_attempt(budget_path, attempt_id, job_id, output, expected_scope=scope)
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    config = {"phase": phase, "recipe": "raw_stats_mlp_v2", "protocol_revision": "R2.1",
              "feature_schema_id": "raw_stats_v2", "fit_role": "outer", "seed": 17, "epochs": epochs,
              "nominal_recipe_epochs": 80, "classes": CLASSES, "attempt_id": attempt_id,
              "job_id": job_id, "producer_hash": producer_hash(), "manifest_hash": manifest["manifest_hash"],
              "split_hash": split["split_hash"], "budget_path": str(budget_path),
              "reservation_seconds": reservation["reserved_seconds"], "budget_scope": scope, "status": "running",
              "python_threads": {"intra": 4, "inter": 1},
              "hyperparameters": dict(HYPERPARAMETERS),
              "versions": {"numpy": np.__version__, "torch": str(torch.__version__)}}
    atomic_json(output / "run.json", config)
    atomic_json(output / "split.json", split)
    try:
        metrics = _fit(manifest, split, cache_dir, output, epochs)
        metrics["process_seconds_before_final_metadata"] = time.perf_counter() - started
        metrics["peak_process_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        atomic_json(output / "metrics.json", metrics)
        config.update(status="complete", fit_ids_hash=digest(split["train_ids"]),
                      validation_ids_hash=digest(split["validation_ids"]),
                      files={name: sha256(output / name) for name in
                             ["model.pt", "preprocessor.npz", "validation.npz", "split.json", "metrics.json"]})
        atomic_json(output / "run.json", config)
        return metrics
    except BaseException as error:
        config.update(status="failed", error_type=type(error).__name__, error=str(error))
        atomic_json(output / "run.json", config)
        raise


def _fit(manifest, split, cache_dir, output, epochs):
    configure_cpu()
    random.seed(17)
    np.random.seed(17)
    torch.manual_seed(17)
    torch.use_deterministic_algorithms(True)
    begin_io = time.perf_counter()
    values = load_stats(cache_dir, manifest)
    lookup = {s["id"]: i for i, s in enumerate(manifest["samples"])}
    train_indices = [lookup[i] for i in split["train_ids"]]
    val_indices = [lookup[i] for i in split["validation_ids"]]
    samples = manifest["samples"]
    labels = np.asarray([CLASSES.index(s["label"]) for s in samples], dtype=np.int64)
    signers = np.asarray([samples[i]["signer"] for i in train_indices])
    scaler = fit_scaler(values[train_indices], split["train_ids"])
    train_x = torch.from_numpy(scale_values(values[train_indices], scaler))
    train_y = torch.from_numpy(labels[train_indices])
    val_x = scale_values(values[val_indices], scaler)
    io_seconds = time.perf_counter() - begin_io
    model = RawStatsMLP()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-3)
    criterion = nn.CrossEntropyLoss()
    steps, epoch_seconds, losses, batch_sizes = [], [], [], []
    for epoch in range(epochs):
        epoch_start = time.perf_counter()
        for group in optimizer.param_groups:
            group["lr"] = learning_rate(epoch)
        model.train()
        total_loss = 0.0
        for batch in balanced_batches(train_y.numpy(), signers, 17, epoch):
            step_start = time.perf_counter()
            indices = torch.from_numpy(batch.copy())
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(train_x[indices]), train_y[indices])
            loss.backward()
            optimizer.step()
            total_loss += float(loss.detach()) * len(batch)
            steps.append(time.perf_counter() - step_start)
            batch_sizes.append(len(batch))
        losses.append(total_loss / len(train_x))
        epoch_seconds.append(time.perf_counter() - epoch_start)
    post_warmup = steps[5:]
    if len(post_warmup) < 10:
        raise ValueError("Pilot needs at least ten measured steps after five warm-up steps")
    evaluation_start = time.perf_counter()
    model.eval()
    with torch.inference_mode():
        logits_tensor = model(torch.as_tensor(val_x, dtype=torch.float32))
        logits = logits_tensor.numpy()
        probs = torch.softmax(logits_tensor, dim=1).numpy()
    evaluation_seconds = time.perf_counter() - evaluation_start
    confusion = np.zeros((5, 5), dtype=np.int64)
    for truth, predicted in zip(labels[val_indices], probs.argmax(axis=1)):
        confusion[truth, predicted] += 1
    probe_metrics = None
    if epochs == 2:
        # Exercise a complete batch-60 optimizer step without modifying checkpoint weights.
        if len(train_x) < 60:
            raise ValueError("Batch-60 probe requires sixty fit-only examples")
        probe = copy.deepcopy(model).train()
        probe_optimizer = torch.optim.AdamW(probe.parameters(), lr=1e-3, weight_decay=1e-3)
        probe_start = time.perf_counter()
        probe_optimizer.zero_grad(set_to_none=True)
        probe_loss = criterion(probe(train_x[:60]), train_y[:60])
        probe_loss.backward()
        probe_optimizer.step()
        probe_seconds = time.perf_counter() - probe_start
        del probe, probe_optimizer
        probe_metrics = {"size": 60, "fit_only": True, "discarded_copy": True,
                         "backward_optimizer_step": True, "seconds": probe_seconds}
    write_start = time.perf_counter()
    torch.save(model.state_dict(), output / "model.pt")
    np.savez_compressed(output / "preprocessor.npz", **scaler)
    np.savez_compressed(output / "validation.npz", ids=np.asarray(split["validation_ids"]),
                        probabilities=probs, logits=logits, labels=labels[val_indices])
    write_seconds = time.perf_counter() - write_start
    steps_per_epoch = len(steps) // epochs
    epoch_estimate = float(np.median(post_warmup)) * steps_per_epoch
    projected = 1.5 * (80 * epoch_estimate + io_seconds + evaluation_seconds + write_seconds)
    return {"metric_scope": ("two_epoch_diagnostic_not_candidate" if epochs == 2 else "fixed_80_epoch_outer_fold"), "train_clips": len(train_indices),
            "validation_clips": len(val_indices), "validation_accuracy": float(np.trace(confusion) / confusion.sum()),
            "confusion": confusion.tolist(), "training_losses": losses, "epoch_seconds": epoch_seconds,
            "io_and_scaling_seconds": io_seconds, "evaluation_seconds": evaluation_seconds,
            "artifact_write_seconds": write_seconds, "warmup_measurement_steps": 5,
            "measured_step_count": len(post_warmup), "post_warmup_step_median_seconds": float(np.median(post_warmup)),
            "batch_sizes": batch_sizes, "batch60_probe": probe_metrics,
            "projected_80_epoch_seconds_with_margin": projected,
            "parameter_count": sum(p.numel() for p in model.parameters())}
