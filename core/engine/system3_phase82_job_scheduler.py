"""
System3 Phase 82 - Async Job Scheduler

Provide a job scheduler abstraction to run tasks (fetch, train, eval, reports)
in a controlled way.
"""

import os
import sys
import json
import time
import signal
import threading
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
CONFIG_DIR = PROJECT_ROOT / "config"
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"

# Config file
CONFIG_JSON = CONFIG_DIR / "system3_job_scheduler.json"

# Output files
STATE_JSON = STORAGE_ULTRA / "phase82_job_scheduler_state.json"
LOG_MD = STORAGE_ULTRA / "phase82_job_scheduler_log.md"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)


def create_default_config() -> None:
    """Create default job scheduler config if it doesn't exist."""
    if CONFIG_JSON.exists():
        return

    default_config = {
        "jobs": [
            {
                "id": "daily_status",
                "name": "Daily Status Check",
                "module": "core.engine.check_system3_status",
                "enabled": True,
                "type": "daily",
            }
        ]
    }

    with CONFIG_JSON.open("w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=2)
    print(f"[PH82] Created default config: {CONFIG_JSON}")


def load_config() -> Dict[str, Any]:
    """Load job scheduler config."""
    create_default_config()

    try:
        with CONFIG_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[PH82] Error loading config: {e}")
        return {"jobs": []}


def load_state() -> Dict[str, Any]:
    """Load job scheduler state."""
    if not STATE_JSON.exists():
        return {"jobs": {}}

    try:
        with STATE_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"jobs": {}}


