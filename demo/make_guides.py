"""Build skeleton guide animations (no video, no face texture) from train landmarks.

Output stays out of Git (demo/static/private/): it is derived from LSC5 train data.
"""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "data" / "train"
OUT = ROOT / "demo" / "static" / "private"
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176,
             149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]


def pick(sign, signer):
    files = sorted((TRAIN / "landmarks" / f"sign_0{sign}").glob(f"S0{sign}_{signer}_V01_*.npy"))
    lens = np.array([len(np.load(f, mmap_mode="r")) for f in files])
    return files[int(np.argsort(lens)[len(lens) // 2])]


def pack(x):
    r = lambda a: np.round(a, 4).tolist()
    pose = x[:, :132].reshape(len(x), 33, 4)[:, :25, :2]
    face = x[:, 132:1536].reshape(len(x), 468, 3)[:, :, :2]
    lh = x[:, 1536:1599].reshape(len(x), 21, 3)[:, :, :2]
    rh = x[:, 1599:1662].reshape(len(x), 21, 3)[:, :, :2]
    present = lambda b: b.reshape(len(b), -1).any(1).tolist()
    return {"pose": r(pose), "oval": r(face[:, FACE_OVAL]), "lips": r(face[:, LIPS]),
            "lh": r(lh), "rh": r(rh), "lh_on": present(lh), "rh_on": present(rh), "face_on": present(face)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    guides, videos = {}, {}
    for s in range(1, 6):
        guides[f"sign_0{s}"] = []
        for signer in ("M03", "M04", "M02"):
            f = pick(s, signer)
            g = pack(np.load(f))
            g["signer"] = signer
            guides[f"sign_0{s}"].append(g)
            videos.setdefault(f"sign_0{s}", []).append(f"sign_0{s}/{f.stem}.mp4")
    (OUT / "guides.json").write_text(json.dumps(guides, separators=(",", ":")))
    (OUT / "videos.json").write_text(json.dumps(videos))
    print({k: [len(g["pose"]) for g in v] for k, v in guides.items()}, (OUT / "guides.json").stat().st_size // 1024, "KiB")


if __name__ == "__main__":
    main()
