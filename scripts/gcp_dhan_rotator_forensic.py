#!/usr/bin/env python3
"""Read-only forensic classification for one Dhan Cloud Run Job execution.

The script describes one execution, reads only execution-scoped Cloud Logging
entries, extracts allow-listed rotator status markers, and snapshots the public
broker status. It never reads Secret Manager payloads and never runs the job.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.getenv("GCP_REGION", "asia-south1")
JOB = os.getenv("DHAN_ROTATION_JOB", "genesis-system3-dhan-token-rotate")
SERVICE = os.getenv("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
OUT = Path("reports/latest/dhan_rotator_forensics")

_SECRET_KEY = re.compile(r"(?i)(token|secret|password|passwd|pin|totp|authorization|api[_-]?key|cookie)")
_BEARER = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+\-/]+=*")
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")

_STATUS_CLASS = {
    "ROTATED_AND_VERIFIED": "ROTATION_SUCCESS",
    "ROTATION_FAILED": "MINT_PATH_FAILED_UNCLASSIFIED",
    "SKIPPED_CONCURRENT_ROTATION_WON": "CONCURRENT_ROTATION_ALREADY_HEALED",
    "SKIPPED_TOKEN_HEALTHY": "TOKEN_HEALTHY_NO_ROTATION",
    "SKIPPED_TOKEN_HEALTHY_AFTER_STAGGER": "TOKEN_HEALTHY_AFTER_COORDINATION",
    "BLOCKED_TRANSIENT_PROFILE_ERROR": "TRANSIENT_PROFILE_FAILURE_NO_MINT",
    "BLOCKED_PROFILE_CONFIG_ERROR": "CREDENTIAL_CONFIGURATION_FAILURE_NO_MINT",
    "BLOCKED_STAGGER_REVALIDATION_ERROR": "TRANSIENT_REVALIDATION_FAILURE_NO_MINT",
    "BLOCKED_MINT_NOT_AUTHORIZED": "MINT_AUTHORITY_REVOKED_NO_MINT",
}


def _run(*args: str, timeout: int = 90) -> tuple[int, str]:
    proc = subprocess.run(list(args), text=True, capture_output=True, timeout=timeout, check=False)
    return proc.returncode, proc.stdout or ""


def _json_command(*args: str, timeout: int = 90) -> tuple[Any | None, str | None]:
    rc, out = _run(*args, timeout=timeout)
    if rc:
        return None, f"command_failed_rc_{rc}"
    try:
        return json.loads(out or "null"), None
    except Exception as exc:
        return None, f"json_decode_{type(exc).__name__}"


def _latest_execution() -> str:
    rc, out = _run(
        "gcloud", "run", "jobs", "executions", "list",
        f"--job={JOB}", f"--project={PROJECT}", f"--region={REGION}",
        "--limit=1", "--sort-by=~metadata.creationTimestamp", "--format=value(metadata.name)",
    )
    return out.strip() if rc == 0 else ""


def _redact(value: Any, key: str = "") -> Any:
    if _SECRET_KEY.search(key):
        if key.lower() in {"secret_version", "secretversion", "secret_id", "secretid", "token_source"}:
            return value
        return "<redacted>"
    if isinstance(value, dict):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, str):
        clean = _BEARER.sub("Bearer <redacted>", value)
        clean = _JWT.sub("<jwt-redacted>", clean)
        return clean[:1000]
    return value


def _strings(value: Any):
    if isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, str):
        yield value


def _status_evidence(logs: list[Any]) -> tuple[list[str], str, str]:
    matched: list[str] = []
    observed: list[str] = []
    for text in _strings(logs):
        for status in _STATUS_CLASS:
            if status in text:
                observed.append(status)
                safe = str(_redact(text))[:500]
                if safe not in matched and len(matched) < 20:
                    matched.append(safe)
    status = observed[-1] if observed else "STATUS_MARKER_NOT_FOUND"
    classification = _STATUS_CLASS.get(status, "NOT_CLASSIFIED_FROM_SAFE_STATUS")
    return matched, status, classification


def _execution_summary(raw: dict[str, Any]) -> dict[str, Any]:
    meta = raw.get("metadata") or {}
    status = raw.get("status") or {}
    conditions = []
    for row in status.get("conditions") or []:
        if isinstance(row, dict):
            conditions.append({
                "type": row.get("type"),
                "status": row.get("status"),
                "reason": row.get("reason"),
                "message": _redact(row.get("message") or ""),
                "lastTransitionTime": row.get("lastTransitionTime"),
            })
    return {
        "name": meta.get("name"),
        "creationTimestamp": meta.get("creationTimestamp"),
        "completionTime": status.get("completionTime"),
        "startTime": status.get("startTime"),
        "failedCount": status.get("failedCount"),
        "succeededCount": status.get("succeededCount"),
        "conditions": conditions,
        "creator": (meta.get("annotations") or {}).get("run.googleapis.com/creator"),
    }


def _broker_snapshot() -> dict[str, Any]:
    service, err = _json_command(
        "gcloud", "run", "services", "describe", SERVICE,
        f"--project={PROJECT}", f"--region={REGION}", "--format=json",
    )
    if err or not isinstance(service, dict):
        return {"state": "NOT_PROVEN", "error": err}
    url = str(((service.get("status") or {}).get("url")) or service.get("uri") or "").rstrip("/")
    if not url.startswith("https://"):
        return {"state": "NOT_PROVEN", "error": "service_url_missing"}
    try:
        response = requests.get(f"{url}/api/broker/status", timeout=20)
        data = response.json() if "application/json" in response.headers.get("content-type", "").lower() else {}
    except Exception as exc:
        return {"state": "NOT_PROVEN", "error": type(exc).__name__}
    proof = (data.get("token_proof") or {}) if isinstance(data, dict) else {}
    return {
        "http_status": response.status_code,
        "connected": bool(data.get("connected")) if isinstance(data, dict) else None,
        "error": str(data.get("error") or "")[:120] if isinstance(data, dict) else None,
        "token_source": proof.get("source"),
        "secret_version": proof.get("secret_version"),
        "expires_at_utc": proof.get("expires_at_utc"),
        "hours_remaining": proof.get("hours_remaining"),
        "expired": proof.get("expired"),
        "token_value_exposed": bool(proof.get("token_value_exposed")),
        "live_trading_enabled": bool(data.get("live_trading_enabled")) if isinstance(data, dict) else None,
        "order_placement_allowed": bool(data.get("order_placement_allowed")) if isinstance(data, dict) else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution", default="")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    execution = args.execution.strip() or _latest_execution()
    if not execution:
        report = {"state": "NOT_PROVEN", "reason": "execution_name_missing", "secret_payloads_accessed": False}
        (OUT / "rotator_forensic.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return 2

    raw, describe_error = _json_command(
        "gcloud", "run", "jobs", "executions", "describe", execution,
        f"--project={PROJECT}", f"--region={REGION}", "--format=json",
    )
    log_filter = f'labels.execution_name="{execution}"'
    logs, logs_error = _json_command(
        "gcloud", "run", "jobs", "logs", "read", JOB,
        f"--project={PROJECT}", f"--region={REGION}", "--freshness=7d",
        f"--log-filter={log_filter}", "--limit=300", "--order=asc", "--format=json",
        timeout=120,
    )

    safe_logs = _redact(logs if isinstance(logs, list) else [])
    status_lines, safe_status, classification = _status_evidence(safe_logs)
    summary = _execution_summary(raw) if isinstance(raw, dict) else {"name": execution}
    broker = _broker_snapshot()
    failed = bool(summary.get("failedCount"))

    report = {
        "schema": "genesis-system3-dhan-rotator-forensic-v2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "state": "FAIL" if failed else "PASS",
        "project": PROJECT,
        "region": REGION,
        "job": JOB,
        "execution": execution,
        "execution_summary": summary,
        "describe_error": describe_error,
        "logs_error": logs_error,
        "log_entry_count": len(safe_logs),
        "safe_status": safe_status,
        "failure_classification": classification,
        "status_evidence": status_lines,
        "broker_after_execution": broker,
        "secret_payloads_accessed": False,
        "secret_values_exposed": False,
        "job_execution_triggered": False,
        "order_actions_performed": False,
        "live_trading_enabled": False,
    }
    (OUT / "rotator_forensic.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print("DHAN_ROTATOR_FORENSIC", json.dumps({
        "state": report["state"],
        "execution": execution,
        "safe_status": safe_status,
        "classification": classification,
        "broker_connected": broker.get("connected"),
        "secret_version": broker.get("secret_version"),
        "job_execution_triggered": False,
        "secret_payloads_accessed": False,
    }, sort_keys=True))
    return 0 if describe_error is None and logs_error is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
