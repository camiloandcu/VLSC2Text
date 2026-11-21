"""Iteration 2 feature/augmentation variants on top of the frozen wave pipeline (wave.py stays unchanged)."""
from __future__ import annotations

import math

import numpy as np

from . import wave

POSE_KEEP = wave.POSE_KEEP


def _geometry(x):
    pose, _, lh, rh = wave.split_blocks(x)
    width = np.linalg.norm(pose[:, 11, :2] - pose[:, 12, :2], axis=1)
    valid = (width > 1e-3) & (pose[:, 11, 3] >= 0.5) & (pose[:, 12, 3] >= 0.5)
    if valid.any():
        centre = np.median((pose[valid, 11, :2] + pose[valid, 12, :2]) / 2, axis=0)
        scale = np.median(width[valid])
    else:
        centre, scale = np.array([0.5, 0.5]), 1.0
    return pose, lh, rh, centre, scale


def relation_features(x):
    """Inter-hand and hand-to-face relations (scale units); zeros + flags when a hand is missing."""
    pose, lh, rh, centre, scale = _geometry(x)
    nose = (pose[:, 0, :2] - centre) / scale
    feats = []
    cents = []
    for hand in (lh, rh):
        present = (hand != 0).any((1, 2))
        c = np.where(present[:, None], (hand[:, :, :2].mean(1) - centre) / scale, 0.0)
        cents.append((c, present))
        feats.append(np.where(present[:, None], c - nose, 0.0))                       # hand relative to nose
    (cl, pl), (cr, pr) = cents
    both = pl & pr
    diff = np.where(both[:, None], cl - cr, 0.0)
    feats += [diff, np.linalg.norm(diff, axis=1, keepdims=True), both[:, None].astype(float)]
    return np.concatenate(feats, 1).astype(np.float32)                                   # 2+2+2+1+1 = 8


def handshape_features(x):
    """Rotation/scale-invariant handshape: fingertip-to-wrist and fingertip-to-thumb-tip distances."""
    _, _, lh, rh = wave.split_blocks(x)
    out = []
    for hand in (lh, rh):
        present = (hand != 0).any((1, 2))
        xy = hand[:, :, :2]
        span = np.linalg.norm(xy[:, 9] - xy[:, 0], axis=1)
        span = np.where(span > 1e-4, span, 1.0)
        tips = [4, 8, 12, 16, 20]
        d_wrist = np.stack([np.linalg.norm(xy[:, t] - xy[:, 0], axis=1) for t in tips], 1) / span[:, None]
        d_thumb = np.stack([np.linalg.norm(xy[:, t] - xy[:, 4], axis=1) for t in tips[1:]], 1) / span[:, None]
        out.append(np.where(present[:, None], np.concatenate([d_wrist, d_thumb], 1), 0.0))
    return np.concatenate(out, 1).astype(np.float32)                                     # 2*(5+4) = 18


def sequence(x, relations=False, handshape=False):
    parts = [wave.body_sequence(x)]
    if relations:
        parts.append(relation_features(x))
    if handshape:
        parts.append(handshape_features(x))
    return np.concatenate(parts, 1)


def view_augment(x, rng, yaw_lo=0.7, max_roll=8.0):
    """Simulate camera yaw/roll/zoom on raw image-fraction coordinates of pose and hands (train only)."""
    pose, face, lh, rh = (b.copy() for b in wave.split_blocks(x))
    sh = pose[:, [11, 12], :2]
    c = np.median(sh.reshape(-1, 2), axis=0)
    yaw = rng.uniform(yaw_lo, 1.0)                    # horizontal foreshortening
    ang = math.radians(rng.uniform(-max_roll, max_roll))
    zoom = rng.uniform(0.85, 1.15)
    rot = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    for block in (pose, lh, rh):
        nz = (block[..., :2] != 0).any(-1, keepdims=True)
        p = block[..., :2] - c
        p[..., 0] *= yaw
        block[..., :2] = np.where(nz, (p @ rot.T) * zoom + c, 0.0)
    return wave.join_blocks(pose, face, lh, rh)


def time_augment(x, rng):
    t = len(x)
    new_t = int(np.clip(round(t * rng.uniform(0.8, 1.2)), 8, 128))
    return x[np.clip(np.round(np.linspace(0, t - 1, new_t)).astype(int), 0, t - 1)]


