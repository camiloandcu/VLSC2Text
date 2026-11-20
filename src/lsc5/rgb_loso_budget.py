"""Closed E07/E08 profiles in the canonical mixed CPU/local-GPU ledger."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import math
import time

from .budget import ledger, totals
from .data import validate_baseline_manifest
from .io import digest, producer_hash, read_json, sha256
from .rgb_budget import machine_identity

SCOPE = "rgb-global-loso"
BASELINE_SHA = "0c66634dad513803a80c3edfa180f05264c1230ec77e30081327a5c5dcd0c248"
PROFILES = {"extract": (18000, 18060), "restore": (18000, 18060),
            "pilot": (300, 360), "M02": (900, 960), "M03": (900, 960), "M04": (900, 960)}
CUTOFF = datetime(2026, 11, 22, 17, tzinfo=ZoneInfo("America/Bogota")).timestamp()


def start_deadline(data):
    rows = [a for a in data["attempts"] if a["scope"] == SCOPE]
    pending = sum(a["reserved_seconds"] for a in rows if a["state"] == "committed")
    unattempted = sum(v[1] for k, v in PROFILES.items() if k not in {a["profile"] for a in rows})
    return CUTOFF-pending-unattempted-3600


def check_start_data(data, row):
    admission = data.get("rgb_loso_admission", {})
    if (admission.get("producer_hash") != producer_hash() or row.get("producer_hash") != producer_hash()
            or row.get("manifest_hash") != admission.get("manifest_hash")
            or time.time() > start_deadline(data)):
        raise ValueError("Full RGB chain no longer fits calendar at actual start")


def enable(path, manifest):
    validate_baseline_manifest(manifest)
    with ledger(path) as data:
        if data is None:
            raise ValueError("Existing canonical ledger required")
        if data.get("rgb_loso_admission"):
            raise ValueError("Do not replace chain admission")
        spent, pending = totals(data)
        if (spent+pending+39360+data["final_reserve_seconds"] > data["cpu_limit_seconds"]
                or time.time()+39360+4*3600+3600 > CUTOFF):
            raise ValueError("Complete bounded scenario does not fit budget/calendar")
        if SCOPE in data["scope_limits_seconds"]:
            raise ValueError("Scope already exists")
        data["scope_limits_seconds"][SCOPE] = 43200
        data["rgb_loso_admission"] = {"producer_hash": producer_hash(),
            "manifest_hash": manifest["manifest_hash"], "baseline_report_sha256": BASELINE_SHA,
            "bounded_scenario_seconds": 39360, "measured_head_gate": False,
            "admitted_unix": time.time(), "operational_cutoff_unix": CUTOFF}


def reserve(path, attempt, profile, manifest):
    validate_baseline_manifest(manifest)
    if profile not in PROFILES:
        raise ValueError("Unknown fixed RGB LOSO profile")
    limit, seconds = PROFILES[profile]
    with ledger(path) as data:
        admission = data.get("rgb_loso_admission", {}) if data else {}
        if (admission.get("producer_hash") != producer_hash()
                or admission.get("manifest_hash") != manifest["manifest_hash"]):
            raise ValueError("Compatible bounded scenario required")
        rows = [a for a in data["attempts"] if a["scope"] == SCOPE]
        if any(a["id"] == attempt for a in data["attempts"]) or any(a["profile"] == profile for a in rows):
            raise ValueError("One attempt per authorized phase/fold")
        if profile != "extract" and not any(a["profile"] == "extract" and a["state"] == "settled"
                and a["terminal_state"] == "COMPLETED" for a in rows):
            raise ValueError("Complete reconciled extraction required")
        if profile in {"M02", "M03", "M04"} and not data.get("rgb_loso_gate"):
            raise ValueError("Measured restored head pilot gate required")
        if profile == "restore" and not {"M02", "M03", "M04"}.issubset({a["profile"] for a in rows if a["state"] == "settled"
                and a["terminal_state"] == "COMPLETED"}):
            raise ValueError("Three completed reconciled folds required")
        spent, pending = totals(data)
        scoped, reserved = totals(data, SCOPE)
        # Reserve the maximum of every not-yet-attempted phase in the chain.
        remaining = sum(v[1] for k, v in PROFILES.items() if k not in {a["profile"] for a in rows})
        if (spent+pending+remaining+data["final_reserve_seconds"] > data["cpu_limit_seconds"]
                or scoped+reserved+remaining > data["scope_limits_seconds"][SCOPE]
                or time.time()+remaining+3600 > CUTOFF):
            raise ValueError("Remaining complete chain does not fit budget/calendar")
        row = {"id": attempt, "scope": SCOPE, "profile": profile,
               "execution_kind": "local_gpu_rgb_full" if profile in {"extract", "restore"} else "slurm_cpu_rgb_head",
               "state": "committed", "reserved_seconds": seconds, "time_limit_seconds": limit,
               "kill_wait_seconds": 60, "job_id": None, "actual_seconds": None, "claimed": False,
               "producer_hash": producer_hash(), "manifest_hash": manifest["manifest_hash"],
               "created_unix": time.time()}
        data["attempts"].append(row)
        return dict(row)


def claim_gpu(path, attempt, run_directory, machine):
    if not Path(run_directory).is_absolute() or ".." in Path(run_directory).parts or len(machine) != 64:
        raise ValueError("Absolute output and machine identity required")
    with ledger(path) as data:
        row = next(a for a in data["attempts"] if a["id"] == attempt)
        if (row.get("scope") != SCOPE or row.get("execution_kind") != "local_gpu_rgb_full"
                or row.get("profile") not in {"extract", "restore"} or row["claimed"]
                or row["state"] != "committed" or row["producer_hash"] != producer_hash() or row["job_id"] is not None):
            raise ValueError("No unclaimed full GPU reservation")
        check_start_data(data, row)
        row.update(claimed=True, claimed_unix=time.time(), execution_started=True,
                   run_directory=str(run_directory), machine_id_sha256=machine,
                   start_deadline_unix=start_deadline(data))
        return {**row, "reservation_hash": digest(row)}


def validate_gpu_reservation(row, manifest):
    validate_baseline_manifest(manifest)
    profile = row.get("profile")
    expected = {"scope": SCOPE, "execution_kind": "local_gpu_rgb_full", "state": "committed",
                "claimed": True, "job_id": None, "producer_hash": producer_hash(),
                "manifest_hash": manifest["manifest_hash"], "machine_id_sha256": machine_identity(),
                "reserved_seconds": 18060, "time_limit_seconds": 18000, "kill_wait_seconds": 60,
                "execution_started": True}
    if (profile not in {"extract", "restore"} or any(row.get(k) != v for k, v in expected.items())
            or digest({k:v for k,v in row.items() if k != "reservation_hash"}) != row.get("reservation_hash")
            or not 0 <= time.time()-row.get("claimed_unix", 0) <= 3600
            or time.time() > row.get("start_deadline_unix", 0)):
        raise ValueError("Invalid/expired full GPU claim")


def settle_gpu(path, receipt):
    seconds = receipt.get("actual_seconds", -1)
    if not math.isfinite(seconds) or seconds < 0 or receipt.get("terminal_state") not in {
            "COMPLETED", "FAILED", "TIMEOUT", "RESOURCE_LIMIT"}:
        raise ValueError("Measured terminal receipt required")
    with ledger(path) as data:
        row = next(a for a in data["attempts"] if a["id"] == receipt["attempt_id"])
        if (row.get("scope") != SCOPE or row.get("execution_kind") != "local_gpu_rgb_full"
                or not row["claimed"] or row["state"] != "committed"
                or digest(row) != receipt.get("reservation_hash") or row["producer_hash"] != receipt.get("producer_hash")):
            raise ValueError("Settlement disagrees with claimed full GPU attempt")
        if receipt["terminal_state"] == "COMPLETED" and (
                [s.get("name") for s in receipt.get("stages", [])] != [row["profile"]]
                or receipt["stages"][0].get("returncode") != 0
                or len(receipt.get("full_result_sha256", "")) != 64):
            raise ValueError("Completed full GPU result evidence required")
        row.update(state="settled", actual_seconds=float(seconds), terminal_state=receipt["terminal_state"],
                   receipt_hash=digest(receipt), reservation_overrun=seconds > row["reserved_seconds"],
                   gpu_forward_seconds=receipt.get("gpu_forward_seconds"), accounting="whole_local_wall_once")
        return dict(row)


def check_gate(path, manifest_hash):
    with ledger(path) as data:
        gate = data.get("rgb_loso_gate", {})
        if (gate.get("producer_hash") != producer_hash() or gate.get("manifest_hash") != manifest_hash
                or gate.get("projected_fold_seconds_with_margin", math.inf) > 900):
            raise ValueError("Compatible measured head gate required")
        return dict(gate)


def admit(path, manifest, directory, restoration_receipt):
    from .rgb_head_restore import load_run, verify_restoration
    root = Path(directory)
    run, split, _ = load_run(manifest, root)
    receipt = read_json(restoration_receipt)
    verify_restoration(root, manifest, receipt, Path(restoration_receipt).parent, "immutable_full_train_cache")
    metrics = read_json(root/"metrics.json")
    if run["phase"] != "rgb_head_pilot" or split["outer_signer"] != "M02":
        raise ValueError("M02 two-epoch pilot required")
    with ledger(path) as data:
        row = next(a for a in data["attempts"] if a["id"] == run["attempt_id"])
        if (row["state"] != "settled" or row["terminal_state"] != "COMPLETED"
                or row["scope"] != SCOPE or row["profile"] != "pilot" or row["job_id"] != run["job_id"]):
            raise ValueError("Reconciled completed RGB pilot required")
        cold = max(0, row["actual_seconds"]-metrics["process_seconds_before_final_metadata"])+2
        projected = metrics["projected_fold_seconds_with_margin"]+1.5*cold
        refit = metrics["projected_refit_seconds_with_margin"]+1.5*cold
        probe = metrics.get("batch60_probe") or {}
        if (not math.isfinite(projected+refit) or projected > 900 or refit+5388.420+1800 > data["final_reserve_seconds"]
                or metrics["measured_step_count"] < 10 or not probe.get("fit_only")
                or not probe.get("discarded_copy") or not probe.get("backward_optimizer_step") or probe.get("size") != 60):
            raise ValueError("Measured head/refit chain does not fit")
        spent, pending = totals(data)
        scoped, reserved = totals(data, SCOPE)
        remaining = 3*960+18060
        if (spent+pending+remaining+data["final_reserve_seconds"] > data["cpu_limit_seconds"]
                or scoped+reserved+remaining > data["scope_limits_seconds"][SCOPE]
                or time.time()+remaining+3600 > CUTOFF):
            raise ValueError("Measured chain cannot be reserved")
        gate = {"producer_hash": producer_hash(), "manifest_hash": manifest["manifest_hash"],
                "pilot_run_sha256": sha256(root/"run.json"), "restoration_receipt_sha256": sha256(restoration_receipt),
                "cache_metadata_sha256": run["cache_metadata_sha256"],
                "projected_fold_seconds_with_margin": projected, "projected_refit_seconds_with_margin": refit,
                "final_inference_reference_seconds": 5388.420, "packaging_allowance_seconds": 1800}
        if data.get("rgb_loso_gate") and data["rgb_loso_gate"] != gate:
            raise ValueError("Cannot replace measured head gate")
        data["rgb_loso_gate"] = gate
        return dict(gate)
