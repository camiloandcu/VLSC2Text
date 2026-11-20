"""Single locked CPU ledger. Reservations precede job submission."""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
from pathlib import Path
import time

from .io import atomic_json, read_json

SCOPE = "cpu-pilot-walking-path"
BASELINE_SCOPE = "cpu-baseline-loso"
TEMPORAL_SCOPE = "opaque-temporal-tcn"


@contextmanager
def ledger(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.with_suffix(path.suffix + ".lock").open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        data = read_json(path) if path.exists() else None
        yield data
        if data is not None:
            atomic_json(path, data)


def initialize(path):
    path = Path(path)
    with ledger(path) as existing:
        if existing is not None:
            raise FileExistsError("Budget already exists; never reset consumed work")
        atomic_json(path, {"revision": "budget_v1", "cash_limit_usd": 10, "cash_paid_usd": 0,
                           "cpu_limit_seconds": 48 * 3600, "final_reserve_seconds": 12 * 3600,
                           "scope_limits_seconds": {SCOPE: 2 * 3600}, "attempts": []})


def totals(data, scope=None):
    rows = [a for a in data["attempts"] if scope is None or a["scope"] == scope]
    consumed = sum(a["actual_seconds"] for a in rows if a["state"] == "settled")
    pending = sum(a["reserved_seconds"] for a in rows if a["state"] == "committed")
    return consumed, pending


def enable_baseline(path):
    """Admit the authorized increment without resetting existing consumption."""
    with ledger(path) as data:
        if data is None:
            raise ValueError("Existing budget required")
        old = data["scope_limits_seconds"].get(BASELINE_SCOPE)
        if old is not None and old != 3600:
            raise ValueError("Existing scope limit cannot be changed")
        data["scope_limits_seconds"][BASELINE_SCOPE] = 3600


def reserve(path, attempt_id, seconds=900, estimate=120, time_limit=600, kill_wait=30, scope=SCOPE):
    if min(seconds, estimate, time_limit) <= 0 or kill_wait < 0:
        raise ValueError("Invalid duration")
    if seconds < max(estimate * 1.5, time_limit + kill_wait):
        raise ValueError("Reservation does not cover estimated and maximum job duration")
    with ledger(path) as data:
        if data is None:
            raise ValueError("Budget must exist before admission")
        if any(a["id"] == attempt_id for a in data["attempts"]):
            raise ValueError("Attempt already exists")
        spent, pending = totals(data)
        if scope not in {SCOPE, BASELINE_SCOPE, TEMPORAL_SCOPE} or scope not in data["scope_limits_seconds"]:
            raise ValueError("Scope has not been authorized in the ledger")
        if scope == TEMPORAL_SCOPE:
            if time_limit not in {300, 900} or estimate*1.5 > time_limit or kill_wait > 60:
                raise ValueError("Invalid temporal runtime reservation")
            same = [a for a in data["attempts"] if a["scope"] == scope and a["time_limit_seconds"] == time_limit]
            if len(same) >= (1 if time_limit == 300 else 3):
                raise ValueError("Authorized temporal fit count exhausted")
            if time_limit == 900 and not data.get("temporal_gate"):
                raise ValueError("Full fits need measured pilot gate")
        scope_spent, scope_pending = totals(data, scope)
        if spent + pending + seconds + data["final_reserve_seconds"] > data["cpu_limit_seconds"]:
            raise ValueError("Accumulated CPU budget including final reserve is insufficient")
        if scope_spent + scope_pending + seconds > data["scope_limits_seconds"][scope]:
            raise ValueError("Pilot increment CPU budget is insufficient")
        data["attempts"].append({"id": attempt_id, "scope": scope, "state": "committed",
                                  "reserved_seconds": seconds, "estimate_seconds": estimate,
                                  "time_limit_seconds": time_limit, "kill_wait_seconds": kill_wait,
                                  "actual_seconds": None, "job_id": None, "claimed": False,
                                  "created_unix": time.time()})


def bind_job(path, attempt_id, job_id):
    if not str(job_id).isdigit():
        raise ValueError("Expected numeric Slurm job ID")
    with ledger(path) as data:
        attempt = next(a for a in data["attempts"] if a["id"] == attempt_id)
        if (attempt["state"] != "committed" or attempt["job_id"] is not None
                or attempt.get("execution_kind", "").startswith("local_gpu")):
            raise ValueError("Attempt is not awaiting job binding")
        attempt["job_id"] = str(job_id)


def assert_admitted(path, attempt_id, job_id):
    with ledger(path) as data:
        if data is None:
            raise ValueError("Budget missing")
        attempt = next(a for a in data["attempts"] if a["id"] == attempt_id)
        if attempt["state"] != "committed" or attempt["job_id"] != str(job_id):
            raise ValueError("Pilot has no matching committed Slurm reservation")
        return dict(attempt)


def claim_attempt(path, attempt_id, job_id, output, expected_scope=SCOPE):
    with ledger(path) as data:
        if data is None:
            raise ValueError("Budget missing")
        attempt = next(a for a in data["attempts"] if a["id"] == attempt_id)
        if attempt["state"] != "committed" or attempt["job_id"] != str(job_id):
            raise ValueError("No matching committed Slurm reservation")
        if attempt["scope"] != expected_scope:
            raise ValueError("Attempt scope does not match execution profile")
        if attempt.get("claimed"):
            raise ValueError("Attempt was already claimed; every fit needs a new attempt")
        if expected_scope == "rgb-global-loso":
            from .rgb_loso_budget import check_start_data
            check_start_data(data, attempt)
        attempt.update(claimed=True, run_directory=str(Path(output).resolve()))
        return dict(attempt)


def settle(path, attempt_id, actual_seconds, job_id, terminal_state):
    if actual_seconds < 0 or terminal_state not in {"COMPLETED", "FAILED", "TIMEOUT", "CANCELLED", "OUT_OF_MEMORY", "NODE_FAIL",
            "BOOT_FAIL", "DEADLINE", "PREEMPTED", "REVOKED", "SPECIAL_EXIT"}:
        raise ValueError("Only measured terminal jobs can be reconciled")
    with ledger(path) as data:
        attempt = next(a for a in data["attempts"] if a["id"] == attempt_id)
        if attempt["state"] != "committed" or attempt["job_id"] != str(job_id):
            raise ValueError("Reservation settled already or job mismatch")
        attempt.update(state="settled", actual_seconds=float(actual_seconds), terminal_state=terminal_state)
        if actual_seconds > attempt["reserved_seconds"]:
            attempt["reservation_overrun"] = True


def enable_temporal(path):
    with ledger(path) as data:
        if data is None:
            raise ValueError("Existing ledger required")
        old = data["scope_limits_seconds"].get(TEMPORAL_SCOPE)
        if old is not None and old != 3600:
            raise ValueError("Cannot alter existing scope limit")
        data["scope_limits_seconds"][TEMPORAL_SCOPE] = 3600


def check_temporal_gate(path, source_hash, manifest_hash=None):
    with ledger(path) as data:
        gate = data.get("temporal_gate") if data else None
        if not gate or gate["producer_hash"] != source_hash or gate["projected_fold_seconds_with_margin"] > 900:
            raise ValueError("Complete temporal fits require a compatible measured pilot gate")
        if manifest_hash is not None and gate["manifest_hash"] != manifest_hash:
            raise ValueError("Temporal gate manifest mismatch")
        return dict(gate)


def admit_temporal(path, manifest, pilot_directory, restoration_receipt=None):
    from .temporal_restore import load_temporal_run
    from .io import producer_hash, sha256
    from pathlib import Path
    import math
    root = Path(pilot_directory)
    run, split, _ = load_temporal_run(manifest, root)
    metrics = read_json(root/"metrics.json")
    if run["phase"] != "temporal_pilot" or split["outer_signer"] != "M02":
        raise ValueError("Fixed M02 pilot required")
    with ledger(path) as data:
        row = next(a for a in data["attempts"] if a["id"] == run["attempt_id"])
        if (row["state"] != "settled" or row["terminal_state"] != "COMPLETED"
                or row["job_id"] != run["job_id"] or row["scope"] != TEMPORAL_SCOPE):
            raise ValueError("Pilot job must be reconciled as completed first")
        if restoration_receipt is None:
            raise ValueError("Original restoration receipt required before admission")
        import numpy as np
        receipt_path = Path(restoration_receipt)
        receipt = read_json(receipt_path)
        expected = {"source": "original_train_npy", "cache_required": False,
                    "validation_clips": 375, "atol": 1e-6, "rtol": 0,
                    "manifest_hash": manifest["manifest_hash"], "producer_hash": producer_hash(),
                    "run_sha256": sha256(root/"run.json")}
        name = receipt.get("restored_file", "")
        difference = receipt.get("max_abs_difference", float("inf"))
        if (any(receipt.get(k) != v for k, v in expected.items()) or not name
                or Path(name).name != name or not math.isfinite(difference) or not 0 <= difference <= 1e-6):
            raise ValueError("Invalid original restoration receipt")
        restored = receipt_path.parent/name
        if sha256(restored) != receipt.get("restored_sha256"):
            raise ValueError("Restoration hash mismatch")
        with np.load(restored, allow_pickle=False) as replay, np.load(root/"validation.npz", allow_pickle=False) as ref:
            if (replay["ids"].tolist() != split["validation_ids"]
                    or replay["probabilities"].shape != (375, 5)
                    or not np.allclose(replay["probabilities"], ref["probabilities"], atol=1e-6, rtol=0)):
                raise ValueError("Restoration predictions mismatch")
        cold = max(0, row["actual_seconds"]-metrics["process_seconds_before_final_metadata"])+2
        projected = metrics["projected_fold_seconds_with_margin"]+1.5*cold
        probe = metrics.get("batch60_probe") or {}
        if (not math.isfinite(projected) or projected > 900
                or metrics["measured_step_count"] < 10 or not probe.get("backward_optimizer_step")
                or not probe.get("discarded_copy") or probe.get("size") != 60):
            raise ValueError("Pilot does not establish viable full recipe")
        spent, pending = totals(data)
        scope_spent, scope_pending = totals(data, TEMPORAL_SCOPE)
        if (scope_spent+scope_pending+3*960 > data["scope_limits_seconds"][TEMPORAL_SCOPE]
                or spent+pending+3*960+data["final_reserve_seconds"] > data["cpu_limit_seconds"]):
            raise ValueError("Complete chain cannot be reserved")
        gate = {"producer_hash": producer_hash(), "pilot_run_sha256": sha256(root/"run.json"),
                "pilot_attempt": row["id"], "manifest_hash": manifest["manifest_hash"],
                "restoration_receipt_sha256": sha256(receipt_path),
                "restored_sha256": sha256(restored),
                "projected_fold_seconds_with_margin": projected, "remaining_folds": 3}
        existing = data.get("temporal_gate")
        if existing and existing != gate:
            raise ValueError("Cannot replace admitted temporal gate")
        data["temporal_gate"] = gate
        return dict(gate)


def reserve_temporal(path, attempt, kill_wait, pilot=False):
    from .io import producer_hash
    if not 0 <= kill_wait <= 60:
        raise ValueError("Termination grace does not fit fixed reservation")
    if pilot:
        seconds, estimate, limit = 360, 180, 300
    else:
        gate = check_temporal_gate(path, producer_hash())
        seconds, estimate, limit = 960, gate["projected_fold_seconds_with_margin"]/1.5, 900
    if estimate*1.5 > limit:
        raise ValueError("Runtime margin must fit TimeLimit, not termination grace")
    reserve(path, attempt, seconds=seconds, estimate=estimate, time_limit=limit,
            kill_wait=kill_wait, scope=TEMPORAL_SCOPE)
