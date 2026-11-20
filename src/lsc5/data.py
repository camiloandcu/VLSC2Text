"""Train inventory and signer-held-out contracts. Never traverse test."""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import re

import numpy as np

from .io import digest, sha256, train_path

CLASSES = [f"sign_{i:02d}" for i in range(1, 6)]
NAME = re.compile(r"^S(0[1-5])_(M\d{2})_(V\d{2})_(C\d{2})_Clip\d+$")


def read_sequence(path):
    values = np.load(path, mmap_mode="r", allow_pickle=False)
    if values.dtype != np.float64 or values.ndim != 2 or values.shape[1] != 1662:
        raise ValueError("Expected float64 (T,1662) landmarks")
    if len(values) < 1 or not np.isfinite(values).all():
        raise ValueError("Empty or nonfinite sequence")
    return values


def validate_manifest(manifest):
    if manifest.get("data_role") != "train" or manifest.get("revision") != "train_manifest_v1":
        raise ValueError("Not a supported training manifest")
    content = {k: v for k, v in manifest.items() if k != "manifest_hash"}
    if manifest.get("manifest_hash") != digest(content):
        raise ValueError("Manifest hash mismatch")
    ids = [s["id"] for s in manifest["samples"]]
    if not ids or ids != sorted(set(ids)) or manifest["classes"] != CLASSES:
        raise ValueError("Invalid IDs or class mapping")
    hashes = {}
    for sample in manifest["samples"]:
        match = NAME.fullmatch(sample["id"])
        if not match or sample["label"] != CLASSES[int(match[1]) - 1] or sample["signer"] != match[2]:
            raise ValueError("Label/signer/ID disagreement")
        for field, suffix, modality in [("landmarks_path", ".npy", "landmarks"),
                                        ("video_path", ".mp4", "videos")]:
            p = PurePosixPath(sample[field])
            expected = PurePosixPath(modality, sample["label"], sample["id"] + suffix)
            if p != expected:
                raise ValueError("Invalid relative modality path")
        old = hashes.setdefault(sample["landmarks_sha256"], sample["signer"])
        if old != sample["signer"]:
            raise ValueError("Identical landmarks occur across signers")
    return manifest


def build_manifest(train_root, expected_count=None):
    root = Path(train_root).resolve(strict=True)
    if root.name != "train":
        raise ValueError("Expected an explicit train directory")
    samples = []
    for path in sorted((root / "landmarks").rglob("*.npy")):
        relative = path.relative_to(root).as_posix()
        path = train_path(root, relative)
        match = NAME.fullmatch(path.stem)
        if not match or path.parent.name != CLASSES[int(match[1]) - 1]:
            raise ValueError("Unexpected sample name or label folder")
        video_relative = str(PurePosixPath("videos", path.parent.name, path.stem + ".mp4"))
        video = train_path(root, video_relative)
        values = read_sequence(path)
        samples.append({"id": path.stem, "label": path.parent.name, "signer": match[2],
                        "view": match[3], "camera": match[4], "frames": len(values),
                        "dtype": "float64", "landmarks_path": relative,
                        "video_path": video_relative, "landmarks_sha256": sha256(path),
                        "video_sha256": sha256(video)})
    if expected_count is not None and len(samples) != expected_count:
        raise ValueError(f"Expected {expected_count} training clips; got {len(samples)}")
    result = {"revision": "train_manifest_v1", "data_role": "train", "classes": CLASSES,
              "schema_status": "opaque_only_anatomy_unverified", "samples": samples}
    result["manifest_hash"] = digest(result)
    return validate_manifest(result)


def make_splits(manifest):
    validate_manifest(manifest)
    signers = sorted({s["signer"] for s in manifest["samples"]})
    if len(signers) != 3:
        raise ValueError("LOSO requires exactly three training signers")
    splits = []
    for signer in signers:
        split = {"revision": "split_v1", "protocol_revision": "R2.1", "fit_role": "outer",
                 "manifest_hash": manifest["manifest_hash"], "outer_signer": signer,
                 "train_ids": [s["id"] for s in manifest["samples"] if s["signer"] != signer],
                 "validation_ids": [s["id"] for s in manifest["samples"] if s["signer"] == signer]}
        split["split_hash"] = digest(split)
        splits.append(split)
    return splits


def validate_split(manifest, split):
    expected = next((s for s in make_splits(manifest) if s["outer_signer"] == split.get("outer_signer")), None)
    if split != expected:
        raise ValueError("Split roles, IDs or provenance disagree with manifest")
    return split


def validate_baseline_manifest(manifest):
    """The official E01 contract requires the complete balanced training cohort."""
    validate_manifest(manifest)
    expected = {(s, c): 75 for s in ["M02", "M03", "M04"] for c in CLASSES}
    counts = {}
    for sample in manifest["samples"]:
        key = (sample["signer"], sample["label"])
        counts[key] = counts.get(key, 0) + 1
    if len(manifest["samples"]) != 1125 or counts != expected:
        raise ValueError("Complete baseline requires 1125 clips, 75 per signer/class")
    return manifest