def save_state(state: Dict[str, Any]) -> None:
    """Save job scheduler state."""
    with STATE_JSON.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def run_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single job.
    Supports two formats:
      module-based: {"module": "core.engine.foo"}  → python -m core.engine.foo
      script-based: {"script": "scripts/foo.py", "args": ["--mode", "rank"]}
    Optional: {"timeout_minutes": 10} overrides default 5-minute timeout.
    """
    job_id = job["id"]
    print(f"[PH82] Running job: {job.get('name', job_id)} ({job_id})...")

    if "script" in job:
        cmd = [sys.executable, str(PROJECT_ROOT / job["script"])] + job.get("args", [])
    else:
        module_name = job["module"]
        cmd = [sys.executable, "-m", module_name]

    timeout_secs = int(job.get("timeout_minutes", 5)) * 60

    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout_secs,
        )

        return {
            "last_run_time": datetime.now().isoformat(),
            "last_status": "SUCCESS" if result.returncode == 0 else "FAILED",
            "last_error": result.stderr[:500] if result.returncode != 0 else None,
        }
    except subprocess.TimeoutExpired:
        return {
            "last_run_time": datetime.now().isoformat(),
            "last_status": "TIMEOUT",
            "last_error": f"Job timed out after {timeout_secs // 60} minutes",
        }
    except Exception as e:
        return {
            "last_run_time": datetime.now().isoformat(),
            "last_status": "ERROR",
            "last_error": str(e),
        }


def list_jobs() -> None:
    """List all jobs and their status."""
    config = load_config()
    state = load_state()

    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 82 - JOB SCHEDULER - LIST")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(f"[PH82] Loaded {len(config.get('jobs', []))} jobs from {CONFIG_JSON}\n")

    print("| ID | Name | Enabled | Last Status | Last Run Time |")
    print("|----|------|---------|-------------|---------------|")

    for job in config.get("jobs", []):
        job_id = job["id"]
        job_state = state.get("jobs", {}).get(job_id, {})

        print(
            f"| {job_id} | {job['name']} | {job.get('enabled', False)} | "
            f"{job_state.get('last_status', 'NEVER_RUN')} | "
            f"{job_state.get('last_run_time', 'N/A')} |"
        )


def run_all_jobs() -> None:
    """Run all enabled jobs."""
    config = load_config()
    state = load_state()

    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 82 - JOB SCHEDULER - RUN ONCE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    enabled_jobs = [j for j in config.get("jobs", []) if j.get("enabled", False)]
    print(f"[PH82] Running {len(enabled_jobs)} enabled jobs...\n")

    if "jobs" not in state:
        state["jobs"] = {}

    for job in enabled_jobs:
        job_id = job["id"]
        result = run_job(job)
        state["jobs"][job_id] = result
        print(f"[PH82] Job {job_id} completed with status={result['last_status']}\n")

    save_state(state)
    generate_log_md(state, config)


def run_single_job(job_id: str) -> None:
    """Run a single job by ID."""
    config = load_config()
    state = load_state()

    job = next((j for j in config.get("jobs", []) if j["id"] == job_id), None)
    if not job:
        print(f"[PH82] Job not found: {job_id}")
        return

    if "jobs" not in state:
        state["jobs"] = {}

    result = run_job(job)
    state["jobs"][job_id] = result
    save_state(state)
    generate_log_md(state, config)


def generate_log_md(state: Dict[str, Any], config: Dict[str, Any]) -> None:
    """Generate markdown log."""
    with LOG_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 82 - Job Scheduler Log\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n\n")

        f.write("## Job Status\n\n")
        f.write("| id | name | enabled | last_status | last_run_time |\n")
        f.write("|----|------|---------|-------------|---------------|\n")

        for job in config.get("jobs", []):
            job_id = job["id"]
            job_state = state.get("jobs", {}).get(job_id, {})
            f.write(
                f"| {job_id} | {job['name']} | {job.get('enabled', False)} | "
                f"{job_state.get('last_status', 'NEVER_RUN')} | "
                f"{job_state.get('last_run_time', 'N/A')} |\n"
            )


_IST = timezone(timedelta(hours=5, minutes=30))


def _now_ist() -> datetime:
    return datetime.now(_IST)


def _time_matches(schedule_time: str, now: datetime, window_seconds: int = 60) -> bool:
    if not schedule_time or schedule_time.lower() == "daily":
        return False
    try:
        h, m = map(int, schedule_time.split(":"))
    except ValueError:
        return False
    target = now.replace(hour=h, minute=m, second=0, microsecond=0)
    return abs((now - target).total_seconds()) <= window_seconds


def _append_daemon_log(message: str) -> None:
    log_path = PROJECT_ROOT / "CHANGE_LOG.md"
    if not log_path.exists():
        return
    try:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"\n- {message}\n")
    except Exception as e:
        print(f"[Daemon] CHANGE_LOG write failed: {e}")


def run_daemon() -> None:
    """
    Daemon loop: fires enabled jobs at their schedule_time (IST) once per day.
    Weekdays only (skip Saturday/Sunday). Checks every 60 seconds.
    Start: python core/engine/system3_phase82_job_scheduler.py --daemon
    Stop:  kill $(cat state/scheduler_daemon.pid)
    """
    pid_file = PROJECT_ROOT / "state" / "scheduler_daemon.pid"
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(os.getpid()))
    print(f"[PH82-Daemon] Started PID={os.getpid()} at {_now_ist().strftime('%Y-%m-%d %H:%M:%S')} IST")

    last_fired: Dict[str, str] = {}      # job_id → "YYYY-MM-DD HH:MM"
    last_fired_date: Dict[str, str] = {} # job_id → "YYYY-MM-DD" (for daily jobs)
    _stop = {"flag": False}

    def _handle(signum, frame):
        print(f"[PH82-Daemon] Signal {signum} — shutting down...")
        _stop["flag"] = True

    # signal.signal() only works when called from the main thread of the main
    # interpreter. cloud_worker.py runs this daemon inside a background
    # threading.Thread, so registering handlers there raises ValueError on
    # the very first line of setup, before the loop ever ticks once — and
    # that ValueError was being silently caught by the caller's bare
    # `except Exception`, killing the scheduler thread forever with no
    # visible crash. This was the actual root cause of the dead job loop.
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, _handle)
        signal.signal(signal.SIGINT, _handle)
    else:
        print("[PH82-Daemon] Running in non-main thread — skipping OS signal "
              "handlers (daemon=True thread exits with the process).")

    state = load_state()
    if "jobs" not in state:
        state["jobs"] = {}
    state["daemon_started_at"] = _now_ist().isoformat()

    while not _stop["flag"]:
        now = _now_ist()
        today_str = now.strftime("%Y-%m-%d")
        is_weekday = now.weekday() < 5  # 0=Mon … 4=Fri

        # Heartbeat — proves the daemon loop itself is alive, independent of
        # whether any job was due this tick. Without this, a dead/crashed
        # daemon and "no job due yet" look identical from the dashboard.
        state["daemon_heartbeat"] = now.isoformat()
        state["daemon_pid"] = os.getpid()
        save_state(state)

        config = load_config()  # hot-reload each tick
        for job in config.get("jobs", []):
            if not job.get("enabled", False):
                continue
            job_id = job["id"]
            sched = job.get("schedule_time", "daily")

            # Day-of-week filtering: weekdays_only OR explicit days list
            if job.get("weekdays_only", False) and not is_weekday:
                continue
            named_days = job.get("days")
            if named_days and isinstance(named_days, list):
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                if day_names[now.weekday()] not in named_days:
                    continue

            should_fire = False
            if sched.lower() == "daily":
                if last_fired_date.get(job_id) != today_str:
                    should_fire = True
            else:
                if _time_matches(sched, now):
                    fire_key = f"{today_str} {sched}"
                    if last_fired.get(job_id) != fire_key:
                        should_fire = True
                        last_fired[job_id] = fire_key

            if should_fire:
                print(f"[PH82-Daemon] {now.strftime('%H:%M:%S')} IST — FIRING: {job.get('name', job_id)}")
                result = run_job(job)
                state["jobs"][job_id] = result
                save_state(state)
                if sched.lower() == "daily":
                    last_fired_date[job_id] = today_str
                _append_daemon_log(
                    f"[{now.strftime('%Y-%m-%d %H:%M')} IST] [Scheduler-Daemon] "
                    f"JOB FIRED: {job_id} — status={result.get('last_status', 'UNKNOWN')}"
                )
                print(f"[PH82-Daemon] {job_id} done — {result.get('last_status')}")

        if _stop["flag"]:
            break
        time.sleep(60)

    print(f"[PH82-Daemon] Stopped at {_now_ist().strftime('%Y-%m-%d %H:%M:%S')} IST")
    try:
        pid_file.unlink(missing_ok=True)
    except Exception:
        pass
    save_state(state)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="System3 Phase 82 - Job Scheduler")
    parser.add_argument("--list", action="store_true", help="List all jobs")
    parser.add_argument("--run-once", action="store_true", help="Run all enabled jobs")
    parser.add_argument("--job-id", type=str, help="Run a single job by ID")
    parser.add_argument("--daemon", action="store_true", help="Run daemon: fire jobs at scheduled IST times")

    args = parser.parse_args()

    try:
        if args.list:
            list_jobs()
        elif args.run_once:
            run_all_jobs()
        elif args.job_id:
            run_single_job(args.job_id)
        elif args.daemon:
            run_daemon()
        else:
            parser.print_help()

        return 0
    except Exception as e:
        print(f"\n[PH82] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
