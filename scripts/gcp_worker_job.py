"""Bounded Cloud Run Job entry point for Genesis System3.

Unlike ``scripts/cloud_worker.py`` (legacy forever-daemon), every invocation
runs exactly one selected analyzer/paper task and exits.  Live execution flags
are rejected before project modules are imported.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
import hashlib
import base64
from datetime import date
from zoneinfo import ZoneInfo
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_TRUTHY = {"1", "true", "yes", "on", "enabled"}


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
    from dashboard.backend.scheduler_contract import expected_job_targets

    targets = expected_job_targets()
    by_job = {str(row.get("name", "")).rsplit("/", 1)[-1]: row for row in run_rows}

    def _completion_key(row: Dict[str, Any]):
        try:
            return datetime.fromisoformat(str(row["completionTime"]).replace("Z", "+00:00"))
        except Exception:
            return datetime.min.replace(tzinfo=timezone.utc)

    def _row_succeeded(row: Dict[str, Any]) -> bool:
        return int(row.get("succeededCount", 0) or 0) >= int(row.get("taskCount", 1) or 1)

    def _job_fact_from_latest(name: str) -> Dict[str, Any]:
        latest = (by_job.get(name, {}).get("latestCreatedExecution") or {})
        return {
            "name": name,
            "execution": str(latest.get("name", "")).rsplit("/", 1)[-1] or None,
            "completion_status": latest.get("completionStatus") or "MISSING",
            "create_time": latest.get("createTime"),
            "completion_time": latest.get("completionTime"),
            "evidence_role": "latest_created_execution",
        }

    def _prefer_last_succeeded(name: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        if fallback.get("completion_status") == "EXECUTION_SUCCEEDED":
            return fallback
        try:
            history = pages(f"{run_url}/{name}/executions", "executions")
        except Exception:
            return fallback
        succeeded = [row for row in history if row.get("completionTime") and _row_succeeded(row)]
        if not succeeded:
            return fallback
        succeeded.sort(key=_completion_key, reverse=True)
        row = succeeded[0]
        return {
            "name": name,
            "execution": str(row.get("name", "")).rsplit("/", 1)[-1] or None,
            "completion_status": "EXECUTION_SUCCEEDED",
            "create_time": row.get("createTime"),
            "completion_time": row.get("completionTime"),
            "evidence_role": "last_succeeded_within_history",
            "latest_completion_status": fallback.get("completion_status"),
        }

    for name in targets:
        jobs.append(_prefer_last_succeeded(name, _job_fact_from_latest(name)))
    # The collector is currently running, so job.latestCreatedExecution points
    # at itself and cannot prove completion. Use the newest PRIOR completed run,
    # preferring a succeeded prior so one lease collision does not poison health.
    executions_url = f"{run_url}/genesis-system3-scheduler-collector/executions"
    prior = []
    try:
        prior = pages(executions_url, "executions")
    except Exception:
        prior = []
    current_execution = os.environ.get("CLOUD_RUN_EXECUTION", "")
    completed_prior = [row for row in prior if row.get("completionTime") and str(row.get("name", "")).rsplit("/", 1)[-1] != current_execution]
    completed_prior.sort(key=_completion_key, reverse=True)
    succeeded_prior = [row for row in completed_prior if _row_succeeded(row)]
    pick = succeeded_prior[0] if succeeded_prior else (completed_prior[0] if completed_prior else None)
    if pick is not None:
        succeeded = _row_succeeded(pick)
        replacement = {
            "name": "genesis-system3-scheduler-collector",
            "execution": str(pick.get("name", "")).rsplit("/", 1)[-1],
            "completion_status": "EXECUTION_SUCCEEDED" if succeeded else "EXECUTION_FAILED",
            "create_time": pick.get("createTime"),
            "completion_time": pick.get("completionTime"),
            "evidence_role": "prior_succeeded_execution" if succeeded_prior else "prior_completed_execution",
        }
        jobs = [replacement if fact.get("name") == "genesis-system3-scheduler-collector" else fact for fact in jobs]
    return {"schema_version": 1, "observed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "resources": resources, "jobs": jobs, "artifacts": [], "summary": {"source": "google_cloud_control_plane", "live_trading_enabled": False}}


def _run_scheduler_collector() -> Dict[str, Any]:
    import time

    from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend
    owner = os.environ.get("CLOUD_RUN_EXECUTION", "").strip()
    if not owner:
        raise RuntimeError("CLOUD_RUN_EXECUTION unique owner is required")
    backend = FirestoreSchedulerEvidenceBackend()
    facts = _collect_scheduler_facts()
    for lane in ("rank", "forecast", "signals", "validate"):
        try:
            artifact = backend.verify_artifact(lane)
        except ValueError:
            artifact = None
        if artifact:
            facts["artifacts"].append(artifact)
    # Minute cadence overlaps; lease TTL must stay under 60s and collisions must
    # not mark the control plane EXECUTION_FAILED (that poisoned Auto Deploy).
    lease = {"acquired": False}
    for _ in range(8):
        lease = backend.acquire_lease(owner, 45)
        if lease.get("acquired"):
            break
        time.sleep(2)
    if not lease.get("acquired"):
        return {
            **_base_result("scheduler-collector"),
            "status": "SKIPPED",
            "reason_code": "LEASE_HELD",
            "detail": "Another collector holds the publish fence; skipping without failing control plane",
            "lease_owner": lease.get("owner"),
        }
    return backend.publish(facts, owner=owner, fence=lease["fence"])

def _business_context(lane: str) -> tuple[str, bool, str]:
    now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    today = now_ist.date()
    if today.weekday() >= 5:
        return today.isoformat(), False, "WEEKEND"
    try:
        from core.utils.nse_holidays import is_trading_holiday
        holiday, reason = is_trading_holiday(today)
        if holiday:
            return today.isoformat(), False, str(reason or "EXCHANGE_HOLIDAY")
    except Exception:
        return today.isoformat(), False, "UNKNOWN_CALENDAR"
    minute = now_ist.hour * 60 + now_ist.minute
    if lane == "validate":
        # Post-close validation window (15:30–16:45 IST).
        window = (15 * 60 + 30, 16 * 60 + 45)
    elif lane in {"rank", "forecast"}:
        window = (9 * 60, 15 * 60 + 30)
    else:
        window = (18 * 60 + 30, 23 * 60)
    if not (window[0] <= minute <= window[1]):
        return today.isoformat(), False, "MARKET_SESSION_CLOSED"
    return today.isoformat(), True, "OPEN_SESSION"


def _artifact(lane: str, payload: Dict[str, Any], source_bytes: bytes, output_bytes: bytes) -> Dict[str, Any]:
    from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend
    business_date, _, _ = _business_context(lane)
    run_id = os.environ.get("CLOUD_RUN_EXECUTION", "").strip()
    if not run_id:
        raise RuntimeError("CLOUD_RUN_EXECUTION is required for immutable business artifacts")
    code_paths = [Path(__file__), ROOT / "dashboard/backend/firestore_state_backend.py"]
    if lane == "rank":
        code_paths.append(ROOT / "scripts/daily_gain_rank_and_validate.py")
    elif lane == "validate":
        code_paths.append(ROOT / "scripts/daily_gain_rank_and_validate.py")
        code_paths.append(ROOT / "src/validation/market_result_validator.py")
    elif lane == "signals":
        code_paths.append(ROOT / "scripts/run_signal_engine_from_bhavcopy.py")
    code_bytes = b"".join(path.read_bytes() for path in code_paths)
    value = {"schema_version": 1, "lane": lane, "run_id": run_id, "produced_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "business_date": business_date, "status": payload.get("status", "PASS"), "reason_code": payload.get("reason_code"), "payload": payload, "source_sha256": hashlib.sha256(source_bytes).hexdigest(), "code_sha256": hashlib.sha256(code_bytes).hexdigest(), "output_sha256": hashlib.sha256(output_bytes).hexdigest(), "output_bytes_b64": base64.b64encode(output_bytes).decode("ascii")}
    return FirestoreSchedulerEvidenceBackend().publish_artifact(lane, value)


def _run_validate_lane() -> Dict[str, Any]:
    """Post-close Spearman day using durable rank predictions + Dhan actuals."""
    from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend
    from src.validation.market_result_validator import MarketResultValidator

    business_date, is_open_day, reason = _business_context("validate")
    if not is_open_day:
        status = "PENDING" if reason == "UNKNOWN_CALENDAR" else "SKIPPED"
        raw = json.dumps({"status": status, "reason_code": reason, "business_date": business_date}, sort_keys=True).encode()
        return _artifact("validate", {"status": status, "reason_code": reason}, b"exchange-calendar", raw)

    backend = FirestoreSchedulerEvidenceBackend()
    rank = backend.load_artifact("rank")
    if not rank or rank.get("business_date") != business_date or rank.get("status") != "PASS":
        payload = {"status": "PENDING", "reason_code": "VALIDATION_NO_PREDICTIONS", "business_date": business_date}
        raw = json.dumps(payload, sort_keys=True).encode()
        return _artifact("validate", payload, b"missing-rank-artifact", raw)

    rows = (rank.get("payload") or {}).get("rows") or []
    predictions = []
    for row in rows:
        underlying = str(row.get("underlying") or "").strip().upper()
        if not underlying:
            continue
        try:
            predictions.append({"underlying": underlying, "rank": int(row.get("rank") or len(predictions) + 1)})
        except (TypeError, ValueError):
            continue
    if not predictions:
        payload = {"status": "PENDING", "reason_code": "VALIDATION_NO_PREDICTIONS", "business_date": business_date}
        raw = json.dumps(payload, sort_keys=True).encode()
        return _artifact("validate", payload, b"empty-rank-rows", raw)

    report = MarketResultValidator().validate_today(prediction_snapshot=predictions)
    if report.get("error"):
        reason_code = (
            "VALIDATION_ACTUALS_UNAVAILABLE"
            if "actual" in str(report.get("error") or "").lower()
            else "VALIDATION_BLOCKED"
        )
        payload = {"status": "PENDING", "reason_code": reason_code, "validation": report}
        raw = json.dumps(payload, sort_keys=True, default=str).encode()
        return _artifact("validate", payload, b"validation-blocked", raw)

    report = {**report, "source": "dhan_validate_lane", "date": report.get("date") or business_date}
    stored_day = backend.upsert_validation_day(report)
    output = json.dumps({"validation": report, "stored_day": stored_day}, sort_keys=True, default=str, separators=(",", ":")).encode()
    source = base64.b64decode(rank["output_bytes_b64"], validate=True)
    return _artifact("validate", {"status": "PASS", "validation": report, "stored_day": stored_day}, source, output)


def _run_rank_lane() -> Dict[str, Any]:
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

    from scripts.daily_gain_rank_and_validate import REPORT_DIR, run_ranking
    business_date, is_open_day, reason = _business_context("rank")
    if not is_open_day:
        status = "PENDING" if reason == "UNKNOWN_CALENDAR" else "SKIPPED"
        raw = json.dumps({"status": status, "reason_code": reason, "business_date": business_date}, sort_keys=True).encode()
        return _artifact("rank", {"status": status, "reason_code": reason}, b"exchange-calendar", raw)
    # Hard wall clock so Cloud Run never sits on hung broker/NSE fallbacks until task timeout.
    rank_deadline_s = int(os.environ.get("SYSTEM3_RANK_LANE_TIMEOUT_S", "480"))
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(run_ranking).result(timeout=rank_deadline_s)
    except FuturesTimeout:
        payload = {"status": "PENDING", "reason_code": "RANK_LANE_TIMEOUT", "business_date": business_date, "timeout_s": rank_deadline_s}
        raw = json.dumps(payload, sort_keys=True).encode()
        return _artifact("rank", payload, b"rank-lane-timeout", raw)
    summary_path = REPORT_DIR / "summary.json"
    ranked_path = REPORT_DIR / "ranked.json"
    if not summary_path.exists():
        payload = {"status": "PENDING", "reason_code": "RANK_SUMMARY_MISSING", "business_date": business_date}
        raw = json.dumps(payload, sort_keys=True).encode()
        return _artifact("rank", payload, b"missing-rank-summary", raw)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    rows = json.loads(ranked_path.read_text(encoding="utf-8")) if ranked_path.exists() else []
    if summary.get("status") != "PASS" or not rows:
        payload = {
            "status": "PENDING",
            "reason_code": "RANK_NOT_READY",
            "business_date": business_date,
            "summary": summary,
        }
        raw = json.dumps(payload, sort_keys=True, default=str).encode()
        return _artifact("rank", payload, b"rank-not-ready", raw)
    output = ranked_path.read_bytes()
    return _artifact("rank", {"summary": summary, "rows": rows}, output, output)


def _run_forecast_lane() -> Dict[str, Any]:
    from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend
    rank = FirestoreSchedulerEvidenceBackend().load_artifact("rank")
    business_date, is_open_day, reason = _business_context("forecast")
    if not is_open_day:
        status = "PENDING" if reason == "UNKNOWN_CALENDAR" else "SKIPPED"
        raw = json.dumps({"status": status, "reason_code": reason, "business_date": business_date}, sort_keys=True).encode()
        return _artifact("forecast", {"status": status, "reason_code": reason}, b"exchange-calendar", raw)
    if not rank or rank.get("business_date") != business_date or rank.get("status") != "PASS":
        raise RuntimeError("fresh durable rank artifact is required")
    rows = (rank.get("payload") or {}).get("rows") or []
    dependencies = [{"underlying": row.get("underlying"), "rank": row.get("rank"), "source_rank_sha256": rank.get("output_sha256")} for row in rows if row.get("underlying")]
    if not dependencies:
        raise RuntimeError("forecast lane received empty rank artifact")
    # Rank evidence is not a forecast. Persist dependency readiness truth until
    # a separately validated forecast model contract is introduced.
    payload = {"status": "PENDING", "reason_code": "VALIDATED_FORECAST_MODEL_NOT_CONFIGURED", "rank_dependencies": dependencies}
    output = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    source = base64.b64decode(rank["output_bytes_b64"], validate=True)
    if hashlib.sha256(source).hexdigest() != rank.get("output_sha256"):
        raise RuntimeError("durable rank dependency hash mismatch")
    return _artifact("forecast", payload, source, output)


def _run_signals_lane() -> Dict[str, Any]:
    from scripts.bhavcopy_downloader import _get_session, download_bhavcopy
    from scripts.run_signal_engine_from_bhavcopy import SIGNALS_CSV, _latest_bhavcopy, run
    business_date, is_open_day, reason = _business_context("signals")
    if not is_open_day:
        status = "PENDING" if reason == "UNKNOWN_CALENDAR" else "SKIPPED"
        raw = json.dumps({"status": status, "reason_code": reason, "business_date": business_date}, sort_keys=True).encode()
        return _artifact("signals", {"status": status, "reason_code": reason}, b"exchange-calendar", raw)
    today = date.fromisoformat(business_date)
    # NSE does not always have today's bhavcopy published at the exact
    # scheduled run time — observed the same URL 404 at run time and 200 a
    # short while later. Retry with a bounded wait instead of failing the
    # whole day's signal lane on a single early miss (job timeout is 600s).
    session = _get_session()
    download_status = "failed"
    max_attempts = 5
    retry_delay_s = 90
    for attempt in range(1, max_attempts + 1):
        download_status = download_bhavcopy(today, session)
        if download_status != "failed":
            break
        if attempt < max_attempts:
            print(
                f"[signals] bhavcopy not yet available (attempt {attempt}/{max_attempts}); "
                f"retrying in {retry_delay_s}s"
            )
            time.sleep(retry_delay_s)
    if download_status == "failed" or not run():
        raise RuntimeError("session-bound bhavcopy signal lane failed")
    payload = {"artifact": "storage/live/dhan_index_ai_signals.csv", "bytes": SIGNALS_CSV.stat().st_size}
    source_path = _latest_bhavcopy()
    if source_path is None:
        raise RuntimeError("session bhavcopy source missing after download")
    return _artifact("signals", payload, source_path.read_bytes(), SIGNALS_CSV.read_bytes())


def _run_ml_history_bootstrap() -> Dict[str, Any]:
    """Cloud-only historical Spearman seed (replaces laptop smoke --write-firestore)."""
    if not _truthy(os.environ.get("SYSTEM3_ALLOW_ML_HISTORY_BOOTSTRAP", "0")):
        raise RuntimeError("ml-history-bootstrap requires SYSTEM3_ALLOW_ML_HISTORY_BOOTSTRAP=1")
    from scripts.smoke_ml_validate_e2e import _hist_days, _write_firestore

    days = _hist_days()
    for day in days:
        day["source"] = "cloud_ml_history_bootstrap"
    written = _write_firestore(days)
    return {
        "status": "PASS",
        "writes": len(written),
        "dates": [row.get("date") for row in written],
        "source": "cloud_ml_history_bootstrap",
        "live_trading_enabled": False,
    }


def _log_structured(event: str, **fields: Any) -> None:
    """Cloud Logging–friendly JSON line (severity + execution kind as trace)."""
    payload = {
        "severity": str(fields.pop("severity", "INFO")),
        "message": event,
        "event": event,
        "system3_job_kind": os.environ.get("SYSTEM3_JOB_KIND"),
        "cloud_run_execution": os.environ.get("CLOUD_RUN_EXECUTION"),
        "cloud_run_job": os.environ.get("CLOUD_RUN_JOB"),
        "deploy_git_sha": os.environ.get("DEPLOY_GIT_SHA") or os.environ.get("SYSTEM3_GIT_SHA"),
        "live_trading_enabled": False,
        **fields,
    }
    print(json.dumps(payload, sort_keys=True, default=str), flush=True)


def _run_control_plane_verify() -> Dict[str, Any]:
    """Upstream/downstream cloud proof: public health API must match SSOT contract."""
    import urllib.error
    import urllib.request

    base = (os.environ.get("SYSTEM3_SERVICE_URL") or "").strip().rstrip("/")
    if not base:
        raise RuntimeError("SYSTEM3_SERVICE_URL is required for control-plane-verify")
    pass_no = int(os.environ.get("SYSTEM3_VERIFY_PASS", "1") or "1")
    url = f"{base}/api/scheduler/health?refresh=true"
    req = urllib.request.Request(url, headers={"User-Agent": "genesis-system3-control-plane-verify"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            http_status = int(getattr(resp, "status", 200) or 200)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"scheduler health HTTP {exc.code}") from exc
    except Exception as exc:
        raise RuntimeError(f"scheduler health unreachable: {type(exc).__name__}") from exc

    coverage = body.get("coverage") if isinstance(body.get("coverage"), dict) else {}
    observability = body.get("observability") if isinstance(body.get("observability"), dict) else {}
    checks = {
        "http_ok": http_status == 200,
        "healthy": body.get("healthy") is True,
        "contract_matched": coverage.get("contract_matched") is True,
        "total_nine": coverage.get("total") == 9 and coverage.get("expected_total") == 9,
        "live_off": body.get("live_trading_enabled") is not True,
        "alert_none": observability.get("alert_severity") in {None, "none"},
    }
    ok = all(checks.values())
    result = {
        "status": "PASS" if ok else "FAIL",
        "pass_number": pass_no,
        "service_url": base,
        "checks": checks,
        "evidence_version": body.get("evidence_version"),
        "coverage": {
            "total": coverage.get("total"),
            "enabled": coverage.get("enabled"),
            "paused": coverage.get("paused"),
            "contract_matched": coverage.get("contract_matched"),
        },
        "observability": observability,
        "deploy_git_sha": body.get("deploy_git_sha") or os.environ.get("DEPLOY_GIT_SHA"),
        "live_trading_enabled": False,
    }
    if not ok:
        raise RuntimeError(f"control-plane-verify failed pass={pass_no} checks={checks}")
    return result


def run_job(kind: Optional[str] = None) -> Dict[str, Any]:
    _assert_analyzer_only()
    kind = (kind or os.environ.get("SYSTEM3_JOB_KIND", "smoke")).strip().lower()
    result = _base_result(kind)

    if kind == "smoke":
        result["detail"] = "Analyzer-only bounded worker smoke test"
    elif kind == "scheduler-collector":
        result["scheduler_evidence"] = _run_scheduler_collector()
        result["detail"] = "One fenced raw scheduler control-plane collection completed"
    elif kind == "rank":
        result["business_artifact"] = _run_rank_lane()
    elif kind == "validate":
        result["business_artifact"] = _run_validate_lane()
    elif kind == "forecast":
        result["business_artifact"] = _run_forecast_lane()
    elif kind == "signals":
        result["business_artifact"] = _run_signals_lane()
    elif kind == "ml-history-bootstrap":
        result["ml_history_bootstrap"] = _run_ml_history_bootstrap()
        result["detail"] = "Cloud Firestore historical Spearman days upserted"
    elif kind == "control-plane-verify":
        result["control_plane_verify"] = _run_control_plane_verify()
        result["detail"] = "Upstream/downstream scheduler health contract verified"
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
    kind = (os.environ.get("SYSTEM3_JOB_KIND", "smoke") or "smoke").strip().lower()
    _log_structured("job_start", severity="INFO", kind=kind)
    try:
        result = run_job(kind)
        _log_structured(
            "job_complete",
            severity="INFO",
            kind=kind,
            status=result.get("status"),
            detail=result.get("detail"),
        )
        print(json.dumps(result, sort_keys=True, default=str))
        return 0
    except Exception as exc:
        _log_structured("job_fail", severity="ERROR", kind=kind, error=str(exc))
        print(json.dumps({"status": "FAIL", "error": str(exc), "live_trading_enabled": False}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
