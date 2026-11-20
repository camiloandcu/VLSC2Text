"""Strict fixed-recipe OOF aggregation; no model or checkpoint selection."""
from pathlib import Path
import os
import shutil
import tempfile

import numpy as np

from .data import CLASSES, validate_baseline_manifest
from .io import atomic_json, producer_hash, read_json, sha256
from .restore import load_run


def classification_metrics(labels, predictions):
    confusion = np.zeros((5, 5), dtype=np.int64)
    np.add.at(confusion, (labels, predictions), 1)
    support = confusion.sum(1)
    denominator = support + confusion.sum(0)
    f1 = np.divide(2 * confusion.diagonal(), denominator,
                   out=np.zeros(5, dtype=float), where=denominator != 0)
    return {"clips": int(len(labels)), "correct": int(np.trace(confusion)),
            "accuracy": float(np.trace(confusion) / len(labels)),
            "macro_f1": float(f1.mean()), "confusion": confusion.tolist(),
            "class_support": support.tolist()}


def _validation_arrays(root, split, by_id):
    with np.load(root / "validation.npz", allow_pickle=False) as archive:
        ids, labels = archive["ids"], archive["labels"]
        logits, probs = archive["logits"], archive["probabilities"]
    expected = [CLASSES.index(by_id[i]["label"]) for i in split["validation_ids"]]
    n = len(expected)
    if ids.tolist() != split["validation_ids"] or labels.shape != (n,) or labels.dtype != np.int64:
        raise ValueError("Invalid validation ID/label order or shape")
    if labels.tolist() != expected:
        raise ValueError("Validation truth disagrees with train manifest")
    if any(x.shape != (n, 5) or x.dtype != np.float32 or not np.isfinite(x).all()
           for x in [logits, probs]):
        raise ValueError("Invalid logits/probability shape, dtype or finiteness")
    exp = np.exp(logits.astype(np.float64) - logits.max(1, keepdims=True))
    reference = exp / exp.sum(1, keepdims=True)
    if (np.any(probs < 0) or np.any(probs > 1)
            or not np.allclose(probs.sum(1), 1, atol=1e-6, rtol=0)
            or not np.allclose(probs, reference, atol=1e-6, rtol=0)):
        raise ValueError("Invalid probability distribution or softmax disagreement")
    return ids, labels, logits, probs


