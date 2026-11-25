"""In-memory wrapper around the frozen iter4 bundle for the live demo.

Same steps as ``lsc5.wave_iter.predict_bundle_v3`` (hash checks, canonicalisation,
features, mean of the three seeds), but it takes a landmark array instead of a path.
"""
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn

from lsc5 import wave
from lsc5.io import sha256
from lsc5.wave_iter import BUNDLE_V3, canonical_cfg, features

DATASET_FPS = 24.0


class Predictor:
    def __init__(self, bundle_dir):
        bundle_dir = Path(bundle_dir)
        bundle = json.loads((bundle_dir / "bundle.json").read_text())
        if bundle.get("revision") != BUNDLE_V3 or bundle.get("classes") != wave.CLASSES:
            raise ValueError("Unsupported bundle")
        if sha256(bundle_dir / "face_perm.npy") != bundle["face_perm_sha256"]:
            raise ValueError("Bundle file hash mismatch")
        wave.configure_cpu()
        self.classes = bundle["classes"]
        self.face_perm = np.load(bundle_dir / "face_perm.npy")
        self.cfg = bundle["cfg"]
        self.models = []
        for m in bundle["members"]:
            if (sha256(bundle_dir / f"{m['name']}.pt") != m["model_sha256"]
                    or sha256(bundle_dir / f"{m['name']}_norm.npz") != m["norm_sha256"]):
                raise ValueError("Bundle file hash mismatch")
            model = nn.Sequential(nn.Linear(m["dim"], m["hidden"]), nn.ReLU(), nn.Dropout(m["dropout"]),
                                  nn.Linear(m["hidden"], 5))
            model.load_state_dict(torch.load(bundle_dir / f"{m['name']}.pt", weights_only=True))
            model.eval()
            with np.load(bundle_dir / f"{m['name']}_norm.npz", allow_pickle=False) as z:
                self.models.append((model, z["mean"], z["std"]))

    @staticmethod
    def resample(x, timestamps_ms):
        """Nearest-frame resampling to the dataset frame rate, using capture timestamps."""
        t = (np.asarray(timestamps_ms, dtype=np.float64) - timestamps_ms[0]) / 1000.0
        n = max(int(round(t[-1] * DATASET_FPS)) + 1, 1)
        grid = np.arange(n) / DATASET_FPS
        idx = np.clip(np.searchsorted(t, grid), 0, len(t) - 1)
        prev = np.clip(idx - 1, 0, len(t) - 1)
        idx = np.where(np.abs(t[prev] - grid) < np.abs(t[idx] - grid), prev, idx)
        return x[idx]

    def predict(self, x, timestamps_ms=None):
        x = np.asarray(x, dtype=np.float64)
        if x.ndim != 2 or x.shape[1] != 1662 or len(x) < 1 or not np.isfinite(x).all():
            raise ValueError("Expected finite (T,1662) landmarks")
        if timestamps_ms is not None:
            x = self.resample(x, timestamps_ms)
        c = canonical_cfg(x, self.face_perm, self.cfg)
        views = self.cfg.get("tta") or [None]
        with torch.inference_mode():
            probs = [torch.softmax(m(torch.from_numpy(((features(c, self.cfg, view=v) - mu) / sd).astype(np.float32))[None]), 1).numpy()[0]
                     for v in views for m, mu, sd in self.models]
        return np.mean(probs, 0)
