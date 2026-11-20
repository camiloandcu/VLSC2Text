"""Full extraction and fresh original-video restoration, under fixed GPU claims."""
from pathlib import Path

from .io import atomic_json, read_json, sha256
from .rgb_loso_budget import validate_gpu_reservation
from .rgb_pilot import run_pilot


def run_full(train_root, manifest, assets, reservation, output, runs=None):
    validate_gpu_reservation(reservation, manifest)
    profile = reservation["profile"]
    if profile == "restore":
        from .rgb_head_restore import load_run
        if runs is None or len(runs) != 3:
            raise ValueError("Three fixed outer models required for original restoration")
        signers, cache_hashes = set(), set()
        for directory in runs:
            run, split, _ = load_run(manifest, directory)
            if run["phase"] != "outer_rgb":
                raise ValueError("Only complete models can be restored from originals")
            signers.add(split["outer_signer"])
            cache_hashes.add(run["cache_metadata_sha256"])
        if signers != {"M02", "M03", "M04"} or len(cache_hashes) != 1:
            raise ValueError("Mixed/incomplete original restoration models")
    elif runs:
        raise ValueError("Extraction does not consume classifiers")
    output = Path(output)
    metrics = run_pilot(train_root, manifest, assets, reservation, output, coverage="full1125")
    result = {"profile": profile, "status": "complete", "classification_trained": False,
              "clips": 1125, "cache_metadata_sha256": sha256(output/"cache/metadata.json"),
              "run_sha256": sha256(output/"run.json"), "metrics_sha256": sha256(output/"metrics.json"),
              "restorations": [], "gpu_forward_seconds": sum(b["forward_seconds"] for b in metrics["batches"])}
    if profile == "restore":
        from .rgb_head import load_embeddings
        from .rgb_head_restore import restore_embeddings, verify_restoration
        values, _ = load_embeddings(output/"cache", manifest)
        for directory in runs:
            signer = read_json(Path(directory)/"split.json")["outer_signer"]
            receipt = restore_embeddings(manifest, directory, values, output/(signer+".npz"),
                                         "original_train_videos_and_pinned_weight")
            atomic_json(output/(signer+".json"), receipt)
            verify_restoration(directory, manifest, receipt, output, "original_train_videos_and_pinned_weight")
            result["restorations"].append({"outer_signer": signer, "receipt": signer+".json",
                "receipt_sha256": sha256(output/(signer+".json")), "max_abs_difference": receipt["max_abs_difference"]})
    atomic_json(output/"result.json", result)
    return result