def velocity_features(seq, n_points=49):
    """Frame differences of the 49 global points; zero where a point is missing in either frame."""
    xy = seq[:, :n_points * 2].reshape(len(seq), n_points, 2)
    present = (xy != 0).any(-1)
    d = np.zeros_like(xy)
    ok = present[1:] & present[:-1]
    d[1:] = np.where(ok[..., None], xy[1:] - xy[:-1], 0.0)
    return d.reshape(len(seq), -1).astype(np.float32)


def rest_relative(seq, n_points=49, k=3):
    """Displacement of each global point from its own rest position (median of first/last k present frames)."""
    xy = seq[:, :n_points * 2].reshape(len(seq), n_points, 2)
    out = np.zeros_like(xy)
    for j in range(n_points):
        pres = np.where((xy[:, j] != 0).any(-1))[0]
        if len(pres) == 0:
            continue
        ends = np.concatenate([pres[:k], pres[-k:]])
        rest = np.median(xy[ends, j], axis=0)
        out[pres, j] = xy[pres, j] - rest
    return out.reshape(len(seq), -1).astype(np.float32)


def present_stats(seq, n_points=49):
    """Mean/std of each point only over frames where it is present, plus presence fraction."""
    xy = seq[:, :n_points * 2].reshape(len(seq), n_points, 2)
    pres = (xy != 0).any(-1)
    cnt = pres.sum(0)
    mean = np.where(cnt[:, None] > 0, (xy * pres[..., None]).sum(0) / np.maximum(cnt, 1)[:, None], 0.0)
    var = np.where(cnt[:, None] > 0, (((xy - mean) ** 2) * pres[..., None]).sum(0) / np.maximum(cnt, 1)[:, None], 0.0)
    return np.concatenate([mean.ravel(), np.sqrt(var).ravel(), cnt / len(seq)]).astype(np.float32)


# ---------------------------------------------------------------- iteration-2 candidate bundle
BUNDLE_REVISION = "lsc5_iter2_bundle_v1"
N_VIEW_AUG = 4
AUG_SEED = 123


def candidate_features(canonical_clip):
    """velocity + handshape + body-normalised features over the active segment, summarised by masked_stats."""
    c = canonical_clip[wave.active_segment(canonical_clip)]
    s = sequence(c, handshape=True)
    return wave.masked_stats(np.concatenate([s, velocity_features(s)], 1))


def finalfit(train_root, manifest, out, seeds=wave.SEEDS):
    import json
    from pathlib import Path
    import torch
    from .io import sha256
    ids, xs, y, signers = wave.load_train(train_root, manifest)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    faces = []
    for s, x in zip(manifest["samples"], xs):
        if s["view"] == "V01":
            f = x[:, wave.FACE].reshape(len(x), 468, 3)
            ok = (f != 0).any((1, 2))
            if ok.any():
                faces.append(np.median(f[ok], 0))
    face_perm = wave.face_permutation(faces)
    np.save(out / "face_perm.npy", face_perm)
    canon = [wave.canonical(x, face_perm) for x in xs]
    rng = np.random.default_rng(AUG_SEED)
    feats = [candidate_features(c) for c in canon]
    extra = [[candidate_features(view_augment(c, rng)) for _ in range(N_VIEW_AUG)] for c in canon]
    fx = feats + [extra[i][k] for k in range(N_VIEW_AUG) for i in range(len(canon))]
    fy, fs = np.tile(y, N_VIEW_AUG + 1), np.tile(signers, N_VIEW_AUG + 1)
    members, ref = [], []
    for seed in seeds:
        predictor = wave.fit_mlp(fx, fy, fs, seed)
        st = predictor.state
        name = f"mlp_s{seed}"
        torch.save(st["model"].state_dict(), out / f"{name}.pt")
        np.savez_compressed(out / f"{name}_norm.npz", mean=st["mean"], std=st["std"])
        members.append({"name": name, "kind": "mlp", "seed": seed, "dim": int(st["dim"]),
                        "model_sha256": sha256(out / f"{name}.pt"), "norm_sha256": sha256(out / f"{name}_norm.npz")})
        ref.append(predictor(feats))
    np.savez_compressed(out / "train_reference.npz", ids=np.asarray(ids), probabilities=np.mean(ref, 0))
    bundle = {"revision": BUNDLE_REVISION, "classes": wave.CLASSES, "members": members,
              "combination": "mean of MLP seeds", "features": "canonical handedness -> active segment -> "
              "body-normalised R1/R2 + handshape distances + velocities -> mean/std/3-segment means",
              "train_augmentation": f"{N_VIEW_AUG} view-augmented copies per clip, rng {AUG_SEED}",
              "face_perm_sha256": sha256(out / "face_perm.npy"), "fit_clips": len(ids),
              "manifest_hash": manifest["manifest_hash"],
              "versions": {"numpy": np.__version__, "torch": str(torch.__version__)}}
    (out / "bundle.json").write_text(json.dumps(bundle, indent=2))
    return bundle