def aggregate_oof(manifest, run_directories, output, rgb_restoration=None):
    validate_baseline_manifest(manifest)
    if len(run_directories) != 3:
        raise ValueError("Exactly three folds required")
    by_id = {s["id"]: s for s in manifest["samples"]}
    rows, folds, sources, attempts = {}, set(), [], set()
    identity = None
    for directory in run_directories:
        root = Path(directory)
        metadata = read_json(root / "run.json")
        if metadata.get("recipe") == "opaque_tcn_v1":
            from .temporal_restore import load_temporal_run
            run, split, _ = load_temporal_run(manifest, root)
        elif metadata.get("recipe") == "rgb_pyramid_mlp_v2":
            from .rgb_head_restore import load_run as load_rgb_run, verify_restoration
            run, split, _ = load_rgb_run(manifest, root)
            if rgb_restoration is None:
                raise ValueError("RGB OOF needs complete original-video restoration")
            receipt_root = Path(rgb_restoration).parent
            restoration = read_json(rgb_restoration)
            if (restoration.get("profile") != "restore" or restoration.get("status") != "complete"
                    or restoration.get("clips") != 1125 or restoration.get("classification_trained") is not False
                    or {s.get("outer_signer") for s in restoration.get("restorations", [])} != {"M02", "M03", "M04"}):
                raise ValueError("Incomplete RGB original restoration")
            entry = next(r for r in restoration["restorations"] if r["outer_signer"] == split["outer_signer"])
            name = entry["receipt"]
            if Path(name).name != name or sha256(receipt_root/name) != entry["receipt_sha256"]:
                raise ValueError("RGB original restoration receipt hash mismatch")
            verify_restoration(root, manifest, read_json(receipt_root/name), receipt_root,
                               "original_train_videos_and_pinned_weight")
        else:
            run, split, _ = load_run(manifest, root)
        signature = (run["recipe"], run["protocol_revision"])
        if identity is not None and identity != signature:
            raise ValueError("Mixed OOF recipes")
        identity = signature
        if run["phase"] not in {"outer_baseline", "outer_temporal", "outer_rgb"}:
            raise ValueError("Diagnostic runs cannot enter complete OOF")
        signer = split["outer_signer"]
        if signer in folds or run["attempt_id"] in attempts:
            raise ValueError("Duplicate fold or attempt")
        folds.add(signer)
        attempts.add(run["attempt_id"])
        ids, labels, logits, probs = _validation_arrays(root, split, by_id)
        for i, sample_id in enumerate(ids.tolist()):
            if sample_id in rows:
                raise ValueError("Duplicate OOF ID")
            rows[sample_id] = (labels[i], logits[i], probs[i], signer)
        sources.append({"outer_signer": signer, "attempt_id": run["attempt_id"],
                        "job_id": run["job_id"], "run_sha256": sha256(root / "run.json"),
                        "files": run["files"]})
    if folds != {"M02", "M03", "M04"} or set(rows) != set(by_id):
        raise ValueError("Incomplete OOF coverage or unexpected signers")
    ids = list(by_id)
    labels = np.asarray([rows[i][0] for i in ids], dtype=np.int64)
    logits = np.stack([rows[i][1] for i in ids])
    probs = np.stack([rows[i][2] for i in ids])
    predictions = probs.argmax(1)
    report = {"revision": "oof_v1", "experiment_id": {"opaque_tcn_v1": "R2-E02O", "raw_stats_mlp_v2": "R2-E01",
                                                    "rgb_pyramid_mlp_v2": "R2-E08"}[identity[0]],
              "protocol_revision": identity[1], "recipe": identity[0], "seed": 17, "epochs": 80,
              "classes": CLASSES, "manifest_hash": manifest["manifest_hash"],
              "producer_hash": producer_hash(), "sources": sorted(sources, key=lambda s: s["outer_signer"]),
              "metric_scope": "development_loso_not_population_or_test",
              "overall": classification_metrics(labels, predictions), "diagnostics": {},
              "anatomical_missingness": "unknown_unverified_schema",
              "length_bins": ["<=40", "41-60", ">60"]}
    if identity[0] == "rgb_pyramid_mlp_v2":
        reversed_rows = {}
        for directory in run_directories:
            with np.load(Path(directory)/"validation.npz", allow_pickle=False) as archive:
                reverse = archive["reversed_probabilities"]
                if (reverse.shape != (375, 5) or reverse.dtype != np.float32 or not np.isfinite(reverse).all()
                        or np.any(reverse < 0) or not np.allclose(reverse.sum(1), 1, atol=1e-6, rtol=0)):
                    raise ValueError("Invalid RGB reverse diagnostic")
                reversed_rows.update(zip(archive["ids"].tolist(), reverse))
        reversed_predictions = np.stack([reversed_rows[i] for i in ids]).argmax(1)
        report["temporal_reverse_diagnostic"] = classification_metrics(labels, reversed_predictions)
        report["temporal_reverse_scope"] = "validation_only_same_model_no_direction_selection"
        report["original_restoration_sha256"] = sha256(rgb_restoration)
    fields = {"signer": [by_id[i]["signer"] for i in ids],
              "class": [by_id[i]["label"] for i in ids],
              "view": [by_id[i]["view"] for i in ids],
              "length": [("<=40" if by_id[i]["frames"] <= 40 else
                          "41-60" if by_id[i]["frames"] <= 60 else ">60") for i in ids]}
    for field, groups in fields.items():
        groups = np.asarray(groups)
        report["diagnostics"][field] = {
            str(g): classification_metrics(labels[groups == g], predictions[groups == g])
            for g in sorted(set(groups.tolist()))}
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    # A single-writer lock and atomic directory publication prevent partial results.
    lock = output.parent / ("." + output.name + ".lock")
    with lock.open("x"):
        staging = Path(tempfile.mkdtemp(prefix="." + output.name, dir=output.parent))
        try:
            if output.exists():
                raise FileExistsError(output)
            np.savez_compressed(staging / "oof.npz", ids=np.asarray(ids), labels=labels,
                                logits=logits, probabilities=probs, predictions=predictions,
                                correct=predictions == labels,
                                outer_signers=np.asarray([rows[i][3] for i in ids]))
            report.update(complete=True, oof_sha256=sha256(staging / "oof.npz"))
            atomic_json(staging / "report.json", report)
            os.rename(staging, output)
        finally:
            shutil.rmtree(staging, ignore_errors=True)
            lock.unlink()
    return report


