"""Pilot-only frozen RGB cache, metrics and replay. No classifier or labels as features."""
from pathlib import Path
import hashlib
import os
import resource
import shutil
import subprocess
import tempfile
import time

import numpy as np

from .io import atomic_json, digest, producer_hash, read_json, sha256
from .rgb_budget import validate_reservation
from .rgb_encoder import Encoder, COMMIT, WEIGHT_SHA256, SOURCE_INVENTORY_HASH
from .rgb_frames import TRANSFORM, decode, indices, select_pilot

CACHE_FIELDS = {"cache_schema_version": "rgb_cache_v1", "protocol_revision": "R2.1_RGB_pilot",
                "feature_schema_id": "dinov2s14_cls_v2", "cache_kind": "cls"}


def require_supervisor():
    if os.environ.get("LSC5_RGB_SUPERVISOR_PID") != str(os.getppid()):
        raise ValueError("RGB workers must run through the monitored supervisor")


def load_cache(directory, manifest, expected_ids=None, coverage="pilot30"):
    root = Path(directory)
    meta = read_json(root/"metadata.json")
    if coverage not in {"pilot30", "full1125"}:
        raise ValueError("Unknown RGB coverage")
    from .data import validate_baseline_manifest
    validate_baseline_manifest(manifest)
    samples = select_pilot(manifest) if coverage == "pilot30" else manifest["samples"]
    ids = [s["id"] for s in samples]
    expected = {**CACHE_FIELDS, "coverage": coverage, "scope": "train", "complete": True,
                "manifest_hash": manifest["manifest_hash"], "producer_hash": producer_hash(),
                "ids": ids, "selection_hash": digest(ids), "transform": TRANSFORM,
                "learned_dependencies": [], "compute_dtype": "float32", "storage_dtype": "float32"}
    if any(meta.get(k) != v for k, v in expected.items()) or expected_ids is not None and ids != expected_ids:
        raise ValueError("Pilot cache coverage/identity incompatible; not full train")
    asset = meta.get("encoder", {})
    versions = meta.get("versions", {})
    if any(versions.get(k) != v for k, v in {"torch": "2.4.1+cu121", "torchvision": "0.19.1+cu121",
                                              "pillow": "11.3.0"}.items()):
        raise ValueError("Cache environment versions mismatch")
    if (asset.get("commit") != COMMIT or asset.get("weight_sha256") != WEIGHT_SHA256
            or asset.get("source_inventory_hash") != SOURCE_INVENTORY_HASH
            or asset.get("architecture") != "dinov2_vits14_no_registers"
            or asset.get("eval") is not True or asset.get("frozen") is not True
            or asset.get("weight_url") != "https://dl.fbaipublicfiles.com/dinov2/dinov2_vits14/dinov2_vits14_pretrain.pth"):
        raise ValueError("Cache encoder identity mismatch")
    rows = meta.get("clips", [])
    if len(rows) != len(samples) or {p.name for p in root.glob("*.npz")} != {f"{i:04d}.npz" for i in range(len(samples))}:
        raise ValueError("Incomplete pilot cache inventory")
    for i, (row, sample) in enumerate(zip(rows, samples)):
        path = root/f"{i:04d}.npz"
        if (row.get("id") != sample["id"] or row.get("video_sha256") != sample["video_sha256"]
                or row.get("file") != path.name or sha256(path) != row.get("sha256")
                or len(row.get("pixels_sha256", "")) != 64
                or row.get("indices") != indices(row["video_frames"]).tolist()):
            raise ValueError("Pilot cache clip provenance mismatch")
        with np.load(path, allow_pickle=False) as archive:
            x = archive["embeddings"]
        if x.shape != (16, 384) or x.dtype != np.float32 or not np.isfinite(x).all():
            raise ValueError("Invalid pilot embeddings")
    return meta