def predict_bundle(bundle_dir, paths, allow_test=False):
    import json
    from pathlib import Path
    import torch
    from .data import read_sequence
    from .io import sha256
    if not allow_test and any("test" in Path(p).resolve().parts for p in paths):
        raise ValueError("Test payloads are reserved for an authorised frozen run")
    wave.configure_cpu()
    bundle_dir = Path(bundle_dir)
    bundle = json.loads((bundle_dir / "bundle.json").read_text())
    if bundle.get("revision") != BUNDLE_REVISION or bundle.get("classes") != wave.CLASSES:
        raise ValueError("Unsupported bundle")
    if sha256(bundle_dir / "face_perm.npy") != bundle["face_perm_sha256"]:
        raise ValueError("Bundle file hash mismatch")
    face_perm = np.load(bundle_dir / "face_perm.npy")
    models = []
    for m in bundle["members"]:
        if sha256(bundle_dir / f"{m['name']}.pt") != m["model_sha256"] or sha256(bundle_dir / f"{m['name']}_norm.npz") != m["norm_sha256"]:
            raise ValueError("Bundle file hash mismatch")
        model = wave.MLP(m["dim"])
        model.load_state_dict(torch.load(bundle_dir / f"{m['name']}.pt", weights_only=True))
        model.eval()
        with np.load(bundle_dir / f"{m['name']}_norm.npz", allow_pickle=False) as z:
            models.append((model, z["mean"], z["std"]))
    rows = []
    with torch.inference_mode():
        for path in paths:
            f = candidate_features(wave.canonical(np.asarray(read_sequence(path)), face_perm))
            rows.append(np.mean([torch.softmax(m(torch.from_numpy(((f - mu) / sd).astype(np.float32))[None]), 1).numpy()[0]
                                 for m, mu, sd in models], 0))
    return np.stack(rows)


# ---------------------------------------------------------------- iteration 3 options
def peak_handshape(c, top=0.25):
    """Right-hand (dominant after canonicalisation) shape averaged over the most elevated wrist frames."""
    pose, _, _, rh = wave.split_blocks(c)
    present = (rh != 0).any((1, 2))
    if not present.any():
        return np.zeros(42 + 9, np.float32)
    elev = -pose[:, 16, 1]
    idx = np.where(present)[0]
    k = max(1, int(round(top * len(idx))))
    sel = idx[np.argsort(elev[idx])[-k:]]
    xy = rh[sel, :, :2]
    span = np.linalg.norm(xy[:, 9] - xy[:, 0], axis=1)
    span = np.where(span > 1e-4, span, 1.0)
    local = ((xy - xy[:, :1]) / span[:, None, None]).mean(0).ravel()
    tips = [4, 8, 12, 16, 20]
    d_wrist = np.stack([np.linalg.norm(xy[:, t] - xy[:, 0], axis=1) for t in tips], 1) / span[:, None]
    d_thumb = np.stack([np.linalg.norm(xy[:, t] - xy[:, 4], axis=1) for t in tips[1:]], 1) / span[:, None]
    return np.concatenate([local, d_wrist.mean(0), d_thumb.mean(0)]).astype(np.float32)


def jitter_segment(c, rng, max_shift=4):
    seg = wave.active_segment(c)
    a = int(np.clip(seg.start + rng.integers(-max_shift, max_shift + 1), 0, len(c) - 8))
    b = int(np.clip(seg.stop + rng.integers(-max_shift, max_shift + 1), a + 8, len(c)))
    return c[a:b]


