"""E01 delivery path: seeded LOSO, full-train refit, portable bundle, prediction and CSV validation."""
from __future__ import annotations

import csv
import io
import json
import math
import os
from pathlib import Path
import random
import tempfile
import time

import numpy as np
import torch
from torch import nn

from .data import CLASSES, read_sequence
from .features import fit_scaler, raw_stats, scale_values
from .io import sha256
from .models import RawStatsMLP
from .training import balanced_batches, configure_cpu, learning_rate

SEEDS = (17, 29, 43)
EPOCHS = 80
RECIPE = "raw_stats_mlp_v2"
BUNDLE_REVISION = "r0_mlp_bundle_v1"


def check_seed(seed):
    if seed not in SEEDS:
        raise ValueError(f"Seed {seed} outside the closed set {SEEDS}")
    return seed


def _reject_test(path):
    parts = Path(path).resolve().parts
    if "test" in parts:
        raise ValueError("Test payloads are reserved for a frozen bundle; refused in this item")


def r0_from_paths(paths, allow_test=False):
    rows = []
    for path in paths:
        if not allow_test:
            _reject_test(path)
        rows.append(raw_stats(read_sequence(path)))
    return np.stack(rows)


def train_r0(train_root, manifest):
    _reject_test(train_root)
    samples = manifest["samples"]
    values = r0_from_paths([Path(train_root) / s["landmarks_path"] for s in samples])
    ids = [s["id"] for s in samples]
    labels = np.asarray([CLASSES.index(s["label"]) for s in samples], dtype=np.int64)
    signers = np.asarray([s["signer"] for s in samples])
    return ids, values, labels, signers


def fit_model(values, labels, signers, fit_ids, seed):
    """Exact R2-E01 optimisation with the seed as the only free parameter."""
    check_seed(seed)
    configure_cpu()
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    scaler = fit_scaler(values, list(fit_ids))
    x = torch.from_numpy(scale_values(values, scaler))
    y = torch.from_numpy(labels)
    model = RawStatsMLP()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-3)
    criterion = nn.CrossEntropyLoss()
    losses = []
    for epoch in range(EPOCHS):
        for group in optimizer.param_groups:
            group["lr"] = learning_rate(epoch)
        model.train()
        total = 0.0
        for batch in balanced_batches(y.numpy(), signers, seed, epoch):
            index = torch.from_numpy(batch.copy())
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(x[index]), y[index])
            loss.backward()
            optimizer.step()
            total += float(loss.detach()) * len(batch)
        losses.append(total / len(x))
    model.eval()
    return model, scaler, losses


def predict(model, scaler, values):
    configure_cpu()
    model.eval()
    with torch.inference_mode():
        return torch.softmax(model(torch.as_tensor(scale_values(values, scaler))), dim=1).numpy()


def loso(train_root, manifest, splits_dir, seed, out):
    ids, values, labels, signers = train_r0(train_root, manifest)
    lookup = {i: k for k, i in enumerate(ids)}
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    report = {"recipe": RECIPE, "seed": seed, "epochs": EPOCHS, "folds": {}}
    oof = np.full((len(ids), 5), np.nan, dtype=np.float32)
    for held in ("M02", "M03", "M04"):
        split = json.loads((Path(splits_dir) / f"{held}.json").read_text())
        fit = [lookup[i] for i in split["train_ids"]]
        val = [lookup[i] for i in split["validation_ids"]]
        if set(signers[val]) != {held} or held in set(signers[fit]):
            raise ValueError("Split does not hold out exactly one signer")
        start = time.perf_counter()
        model, scaler, losses = fit_model(values[fit], labels[fit], signers[fit], split["train_ids"], seed)
        probs = predict(model, scaler, values[val])
        oof[val] = probs
        fold = out / held
        fold.mkdir(mode=0o700)
        torch.save(model.state_dict(), fold / "model.pt")
        np.savez_compressed(fold / "preprocessor.npz", **scaler)
        np.savez_compressed(fold / "validation.npz", ids=np.asarray(split["validation_ids"]),
                            probabilities=probs, labels=labels[val])
        report["folds"][held] = {"correct": int((probs.argmax(1) == labels[val]).sum()), "clips": len(val),
                                 "final_loss": losses[-1], "seconds": time.perf_counter() - start,
                                 "files": {n: sha256(fold / n) for n in ("model.pt", "preprocessor.npz", "validation.npz")}}
    if np.isnan(oof).any():
        raise ValueError("Incomplete OOF coverage")
    np.savez_compressed(out / "oof.npz", ids=np.asarray(ids), probabilities=oof, labels=labels, signers=signers)
    report["oof_correct"] = int((oof.argmax(1) == labels).sum())
    (out / "report.json").write_text(json.dumps(report, indent=2))
    return report


