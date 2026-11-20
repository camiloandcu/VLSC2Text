"""Official pinned DINOv2 backbone; no training, hub download or AMP."""
from pathlib import Path
import os
import sys
import time

import numpy as np

from .io import digest, read_json, sha256
from .rgb_frames import TRANSFORM

COMMIT = "7764ea0f912e53c92e82eb78a2a1631e92725fc8"
SOURCE_INVENTORY_HASH = "c2c37d49b24e354c91695086887ae7222439e482e8256d221dc0be40ea903ee8"
WEIGHT_SHA256 = "b938bf1bc15cd2ec0feacfe3a1bb553fe8ea9ca46a7e1d8d00217f29aef60cd9"


def verify_assets(assets_root):
    root = Path(assets_root).resolve(strict=True)
    record = read_json(root/"assets.json")
    if (record.get("commit") != COMMIT or record["weight"]["sha256"] != WEIGHT_SHA256
            or sha256(root/"dinov2_vits14_pretrain.pth") != WEIGHT_SHA256):
        raise ValueError("Pinned official weight/source identity mismatch")
    source = root/"source"
    inventory = record["source_files"]
    if digest(inventory) != SOURCE_INVENTORY_HASH:
        raise ValueError("Unapproved source inventory identity")
    actual = {str(p.relative_to(source)) for p in source.rglob("*") if p.is_file()
              and "__pycache__" not in p.parts and p.suffix != ".pyc"}
    if actual != set(inventory):
        raise ValueError("Upstream source inventory mismatch")
    for name, expected in inventory.items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or sha256(source/path) != expected:
            raise ValueError("Upstream source hash mismatch")
    return {"commit": COMMIT, "weight_sha256": WEIGHT_SHA256,
            "source_inventory_hash": digest(inventory), "license": "Apache-2.0",
            "architecture": "dinov2_vits14_no_registers", "eval": True, "frozen": True,
            "weight_url": "https://dl.fbaipublicfiles.com/dinov2/dinov2_vits14/dinov2_vits14_pretrain.pth"}


class Encoder:
    def __init__(self, assets_root):
        self.identity = verify_assets(assets_root)
        os.environ["XFORMERS_DISABLED"] = "1"
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
        import torch
        import torchvision
        import PIL
        if torch.__version__ != "2.4.1+cu121" or not torch.cuda.is_available():
            raise ValueError("Approved CUDA PyTorch environment required")
        if torchvision.__version__ != "0.19.1+cu121" or PIL.__version__ != "11.3.0":
            raise ValueError("Approved torchvision/Pillow versions required")
        self.versions = {"torch": torch.__version__, "torchvision": torchvision.__version__, "pillow": PIL.__version__}
        torch.set_num_threads(2)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        sys.path.insert(0, str(Path(assets_root).resolve()/"source"))
        from dinov2.hub.backbones import dinov2_vits14
        import dinov2
        if not Path(dinov2.__file__).resolve().is_relative_to(Path(assets_root).resolve()/"source"):
            raise ValueError("Unapproved upstream import")
        model = dinov2_vits14(pretrained=False)
        state = torch.load(Path(assets_root)/"dinov2_vits14_pretrain.pth", map_location="cpu", weights_only=True)
        model.load_state_dict(state, strict=True)
        del state
        self.model = model.requires_grad_(False).eval().cuda()
        self.torch = torch
        self.mean = torch.tensor(TRANSFORM["mean"], device="cuda").view(1, 3, 1, 1)
        self.std = torch.tensor(TRANSFORM["std"], device="cuda").view(1, 3, 1, 1)
        self.parameter_count = sum(p.numel() for p in model.parameters())
        torch.cuda.reset_peak_memory_stats()

    def memory_stats(self):
        return {"torch_peak_allocated_bytes": self.torch.cuda.max_memory_allocated(),
                "torch_peak_reserved_bytes": self.torch.cuda.max_memory_reserved()}

    def extract(self, pixels, batch_size=4):
        if (pixels.dtype != np.uint8 or pixels.ndim != 4 or pixels.shape[1:] != (224, 224, 3)
                or batch_size not in {1, 4}):
            raise ValueError("Fixed RGB input/microbatch required")
        torch = self.torch
        features, timings = [], []
        with torch.inference_mode():
            for start in range(0, len(pixels), batch_size):
                tick = time.perf_counter()
                x = torch.from_numpy(pixels[start:start+batch_size].copy()).permute(0, 3, 1, 2)
                x = (x.to(device="cuda", dtype=torch.float32)/255-self.mean)/self.std
                torch.cuda.synchronize()
                transfer = time.perf_counter()-tick
                tick = time.perf_counter()
                y = self.model.forward_features(x)["x_norm_clstoken"]
                torch.cuda.synchronize()
                forward = time.perf_counter()-tick
                tick = time.perf_counter()
                value = y.cpu().numpy().copy()
                transfer_back = time.perf_counter()-tick
                if value.shape != (len(x), 384) or value.dtype != np.float32 or not np.isfinite(value).all():
                    raise ValueError("Invalid frozen embedding")
                if torch.cuda.max_memory_reserved() > 3*1024**3:
                    raise MemoryError("PyTorch reserved VRAM exceeds 3GiB limit")
                features.append(value)
                timings.append({"h2d_and_normalization_seconds": transfer, "forward_seconds": forward,
                                "d2h_seconds": transfer_back})
        return np.concatenate(features), timings
