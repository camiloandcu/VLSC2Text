"""Portable hashes, safe paths and atomic private artifact writes."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def sha256(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def producer_hash():
    root = Path(__file__).parent
    return digest({p.name: sha256(p) for p in sorted(root.glob("*.py"))})


def read_json(path):
    with Path(path).open() as handle:
        return json.load(handle)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix="." + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def train_path(train_root, relative):
    root = Path(train_root).resolve(strict=True)
    relative = Path(relative)
    if root.name != "train" or relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Only relative paths inside an explicit train directory are allowed")
    path = (root / relative).resolve(strict=True)
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError("Input escapes train or is not a regular file")
    return path