def features(c, cfg, rng=None, augment=False):
    """Configurable iteration-3 feature builder; augment applies the configured train-only transforms."""
    if cfg.get("gate"):
        c = rest_gate(c, low=cfg["gate"])
    if augment and "view" in cfg.get("aug", ()):
        c = view_augment(c, rng, yaw_lo=cfg.get("yaw_lo", 0.7), max_roll=cfg.get("roll", 8.0))
    if cfg.get("active"):
        c = jitter_segment(c, rng, cfg.get("jitter", 0)) if (augment and cfg.get("jitter")) else c[wave.active_segment(c)]
    s = sequence(c, handshape=cfg.get("shape", False))
    parts = [s]
    if cfg.get("vel"):
        parts.append(velocity_features(s))
    out = wave.masked_stats(np.concatenate(parts, 1))
    if cfg.get("peak"):
        out = np.concatenate([out, peak_handshape(c)])
    if cfg.get("contact"):
        out = np.concatenate([out, contact_features(c, scale_mode=cfg.get("contact_scale", "width"))])
    if cfg.get("bimanual"):
        out = np.concatenate([out, bimanual_features(c)])
    if cfg.get("early"):
        out = np.concatenate([out, early_features(c)])
    return out


def fit_mlp_cfg(x, y, signers, seed, hidden=128, dropout=0.3, epochs=80, wd=1e-3):
    """Same optimisation as wave.fit_mlp with configurable width/dropout/weight decay."""
    import torch
    from torch import nn
    wave._seed(seed)
    x = np.stack(x)
    mean, std = x.mean(0), x.std(0)
    std[std < 1e-6] = 1
    xt = torch.from_numpy(((x - mean) / std).astype(np.float32))
    yt = torch.from_numpy(y)
    model = nn.Sequential(nn.Linear(x.shape[1], hidden), nn.ReLU(), nn.Dropout(dropout), nn.Linear(hidden, 5))
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=wd)
    loss_fn = nn.CrossEntropyLoss()
    for epoch in range(epochs):
        for g in opt.param_groups:
            g["lr"] = wave.learning_rate(epoch)
        model.train()
        for batch in wave.balanced_batches(y, signers, seed, epoch):
            idx = torch.from_numpy(batch.copy())
            opt.zero_grad(set_to_none=True)
            loss_fn(model(xt[idx]), yt[idx]).backward()
            opt.step()
    model.eval()

    def predict(v):
        with torch.inference_mode():
            v = np.stack(v)
            return torch.softmax(model(torch.from_numpy(((v - mean) / std).astype(np.float32))), 1).numpy()
    predict.state = {"kind": "mlp_cfg", "dim": x.shape[1], "hidden": hidden, "dropout": dropout,
                     "mean": mean, "std": std, "model": model}
    return predict


def rest_gate(c, low=1.3, slow=0.03):
    """Zero a hand on frames where it rests: wrist lower than `low` shoulder widths below the shoulder midpoint
    and moving less than `slow` shoulder widths/frame (±2-frame mean). Deterministic, per clip, label-free."""
    pose, face, lh, rh = (b.copy() for b in wave.split_blocks(c))
    width = np.linalg.norm(pose[:, 11, :2] - pose[:, 12, :2], axis=1)
    ok = width > 1e-3
    scale = np.median(width[ok]) if ok.any() else 1.0
    mid_y = np.median(((pose[:, 11, 1] + pose[:, 12, 1]) / 2)[ok]) if ok.any() else 0.5
    for hand in (lh, rh):
        present = (hand != 0).any((1, 2))
        if not present.any():
            continue
        wy = (hand[:, 0, 1] - mid_y) / scale
        w = hand[:, 0, :2] / scale
        step = np.zeros(len(hand))
        both = present[1:] & present[:-1]
        step[1:] = np.where(both, np.linalg.norm(w[1:] - w[:-1], axis=1), np.inf)
        speed = np.convolve(np.where(np.isfinite(step), step, 1.0), np.ones(5) / 5, mode="same")
        rest = present & (wy > low) & (speed < slow)
        hand[rest] = 0.0
    return wave.join_blocks(pose, face, lh, rh)


