"""Linux process-group watchdog for the single approved local GPU pilot."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import fcntl
import os
import resource
import shutil
import signal
import subprocess
import sys
import time

from .io import atomic_json, producer_hash, read_json, sha256
from .rgb_budget import validate_reservation


def available_ram():
    fields = dict(line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())
    return int(fields["MemAvailable"].split()[0])*1024


def gpu_memory():
    r = subprocess.run(["nvidia-smi", "-i", "0", "--query-gpu=memory.total,memory.used,memory.free",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True, timeout=10)
    total, used, free = [int(x.strip())*1024**2 for x in r.stdout.strip().split(",")]
    return {"total_bytes": total, "used_bytes": used, "free_bytes": free}


def admission(directory):
    mem, gpu, disk = available_ram(), gpu_memory(), shutil.disk_usage(directory).free
    now = datetime.now(ZoneInfo("America/Bogota"))
    if now >= datetime(2026, 11, 22, 17, tzinfo=ZoneInfo("America/Bogota")):
        raise ValueError("Pilot must preserve one hour before branch cutoff")
    if mem < 2*1024**3 or gpu["free_bytes"] < 3*1024**3 or disk < 8*1024**3:
        raise MemoryError("Initial RAM/VRAM/disk admission failed")
    return {"available_ram_bytes": mem, "gpu": gpu, "free_disk_bytes": disk,
            "bogota_time": now.isoformat()}


def group_rss(group):
    total = 0
    for p in Path("/proc").glob("[0-9]*/stat"):
        try:
            fields = p.read_text().rsplit(")", 1)[1].split()
            if int(fields[2]) == group or p.parent.name == str(os.getpid()):
                total += int((p.parent/"statm").read_text().split()[1])*os.sysconf("SC_PAGE_SIZE")
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
    return total


def guard_directory():
    path = Path.home()/".cache/lsc5"
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def start_gpu_query():
    return subprocess.Popen(["nvidia-smi", "-i", "0", "--query-gpu=memory.total,memory.used,memory.free",
                             "--format=csv,noheader,nounits"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def finish_gpu_query(process):
    stdout, stderr = process.communicate(timeout=1)
    if process.returncode:
        raise RuntimeError("GPU sample query failed")
    total, used, free = [int(x.strip())*1024**2 for x in stdout.decode().strip().split(",")]
    return {"total_bytes": total, "used_bytes": used, "free_bytes": free}


def stop_group(group):
    try:
        os.killpg(group, signal.SIGTERM)
    except ProcessLookupError:
        return
    until = time.monotonic()+10
    while time.monotonic() < until:
        live = False
        for p in Path("/proc").glob("[0-9]*/stat"):
            try:
                fields = p.read_text().rsplit(")", 1)[1].split()
                live |= int(fields[2]) == group and fields[0] != "Z"
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                continue
        if not live:
            return
        time.sleep(.1)
    try:
        os.killpg(group, signal.SIGKILL)
    except ProcessLookupError:
        pass


def supervise(train_root, manifest_path, assets, reservation_path, output, runs=None):
    manifest, reservation = read_json(manifest_path), read_json(reservation_path)
    full = reservation.get("execution_kind") == "local_gpu_rgb_full"
    if full:
        from .rgb_loso_budget import validate_gpu_reservation
        validate_gpu_reservation(reservation, manifest)
    else:
        validate_reservation(reservation, manifest)
    output = Path(output).resolve()
    if str(output) != reservation.get("run_directory"):
        raise ValueError("Output must match the execution atomically bound in the ledger")
    guard = guard_directory()
    lock_path = guard/"local-gpu.lock"
    lock_path.touch(mode=0o600, exist_ok=True)
    lock = lock_path.open("a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if output.exists():
            raise FileExistsError(output)
        marker = guard/(reservation["reservation_hash"]+".used")
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(reservation["id"])
        output.mkdir(parents=True, exist_ok=False, mode=0o700)
    except BaseException:
        lock.close()
        raise
    started = time.monotonic()
    receipt = {"attempt_id": reservation["id"], "reservation_hash": reservation["reservation_hash"],
               "producer_hash": producer_hash(), "terminal_state": "FAILED", "stages": [],
               "peak_aggregate_rss_bytes": 0, "minimum_available_ram_bytes": available_ram(),
               "gpu_memory_samples": []}
    child, gpu_query = None, None
    previous_signals = {s: signal.getsignal(s) for s in [signal.SIGTERM, signal.SIGINT]}
    def interrupted(signum, frame):
        raise RuntimeError(f"Supervisor interrupted by signal {signum}")
    for s in previous_signals:
        signal.signal(s, interrupted)
    try:
        receipt["admission"] = admission(output)
        common = ["--data-root", str(Path(train_root).resolve().parent), "--manifest", str(Path(manifest_path).resolve()),
                  "--assets", str(Path(assets).resolve())]
        stages = [("pilot", ["rgb-pilot"]+common+["--reservation", str(Path(reservation_path).resolve()),
                    "--out", str(output/"pilot")]),
                  ("replay", ["rgb-replay"]+common+["--run", str(output/"pilot"), "--out", str(output/"replay.json")])]
        if full:
            stages = [(reservation["profile"], ["rgb-full-worker"]+common+
                       ["--reservation", str(Path(reservation_path).resolve()), "--out", str(output/"full")]+
                       (["--runs"]+[str(Path(p).resolve()) for p in runs] if runs else []))]
        last_gpu_check = 0.
        for label, arguments in stages:
            stage_start = time.monotonic()
            with (output/(label+".stdout.txt")).open("x") as stdout, (output/(label+".stderr.txt")).open("x") as stderr:
                child = subprocess.Popen([sys.executable, "-m", "lsc5.cli"]+arguments, stdout=stdout, stderr=stderr,
                                         start_new_session=True,
                                         env=dict(os.environ, LSC5_RGB_SUPERVISOR_PID=str(os.getpid())))
                while child.poll() is None:
                    elapsed = time.monotonic()-started
                    mem, rss = available_ram(), group_rss(child.pid)
                    receipt["peak_aggregate_rss_bytes"] = max(receipt["peak_aggregate_rss_bytes"], rss)
                    receipt["minimum_available_ram_bytes"] = min(receipt["minimum_available_ram_bytes"], mem)
                    if elapsed > reservation["time_limit_seconds"]:
                        receipt["terminal_state"] = "TIMEOUT"
                        raise TimeoutError("Whole pilot/replay process deadline exceeded")
                    if mem < 512*1024**2 or rss > 2*1024**3:
                        receipt["terminal_state"] = "RESOURCE_LIMIT"
                        raise MemoryError("Runtime RAM threshold exceeded")
                    if gpu_query is not None:
                        if gpu_query.poll() is not None:
                            try:
                                receipt["gpu_memory_samples"].append(finish_gpu_query(gpu_query))
                            except Exception as error:
                                receipt.setdefault("gpu_sample_errors", []).append(str(error))
                            gpu_query = None
                        elif elapsed-last_gpu_check > 10:
                            gpu_query.kill()
                            gpu_query.communicate(timeout=1)
                            gpu_query = None
                            receipt.setdefault("gpu_sample_errors", []).append("Async GPU sample timeout")
                    if gpu_query is None and elapsed-last_gpu_check >= 1:
                        gpu_query = start_gpu_query()
                        last_gpu_check = elapsed
                    time.sleep(.1)
            child.wait(timeout=5)
            stop_group(child.pid)
            receipt["stages"].append({"name": label, "returncode": child.returncode,
                                      "seconds": time.monotonic()-stage_start})
            if child.returncode:
                raise RuntimeError("Worker failed; details retained in private stderr")
            child = None
        if full:
            result = read_json(output/"full/result.json")
            if result["status"] != "complete" or result["profile"] != reservation["profile"] or result["clips"] != 1125:
                raise ValueError("Full GPU phase did not complete")
            receipt.update(terminal_state="COMPLETED", full_result_sha256=sha256(output/"full/result.json"),
                           gpu_forward_seconds=result["gpu_forward_seconds"],
                           gpu_timing_scope="synchronized_forward_wall_excludes_setup_warmup_and_transfers")
        else:
            metrics = read_json(output/"pilot/metrics.json")
            replay = read_json(output/"replay.json")
            receipt.update(terminal_state="COMPLETED", pilot_run_sha256=sha256(output/"pilot/run.json"),
                       cache_metadata_sha256=sha256(output/"pilot/cache/metadata.json"),
                       metrics_sha256=sha256(output/"pilot/metrics.json"),
                       replay_receipt_sha256=sha256(output/"replay.json"),
                       gpu_forward_seconds=sum(b["forward_seconds"] for b in metrics["batches"])+replay["forward_seconds"],
                       gpu_timing_scope="synchronized_forward_wall_excludes_setup_warmup_and_transfers")
    except BaseException as error:
        receipt.update(error_type=type(error).__name__, error=str(error))
    finally:
        cleanup_errors = []
        def cleanup(label, operation):
            try:
                return operation()
            except BaseException as error:
                cleanup_errors.append({"operation": label, "error_type": type(error).__name__, "error": str(error)})
                return None
        for sig in previous_signals:
            cleanup("ignore_signal", lambda sig=sig: signal.signal(sig, signal.SIG_IGN))
        if child is not None:
            cleanup("stop_worker_group", lambda: stop_group(child.pid))
            cleanup("wait_worker", lambda: child.wait(timeout=5))
            receipt["worker_termination_confirmed"] = cleanup("poll_worker", child.poll) is not None
        if gpu_query is not None:
            if cleanup("poll_gpu_query", gpu_query.poll) is None:
                cleanup("kill_gpu_query", gpu_query.kill)
            cleanup("reap_gpu_query", lambda: gpu_query.communicate(timeout=1))
        usage = cleanup("child_usage", lambda: resource.getrusage(resource.RUSAGE_CHILDREN))
        if usage is not None:
            receipt["children_cpu_seconds"] = usage.ru_utime+usage.ru_stime
        memory = cleanup("final_gpu_memory", gpu_memory)
        if memory is not None:
            receipt["final_gpu_memory"] = memory
        receipt["actual_seconds"] = time.monotonic()-started
        if cleanup_errors:
            receipt["cleanup_errors"] = cleanup_errors
            if receipt["terminal_state"] == "COMPLETED":
                receipt["terminal_state"] = "FAILED"
        try:
            atomic_json(output/"execution.json", receipt)
        finally:
            cleanup("close_lock", lock.close)
            for sig, handler in previous_signals.items():
                cleanup("restore_signal", lambda sig=sig, handler=handler: signal.signal(sig, handler))
    return receipt
