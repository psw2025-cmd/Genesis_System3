"""Bounded Cloud Run Job entry point for Genesis System3.

Unlike ``scripts/cloud_worker.py`` (legacy forever-daemon), every invocation
runs exactly one selected analyzer/paper task and exits.  Live execution flags
are rejected before project modules are imported.
"""

from __future__ import annotations

import json
import os
import re
import urllib.parse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_TRUTHY = {"1", "true", "yes", "on", "enabled"}
_EXPECTED_SCHEDULERS = {
    "genesis-system3-forecast-daily": ("ENABLED", "genesis-system3-forecast"),
    "genesis-system3-rank-daily": ("ENABLED", "genesis-system3-rank"),
    "genesis-system3-signals-daily": ("ENABLED", "genesis-system3-signals"),
    "genesis-system3-dhan-token-rotate-daily": ("ENABLED", "genesis-system3-dhan-token-rotate"),
    "genesis-system3-forecast-schedule": ("PAUSED", "genesis-system3-forecast"),
    "genesis-system3-rank-schedule": ("PAUSED", "genesis-system3-rank"),
    "genesis-system3-signals-schedule": ("PAUSED", "genesis-system3-signals"),
}


def _parse_scheduler_target(uri: str, project: str, region: str) -> tuple[Optional[str], bool]:
    try:
        parsed = urllib.parse.urlsplit(uri)
        match = re.fullmatch(
            rf"/v2/projects/{re.escape(project)}/locations/{re.escape(region)}/jobs/([^/:]+):run",
            parsed.path,
        )
        valid = bool(parsed.scheme == "https" and parsed.hostname == "run.googleapis.com" and parsed.port is None and not parsed.username and not parsed.password and not parsed.query and not parsed.fragment and match)
        return (match.group(1) if match else None), valid
    except Exception:
        return None, False


def _truthy(value: Optional[str]) -> bool:
    return str(value or "").strip().lower() in _TRUTHY


def _assert_analyzer_only() -> None:
    forbidden = {
        name: os.environ.get(name, "0")
        for name in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED")
        if _truthy(os.environ.get(name, "0"))
    }
    if forbidden:
        raise RuntimeError(f"Live execution flags are forbidden in Cloud Run Jobs: {sorted(forbidden)}")
    os.environ["LIVE_TRADING_ENABLED"] = "0"
    os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
    os.environ["SYSTEM3_MODE"] = "analyzer"
    os.environ["ANALYZE_MODE"] = "1"
    os.environ["CLOUD_WORKER"] = "true"


