"""Torch-free predictor for small servers: same features and same MLP maths as demo/predictor.py.

The MLP weights are exported once from the frozen bundle (demo/export_numpy.py) to mlp_sXX_weights.npz.
lsc5 imports torch at module level for training code only; when torch is absent a stub is installed
so the feature functions (pure numpy) can be imported. Parity with the torch path is checked by the
export script.
"""
import importlib.util
import json
import sys
import types
from pathlib import Path

import numpy as np

if importlib.util.find_spec("torch") is None:
    class _Any:
        def __init__(self, *a, **k): pass
        def __call__(self, *a, **k): return self
        def __getattr__(self, name): return _Any()
    torch = types.ModuleType("torch")
    torch.nn = types.ModuleType("torch.nn")
    torch.nn.Module = type("Module", (), {})
    torch.__getattr__ = lambda name: _Any()
    torch.nn.__getattr__ = lambda name: _Any
    sys.modules["torch"], sys.modules["torch.nn"] = torch, torch.nn

from lsc5 import wave  # noqa: E402
from lsc5.io import sha256  # noqa: E402
from lsc5.wave_iter import BUNDLE_V3, canonical_cfg, features  # noqa: E402

DATASET_FPS = 24.0


class Predictor:
    def __init__(self, bundle_dir):
        bundle_dir = Path(bundle_dir)
        bundle = json.loads((bundle_dir / "bundle.json").read_text())
        if bundle.get("revision") != BUNDLE_V3 or bundle.get("classes") != wave.CLASSES:
            raise ValueError("Unsupported bundle")
        if sha256(bundle_dir / "face_perm.npy") != bundle["face_perm_sha256"]:
            raise ValueError("Bundle file hash mismatch")
        self.classes = bundle["classes"]
        self.face_perm = np.load(bundle_dir / "face_perm.npy")
        self.cfg = bundle["cfg"]
        self.models = []
        for m in bundle["members"]:
            if sha256(bundle_dir / f"{m['name']}_norm.npz") != m["norm_sha256"]:
                raise ValueError("Bundle file hash mismatch")
            with np.load(bundle_dir / f"{m['name']}_weights.npz", allow_pickle=False) as w:
                if str(w["source_sha256"]) != m["model_sha256"]:
                    raise ValueError("Exported weights do not come from this bundle")
                layers = (w["w0"], w["b0"], w["w1"], w["b1"])
            with np.load(bundle_dir / f"{m['name']}_norm.npz", allow_pickle=False) as z:
                self.models.append((layers, z["mean"], z["std"]))

    resample = staticmethod(lambda x, t: _resample(x, t))

    def predict(self, x, timestamps_ms=None):
        x = np.asarray(x, dtype=np.float64)
        if x.ndim != 2 or x.shape[1] != 1662 or len(x) < 1 or not np.isfinite(x).all():
            raise ValueError("Expected finite (T,1662) landmarks")
        if timestamps_ms is not None:
            x = _resample(x, timestamps_ms)
        c = canonical_cfg(x, self.face_perm, self.cfg)
        views = self.cfg.get("tta") or [None]
        out = []
        for v in views:
            f = features(c, self.cfg, view=v)
            for (w0, b0, w1, b1), mu, sd in self.models:
                h = ((f - mu) / sd).astype(np.float32) @ w0.T + b0
                z = np.maximum(h, 0) @ w1.T + b1
                e = np.exp(z - z.max())
                out.append(e / e.sum())
        return np.mean(out, 0)


def _resample(x, timestamps_ms):
    t = (np.asarray(timestamps_ms, dtype=np.float64) - timestamps_ms[0]) / 1000.0
    n = max(int(round(t[-1] * DATASET_FPS)) + 1, 1)
    grid = np.arange(n) / DATASET_FPS
    idx = np.clip(np.searchsorted(t, grid), 0, len(t) - 1)
    prev = np.clip(idx - 1, 0, len(t) - 1)
    idx = np.where(np.abs(t[prev] - grid) < np.abs(t[idx] - grid), prev, idx)
    return np.asarray(x)[idx]