def run_pilot(train_root, manifest, assets_root, reservation, output, coverage="pilot30"):
    require_supervisor()
    if coverage == "pilot30":
        validate_reservation(reservation, manifest)
        selected = select_pilot(manifest)
    elif coverage == "full1125":
        from .rgb_loso_budget import validate_gpu_reservation
        validate_gpu_reservation(reservation, manifest)
        selected = manifest["samples"]
    else:
        raise ValueError("Unknown RGB coverage")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    run = {"phase": "rgb_encoder_pilot_not_candidate" if coverage == "pilot30" else "rgb_encoder_full_not_classifier", "status": "running",
           "attempt_id": reservation["id"], "reservation_hash": reservation["reservation_hash"],
           "producer_hash": producer_hash(), "manifest_hash": manifest["manifest_hash"],
           "classification_trained": False}
    atomic_json(output/"run.json", run)
    stage = Path(tempfile.mkdtemp(prefix=".cache-", dir=output))
    started = time.perf_counter()
    try:
        encoder = Encoder(assets_root)
        encoder_startup = time.perf_counter()-started
        clips, batches, warmup_seconds = [], [], 0.
        for i, sample in enumerate(selected):
            tick = time.perf_counter()
            pixels, info = decode(train_root, sample)
            if i == 0:
                warm = time.perf_counter()
                for _ in range(5):
                    encoder.extract(pixels[:4])
                warmup_seconds = time.perf_counter()-warm
            values, timings = encoder.extract(pixels)
            batches.extend(timings)
            write = time.perf_counter()
            path = stage/f"{i:04d}.npz"
            np.savez_compressed(path, embeddings=values)
            info.update(file=path.name, sha256=sha256(path), embedding_bytes=path.stat().st_size,
                        write_and_verification_seconds=time.perf_counter()-write,
                        complete_clip_seconds=time.perf_counter()-tick-(warmup_seconds if i == 0 else 0))
            clips.append(info)
            if coverage == "full1125" and (i+1) % 25 == 0:
                atomic_json(output/"progress.json", {"complete_clips": i+1, "total": len(selected),
                                                       "elapsed_seconds": time.perf_counter()-started})
        if len(batches) < 10:
            raise ValueError("Insufficient measured batches after warm-up")
        finalize = time.perf_counter()
        versions = {**encoder.versions,
                    "ffmpeg": subprocess.check_output(["ffmpeg", "-version"], text=True).splitlines()[0],
                    "ffprobe": subprocess.check_output(["ffprobe", "-version"], text=True).splitlines()[0]}
        meta = {**CACHE_FIELDS, "coverage": coverage, "scope": "train", "complete": True,
                "manifest_hash": manifest["manifest_hash"], "producer_hash": producer_hash(),
                "ids": [s["id"] for s in selected], "transform": TRANSFORM,
                "selection_hash": digest([s["id"] for s in selected]), "encoder": encoder.identity,
                "learned_dependencies": [], "compute_dtype": "float32", "storage_dtype": "float32",
                "versions": versions, "clips": clips}
        atomic_json(stage/"metadata.json", meta)
        load_cache(stage, manifest, coverage=coverage)
        os.rename(stage, output/"cache")
        finalization_seconds = time.perf_counter()-finalize
        maximum = max(r["complete_clip_seconds"] for r in clips)
        startup = encoder_startup+warmup_seconds
        metrics = {"clips": len(selected), "image_forwards": 16*len(selected), "warmup_batches": 5,
                   "measured_batches": len(batches), "batches": batches, "encoder_startup_seconds": encoder_startup,
                   "warmup_seconds": warmup_seconds, "maximum_complete_clip_seconds": maximum,
                   "process_seconds": time.perf_counter()-started,
                   "parent_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   "decoder_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                   **encoder.memory_stats(),
                   "parameter_count": encoder.parameter_count, "versions": versions,
                   "finalization_seconds": finalization_seconds,
                   "projected_train_extraction_seconds_with_margin": 1.5*(1125*maximum+startup+finalization_seconds),
                   "projected_375_clip_extraction_seconds_with_margin": 1.5*(375*maximum+startup+finalization_seconds),
                   "projection_condition": "similar_video_lengths_hardware_load_and_decoder; head/refit_unknown",
                   "whole_chain_admitted": False}
        atomic_json(output/"metrics.json", metrics)
        run.update(status="complete", files={"metrics.json": sha256(output/"metrics.json"),
                                            "cache/metadata.json": sha256(output/"cache/metadata.json")})
        atomic_json(output/"run.json", run)
        return metrics
    except BaseException as error:
        run.update(status="failed", error_type=type(error).__name__, error=str(error))
        atomic_json(output/"run.json", run)
        raise


def replay(train_root, manifest, assets_root, directory, output):
    require_supervisor()
    root = Path(directory)
    meta = load_cache(root/"cache", manifest)
    run = read_json(root/"run.json")
    if (run.get("status") != "complete" or run.get("phase") != "rgb_encoder_pilot_not_candidate"
            or run.get("producer_hash") != producer_hash()
            or any(sha256(root/n) != value for n, value in run.get("files", {}).items())
            or set(run.get("files", {})) != {"metrics.json", "cache/metadata.json"}):
        raise ValueError("Incompatible pilot run for replay")
    sample = select_pilot(manifest)[0]
    pixels, info = decode(train_root, sample)
    if info["pixels_sha256"] != meta["clips"][0]["pixels_sha256"]:
        raise ValueError("Replay pixels disagree")
    encoder = Encoder(assets_root)
    one, one_times = encoder.extract(pixels, batch_size=1)
    four, four_times = encoder.extract(pixels, batch_size=4)
    with np.load(root/"cache/0000.npz", allow_pickle=False) as archive:
        reference = archive["embeddings"]
    errors = [float(np.linalg.norm((x-reference).astype(np.float64))/max(np.linalg.norm(reference.astype(np.float64)), 1e-12))
              for x in [one, four]]
    direct = float(np.linalg.norm((one-four).astype(np.float64))/max(np.linalg.norm(four.astype(np.float64)), 1e-12))
    if not np.isfinite(errors+[direct]).all() or max(errors+[direct]) > 1e-4:
        raise ValueError("Replay relative L2 exceeds 1e-4")
    output = Path(output)
    if output.exists() or output.with_suffix(".npz").exists():
        raise FileExistsError(output)
    np.savez_compressed(output.with_suffix(".npz"), batch1=one, batch4=four)
    result = {"status": "complete", "source": "original_train_video_and_pinned_weight",
              "sample_id": sample["id"], "pixels_sha256": info["pixels_sha256"],
              "producer_hash": producer_hash(), "manifest_hash": manifest["manifest_hash"],
              "pilot_run_sha256": sha256(root/"run.json"), "encoder": encoder.identity,
              "relative_l2_batch1_batch4_vs_reference": errors,
              "relative_l2_batch1_vs_batch4": direct,
              "maximum_absolute_error": float(max(np.max(np.abs(x-reference)) for x in [one, four])),
              "forward_seconds": sum(b["forward_seconds"] for b in one_times+four_times),
              "arrays_file": output.with_suffix(".npz").name, "arrays_sha256": sha256(output.with_suffix(".npz"))}
    atomic_json(output, result)
    return result
