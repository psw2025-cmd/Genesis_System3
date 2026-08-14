#!/usr/bin/env python3
"""Capture sanitized forensic evidence for one Dhan Cloud Run Job execution.

Read-only only: describes execution/job, reads execution-scoped Cloud Logging
entries, and snapshots the public broker status. Secret payloads are never read.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
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


def _run(*args: str, timeout: int = 90, allow_fail: bool = False) -> tuple[int, str, str]:
    proc = subprocess.run(list(args), text=True, capture_output=True, timeout=timeout, check=False)
    if proc.returncode and not allow_fail:
        raise RuntimeError(f"command_failed:{args[0]}:{proc.returncode}:{proc.stderr[:160]}")
    return proc.returncode, proc.stdout, proc.stderr


def _json_command(*args: str, timeout: int = 90, allow_fail: bool = False) -> tuple[Any | None, str | None]:
    rc, out, err = _run(*args, timeout=timeout, allow_fail=True)
    if rc:
        if allow_fail:
            return None, f"rc={rc}:{err[:180]}"
        raise RuntimeError(f"command_failed:{args[0]}:{rc}:{err[:160]}")
    try:
        return json.loads(out or "null"), None
    except Exception as exc:
        return None, f"json_decode:{type(exc).__name__}:{str(exc)[:120]}"


def _latest_execution() -> str:
    rc, out, _ = _run(
        "gcloud", "run", "jobs", "executions", "list",
        f"--job={JOB}", f"--project={PROJECT}", f"--region={REGION}",
        "--limit=1", "--sort-by=~metadata.creationTimestamp", "--format=value(metadata.name)",
        allow_fail=True,
    )
    return out.strip() if rc == 0 else ""


def _redact(value: Any, key: str = "") -> Any:
    if _SECRET_KEY.search(key):
        # Metadata names are allowed; values are not.
        if key.lower() in {"secret_version", "secretversion", "secret_id", "secretid", "token_source"}:
            return value
        return "<redacted>"
    if isinstance(value, dict):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, str):
        value = _BEARER.sub("Bearer <redacted>", value)
        value = _JWT.sub("<jwt-redacted>", value)
        return value[:4000]
    return value


def _execution_summary(raw: dict[str, Any]) -> dict[str, Any]:
    meta = raw.get("metadata") or {}
    status = raw.get("status") or {}
    spec = raw.get("spec") or {}
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
        "runningCount": status.get("runningCount"),
        "cancelledCount": status.get("cancelledCount"),
        "conditions": conditions,
        "taskCount": spec.get("taskCount"),
        "parallelism": spec.get("parallelism"),
        "creator": (meta.get("annotations") or {}).get("run.googleapis.com/creator"),
    }


def _broker_snapshot() -> dict[str, Any]:
    service, err = _json_command(
        "gcloud", "run", "services", "describe", SERVICE,
        f"--project={PROJECT}", f"--region={REGION}", "--format=json", allow_fail=True,
    )
    if err or not isinstance(service, dict):
        return {"state": "NOT_PROVEN", "error": err}
    url = str(((service.get("status") or {}).get("url")) or service.get("uri") or "").rstrip("/")
    if not url.startswith("https://"):
        return {"state": "NOT_PROVEN", "error": "service_url_missing"}
    try:
        r = requests.get(f"{url}/api/broker/status", timeout=30)
        data = r.json() if r.headers.get("content-type", "").lower().startswith("application/json") else {}
    except Exception as exc:
        return {"state": "NOT_PROVEN", "error": f"{type(exc).__name__}:{str(exc)[:120]}"}
    proof = data.get("token_proof") or {} if isinstance(data, dict) else {}
    return {
        "state": "PASS" if r.status_code == 200 else "FAIL",
        "http_status": r.status_code,
        "connected": bool(data.get("connected")) if isinstance(data, dict) else None,
        "error_present": bool(data.get("error")) if isinstance(data, dict) else None,
        "token_source": proof.get("source"),
        "secret_version": proof.get("secret_version"),
        "token_value_exposed": bool(proof.get("token_value_exposed")),
        "live_trading_enabled": bool(data.get("live_trading_enabled")) if isinstance(data, dict) else None,
        "order_placement_allowed": bool(data.get("order_placement_allowed")) if isinstance(data, dict) else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execution", default="")
    ap.add_argument("--trigger-rc", type=int, default=0)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    execution = args.execution.strip() or _latest_execution()
    if not execution:
        report = {"state": "NOT_PROVEN", "reason": "execution_name_missing", "secret_payloads_accessed": False}
        (OUT / "rotator_forensic.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return 2

    raw, describe_err = _json_command(
        "gcloud", "run", "jobs", "executions", "describe", execution,
        f"--project={PROJECT}", f"--region={REGION}", "--format=json", allow_fail=True,
    )
    log_filter = f'labels.execution_name="{execution}"'
    logs, logs_err = _json_command(
        "gcloud", "run", "jobs", "logs", "read", JOB,
        f"--project={PROJECT}", f"--region={REGION}", "--freshness=7d",
        f"--log-filter={log_filter}", "--limit=300", "--order=asc", "--format=json",
        timeout=120, allow_fail=True,
    )
    summary = _execution_summary(raw) if isinstance(raw, dict) else {"name": execution}
    safe_logs = _redact(logs if isinstance(logs, list) else [])
    broker = _broker_snapshot()
    failed = bool(summary.get("failedCount")) or any(
        str(c.get("status")).lower() == "false" for c in summary.get("conditions") or []
        if c.get("type") in {"Completed", "Ready"}
    )
    report = {
        "schema": "genesis-system3-dhan-rotator-forensic-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "state": "FAIL" if failed or args.trigger_rc else "PASS",
        "project": PROJECT,
        "region": REGION,
        "job": JOB,
        "execution": execution,
        "trigger_return_code": args.trigger_rc,
        "execution_summary": summary,
        "describe_error": describe_err,
        "logs_error": logs_err,
        "log_entry_count": len(safe_logs),
        "logs": safe_logs,
        "broker_after_execution": broker,
        "secret_payloads_accessed": False,
        "secret_values_exposed": False,
        "order_actions_performed": False,
        "live_trading_enabled": False,
    }
    (OUT / "rotator_forensic.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md = [
        "# Dhan Rotator Execution Forensics", "",
        f"- Execution: `{execution}`", f"- State: **{report['state']}**",
        f"- Trigger return code: `{args.trigger_rc}`",
        f"- Failed tasks: `{summary.get('failedCount')}`; succeeded: `{summary.get('succeededCount')}`",
        f"- Log entries captured: `{len(safe_logs)}`",
        f"- Broker connected after execution: `{broker.get('connected')}`",
        f"- Broker token Secret Manager version: `{broker.get('secret_version')}`",
        "- Secret payloads accessed: **false**", "- Order actions performed: **false**", "- LIVE enabled: **false**", "",
    ]
    (OUT / "rotator_forensic.md").write_text("\n".join(md), encoding="utf-8")
    print("DHAN_ROTATOR_FORENSIC " + json.dumps({
        "state": report["state"], "execution": execution, "logs": len(safe_logs),
        "broker_connected": broker.get("connected"), "secret_version": broker.get("secret_version"),
    }, sort_keys=True))
    return 0 if describe_err is None and logs_err is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
