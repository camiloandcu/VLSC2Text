"""Deterministic train-only RGB sampling and bounded streaming decode."""
from pathlib import Path
import hashlib
import json
import math
import subprocess
import tempfile
import time

import numpy as np

from .data import CLASSES, validate_baseline_manifest
from .io import digest, sha256, train_path

TRANSFORM = {"schema": "dinov2s14_cls_v2", "K": 16, "size": 224,
             "resize": "Pillow_bilinear_half_up", "padding_rgb": [124, 116, 104],
             "mean": [.485, .456, .406], "std": [.229, .224, .225],
             "orientation": "reject_nonzero_rotation", "pixel_format": "rgb24",
             "sampling": "floor(j*(N-1)/15+0.5)", "dtype": "float32",
             "feature": "x_norm_clstoken_LayerNorm_not_L2", "registers": 0}


def select_pilot(manifest):
    validate_baseline_manifest(manifest)
    selected = []
    for signer in ["M02", "M03", "M04"]:
        for label in CLASSES:
            group = sorted((s for s in manifest["samples"] if s["signer"] == signer
                            and s["label"] == label), key=lambda s: (s["frames"], s["id"]))
            selected.extend([group[0], group[-1]])
    if len({s["id"] for s in selected}) != 30:
        raise ValueError("Pilot requires thirty distinct preselected train clips")
    return selected


def indices(n):
    if not isinstance(n, int) or n < 1:
        raise ValueError("Positive real video frame count required")
    return np.asarray([(2*j*(n-1)+15)//30 for j in range(16)], dtype=np.int64)


def letterbox(frame):
    from PIL import Image
    if frame.dtype != np.uint8 or frame.ndim != 3 or frame.shape[2] != 3 or min(frame.shape[:2]) < 1:
        raise ValueError("Expected nonempty RGB uint8 frame")
    h, w = frame.shape[:2]
    scale = 224/max(w, h)
    nw, nh = max(1, math.floor(w*scale+.5)), max(1, math.floor(h*scale+.5))
    resized = Image.fromarray(frame).resize((nw, nh), resample=Image.Resampling.BILINEAR)
    canvas = Image.new("RGB", (224, 224), tuple(TRANSFORM["padding_rgb"]))
    canvas.paste(resized, ((224-nw)//2, (224-nh)//2))
    return np.asarray(canvas)


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-threads", "1", "-select_streams", "v:0",
                        "-count_frames", "-show_streams", "-of", "json", str(path)],
                       capture_output=True, text=True, timeout=30, check=True)
    if r.stderr.strip():
        raise ValueError("Video probe reported decode errors")
    streams = json.loads(r.stdout)["streams"]
    if len(streams) != 1:
        raise ValueError("Exactly one selected video stream required")
    s = streams[0]
    rotations = [s.get("tags", {}).get("rotate", 0)]
    rotations += [item.get("rotation", 0) for item in s.get("side_data_list", [])]
    if any(not math.isfinite(float(v)) or float(v) % 360 != 0 for v in rotations):
        raise ValueError("Nonzero video rotation requires explicit protocol revision")
    n, w, h = int(s["nb_read_frames"]), int(s["width"]), int(s["height"])
    if n < 1 or min(w, h) < 1 or w*h > 4096*4096:
        raise ValueError("Invalid or unbounded video dimensions/count")
    return n, w, h


def _read_exact(pipe, size):
    chunks, left = [], size
    while left:
        part = pipe.read(left)
        if not part:
            break
        chunks.append(part)
        left -= len(part)
    return b"".join(chunks)


def decode(train_root, sample, selected_transport=True):
    started = time.perf_counter()
    path = train_path(train_root, sample["video_path"])
    if sha256(path) != sample["video_sha256"]:
        raise ValueError("Original video hash mismatch")
    hash_seconds = time.perf_counter()-started
    tick = time.perf_counter()
    n, w, h = probe(path)
    count_seconds = time.perf_counter()-tick
    chosen = indices(n)
    positions = {}
    for j, i in enumerate(chosen.tolist()):
        positions.setdefault(i, []).append(j)
    result = np.empty((16, 224, 224, 3), dtype=np.uint8)
    command = ["ffmpeg", "-v", "error", "-xerror", "-threads", "1", "-filter_threads", "1",
               "-noautorotate", "-i", str(path), "-map", "0:v:0", "-an", "-sn", "-dn",
               "-vsync", "0", "-threads", "1"]
    selected = sorted(positions)
    if selected_transport:
        command += ["-vf", "select="+"+".join(f"eq(n\\,{i})" for i in selected)]
    command += ["-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"]
    tick = time.perf_counter()
    resize_seconds, count = 0., 0
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=errors)
        try:
            while True:
                raw = _read_exact(process.stdout, w*h*3)
                if not raw:
                    break
                if len(raw) != w*h*3:
                    raise ValueError("Truncated decoded RGB frame")
                frame_index = selected[count] if selected_transport and count < len(selected) else count
                if frame_index in positions:
                    t = time.perf_counter()
                    image = letterbox(np.frombuffer(raw, np.uint8).reshape(h, w, 3))
                    for j in positions[frame_index]:
                        result[j] = image
                    resize_seconds += time.perf_counter()-t
                count += 1
            process.wait(timeout=10)
            errors.seek(0)
            expected_count = len(selected) if selected_transport else n
            if process.returncode or errors.read(4096).strip() or count != expected_count:
                raise ValueError("Video decoding failed or actual frame count changed")
        finally:
            process.stdout.close()
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
    elapsed = time.perf_counter()-tick
    return result, {"id": sample["id"], "video_sha256": sample["video_sha256"],
                    "video_frames": n, "indices": chosen.tolist(), "width": w, "height": h,
                    "pixels_sha256": hashlib.sha256(result.tobytes()).hexdigest(),
                    "selected_transport": selected_transport,
                    "video_bytes": path.stat().st_size, "hash_seconds": hash_seconds,
                    "count_seconds": count_seconds, "resize_seconds": resize_seconds,
                    "decode_seconds_excluding_resize": elapsed-resize_seconds}
