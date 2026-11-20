"""Fit-only channel statistics and the fixed global/half temporal pyramid."""
import numpy as np
import torch
from torch import nn

from .rgb_pilot import load_cache
from .training import HYPERPARAMETERS as BASE_HYPERPARAMETERS

HYPERPARAMETERS = {**BASE_HYPERPARAMETERS, "input_dim": 1152, "encoder_channels": 384,
                   "frames": 16, "pyramid": ["mean_all", "mean_first8", "mean_last8"],
                   "scaler": "channel_population_all_fit_frames_float64"}


def load_embeddings(cache, manifest):
    meta = load_cache(cache, manifest, coverage="full1125")
    from pathlib import Path
    values = []
    for row in meta["clips"]:
        with np.load(Path(cache)/row["file"], allow_pickle=False) as a:
            values.append(a["embeddings"])
    return np.stack(values), meta


def fit_scaler(values, fit_ids):
    x = np.asarray(values)
    if (x.shape != (len(fit_ids), 16, 384) or x.dtype != np.float32 or not np.isfinite(x).all()
            or not len(fit_ids) or len(set(fit_ids)) != len(fit_ids)):
        raise ValueError("Invalid channel-scaler fit inputs")
    flat = x.astype(np.float64).reshape(-1, 384)
    mean = flat.mean(0)
    scale = flat.std(0, ddof=0)
    scale[scale < 1e-6] = 1
    return {"mean": mean.astype(np.float32), "scale": scale.astype(np.float32),
            "fit_ids": np.asarray(fit_ids)}


def pyramid(values, scaler, reverse=False):
    x = np.asarray(values)
    if x.ndim != 3 or x.shape[1:] != (16, 384) or x.dtype != np.float32 or not np.isfinite(x).all():
        raise ValueError("Expected float32 N×16×384 embeddings")
    if reverse:
        x = x[:, ::-1]
    scaled = (x-scaler["mean"])/scaler["scale"]
    return np.concatenate([a.mean(1, dtype=np.float64) for a in
                           [scaled, scaled[:, :8], scaled[:, 8:]]], axis=1).astype(np.float32)


class RGBPyramidMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(1152, 128), nn.ReLU(), nn.Dropout(.3), nn.Linear(128, 5))

    def forward(self, x):
        if x.ndim != 2 or x.shape[1] != 1152:
            raise ValueError("Expected temporal pyramid1152")
        return self.layers(x)


def infer(model, features):
    model.eval()
    with torch.inference_mode():
        logits = model(torch.as_tensor(features, dtype=torch.float32))
        return logits.numpy(), torch.softmax(logits, 1).numpy()
