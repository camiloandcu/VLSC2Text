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


def view_augment(x, rng):
    """Simulate camera yaw/roll/zoom on raw image-fraction coordinates of pose and hands (train only)."""
    pose, face, lh, rh = (b.copy() for b in wave.split_blocks(x))
    sh = pose[:, [11, 12], :2]
    c = np.median(sh.reshape(-1, 2), axis=0)
    yaw = rng.uniform(0.7, 1.0)                       # horizontal foreshortening
    ang = math.radians(rng.uniform(-8, 8))
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
