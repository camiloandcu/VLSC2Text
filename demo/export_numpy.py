"""Export the frozen MLP weights to numpy and check the torch-free predictor against the torch one.

Run with the torch environment: PYTHONPATH=src:demo .venv/bin/python demo/export_numpy.py <bundle_dir> <check_npy_glob>
"""
import glob, json, sys
from pathlib import Path
import numpy as np
import torch
from lsc5.io import sha256

bundle = Path(sys.argv[1])
meta = json.loads((bundle / "bundle.json").read_text())
for m in meta["members"]:
    sd = torch.load(bundle / f"{m['name']}.pt", weights_only=True)
    np.savez(bundle / f"{m['name']}_weights.npz", w0=sd["0.weight"].numpy(), b0=sd["0.bias"].numpy(),
             w1=sd["3.weight"].numpy(), b1=sd["3.bias"].numpy(), source_sha256=np.array(sha256(bundle / f"{m['name']}.pt")))
from predictor import Predictor as Torch
from predictor_np import Predictor as Numpy
a, b = Torch(bundle), Numpy(bundle)
files = sorted(glob.glob(sys.argv[2]))
d = max(np.abs(a.predict(np.load(f)) - b.predict(np.load(f))).max() for f in files)
same = all(a.predict(np.load(f)).argmax() == b.predict(np.load(f)).argmax() for f in files)
print(f"clips {len(files)}  max |p_torch - p_numpy| = {d:.2e}  same top-1: {same}")