# ---------------------------------------------------------------- iteration-3 configurable bundle
BUNDLE_V3 = "lsc5_iter3_bundle_v1"
CANDIDATE_V3 = dict(shape=True, vel=True, active=True, aug=["view"], n_aug=4, gate=1.3)
CANDIDATE_V4 = dict(CANDIDATE_V3, contact=True, bimanual=True)
CANDIDATES = {"v3_gate13": CANDIDATE_V3, "v4_contact_bimanual": CANDIDATE_V4}


def finalfit_v3(train_root, manifest, out, cfg=None, seeds=wave.SEEDS):
    import json
    from pathlib import Path
    import torch
    from .io import sha256
    cfg = dict(CANDIDATE_V3 if cfg is None else cfg)
    ids, xs, y, signers = wave.load_train(train_root, manifest)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    faces = []
    for s, x in zip(manifest["samples"], xs):
        if s["view"] == "V01":
            f = x[:, wave.FACE].reshape(len(x), 468, 3)
            ok = (f != 0).any((1, 2))
            if ok.any():
                faces.append(np.median(f[ok], 0))
    face_perm = wave.face_permutation(faces)
    np.save(out / "face_perm.npy", face_perm)
    canon = [wave.canonical(x, face_perm) for x in xs]
    rng = np.random.default_rng(AUG_SEED)
    n = cfg.get("n_aug", 0)
    feats = [features(c, cfg) for c in canon]
    extra = [[features(c, cfg, rng, augment=True) for _ in range(n)] for c in canon]
    fx = feats + [extra[i][k] for k in range(n) for i in range(len(canon))]
    fy, fs = np.tile(y, n + 1), np.tile(signers, n + 1)
    members, ref = [], []
    for seed in seeds:
        p = fit_mlp_cfg(fx, fy, fs, seed, hidden=cfg.get("hidden", 128), dropout=cfg.get("dropout", 0.3),
                        wd=cfg.get("wd", 1e-3))
        name = f"mlp_s{seed}"
        torch.save(p.state["model"].state_dict(), out / f"{name}.pt")
        np.savez_compressed(out / f"{name}_norm.npz", mean=p.state["mean"], std=p.state["std"])
        members.append({"name": name, "seed": seed, "dim": int(p.state["dim"]), "hidden": cfg.get("hidden", 128),
                        "dropout": cfg.get("dropout", 0.3), "model_sha256": sha256(out / f"{name}.pt"),
                        "norm_sha256": sha256(out / f"{name}_norm.npz")})
        ref.append(p(feats))
    np.savez_compressed(out / "train_reference.npz", ids=np.asarray(ids), probabilities=np.mean(ref, 0))
    bundle = {"revision": BUNDLE_V3, "classes": wave.CLASSES, "cfg": cfg, "members": members,
              "combination": "mean of MLP seeds", "aug_rng": AUG_SEED,
              "face_perm_sha256": sha256(out / "face_perm.npy"), "fit_clips": len(ids),
              "manifest_hash": manifest["manifest_hash"],
              "versions": {"numpy": np.__version__, "torch": str(torch.__version__)}}
    (out / "bundle.json").write_text(json.dumps(bundle, indent=2))
    return bundle


def predict_bundle_v3(bundle_dir, paths, allow_test=False):
    import json
    from pathlib import Path
    import torch
    from torch import nn
    from .data import read_sequence
    from .io import sha256
    if not allow_test and any("test" in Path(p).resolve().parts for p in paths):
        raise ValueError("Test payloads are reserved for an authorised frozen run")
    wave.configure_cpu()
    bundle_dir = Path(bundle_dir)
    bundle = json.loads((bundle_dir / "bundle.json").read_text())
    if bundle.get("revision") != BUNDLE_V3 or bundle.get("classes") != wave.CLASSES:
        raise ValueError("Unsupported bundle")
    if sha256(bundle_dir / "face_perm.npy") != bundle["face_perm_sha256"]:
        raise ValueError("Bundle file hash mismatch")
    face_perm, cfg = np.load(bundle_dir / "face_perm.npy"), bundle["cfg"]
    models = []
    for m in bundle["members"]:
        if sha256(bundle_dir / f"{m['name']}.pt") != m["model_sha256"] or sha256(bundle_dir / f"{m['name']}_norm.npz") != m["norm_sha256"]:
            raise ValueError("Bundle file hash mismatch")
        model = nn.Sequential(nn.Linear(m["dim"], m["hidden"]), nn.ReLU(), nn.Dropout(m["dropout"]), nn.Linear(m["hidden"], 5))
        model.load_state_dict(torch.load(bundle_dir / f"{m['name']}.pt", weights_only=True))
        model.eval()
        with np.load(bundle_dir / f"{m['name']}_norm.npz", allow_pickle=False) as z:
            models.append((model, z["mean"], z["std"]))
    rows = []
    with torch.inference_mode():
        for path in paths:
            f = features(wave.canonical(np.asarray(read_sequence(path)), face_perm), cfg)
            rows.append(np.mean([torch.softmax(m(torch.from_numpy(((f - mu) / sd).astype(np.float32))[None]), 1).numpy()[0]
                                 for m, mu, sd in models], 0))
    return np.stack(rows)


