"""Accuracy wave X4/X6/X8: handedness canonicalisation, body normalisation and sequence models.

Layout accredited empirically (07 §13): pose 33x(x,y,z,vis) | face 468x3 | left hand 21x3 | right hand 21x3,
image-fraction units, signer-perspective laterality.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import random
import time

import numpy as np
import torch
from torch import nn

from .data import CLASSES, read_sequence
from .training import balanced_batches, configure_cpu, learning_rate

POSE, FACE, LH, RH = slice(0, 132), slice(132, 1536), slice(1536, 1599), slice(1599, 1662)
POSE_PAIRS = [(1, 4), (2, 5), (3, 6), (7, 8), (9, 10), (11, 12), (13, 14), (15, 16), (17, 18), (19, 20),
              (21, 22), (23, 24), (25, 26), (27, 28), (29, 30), (31, 32)]
POSE_KEEP = [0, 11, 12, 13, 14, 15, 16]
SEEDS = (17, 29, 43)


def split_blocks(x):
    t = len(x)
    return (x[:, POSE].reshape(t, 33, 4), x[:, FACE].reshape(t, 468, 3),
            x[:, LH].reshape(t, 21, 3), x[:, RH].reshape(t, 21, 3))


def join_blocks(pose, face, lh, rh):
    t = len(pose)
    return np.concatenate([pose.reshape(t, -1), face.reshape(t, -1), lh.reshape(t, -1), rh.reshape(t, -1)], 1)


def wrist_lift(x):
    """Label-free activity of left/right wrist: max rise above the final rest pose, in shoulder widths."""
    pose = x[:, POSE].reshape(len(x), 33, 4)
    width = np.abs(pose[:, 11, 0] - pose[:, 12, 0])
    scale = np.median(width[width > 1e-3]) if (width > 1e-3).any() else 1.0
    rest = np.median(pose[-3:, :, 1], axis=0)
    return [(rest[w] - pose[:, w, 1].min()) / scale for w in (15, 16)]


def left_dominant(x):
    left, right = wrist_lift(x)
    return bool(left > right)


def face_permutation(faces):
    """Mirror-symmetric face index map estimated from frontal train faces (label-free)."""
    f = np.median(np.stack(faces), axis=0)[:, :2]
    f = (f - f.mean(0)) / f.std(0)
    mirrored = f * np.array([-1.0, 1.0])
    d = ((mirrored[:, None, :] - f[None, :, :]) ** 2).sum(-1)
    return d.argmin(1)


def mirror(x, face_perm):
    pose, face, lh, rh = (b.copy() for b in split_blocks(x))
    for block in (pose, face, lh, rh):
        nz = (block[..., :3] != 0).any(-1)
        block[..., 0] = np.where(nz, 1.0 - block[..., 0], 0.0)
    for a, b in POSE_PAIRS:
        pose[:, [a, b]] = pose[:, [b, a]]
    face = face[:, face_perm]
    return join_blocks(pose, face, rh, lh)


def canonical(x, face_perm):
    return mirror(x, face_perm) if left_dominant(x) else x


def r0(x):
    return np.concatenate([x.mean(0), x.std(0)]).astype(np.float32)


def body_sequence(x):
    """Per-frame body-normalised features (R1/R2 of 04 §4 with masks), F=191."""
    pose, _, lh, rh = split_blocks(x)
    t = len(x)
    width = np.linalg.norm(pose[:, 11, :2] - pose[:, 12, :2], axis=1)
    valid = (width > 1e-3) & (pose[:, 11, 3] >= 0.5) & (pose[:, 12, 3] >= 0.5)
    if valid.any():
        centre = np.median((pose[valid, 11, :2] + pose[valid, 12, :2]) / 2, axis=0)
        scale = np.median(width[valid])
    else:
        centre, scale = np.array([0.5, 0.5]), 1.0
    pose_xy = (pose[:, POSE_KEEP, :2] - centre) / scale
    pose_mask = (pose[:, POSE_KEEP, 3] >= 0.5).astype(np.float32)
    pose_xy = pose_xy * pose_mask[..., None]
    glob_parts, local_parts, present_parts = [pose_xy.reshape(t, -1)], [], []
    for hand in (lh, rh):
        present = (hand != 0).any((1, 2))
        glob = np.where(present[:, None, None], (hand[..., :2] - centre) / scale, 0.0)
        span = np.linalg.norm(hand[:, 9, :2] - hand[:, 0, :2], axis=1)
        good = present & (span > 1e-3)
        hscale = np.median(span[good]) if good.any() else 1.0
        local = np.where(good[:, None, None], (hand[..., :2] - hand[:, :1, :2]) / hscale, 0.0)
        glob_parts.append(glob.reshape(t, -1))
        local_parts.append(local.reshape(t, -1))
        present_parts.append(present[:, None].astype(np.float32))
    # 49 global xy points first (98), then 9 masks, then 84 local hand-shape coordinates.
    feats = glob_parts + [pose_mask] + present_parts + local_parts
    return np.concatenate(feats, 1).astype(np.float32)


def masked_stats(seq):
    """Mean/std over frames plus three-segment temporal pyramid means."""
    thirds = np.array_split(np.arange(len(seq)), 3)
    parts = [seq.mean(0), seq.std(0)] + [seq[i].mean(0) if len(i) else seq.mean(0) for i in thirds]
    return np.concatenate(parts).astype(np.float32)


def active_segment(x, margin=3):
    """Frames where either wrist is raised above rest; deterministic per clip."""
    pose = x[:, POSE].reshape(len(x), 33, 4)
    width = np.abs(pose[:, 11, 0] - pose[:, 12, 0])
    scale = np.median(width[width > 1e-3]) if (width > 1e-3).any() else 1.0
    rest = np.median(pose[-3:, :, 1], axis=0)
    lift = np.maximum(rest[15] - pose[:, 15, 1], rest[16] - pose[:, 16, 1]) / scale
    on = np.where(lift > 0.25 * lift.max())[0] if lift.max() > 0 else np.arange(len(x))
    a, b = max(on.min() - margin, 0), min(on.max() + margin + 1, len(x))
    return slice(a, b) if b - a >= 8 else slice(0, len(x))


# ---------------------------------------------------------------- models
class MLP(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(dim, 128), nn.ReLU(), nn.Dropout(0.3), nn.Linear(128, 5))

    def forward(self, x):
        return self.layers(x)


class TCN(nn.Module):
    """compact_tcn_v2 of 04 §5 with an explicit time mask."""

    def __init__(self, dim, width=64):
        super().__init__()
        self.proj = nn.Linear(dim, width)
        self.convs = nn.ModuleList(nn.Conv1d(width, width, 5, dilation=d, padding=2 * d) for d in (1, 2, 4))
        self.norms = nn.ModuleList(nn.LayerNorm(width) for _ in range(3))
        self.drop = nn.Dropout(0.2)
        self.head = nn.Linear(width, 5)

    def forward(self, x, mask):
        m = mask.unsqueeze(-1).float()
        h = self.proj(x) * m
        for conv, norm in zip(self.convs, self.norms):
            r = conv(h.transpose(1, 2)).transpose(1, 2)
            h = (h + self.drop(nn.functional.gelu(norm(r)))) * m
        return self.head((h * m).sum(1) / m.sum(1).clamp(min=1))


def _seed(seed):
    configure_cpu()
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


def fit_mlp(x, y, signers, seed, epochs=80):
    _seed(seed)
    x = np.stack(x)
    mean, std = x.mean(0), x.std(0)
    std[std < 1e-6] = 1
    xt = torch.from_numpy(((x - mean) / std).astype(np.float32))
    yt = torch.from_numpy(y)
    model = MLP(x.shape[1])
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-3)
    loss_fn = nn.CrossEntropyLoss()
    for epoch in range(epochs):
        for g in opt.param_groups:
            g["lr"] = learning_rate(epoch)
        model.train()
        for batch in balanced_batches(y, signers, seed, epoch):
            idx = torch.from_numpy(batch.copy())
            opt.zero_grad(set_to_none=True)
            loss_fn(model(xt[idx]), yt[idx]).backward()
            opt.step()
    model.eval()

    def predict(v):
        with torch.inference_mode():
            v = np.stack(v)
            return torch.softmax(model(torch.from_numpy(((v - mean) / std).astype(np.float32))), 1).numpy()
    predict.state = {"kind": "mlp", "dim": x.shape[1], "mean": mean, "std": std, "model": model}
    return predict


def _augment(seq, rng, n_points):
    """Random similarity transform on xy point channels and time stretch (train only)."""
    seq = seq.copy()
    xy = seq[:, :n_points * 2].reshape(len(seq), n_points, 2)
    nz = (xy != 0).any(-1, keepdims=True)
    ang = math.radians(rng.uniform(-10, 10))
    rot = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    xy = np.where(nz, xy @ rot.T * rng.uniform(0.9, 1.1) + rng.normal(0, 0.05, 2), 0.0)
    seq[:, :n_points * 2] = xy.reshape(len(seq), -1)
    t = len(seq)
    new_t = int(np.clip(round(t * rng.uniform(0.8, 1.2)), 8, 128))
    return seq[np.clip(np.round(np.linspace(0, t - 1, new_t)).astype(int), 0, t - 1)]


def _pad(seqs):
    t = max(len(s) for s in seqs)
    x = np.zeros((len(seqs), t, seqs[0].shape[1]), np.float32)
    m = np.zeros((len(seqs), t), bool)
    for i, s in enumerate(seqs):
        x[i, :len(s)] = s
        m[i, :len(s)] = True
    return torch.from_numpy(x), torch.from_numpy(m)


def fit_tcn(seqs, y, signers, seed, augment=True, epochs=80, n_points=49):
    _seed(seed)
    frames = np.concatenate(seqs)
    mean, std = frames.mean(0), frames.std(0)
    std[std < 1e-6] = 1
    norm = lambda s: ((s - mean) / std).astype(np.float32)
    rng = np.random.default_rng(seed)
    model = TCN(seqs[0].shape[1])
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-3)
    loss_fn = nn.CrossEntropyLoss()
    yt = torch.from_numpy(y)
    for epoch in range(epochs):
        for g in opt.param_groups:
            g["lr"] = learning_rate(epoch)
        model.train()
        for batch in balanced_batches(y, signers, seed, epoch):
            batch_seqs = [norm(_augment(seqs[i], rng, n_points) if augment else seqs[i]) for i in batch]
            x, m = _pad(batch_seqs)
            opt.zero_grad(set_to_none=True)
            loss_fn(model(x, m), yt[torch.from_numpy(batch.copy())]).backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
    model.eval()

    def predict(vs):
        out = []
        with torch.inference_mode():
            for s in vs:
                x, m = _pad([norm(s)])
                out.append(torch.softmax(model(x, m), 1).numpy()[0])
        return np.stack(out)
    predict.state = {"kind": "tcn", "dim": seqs[0].shape[1], "mean": mean, "std": std, "model": model}
    return predict


# ---------------------------------------------------------------- LOSO driver
def load_train(train_root, manifest):
    samples = manifest["samples"]
    if "test" in Path(train_root).resolve().parts:
        raise ValueError("Train only")
    xs = [np.asarray(read_sequence(Path(train_root) / s["landmarks_path"])) for s in samples]
    y = np.array([CLASSES.index(s["label"]) for s in samples])
    signers = np.array([s["signer"] for s in samples])
    ids = [s["id"] for s in samples]
    return ids, xs, y, signers


def loso(features, y, signers, fit_fn, predict_input=None, seeds=SEEDS, train_extra=None):
    """features: list per clip (vector or sequence). train_extra(i) may add augmented copies for fit."""
    n = len(y)
    per_seed = {}
    for seed in seeds:
        probs = np.zeros((n, 5), np.float32)
        for held in ("M02", "M03", "M04"):
            fit = np.where(signers != held)[0]
            val = np.where(signers == held)[0]
            fx, fy, fs = [features[i] for i in fit], y[fit], signers[fit]
            if train_extra is not None:
                ex = [train_extra(i) for i in fit]
                fx, fy, fs = fx + ex, np.concatenate([fy, fy]), np.concatenate([fs, fs])
            predictor = fit_fn(fx, fy, fs, seed)
            inputs = [features[i] for i in val] if predict_input is None else [predict_input(i) for i in val]
            probs[val] = predictor(inputs)
        per_seed[seed] = probs
    return per_seed


def summarise(per_seed, y, signers, reference=None):
    avg = np.mean(list(per_seed.values()), axis=0)
    ok = avg.argmax(1) == y
    out = {"seeds": {int(s): int((p.argmax(1) == y).sum()) for s, p in per_seed.items()},
           "avg_correct": int(ok.sum()), "avg_accuracy": float(ok.mean()),
           "per_signer": {h: int(ok[signers == h].sum()) for h in ("M02", "M03", "M04")}}
    if reference is not None:
        r = reference.argmax(1) == y
        out["vs_reference"] = {"gained": int((ok & ~r).sum()), "lost": int((~ok & r).sum()),
                               "per_signer_delta": {h: int(ok[signers == h].sum() - r[signers == h].sum())
                                                    for h in ("M02", "M03", "M04")}}
    return out, avg


# ---------------------------------------------------------------- final bundle (X4 MLP + X6 TCN, 50/50)
BUNDLE_REVISION = "lsc5_wave_bundle_v1"


def clip_inputs(x, face_perm):
    """Deterministic per-sample transforms shared by training and inference."""
    c = canonical(x, face_perm)
    return masked_stats(body_sequence(c)), body_sequence(c[active_segment(c)])


def finalfit(train_root, manifest, out, seeds=SEEDS):
    from .io import sha256
    ids, xs, y, signers = load_train(train_root, manifest)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    faces = []
    for s, x in zip(manifest["samples"], xs):
        if s["view"] == "V01":
            f = x[:, FACE].reshape(len(x), 468, 3)
            ok = (f != 0).any((1, 2))
            if ok.any():
                faces.append(np.median(f[ok], 0))
    face_perm = face_permutation(faces)
    np.save(out / "face_perm.npy", face_perm)
    inputs = [clip_inputs(x, face_perm) for x in xs]
    stats, seqs = [i[0] for i in inputs], [i[1] for i in inputs]
    members, reference = [], []
    for seed in seeds:
        for kind, fit, data in (("mlp", fit_mlp, stats), ("tcn", fit_tcn, seqs)):
            start = time.perf_counter()
            predictor = fit(data, y, signers, seed)
            st = predictor.state
            name = f"{kind}_s{seed}"
            torch.save(st["model"].state_dict(), out / f"{name}.pt")
            np.savez_compressed(out / f"{name}_norm.npz", mean=st["mean"], std=st["std"])
            members.append({"name": name, "kind": kind, "seed": seed, "dim": int(st["dim"]),
                            "seconds": time.perf_counter() - start})
            reference.append((kind, predictor(data)))
    for m in members:
        m["model_sha256"] = sha256(out / f"{m['name']}.pt")
        m["norm_sha256"] = sha256(out / f"{m['name']}_norm.npz")
    ref = 0.5 * np.mean([p for k, p in reference if k == "mlp"], 0) + 0.5 * np.mean([p for k, p in reference if k == "tcn"], 0)
    np.savez_compressed(out / "train_reference.npz", ids=np.asarray(ids), probabilities=ref)
    bundle = {"revision": BUNDLE_REVISION, "classes": CLASSES, "members": members,
              "combination": "0.5*mean(mlp seeds) + 0.5*mean(tcn seeds)",
              "features": "canonical handedness (label-free wrist lift) -> body-normalised R1/R2 (191) -> "
                          "mlp: mean/std/3-segment means; tcn: active-segment sequence",
              "face_perm_sha256": sha256(out / "face_perm.npy"), "fit_clips": len(ids),
              "manifest_hash": manifest["manifest_hash"],
              "versions": {"numpy": np.__version__, "torch": str(torch.__version__)}}
    (out / "bundle.json").write_text(json.dumps(bundle, indent=2))
    return bundle


def load_bundle(bundle_dir):
    from .io import sha256
    bundle_dir = Path(bundle_dir)
    bundle = json.loads((bundle_dir / "bundle.json").read_text())
    if bundle.get("revision") != BUNDLE_REVISION or bundle.get("classes") != CLASSES:
        raise ValueError("Unsupported bundle")
    if sha256(bundle_dir / "face_perm.npy") != bundle["face_perm_sha256"]:
        raise ValueError("Bundle file hash mismatch")
    loaded = []
    for m in bundle["members"]:
        if (sha256(bundle_dir / f"{m['name']}.pt") != m["model_sha256"]
                or sha256(bundle_dir / f"{m['name']}_norm.npz") != m["norm_sha256"]):
            raise ValueError("Bundle file hash mismatch")
        model = MLP(m["dim"]) if m["kind"] == "mlp" else TCN(m["dim"])
        model.load_state_dict(torch.load(bundle_dir / f"{m['name']}.pt", weights_only=True))
        model.eval()
        with np.load(bundle_dir / f"{m['name']}_norm.npz", allow_pickle=False) as z:
            loaded.append((m["kind"], model, z["mean"], z["std"]))
    return bundle, np.load(bundle_dir / "face_perm.npy"), loaded


def predict_bundle(bundle_dir, paths, allow_test=False):
    """Per-sample probabilities; each row depends only on its own NPY file."""
    if not allow_test and any("test" in Path(p).resolve().parts for p in paths):
        raise ValueError("Test payloads are reserved for an authorised frozen run")
    configure_cpu()
    _, face_perm, members = load_bundle(bundle_dir)
    rows = []
    for path in paths:
        stats, seq = clip_inputs(np.asarray(read_sequence(path)), face_perm)
        by_kind = {"mlp": [], "tcn": []}
        with torch.inference_mode():
            for kind, model, mean, std in members:
                if kind == "mlp":
                    v = torch.from_numpy(((stats - mean) / std).astype(np.float32))[None]
                    by_kind[kind].append(torch.softmax(model(v), 1).numpy()[0])
                else:
                    x, m = _pad([((seq - mean) / std).astype(np.float32)])
                    by_kind[kind].append(torch.softmax(model(x, m), 1).numpy()[0])
        rows.append(0.5 * np.mean(by_kind["mlp"], 0) + 0.5 * np.mean(by_kind["tcn"], 0))
    return np.stack(rows)
