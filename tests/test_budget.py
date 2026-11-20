import pytest

from lsc5 import budget
from lsc5.io import atomic_json, read_json


def test_consumed_failed_and_pending_work_never_disappears(tmp_path):
    path = tmp_path / "budget.json"
    budget.initialize(path)
    budget.reserve(path, "failed")
    budget.bind_job(path, "failed", "1")
    budget.settle(path, "failed", 500, "1", "FAILED")
    budget.reserve(path, "pending")
    assert budget.totals(read_json(path)) == (500, 900)
    with pytest.raises(ValueError):
        budget.settle(path, "failed", 0, "1", "COMPLETED")
    with pytest.raises(FileExistsError):
        budget.initialize(path)
    data = read_json(path)
    data["cpu_limit_seconds"] = data["final_reserve_seconds"] + 2000
    atomic_json(path, data)
    with pytest.raises(ValueError, match="Accumulated"):
        budget.reserve(path, "too_many")
    assert budget.totals(read_json(path)) == (500, 900)


def test_duration_and_job_binding_guards(tmp_path):
    path = tmp_path / "budget.json"
    budget.initialize(path)
    with pytest.raises(ValueError, match="maximum"):
        budget.reserve(path, "underreserved", seconds=180)
    with pytest.raises(ValueError):
        budget.reserve(path, "excess_grace", kill_wait=400)
    budget.reserve(path, "ok")
    budget.bind_job(path, "ok", "12")
    assert budget.assert_admitted(path, "ok", "12")["reserved_seconds"] == 900
    with pytest.raises(ValueError):
        budget.assert_admitted(path, "ok", "13")
    with pytest.raises(ValueError):
        budget.settle(path, "ok", 1, "12", "RUNNING")


def test_increment_limit_is_also_accumulated(tmp_path):
    path = tmp_path / "budget.json"
    budget.initialize(path)
    data = read_json(path)
    data["scope_limits_seconds"][budget.SCOPE] = 1500
    atomic_json(path, data)
    budget.reserve(path, "first")
    budget.bind_job(path, "first", "1")
    budget.settle(path, "first", 700, "1", "TIMEOUT")
    with pytest.raises(ValueError, match="increment"):
        budget.reserve(path, "second")


def test_attempt_can_only_be_claimed_once(tmp_path):
    path = tmp_path / "budget.json"
    budget.initialize(path)
    budget.reserve(path, "one")
    budget.bind_job(path, "one", "99")
    budget.claim_attempt(path, "one", "99", tmp_path / "run1")
    with pytest.raises(ValueError, match="already claimed"):
        budget.claim_attempt(path, "one", "99", tmp_path / "run2")
