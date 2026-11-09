"""Read-only canonical Dhan authority audit for trusted GitHub WIF runs.

Never fetches any Secret Manager payload, runs the rotator, or posts broker
orders. Only allow-listed metadata is emitted; all errors fail closed.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT = "system3-openalgo-safe"
REGION = "asia-south1"
SERVICE = "genesis-system3-web"
ROTATOR = "genesis-system3-dhan-token-rotate"
ROTATE_SCHEDULE = "genesis-system3-dhan-token-rotate-daily"
CANONICAL = "dhan-access-token"


def _safe_name(value: Any) -> str:
    text = str(value or "")
    return text if re.fullmatch(r"[A-Za-z0-9_.:/-]{1,150}", text) else "NOT_VERIFIED"


def _gcloud_json(args: list[str]) -> tuple[Any, str]:
    """Never echo command stderr/stdout; cloud JSON may contain secrets."""
    try:
        proc = subprocess.run(
            ["gcloud", *args, f"--project={PROJECT}", "--format=json"],
            capture_output=True, text=True, timeout=24, check=False,
            env={**os.environ, "PYTHONPATH": ""},
        )
        if proc.returncode:
            return None, "DENIED_OR_UNAVAILABLE"
        return json.loads(proc.stdout), "PASS"
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None, "UNAVAILABLE"


def _status_code(value: Any) -> str:
    return str(value) if type(value) is int and 0 <= value <= 20 else "UNREPORTED"


def _executable_metadata(job: dict[str, Any]) -> dict[str, Any]:
    template = (job.get("spec") or {}).get("template") or job.get("template") or {}
    task_template = template.get("spec") or template.get("template") or {}
    nested = task_template.get("template") or {}
    spec = nested.get("spec") or task_template.get("spec") or task_template
    containers = spec.get("containers") or []
    first = containers[0] if len(containers) == 1 else {}
    image = str(first.get("image") or "")
    env = first.get("env") or []
    names = {str(e.get("name") or "") for e in env if isinstance(e, dict)}
    return {
        "single_container": len(containers) == 1,
        "image_present": bool(image),
        "image_digest_pinned": bool(re.search(r"@sha256:[0-9a-f]{64}$", image)),
        "command_configured": bool(first.get("command") or first.get("args")),
        "client_id_binding_present": "DHAN_CLIENT_ID" in names,
        "paper_mode_configured": "PAPER_MODE" in names,
    }


def _runtime_token_source(service: dict[str, Any]) -> dict[str, Any]:
    template = (service.get("spec") or {}).get("template") or service.get("template") or {}
    containers = (template.get("spec") or {}).get("containers") or template.get("containers") or []
    env_list = containers[0].get("env") or [] if len(containers) == 1 else []
    env = {x.get("name"): x for x in env_list if isinstance(x, dict)}
    token = env.get("DHAN_ACCESS_TOKEN") or {}
    source = str((env.get("DHAN_TOKEN_SOURCE") or {}).get("value") or "").lower()
    sid = str((env.get("DHAN_ACCESS_TOKEN_SECRET_ID") or {}).get("value") or "")
    # Broker-status GET may invoke configured auth self-heal/renewal in the
    # deployed application. Avoid that endpoint unless BOTH mechanisms are
    # explicitly off (or absent with fail-closed cloud defaults).
    def inactive(name: str) -> bool:
        setting = env.get(name)
        if setting is None:
            return True  # cloud defaults are OFF
        raw = setting.get("value")
        return raw is not None and str(raw).strip().lower() in (
            "", "0", "false", "no", "off",
        )

    return {
        "broker_status_get_without_autoheal": (
            inactive("DHAN_STATUS_AUTO_REFRESH")
            and inactive("DHAN_CANONICAL_ROTATION_SELF_HEAL")
        ),
        "service_revision": _safe_name((service.get("status") or {}).get("latestReadyRevisionName")),
        "canonical_secret_id": "CANONICAL" if sid == CANONICAL else "DEFAULT_OR_OTHER",
        "token_provider_mode": ("SECRET_MANAGER" if source in ("gcp", "gcp-secret-manager", "gcp-secret-manager-dynamic", "secret-manager") else "AUTO_OR_OTHER"),
        "static_token_value_configured": bool(token.get("value")),
        "token_secret_reference_configured": bool(token.get("valueFrom") or token.get("valueSource")),
    }


def _broker_summary(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"json_shape": "UNEXPECTED"}
    result: dict[str, Any] = {"json_shape": "OBJECT"}
    conn = payload.get("connected")
    result["connected"] = conn if type(conn) is bool else "UNREPORTED"
    error = payload.get("error")
    result["error_present"] = bool(error)
    cls = str(payload.get("auth_classification") or "").upper()
    result["auth_classification"] = cls if cls in {
        "AUTH_OK", "AUTH_FAILED", "TOKEN_EXPIRED_OR_INVALID", "AUTH_NOT_VERIFIED",
        "NOT_VERIFIED", "BLOCKED", "DISCONNECTED",
    } else "UNREPORTED"
    source = str(payload.get("source") or "").upper()
    result["source"] = source if source in {
        "GCP_SECRET_MANAGER_DYNAMIC", "ENVIRONMENT_FALLBACK", "SDK",
        "REST", "SNAPSHOT", "NOT_VERIFIED",
    } else "UNREPORTED"
    return result


def _production_broker_status(service: dict[str, Any]) -> dict[str, Any]:
    url = str((service.get("status") or {}).get("url") or "").rstrip("/")
    if not re.fullmatch(r"https://[a-z0-9-]+\.a\.run\.app", url):
        return {"http_status": "URL_NOT_VERIFIED"}
    token = ""
    try:
        auth = subprocess.run(
            ["gcloud", "auth", "print-identity-token", "--audiences=" + url],
            capture_output=True, text=True, timeout=12, check=False,
            env={**os.environ, "PYTHONPATH": ""},
        )
        if auth.returncode == 0:
            token = auth.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(url + "/api/broker/status", method="GET", headers=headers)
    try:
        with urlopen(request, timeout=12) as r:
            data = r.read(100_001)
            if len(data) > 100_000:
                return {"http_status": "OVERSIZED"}
            return {"http_status": r.status, **_broker_summary(json.loads(data))}
    except HTTPError as exc:
        return {"http_status": exc.code}
    except (URLError, TimeoutError, ValueError, OSError):
        return {"http_status": "NO_HTTP_RESPONSE"}


def audit() -> dict[str, Any]:
    report: dict[str, Any] = {"scope": "READ_ONLY_NO_TOKEN_PAYLOAD_NO_ORDERS"}
    service, ok = _gcloud_json(["run", "services", "describe", SERVICE, f"--region={REGION}"])
    report["service_read"] = ok
    if isinstance(service, dict):
        runtime = _runtime_token_source(service)
        report["runtime"] = runtime
        if runtime["broker_status_get_without_autoheal"]:
            report["production_broker"] = _production_broker_status(service)
        else:
            report["production_broker"] = {
                "http_status": "NOT_PROBED_AUTOHEAL_MAY_ROTATE_TOKEN"
            }
    job, ok = _gcloud_json(["run", "jobs", "describe", ROTATOR, f"--region={REGION}"])
    report["rotation_job_read"] = ok
    if isinstance(job, dict):
        report["rotation_job"] = _executable_metadata(job)
    executions, ok = _gcloud_json([
        "run", "jobs", "executions", "list", "--job=" + ROTATOR,
        f"--region={REGION}", "--limit=3"
    ])
    report["rotation_executions_read"] = ok
    if isinstance(executions, list):
        report["recent_rotation_executions"] = []
        for row in executions[:3]:
            if not isinstance(row, dict):
                continue
            status = row.get("status") or {}
            conditions = status.get("conditions") or []
            completed = next(
                (c.get("status") for c in conditions if c.get("type") == "Completed"), None
            )
            report["recent_rotation_executions"].append({
                "completed": completed if completed in ("True", "False", "Unknown") else "UNREPORTED",
                "succeeded_count": int(status.get("succeededCount") or 0),
                "failed_count": int(status.get("failedCount") or 0),
                "completion_time": _safe_name(status.get("completionTime")),
            })
    scheduler, ok = _gcloud_json([
        "scheduler", "jobs", "describe", ROTATE_SCHEDULE, f"--location={REGION}"
    ])
    report["rotation_scheduler_read"] = ok
    if isinstance(scheduler, dict):
        report["rotation_scheduler"] = {
            "state": _safe_name(scheduler.get("state")),
            "last_attempt": _safe_name(scheduler.get("lastAttemptTime")),
            "delivery_code": _status_code((scheduler.get("status") or {}).get("code")),
            "target_is_run_api": str((scheduler.get("httpTarget") or {}).get("uri") or "").startswith(
                "https://run.googleapis.com/v2/projects/"
            ),
        }
    versions, ok = _gcloud_json([
        "secrets", "versions", "list", "--secret=" + CANONICAL, "--limit=4"
    ])
    report["canonical_secret_metadata_read"] = ok
    if isinstance(versions, list):
        report["canonical_secret_versions"] = [
            {"version": _safe_name(str(row.get("name") or "").rsplit("/", 1)[-1]),
             "state": _safe_name(row.get("state")),
             "created": _safe_name(row.get("createTime"))}
            for row in versions[:4] if isinstance(row, dict)
        ]
    return report


if __name__ == "__main__":
    # This program NEVER invokes secrets versions access or any broker mutation.
    print(json.dumps(audit(), sort_keys=True, separators=(",", ":"), allow_nan=False))
