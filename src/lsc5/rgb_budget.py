"""One local GPU pilot in the existing locked ledger; never impersonate Slurm."""
import math
import time
from pathlib import Path
import hashlib

from .budget import ledger, totals
from .io import digest, producer_hash
from .rgb_frames import select_pilot

SCOPE = "rgb-global-pilot"
RETRY_SCOPE = "rgb-global-pilot-retry"


def valid_profile(row):
    if row.get("scope") == SCOPE:
        return "retry_of" not in row and "retry_parent_receipt_hash" not in row
    return (row.get("scope") == RETRY_SCOPE and isinstance(row.get("retry_of"), str)
            and bool(row["retry_of"]) and len(row.get("retry_parent_receipt_hash", "")) == 64)


def failed_parent(data, attempt, manifest_hash, selection_hash):
    parent = next((a for a in data["attempts"] if a["id"] == attempt), None)
    if (parent is None or parent.get("scope") != SCOPE or parent.get("state") != "settled"
            or parent.get("execution_kind") != "local_gpu_pilot" or parent.get("job_id") is not None
            or parent.get("terminal_state") not in {"FAILED", "TIMEOUT", "RESOURCE_LIMIT"}
            or parent.get("manifest_hash") != manifest_hash or parent.get("selection_hash") != selection_hash
            or len(parent.get("receipt_hash", "")) != 64):
        raise ValueError("Retry requires the settled failed original pilot with identical selection")
    return parent


def machine_identity():
    return hashlib.sha256(Path("/etc/machine-id").read_bytes()).hexdigest()


def reserve_local(path, attempt, manifest, retry_of=None):
    ids = [s["id"] for s in select_pilot(manifest)]
    scope = RETRY_SCOPE if retry_of is not None else SCOPE
    with ledger(path) as data:
        if data is None:
            raise ValueError("Existing canonical ledger required")
        if data["scope_limits_seconds"].get(scope, 660) != 660:
            raise ValueError("Cannot change existing local scope")
        if any(a["id"] == attempt or a["scope"] == scope for a in data["attempts"]):
            raise ValueError("Only one authorized local attempt")
        parent = failed_parent(data, retry_of, manifest["manifest_hash"], digest(ids)) if retry_of is not None else None
        spent, pending = totals(data)
        if spent+pending+660+data["final_reserve_seconds"] > data["cpu_limit_seconds"]:
            raise ValueError("Global budget must preserve final reserve")
        data["scope_limits_seconds"][scope] = 660
        row = {"id": attempt, "scope": scope, "execution_kind": "local_gpu_pilot",
               "state": "committed", "reserved_seconds": 660, "estimate_seconds": 300,
               "time_limit_seconds": 600, "kill_wait_seconds": 60, "job_id": None,
               "actual_seconds": None, "claimed": False, "created_unix": time.time(),
               "producer_hash": producer_hash(), "manifest_hash": manifest["manifest_hash"],
               "selection_hash": digest(ids)}
        if parent is not None:
            row.update(retry_of=retry_of, retry_parent_receipt_hash=parent["receipt_hash"])
        data["attempts"].append(row)
        return dict(row)


def claim_local(path, attempt, run_directory, machine_id_sha256):
    run_directory = str(run_directory)
    if (not Path(run_directory).is_absolute() or ".." in Path(run_directory).parts
            or len(machine_id_sha256) != 64):
        raise ValueError("Local absolute run directory and machine identity required")
    with ledger(path) as data:
        row = next(a for a in data["attempts"] if a["id"] == attempt)
        if (row.get("execution_kind") != "local_gpu_pilot" or not valid_profile(row)
                or row["state"] != "committed" or row["claimed"]
                or row["producer_hash"] != producer_hash() or row["job_id"] is not None):
            raise ValueError("No unclaimed compatible local reservation")
        if row["scope"] == RETRY_SCOPE:
            parent = failed_parent(data, row["retry_of"], row["manifest_hash"], row["selection_hash"])
            if parent["receipt_hash"] != row["retry_parent_receipt_hash"]:
                raise ValueError("Retry parent receipt changed")
        row.update(claimed=True, claimed_unix=time.time(), execution_started=True,
                   run_directory=run_directory, machine_id_sha256=machine_id_sha256)
        receipt = dict(row)
        receipt["reservation_hash"] = digest(row)
        return receipt


def validate_reservation(reservation, manifest):
    if not valid_profile(reservation):
        raise ValueError("Local reservation profile is incompatible")
    content = {k: v for k, v in reservation.items() if k != "reservation_hash"}
    expected = {"scope": reservation["scope"], "execution_kind": "local_gpu_pilot", "state": "committed",
                "reserved_seconds": 660, "time_limit_seconds": 600, "kill_wait_seconds": 60,
                "job_id": None, "claimed": True, "producer_hash": producer_hash(),
                "execution_started": True, "machine_id_sha256": machine_identity(),
                "manifest_hash": manifest["manifest_hash"],
                "selection_hash": digest([s["id"] for s in select_pilot(manifest)])}
    if (any(reservation.get(k) != v for k, v in expected.items())
            or digest(content) != reservation.get("reservation_hash")
            or not 0 <= time.time()-reservation.get("claimed_unix", 0) <= 3600):
        raise ValueError("Local reservation receipt is incompatible or expired")


def settle_local(path, receipt):
    seconds = receipt["actual_seconds"]
    if (not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds < 0
            or receipt.get("terminal_state") not in {"COMPLETED", "FAILED", "TIMEOUT", "RESOURCE_LIMIT"}):
        raise ValueError("Measured local terminal receipt required")
    if receipt["terminal_state"] == "COMPLETED" and (
            [s.get("name") for s in receipt.get("stages", [])] != ["pilot", "replay"]
            or any(s.get("returncode") != 0 for s in receipt["stages"])
            or any(len(receipt.get(k, "")) != 64 for k in ["pilot_run_sha256", "cache_metadata_sha256",
                                                           "metrics_sha256", "replay_receipt_sha256"])):
        raise ValueError("Completed local receipt requires pilot and replay evidence")
    with ledger(path) as data:
        row = next(a for a in data["attempts"] if a["id"] == receipt["attempt_id"])
        if (row.get("execution_kind") != "local_gpu_pilot" or not row["claimed"]
                or row["state"] != "committed" or digest(row) != receipt.get("reservation_hash")
                or row["producer_hash"] != receipt.get("producer_hash")):
            raise ValueError("Settlement does not match claimed local reservation")
        row.update(state="settled", actual_seconds=float(seconds), terminal_state=receipt["terminal_state"],
                   receipt_hash=digest(receipt), reservation_overrun=seconds > row["reserved_seconds"],
                   gpu_forward_seconds=receipt.get("gpu_forward_seconds"),
                   gpu_timing_scope=receipt.get("gpu_timing_scope"), accounting="whole_local_wall_once")
        return dict(row)
