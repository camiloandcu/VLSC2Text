"""Two-epoch admission pilot and three fixed eighty-epoch RGB outer fits."""
from pathlib import Path
import copy
import os
import random
import resource
import time

import numpy as np
import torch
from torch import nn

from . import budget, rgb_loso_budget
from .data import CLASSES, validate_baseline_manifest, validate_split
from .io import atomic_json, digest, producer_hash, sha256
from .rgb_head import HYPERPARAMETERS, RGBPyramidMLP, fit_scaler, infer, load_embeddings, pyramid
from .training import balanced_batches, configure_cpu, learning_rate


def fit(manifest, split, cache, ledger_path, attempt, output, pilot=False):
    started = time.perf_counter()
    validate_baseline_manifest(manifest)
    validate_split(manifest, split)
    if pilot and split["outer_signer"] != "M02":
        raise ValueError("Pilot fixed to M02")
    job = os.environ.get("SLURM_JOB_ID")
    if not job or os.environ.get("SLURM_CPUS_PER_TASK") != "4":
        raise ValueError("Four allocated Slurm CPUs required")
    reservation = budget.claim_attempt(ledger_path, attempt, job, output, expected_scope=rgb_loso_budget.SCOPE)
    if (reservation.get("producer_hash") != producer_hash()
            or reservation.get("manifest_hash") != manifest["manifest_hash"]
            or reservation.get("profile") != ("pilot" if pilot else split["outer_signer"])
            or reservation["time_limit_seconds"] != (300 if pilot else 900)):
        raise ValueError("RGB head reservation profile mismatch")
    if not pilot:
        gate = rgb_loso_budget.check_gate(ledger_path, manifest["manifest_hash"])
        if sha256(Path(cache)/"metadata.json") != gate["cache_metadata_sha256"]:
            raise ValueError("Head cache differs from measured pilot")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    epochs = 2 if pilot else 80
    run = {"phase": "rgb_head_pilot" if pilot else "outer_rgb", "epochs": epochs,
           "nominal_recipe_epochs": 80, "seed": 17, "recipe": "rgb_pyramid_mlp_v2",
           "feature_schema_id": "dinov2s14_cls_v2", "protocol_revision": "R2.1",
           "fit_role": "outer", "classes": CLASSES, "hyperparameters": HYPERPARAMETERS,
           "producer_hash": producer_hash(), "manifest_hash": manifest["manifest_hash"],
           "split_hash": split["split_hash"], "fit_ids_hash": digest(split["train_ids"]),
           "validation_ids_hash": digest(split["validation_ids"]), "job_id": job,
           "attempt_id": attempt, "budget_scope": rgb_loso_budget.SCOPE, "status": "running",
           "cache_metadata_sha256": sha256(Path(cache)/"metadata.json"),
           "baseline_report_sha256": rgb_loso_budget.BASELINE_SHA,
           "versions": {"numpy": np.__version__, "torch": str(torch.__version__)}}
    atomic_json(output/"run.json", run)
    atomic_json(output/"split.json", split)
    try:
        metrics = _fit(manifest, split, cache, output, epochs)
        metrics.update(process_seconds_before_final_metadata=time.perf_counter()-started,
                       peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        atomic_json(output/"metrics.json", metrics)
        run.update(status="complete", files={n: sha256(output/n) for n in
                   ["model.pt", "preprocessor.npz", "validation.npz", "split.json", "metrics.json"]})
        atomic_json(output/"run.json", run)
        return metrics
    except BaseException as error:
        run.update(status="failed", error_type=type(error).__name__, error=str(error))
        atomic_json(output/"run.json", run)
        raise


def _fit(manifest, split, cache, output, epochs):
    configure_cpu()
    random.seed(17)
    np.random.seed(17)
    torch.manual_seed(17)
    torch.use_deterministic_algorithms(True)
    tick = time.perf_counter()
    values, _ = load_embeddings(cache, manifest)
    lookup = {s["id"]: i for i, s in enumerate(manifest["samples"])}
    fit_ids = [lookup[i] for i in split["train_ids"]]
    val = [lookup[i] for i in split["validation_ids"]]
    state = fit_scaler(values[fit_ids], split["train_ids"])
    x = torch.from_numpy(pyramid(values[fit_ids], state))
    labels = np.asarray([CLASSES.index(s["label"]) for s in manifest["samples"]], dtype=np.int64)
    y = torch.from_numpy(labels[fit_ids])
    signers = [manifest["samples"][i]["signer"] for i in fit_ids]
    io_seconds = time.perf_counter()-tick
    model = RGBPyramidMLP()
    opt = torch.optim.AdamW(model.parameters(), lr=.001, weight_decay=.001)
    ce = nn.CrossEntropyLoss()
    steps, losses, sizes, epoch_seconds = [], [], [], []
    for epoch in range(epochs):
        tick = time.perf_counter()
        model.train()
        for group in opt.param_groups:
            group["lr"] = learning_rate(epoch)
        total = 0.
        for batch in balanced_batches(y.numpy(), signers, 17, epoch):
            start = time.perf_counter()
            opt.zero_grad(set_to_none=True)
            loss = ce(model(x[batch.copy()]), y[batch.copy()])
            loss.backward()
            opt.step()
            total += float(loss.detach())*len(batch)
            steps.append(time.perf_counter()-start)
            sizes.append(len(batch))
        losses.append(total/len(fit_ids))
        epoch_seconds.append(time.perf_counter()-tick)
    if len(steps[5:]) < 10:
        raise ValueError("Insufficient measured post-warmup steps")
    tick = time.perf_counter()
    logits, probs = infer(model, pyramid(values[val], state))
    _, reversed_probs = infer(model, pyramid(values[val], state, reverse=True))
    eval_seconds = time.perf_counter()-tick
    probe = None
    if epochs == 2:
        clone = copy.deepcopy(model).train()
        optimizer = torch.optim.AdamW(clone.parameters(), lr=.001, weight_decay=.001)
        start = time.perf_counter()
        optimizer.zero_grad(set_to_none=True)
        loss = ce(clone(x[:60]), y[:60])
        loss.backward()
        optimizer.step()
        probe = {"size": 60, "fit_only": True, "discarded_copy": True,
                 "backward_optimizer_step": True, "seconds": time.perf_counter()-start}
        del clone, optimizer
    tick = time.perf_counter()
    torch.save(model.state_dict(), output/"model.pt")
    np.savez_compressed(output/"preprocessor.npz", **state)
    np.savez_compressed(output/"validation.npz", ids=np.asarray(split["validation_ids"]), labels=labels[val],
                        logits=logits, probabilities=probs, reversed_probabilities=reversed_probs)
    write_seconds = time.perf_counter()-tick
    median = float(np.median(steps[5:]))
    overhead = io_seconds+eval_seconds+write_seconds
    return {"metric_scope": "two_epoch_diagnostic_not_candidate" if epochs == 2 else "fixed_80_epoch_outer_fold",
            "train_clips": len(fit_ids), "validation_clips": len(val), "training_losses": losses,
            "validation_accuracy": float((probs.argmax(1) == labels[val]).mean()),
            "reversed_validation_accuracy_diagnostic": float((reversed_probs.argmax(1) == labels[val]).mean()),
            "batch_sizes": sizes, "epoch_seconds": epoch_seconds, "warmup_measurement_steps": 5,
            "measured_step_count": len(steps[5:]), "post_warmup_step_median_seconds": median,
            "post_warmup_step_max_seconds": max(steps[5:]), "io_and_scaling_seconds": io_seconds,
            "evaluation_seconds": eval_seconds, "artifact_write_seconds": write_seconds, "batch60_probe": probe,
            "projected_fold_seconds_with_margin": 1.5*(80*19*median+overhead),
            "projected_refit_seconds_with_margin": 1.5*(80*19*1.5*median+1.5*overhead),
            "refit_projection_assumption": "batch60_19_steps_equal_strata; linear_batch_size_and_io_cost; not_measured_refit",
            "parameter_count": sum(p.numel() for p in model.parameters())}
