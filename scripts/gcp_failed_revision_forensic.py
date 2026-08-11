#!/usr/bin/env python3
"""Capture secret-safe Cloud Run failed-revision startup evidence.

This diagnostic intentionally reads metadata and logs only. It never accesses a
Secret Manager payload, never mutates Cloud Run, and never calls broker order
endpoints. Raw log entries are not persisted; only redacted message fragments,
revision conditions, image identity, and traffic metadata are written.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("PROJECT_ID") or "system3-openalgo-safe"
REGION = os.environ.get("GCP_REGION") or os.environ.get("REGION") or "asia-south1"
SERVICE = os.environ.get("GCP_CLOUD_RUN_SERVICE") or os.environ.get("SERVICE") or "genesis-system3-web"
REVISION = os.environ.get("FAILED_REVISION", "").strip()
OUT = Path("reports/latest/gcp_failed_revision_forensic")

_SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+"),
    re.compile(r"(?i)((?:api[_-]?key|access[_-]?token|refresh[_-]?token|totp|pin|password|secret)\s*[:=]\s*)[^\s,;]+"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{8,}\b"),
)


def _run(args: list[str]) -> str:
    proc = subprocess.run(args, text=True, capture_output=True, check=False)
    if proc.returncode:
        raise RuntimeError(f"command failed rc={proc.returncode}: {' '.join(args[:5])}")
    return proc.stdout


def _redact(value: Any, limit: int = 700) -> str:
    text = str(value or "").replace("\x00", " ")
    for pattern in _SECRET_PATTERNS:
        if pattern.groups:
            text = pattern.sub(r"\1<redacted>", text)
        else:
            text = pattern.sub("<redacted-jwt>", text)
    text = " ".join(text.split())
    return text[:limit]


def _message(entry: dict[str, Any]) -> str:
    if entry.get("textPayload"):
        raw = entry.get("textPayload")
        # Tracebacks need enough sanitized context to retain the terminal
        # exception line; ordinary messages remain tightly bounded.
        limit = 5000 if "traceback" in str(raw).lower() else 700
        return _redact(raw, limit)
    payload = entry.get("jsonPayload") or {}
    if isinstance(payload, dict):
        for key in ("message", "msg", "error", "exception", "detail"):
            if payload.get(key):
                raw = payload.get(key)
                limit = 5000 if "traceback" in str(raw).lower() else 700
                return _redact(raw, limit)
    proto = entry.get("protoPayload") or {}
    if isinstance(proto, dict):
        status = proto.get("status") or {}
        if isinstance(status, dict) and status.get("message"):
            return _redact(status.get("message"))
    return ""


def _condition_rows(revision: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for c in ((revision.get("status") or {}).get("conditions") or []):
        rows.append(
            {
                "type": c.get("type"),
                "status": c.get("status"),
                "reason": c.get("reason"),
                "message": _redact(c.get("message")),
                "last_transition_time": c.get("lastTransitionTime"),
            }
        )
    return rows


def _container_image(revision: dict[str, Any]) -> str | None:
    containers = ((revision.get("spec") or {}).get("containers") or [])
    if not containers:
        containers = ((((revision.get("spec") or {}).get("template") or {}).get("spec") or {}).get("containers") or [])
    return str((containers[0] if containers else {}).get("image") or "") or None


def main() -> int:
    global REVISION
    service = json.loads(
        _run(
            [
                "gcloud", "run", "services", "describe", SERVICE,
                f"--project={PROJECT}", f"--region={REGION}", "--format=json",
            ]
        )
    )
    status = service.get("status") or {}
    if not REVISION:
        REVISION = str(status.get("latestCreatedRevisionName") or status.get("latestReadyRevisionName") or "")
    if not REVISION:
        raise SystemExit("FAILED_REVISION_FORENSIC_NO_REVISION")

    revision = json.loads(
        _run(
            [
                "gcloud", "run", "revisions", "describe", REVISION,
                f"--project={PROJECT}", f"--region={REGION}", "--format=json",
            ]
        )
    )

    log_filter = (
        'resource.type="cloud_run_revision" '
        f'AND resource.labels.service_name="{SERVICE}" '
        f'AND resource.labels.revision_name="{REVISION}"'
    )
    logs = json.loads(
        _run(
            [
                "gcloud", "logging", "read", log_filter,
                f"--project={PROJECT}", "--limit=300", "--order=asc", "--format=json",
            ]
        )
        or "[]"
    )

    selected: list[dict[str, Any]] = []
    signatures: dict[str, int] = {}
    markers = {
        "python_traceback": ("traceback",),
        "import_error": ("modulenotfounderror", "importerror"),
        "memory_error": ("memoryerror", "out of memory", "oom", "memory limit"),
        "startup_port": ("failed to start", "listen on", "port 8080", "startup probe"),
        "permission_error": ("permissiondenied", "permission denied", "403"),
        "secret_manager": ("secret manager", "secretmanager", "access_secret_version"),
        "firestore": ("firestore", "google.cloud.firestore"),
        "instrument_warmup": ("instrument", "scrip master", "warm-up", "warmup"),
        "process_exit": ("process exited", "exit code", "sigkill", "killed"),
    }
    for entry in logs:
        message = _message(entry)
        if not message:
            continue
        blob = message.lower()
        severity = str(entry.get("severity") or "DEFAULT")
        hit = False
        for name, terms in markers.items():
            if any(term in blob for term in terms):
                signatures[name] = signatures.get(name, 0) + 1
                hit = True
        if severity in {"ERROR", "CRITICAL", "ALERT", "EMERGENCY"}:
            hit = True
        if "[cloud-start]" in blob or "[cloud-bootstrap]" in blob or "uvicorn" in blob:
            hit = True
        if hit:
            selected.append(
                {
                    "timestamp": entry.get("timestamp") or entry.get("receiveTimestamp"),
                    "severity": severity,
                    "message": message,
                }
            )

    traffic = []
    for item in (status.get("traffic") or []):
        if item.get("revisionName") == REVISION or item.get("tag") == "candidate":
            traffic.append(
                {
                    "revision_name": item.get("revisionName"),
                    "percent": int(item.get("percent") or 0),
                    "tag": item.get("tag"),
                    "url_present": bool(item.get("url")),
                }
            )

    report = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project": PROJECT,
        "region": REGION,
        "service": SERVICE,
        "revision": REVISION,
        "service_latest_created_revision": status.get("latestCreatedRevisionName"),
        "service_latest_ready_revision": status.get("latestReadyRevisionName"),
        "revision_image": _container_image(revision),
        "revision_conditions": _condition_rows(revision),
        "candidate_traffic": traffic,
        "log_entries_examined": len(logs),
        "diagnostic_signature_counts": dict(sorted(signatures.items())),
        "selected_sanitized_entries": selected[-80:],
        "raw_log_payloads_persisted": False,
        "secret_payloads_accessed": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "forensic.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md = [
        "# Cloud Run Failed Revision Forensic",
        "",
        f"- Revision: `{REVISION}`",
        f"- Latest created: `{status.get('latestCreatedRevisionName')}`",
        f"- Latest ready: `{status.get('latestReadyRevisionName')}`",
        f"- Log entries examined: `{len(logs)}`",
        f"- Signatures: `{json.dumps(report['diagnostic_signature_counts'], sort_keys=True)}`",
        "- Raw log payloads persisted: `False`",
        "- Secret payloads accessed: `False`",
        "- LIVE trading enabled: `False`",
        "",
        "## Revision conditions",
    ]
    for row in report["revision_conditions"]:
        md.append(f"- `{row['type']}` status=`{row['status']}` reason=`{row['reason']}` message={row['message']}")
    md += ["", "## Sanitized startup/error entries"]
    for row in report["selected_sanitized_entries"]:
        md.append(f"- `{row['timestamp']}` `{row['severity']}` {row['message']}")
    (OUT / "forensic.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(
        "FAILED_REVISION_FORENSIC "
        + json.dumps(
            {
                "revision": REVISION,
                "latest_created": status.get("latestCreatedRevisionName"),
                "latest_ready": status.get("latestReadyRevisionName"),
                "conditions": report["revision_conditions"],
                "traffic": traffic,
                "log_entries_examined": len(logs),
                "signatures": report["diagnostic_signature_counts"],
                "selected_entry_count": len(report["selected_sanitized_entries"]),
                "secret_payloads_accessed": False,
            },
            sort_keys=True,
        )
    )
    for row in report["selected_sanitized_entries"][-30:]:
        print("FORENSIC_LOG " + json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
