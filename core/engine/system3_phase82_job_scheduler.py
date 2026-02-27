"""
System3 Phase 82 - Async Job Scheduler

Provide a job scheduler abstraction to run tasks (fetch, train, eval, reports)
in a controlled way.
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
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
    """Run a single job."""
    job_id = job["id"]
    module_name = job["module"]

    print(f"[PH82] Running job: {job['name']} ({job_id})...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", module_name],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,
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
            "last_error": "Job timed out after 5 minutes",
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="System3 Phase 82 - Job Scheduler")
    parser.add_argument("--list", action="store_true", help="List all jobs")
    parser.add_argument("--run-once", action="store_true", help="Run all enabled jobs")
    parser.add_argument("--job-id", type=str, help="Run a single job by ID")

    args = parser.parse_args()

    try:
        if args.list:
            list_jobs()
        elif args.run_once:
            run_all_jobs()
        elif args.job_id:
            run_single_job(args.job_id)
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