def compare_oof(manifest, candidate, baseline, output, baseline_report_sha256):
    """Compare immutable, hash-checked development predictions by exact train ID."""
    validate_baseline_manifest(manifest)
    if sha256(Path(baseline)/"report.json") != baseline_report_sha256:
        raise ValueError("Frozen baseline report hash mismatch")
    arrays, sources = [], []
    candidate_recipe = read_json(Path(candidate)/"report.json").get("recipe")
    if candidate_recipe not in {"opaque_tcn_v1", "rgb_pyramid_mlp_v2"}:
        raise ValueError("Unsupported comparison candidate")
    if candidate_recipe == "rgb_pyramid_mlp_v2":
        from .rgb_loso_budget import BASELINE_SHA
        if baseline_report_sha256 != BASELINE_SHA:
            raise ValueError("RGB comparison requires the original frozen baseline anchor")
    for directory, recipe in [(candidate, candidate_recipe), (baseline, "raw_stats_mlp_v2")]:
        root = Path(directory)
        report = read_json(root/"report.json")
        if (report.get("manifest_hash") != manifest["manifest_hash"] or report.get("recipe") != recipe
                or not report.get("complete") or report.get("epochs") != 80 or report.get("seed") != 17
                or report.get("classes") != CLASSES or sha256(root/"oof.npz") != report["oof_sha256"]):
            raise ValueError("Incompatible comparison provenance")
        temporal = recipe == "opaque_tcn_v1"
        rgb = recipe == "rgb_pyramid_mlp_v2"
        if (report.get("revision") != "oof_v1"
                or report.get("experiment_id") != ("R2-E02O" if temporal else "R2-E08" if rgb else "R2-E01")
                or report.get("protocol_revision") != ("R2.2" if temporal else "R2.1")
                or report.get("metric_scope") != "development_loso_not_population_or_test"
                or not isinstance(report.get("producer_hash"), str) or len(report["producer_hash"]) != 64
                or (temporal or rgb) and report["producer_hash"] != producer_hash()
                or rgb and len(report.get("original_restoration_sha256", "")) != 64):
            raise ValueError("Incomplete comparison identity")
        provenance = report.get("sources", [])
        required_files = {"model.pt", "preprocessor.npz", "validation.npz", "split.json", "metrics.json"}
        if (len(provenance) != 3 or {s.get("outer_signer") for s in provenance} != {"M02", "M03", "M04"}
                or len({s.get("attempt_id") for s in provenance}) != 3
                or any(not s.get("job_id") or len(s.get("run_sha256", "")) != 64
                       or set(s.get("files", {})) != required_files for s in provenance)):
            raise ValueError("Incomplete OOF sources")
        with np.load(root/"oof.npz", allow_pickle=False) as archive:
            ids, labels, probs = archive["ids"], archive["labels"], archive["probabilities"]
        if (ids.tolist() != [s["id"] for s in manifest["samples"]]
                or labels.tolist() != [CLASSES.index(s["label"]) for s in manifest["samples"]]
                or probs.shape != (1125, 5) or not np.isfinite(probs).all()
                or np.any(probs < 0) or np.any(probs > 1)
                or not np.allclose(probs.sum(1), 1, atol=1e-6, rtol=0)):
            raise ValueError("Invalid comparison predictions")
        arrays.append(probs.argmax(1) == labels)
        sources.append({"report_sha256": sha256(root/"report.json"), "oof_sha256": report["oof_sha256"]})
    new, old = arrays
    signers = np.asarray([s["signer"] for s in manifest["samples"]])
    groups = {}
    for signer in sorted(set(signers.tolist())):
        mask = signers == signer
        groups[signer] = {"gained": int((new & ~old & mask).sum()),
                          "lost": int((~new & old & mask).sum()),
                          "delta_correct": int(new[mask].sum()-old[mask].sum())}
    delta = int(new.sum()-old.sum())
    result = {"revision": "paired_v1", "manifest_hash": manifest["manifest_hash"], "sources": sources,
              "candidate_correct": int(new.sum()), "baseline_correct": int(old.sum()),
              "delta_correct": delta, "by_signer": groups,
              "accuracy_promotion": delta >= 3 and min(g["delta_correct"] for g in groups.values()) >= -3,
              "cost_promotion": "not_assessed_requires_comparable_complete_cost",
              "causal_temporal_effect": "not_identified_input_and_architecture_changed"}
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    atomic_json(output, result)
    return result