# ---------------------------------------------------------------- iteration 4: sign_04 vs sign_05 cues
def _body_scale(pose, mode="width"):
    """Shoulder width (default) or geometric mean of shoulder width and nose-to-shoulder height (less yaw-bound)."""
    width = np.linalg.norm(pose[:, 11, :2] - pose[:, 12, :2], axis=1)
    ok = width > 1e-3
    scale = np.median(width[ok]) if ok.any() else 1.0
    if mode == "geo" and ok.any():
        neck = np.median(np.abs((pose[ok, 11, 1] + pose[ok, 12, 1]) / 2 - pose[ok, 0, 1]))
        if neck > 1e-3:
            scale = math.sqrt(scale * neck)
    return scale


def contact_features(c, scale_mode="width"):
    """Dominant (right after canonicalisation) hand closeness to the chest and when it happens."""
    pose, _, _, rh = wave.split_blocks(c)
    scale = _body_scale(pose, scale_mode)
    chest = (pose[:, 11, :2] + pose[:, 12, :2]) / 2 + np.array([0.0, 0.4]) * scale
    present = (rh != 0).any((1, 2))
    pts = np.where(present[:, None], rh[:, :, :2].mean(1), pose[:, 16, :2])
    d = np.linalg.norm(pts - chest, axis=1) / scale
    t = np.linspace(0, 1, len(d))
    k = int(np.argmin(d))
    return np.array([d.min(), t[k], d[-max(1, len(d) // 5):].mean() - d.min(), (d < 0.6).mean()], np.float32)


def bimanual_features(c):
    """Non-dominant hand activity after the rest gate: presence, motion energy and vertical co-movement."""
    pose, _, lh, rh = wave.split_blocks(c)
    width = np.linalg.norm(pose[:, 11, :2] - pose[:, 12, :2], axis=1)
    ok = width > 1e-3
    scale = np.median(width[ok]) if ok.any() else 1.0
    out = []
    ys = []
    for hand in (lh, rh):
        present = (hand != 0).any((1, 2))
        w = hand[:, 0, :2] / scale
        both = present[1:] & present[:-1]
        energy = float(np.linalg.norm(w[1:] - w[:-1], axis=1)[both].sum()) if both.any() else 0.0
        out += [present.mean(), energy]
        ys.append(np.where(present, w[:, 1], np.nan))
    both = ~np.isnan(ys[0]) & ~np.isnan(ys[1])
    corr = float(np.corrcoef(ys[0][both], ys[1][both])[0, 1]) if both.sum() > 3 and ys[0][both].std() > 1e-6 and ys[1][both].std() > 1e-6 else 0.0
    return np.array(out + [corr, both.mean()], np.float32)


# ---------------------------------------------------------------- iteration 5: onset/offset phase cues
def early_features(c):
    """Where the dominant hand starts and ends relative to the chest (first/last third of the clip), the
    start-to-end displacement, and how present the non-dominant hand is in the first third. Label-free."""
    pose, _, lh, rh = wave.split_blocks(c)
    scale = _body_scale(pose)
    chest = (pose[:, 11, :2] + pose[:, 12, :2]) / 2 + np.array([0.0, 0.4]) * scale
    present = (rh != 0).any((1, 2))
    pts = (np.where(present[:, None], rh[:, :, :2].mean(1), pose[:, 16, :2]) - chest) / scale
    k = max(1, len(pts) // 3)
    start, end = pts[:k].mean(0), pts[-k:].mean(0)
    lpres = (lh != 0).any((1, 2))
    return np.array([*start, *end, *(end - start), np.linalg.norm(start), lpres[:k].mean()], np.float32)