def _base_result(kind: str) -> Dict[str, Any]:
    return {
        "kind": kind,
        "status": "PASS",
        "mode": "PAPER",
        "live_trading_enabled": False,
        "task_index": int(os.environ.get("CLOUD_RUN_TASK_INDEX", "0")),
        "task_attempt": int(os.environ.get("CLOUD_RUN_TASK_ATTEMPT", "0")),
        "completed_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _collect_scheduler_facts(session=None) -> Dict[str, Any]:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    region = os.environ.get("GCP_REGION", "asia-south1").strip()
    if not project:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT is required")
    if session is None:
        from google.auth import default as google_auth_default
        from google.auth.transport.requests import AuthorizedSession
        credentials, _ = google_auth_default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        session = AuthorizedSession(credentials)
    scheduler_url = f"https://cloudscheduler.googleapis.com/v1/projects/{project}/locations/{region}/jobs"
    run_url = f"https://run.googleapis.com/v2/projects/{project}/locations/{region}/jobs"
    def pages(url: str, key: str) -> list:
        rows, token = [], None
        while True:
            response = session.get(url, params={"pageSize": 100, **({"pageToken": token} if token else {})}, timeout=20)
            response.raise_for_status()
            body = response.json()
            page = body.get(key, [])
            if not isinstance(page, list):
                raise RuntimeError(f"Malformed Google API {key} response")
            rows.extend(page)
            token = body.get("nextPageToken")
            if not token:
                return rows
    scheduler_rows = pages(scheduler_url, "jobs")
    run_rows = pages(run_url, "jobs")
    resources = []
    for row in scheduler_rows:
        name = str(row.get("name", "")).rsplit("/", 1)[-1]
        uri = str((row.get("httpTarget") or {}).get("uri") or "")
        target_job, target_valid = _parse_scheduler_target(uri, project, region)
        resources.append({"name": name, "state": row.get("state", "MISSING"), "target_job": target_job, "target_uri_valid": target_valid, "target_type": "http" if uri else ("pubsub" if row.get("pubsubTarget") else "missing"), "schedule": row.get("schedule"), "time_zone": row.get("timeZone"), "last_attempt_time": row.get("lastAttemptTime"), "delivery_status_code": (row.get("status") or {}).get("code", 0), "delivery_status_message": str((row.get("status") or {}).get("message") or "")[:200]})
    jobs = []
    targets = sorted({target for _, target in _EXPECTED_SCHEDULERS.values()})
    by_job = {str(row.get("name", "")).rsplit("/", 1)[-1]: row for row in run_rows}
    for name in targets:
        latest = (by_job.get(name, {}).get("latestCreatedExecution") or {})
        jobs.append({"name": name, "execution": str(latest.get("name", "")).rsplit("/", 1)[-1] or None, "completion_status": latest.get("completionStatus") or "MISSING", "create_time": latest.get("createTime"), "completion_time": latest.get("completionTime")})
    return {"schema_version": 1, "observed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "resources": resources, "jobs": jobs, "artifacts": [], "summary": {"source": "google_cloud_control_plane", "live_trading_enabled": False}}


def _run_scheduler_collector() -> Dict[str, Any]:
    from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend
    owner = os.environ.get("CLOUD_RUN_EXECUTION", "").strip()
    if not owner:
        raise RuntimeError("CLOUD_RUN_EXECUTION unique owner is required")
    facts = _collect_scheduler_facts()
    backend = FirestoreSchedulerEvidenceBackend()
    lease = backend.acquire_lease(owner, 120)
    if not lease.get("acquired"):
        raise RuntimeError("scheduler collector lease held by another execution")
    return backend.publish(facts, owner=owner, fence=lease["fence"])


def run_job(kind: Optional[str] = None) -> Dict[str, Any]:
    _assert_analyzer_only()
    kind = (kind or os.environ.get("SYSTEM3_JOB_KIND", "smoke")).strip().lower()
    result = _base_result(kind)

    if kind == "smoke":
        result["detail"] = "Analyzer-only bounded worker smoke test"
    elif kind == "scheduler-collector":
        result["scheduler_evidence"] = _run_scheduler_collector()
        result["detail"] = "One fenced raw scheduler control-plane collection completed"
    elif kind == "state-sync":
        from dashboard.backend.runtime_state_store import get_state_store

        store = get_state_store(ROOT / "outputs")
        store.sync_from_files()
        result["state_version"] = store.get_state_version()
        result["detail"] = "One bounded local-file-to-SSOT sync completed"
    elif kind == "paper-pipeline-v8":
        if not _truthy(os.environ.get("SYSTEM3_ENABLE_PAPER_JOB", "0")):
            raise RuntimeError("Paper pipeline job requires SYSTEM3_ENABLE_PAPER_JOB=1")
        from dashboard.backend.paper_pipeline_v8 import run_pipeline_once

        pipeline = run_pipeline_once(ROOT, create_paper_orders=True, source="gcp_cloud_run_job")
        result["pipeline"] = {
            key: pipeline.get(key)
            for key in ("status", "forecasts_seen", "paper_orders_written", "blocked_written")
        }
        result["detail"] = "One bounded paper/analyzer pipeline cycle completed"
    else:
        raise ValueError(f"Unsupported SYSTEM3_JOB_KIND={kind!r}")

    if _truthy(os.environ.get("SYSTEM3_JOB_PUBLISH_STATE", "1")):
        from dashboard.backend.runtime_state_store import get_state_store

        store = get_state_store(ROOT / "outputs")
        store.update_state({"cloud_job": result, "mode": "PAPER"})
        result["state_version"] = store.get_state_version()
    return result


def main() -> int:
    try:
        print(json.dumps(run_job(), sort_keys=True, default=str))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc), "live_trading_enabled": False}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
