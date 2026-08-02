"""Bounded Cloud Run Job entry point for Genesis System3.

Unlike ``scripts/cloud_worker.py`` (legacy forever-daemon), every invocation
runs exactly one selected analyzer/paper task and exits.  Live execution flags
are rejected before project modules are imported.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_TRUTHY = {"1", "true", "yes", "on", "enabled"}


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


def run_job(kind: Optional[str] = None) -> Dict[str, Any]:
    _assert_analyzer_only()
    kind = (kind or os.environ.get("SYSTEM3_JOB_KIND", "smoke")).strip().lower()
    result = _base_result(kind)

    if kind == "smoke":
        result["detail"] = "Analyzer-only bounded worker smoke test"
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
