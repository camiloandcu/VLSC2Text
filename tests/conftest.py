from pathlib import Path

import numpy as np
import pytest

from lsc5.data import build_manifest


def training_fixture(root: Path, per_class=1):
    train = root / "train"
    rng = np.random.default_rng(42)
    for subject in [2, 3, 4]:
        for label in range(1, 6):
            for clip in range(per_class):
                name = f"S{label:02d}_M{subject:02d}_V01_C01_Clip{clip + 1}"
                arrays = train / "landmarks" / f"sign_{label:02d}"
                videos = train / "videos" / f"sign_{label:02d}"
                arrays.mkdir(parents=True, exist_ok=True)
                videos.mkdir(parents=True, exist_ok=True)
                values = rng.normal(size=(3, 1662)).astype(np.float64)
                np.save(arrays / (name + ".npy"), values)
                (videos / (name + ".mp4")).write_bytes(name.encode())
    return train, build_manifest(train)


@pytest.fixture
def small_train(tmp_path):
    return training_fixture(tmp_path)