def restore_fold(train_root, manifest, fold_dir):
    """New-process restoration from original NPY files, without any cache."""
    fold_dir = Path(fold_dir)
    by_id = {s["id"]: s for s in manifest["samples"]}
    with np.load(fold_dir / "validation.npz", allow_pickle=False) as v:
        ids, stored = v["ids"].tolist(), v["probabilities"]
    values = r0_from_paths([Path(train_root) / by_id[i]["landmarks_path"] for i in ids])
    model = RawStatsMLP()
    model.load_state_dict(torch.load(fold_dir / "model.pt", weights_only=True))
    with np.load(fold_dir / "preprocessor.npz", allow_pickle=False) as s:
        scaler = {k: s[k] for k in s.files}
    return float(np.abs(predict(model, scaler, values) - stored).max())


def finalfit(train_root, manifest, seeds, out):
    ids, values, labels, signers = train_r0(train_root, manifest)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    members, reference = [], []
    for seed in seeds:
        model, scaler, losses = fit_model(values, labels, signers, ids, check_seed(seed))
        torch.save(model.state_dict(), out / f"model_s{seed}.pt")
        np.savez_compressed(out / f"scaler_s{seed}.npz", mean=scaler["mean"], scale=scaler["scale"])
        members.append({"seed": seed, "final_loss": losses[-1], "model": f"model_s{seed}.pt",
                        "scaler": f"scaler_s{seed}.npz"})
        reference.append(predict(model, scaler, values))
    for member in members:
        member["model_sha256"] = sha256(out / member["model"])
        member["scaler_sha256"] = sha256(out / member["scaler"])
    np.savez_compressed(out / "train_reference.npz", ids=np.asarray(ids), probabilities=np.mean(reference, axis=0))
    bundle = {"revision": BUNDLE_REVISION, "recipe": RECIPE, "epochs": EPOCHS, "classes": CLASSES,
              "combination": "arithmetic_mean_of_member_probabilities", "members": members,
              "fit_clips": len(ids), "input": "float64 (T,1662) landmarks NPY per sample",
              "manifest_hash": manifest["manifest_hash"],
              "versions": {"numpy": np.__version__, "torch": str(torch.__version__)}}
    (out / "bundle.json").write_text(json.dumps(bundle, indent=2))
    return bundle


def load_bundle(bundle_dir):
    bundle_dir = Path(bundle_dir)
    bundle = json.loads((bundle_dir / "bundle.json").read_text())
    if bundle.get("revision") != BUNDLE_REVISION or bundle.get("classes") != CLASSES:
        raise ValueError("Unsupported bundle")
    members = []
    for m in bundle["members"]:
        if sha256(bundle_dir / m["model"]) != m["model_sha256"] or sha256(bundle_dir / m["scaler"]) != m["scaler_sha256"]:
            raise ValueError("Bundle file hash mismatch")
        model = RawStatsMLP()
        model.load_state_dict(torch.load(bundle_dir / m["model"], weights_only=True))
        with np.load(bundle_dir / m["scaler"], allow_pickle=False) as s:
            members.append((model, {"mean": s["mean"], "scale": s["scale"]}))
    return bundle, members


def predict_bundle(bundle_dir, paths, allow_test=False):
    """Per-sample prediction: each output row depends only on its own file."""
    _, members = load_bundle(bundle_dir)
    values = r0_from_paths(paths, allow_test=allow_test)
    return np.mean([predict(m, s, values) for m, s in members], axis=0)


def validate_submission(template_path, submission_path):
    template = Path(template_path).read_text(encoding="utf-8").splitlines()
    if not template or template[0].strip() != "video_id,predicted_sign":
        raise ValueError("Template header mismatch")
    expected = [line.split(",")[0] for line in template[1:] if line.strip()]
    raw = Path(submission_path).read_bytes()
    text = raw.decode("utf-8")
    if text.startswith("﻿"):
        raise ValueError("BOM not allowed")
    rows = list(csv.reader(io.StringIO(text)))
    if not rows or rows[0] != ["video_id", "predicted_sign"]:
        raise ValueError("Header must be exactly video_id,predicted_sign")
    body = rows[1:]
    if any(len(r) != 2 for r in body):
        raise ValueError("Every row must have exactly two columns")
    got = [r[0] for r in body]
    if len(set(got)) != len(got):
        raise ValueError("Duplicated video_id")
    if set(got) != set(expected) or len(got) != len(expected):
        raise ValueError("IDs do not match the template exactly")
    bad = [r for r in body if r[1] not in CLASSES]
    if bad:
        raise ValueError(f"Invalid class code in {len(bad)} rows")
    return {"rows": len(body), "sha256": sha256(submission_path)}


def write_submission(template_path, ids, probabilities, out):
    expected = [l.split(",")[0] for l in Path(template_path).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    if sorted(expected) != sorted(ids):
        raise ValueError("Predictions must cover the template exactly")
    label = {i: CLASSES[int(k)] for i, k in zip(ids, np.asarray(probabilities).argmax(1))}
    out = Path(out)
    with out.open("x", encoding="utf-8", newline="") as handle:
        handle.write("video_id,predicted_sign\n")
        for i in expected:
            handle.write(f"{i},{label[i]}\n")
    return validate_submission(template_path, out)
