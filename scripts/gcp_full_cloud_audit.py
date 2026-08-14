#!/usr/bin/env python3
"""Read-only Google Cloud forensic audit for Genesis System3.

Collects Cloud Run, IAM/ingress, Scheduler/Job, logs, TLS, public endpoint
latency/rate-limit evidence, and durable-export readiness. It never reads a
secret payload and never calls a broker order/mutation endpoint.
"""
from __future__ import annotations

import json
import os
import re
import socket
import ssl
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.getenv("GCP_REGION", "asia-south1")
SERVICE = os.getenv("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
ROTATION_JOB = os.getenv("DHAN_ROTATION_JOB", "genesis-system3-dhan-token-rotate")
ROTATION_SCHEDULER = os.getenv("DHAN_ROTATION_SCHEDULER", "genesis-system3-dhan-token-rotate-daily")
EXPECTED_SHA = os.getenv("GITHUB_SHA", "").strip()
OUT = Path(os.getenv("SYSTEM3_FULL_CLOUD_AUDIT_DIR", "reports/latest/full_cloud_audit"))

REDACT = re.compile(
    r"(?i)(bearer\s+[a-z0-9._~+\-/]+=*|authorization\s*[:=]\s*\S+|"
    r"(?:token|secret|password|pin|totp|api[_-]?key|cookie)\s*[:=]\s*[^\s,;]+)"
)
SECRET_NAMES = ("system3-dhan-client-id", "dhan-access-token", "dhan-pin", "dhan-totp-secret")


def _run_json(args: list[str], timeout: int = 90) -> tuple[Any | None, dict[str, Any]]:
    proc = subprocess.run(args, text=True, capture_output=True, timeout=timeout, check=False)
    meta: dict[str, Any] = {"ok": proc.returncode == 0, "returncode": proc.returncode}
    if proc.returncode:
        meta["error"] = REDACT.sub("[REDACTED]", (proc.stderr or "")[:600]).strip()
        return None, meta
    try:
        return json.loads(proc.stdout or "null"), meta
    except Exception as exc:
        meta.update(ok=False, error=f"invalid_json:{type(exc).__name__}:{str(exc)[:100]}")
        return None, meta


def _cmd_json(*parts: str, timeout: int = 90) -> tuple[Any | None, dict[str, Any]]:
    return _run_json(list(parts), timeout=timeout)


def _service_url(service: dict[str, Any]) -> str:
    return str(((service.get("status") or {}).get("url")) or service.get("uri") or "").rstrip("/")


def _serving_traffic(service: dict[str, Any]) -> dict[str, int]:
    traffic: dict[str, int] = {}
    for row in (service.get("status") or {}).get("traffic") or []:
        name = row.get("revisionName")
        pct = int(row.get("percent") or 0)
        if name and pct:
            traffic[str(name)] = traffic.get(str(name), 0) + pct
    return traffic


def _safe_revision_env(rev: dict[str, Any]) -> dict[str, Any]:
    env: dict[str, Any] = {}
    containers = ((((rev.get("spec") or {}).get("containers")) or []) or
                  (((rev.get("spec") or {}).get("template") or {}).get("spec") or {}).get("containers") or [])
    if not containers:
        containers = (((rev.get("spec") or {}).get("containers")) or [])
    for row in (containers[0].get("env") or []) if containers else []:
        name = str(row.get("name") or "")
        if name in {
            "DEPLOY_GIT_SHA", "ANALYZE_MODE", "SYSTEM3_MODE", "LIVE_TRADING_ENABLED",
            "SYSTEM3_LIVE_TRADING_ALLOWED", "AUTO_EXECUTE_TRADES", "REQUIRE_API_KEY",
            "DHAN_TOKEN_SOURCE", "SYSTEM3_STATE_BACKEND", "SYSTEM3_STATE_BACKEND_REQUIRED",
        } and "value" in row:
            env[name] = row.get("value")
    return env


def _tls(host: str) -> dict[str, Any]:
    try:
        ctx = ssl.create_default_context()
        start = time.perf_counter()
        with socket.create_connection((host, 443), timeout=15) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as tls:
                cert = tls.getpeercert()
                protocol = tls.version()
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        not_after = cert.get("notAfter")
        expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc) if not_after else None
        days = (expiry - datetime.now(timezone.utc)).total_seconds() / 86400 if expiry else None
        return {
            "state": "PASS" if days is not None and days > 7 else "FAIL",
            "protocol": protocol,
            "handshake_ms": elapsed,
            "expires_at_utc": expiry.isoformat() if expiry else None,
            "days_remaining": round(days, 2) if days is not None else None,
            "subject_alt_name_count": len(cert.get("subjectAltName") or []),
        }
    except Exception as exc:
        return {"state": "FAIL", "error": f"{type(exc).__name__}:{str(exc)[:160]}"}


def _endpoint(session: requests.Session, base: str, path: str, samples: int = 5) -> dict[str, Any]:
    latencies: list[float] = []
    statuses: list[int] = []
    retry_after: list[str] = []
    bodies: list[Any] = []
    errors: list[str] = []
    for _ in range(samples):
        try:
            start = time.perf_counter()
            r = session.get(base + path, timeout=30, headers={"Accept": "application/json"})
            latencies.append((time.perf_counter() - start) * 1000)
            statuses.append(r.status_code)
            if r.headers.get("Retry-After"):
                retry_after.append(r.headers["Retry-After"][:80])
            if r.headers.get("content-type", "").lower().startswith("application/json"):
                try:
                    bodies.append(r.json())
                except Exception:
                    pass
        except Exception as exc:
            errors.append(f"{type(exc).__name__}:{str(exc)[:140]}")
        time.sleep(0.15)
    latest = bodies[-1] if bodies and isinstance(bodies[-1], dict) else {}
    summary: dict[str, Any] = {
        "state": "PASS" if statuses and all(200 <= s < 400 for s in statuses) and not errors else "FAIL",
        "samples_requested": samples,
        "samples_completed": len(statuses),
        "status_counts": {str(s): statuses.count(s) for s in sorted(set(statuses))},
        "p50_ms": round(statistics.median(latencies), 2) if latencies else None,
        "p95_ms": round(sorted(latencies)[max(0, min(len(latencies)-1, int(len(latencies)*0.95)-1))], 2) if latencies else None,
        "max_ms": round(max(latencies), 2) if latencies else None,
        "http_429_count": statuses.count(429),
        "retry_after_seen": bool(retry_after),
        "timeout_or_transport_errors": errors,
        "measurement_origin": "github_hosted_runner_external_to_gcp_region",
    }
    if path == "/api/broker/status":
        proof = latest.get("token_proof") if isinstance(latest.get("token_proof"), dict) else {}
        summary.update({
            "connected": latest.get("connected"),
            "error_present": bool(latest.get("error")),
            "token_source": proof.get("source"),
            "secret_version": proof.get("secret_version"),
            "expires_at_utc": proof.get("expires_at_utc"),
            "hours_remaining": proof.get("hours_remaining"),
            "token_value_exposed": proof.get("token_value_exposed"),
            "live_trading_enabled": latest.get("live_trading_enabled"),
            "order_placement_allowed": latest.get("order_placement_allowed"),
        })
    elif path == "/api/health":
        summary.update({"health_status": latest.get("status"), "mode": latest.get("mode")})
    return summary


def _log_findings(entries: list[dict[str, Any]]) -> dict[str, Any]:
    cats = {k: 0 for k in (
        "http_429", "http_5xx", "dhan_auth", "rate_limit_text", "timeout",
        "firestore_permission", "ssl_tls", "oom", "traceback", "restart_or_crash",
    )}
    severities: dict[str, int] = {}
    for row in entries:
        sev = str(row.get("severity") or "DEFAULT").upper()
        severities[sev] = severities.get(sev, 0) + 1
        req = row.get("httpRequest") or {}
        status = int(req.get("status") or 0)
        if status == 429:
            cats["http_429"] += 1
        if 500 <= status <= 599:
            cats["http_5xx"] += 1
        payload = row.get("textPayload") or row.get("jsonPayload") or row.get("protoPayload") or ""
        text = payload if isinstance(payload, str) else json.dumps(payload, default=str, sort_keys=True)
        low = REDACT.sub("[REDACTED]", text).lower()
        if "dhan" in low and any(x in low for x in ("invalid token", "token expired", "unauthorized", "401")):
            cats["dhan_auth"] += 1
        if any(x in low for x in ("rate limit", "too many requests", "429")):
            cats["rate_limit_text"] += 1
        if any(x in low for x in ("timeout", "timed out", "deadline exceeded")):
            cats["timeout"] += 1
        if "firestore" in low and any(x in low for x in ("permission", "denied", "403")):
            cats["firestore_permission"] += 1
        if any(x in low for x in ("ssl", "tls", "certificate verify")):
            cats["ssl_tls"] += 1
        if any(x in low for x in ("out of memory", "oom", "memory limit")):
            cats["oom"] += 1
        if "traceback" in low:
            cats["traceback"] += 1
        if any(x in low for x in ("container terminated", "crash", "restarting", "exit code")):
            cats["restart_or_crash"] += 1
    return {"entries_examined": len(entries), "severity_counts": severities, "categories": cats, "raw_payloads_persisted": False}


def _secret_metadata(name: str) -> dict[str, Any]:
    versions, meta = _cmd_json(
        "gcloud", "secrets", "versions", "list", name,
        f"--project={PROJECT}", "--limit=5", "--sort-by=~createTime", "--format=json",
    )
    if not meta.get("ok") or not isinstance(versions, list):
        return {"state": "NOT_PROVEN", "error": meta.get("error")}
    safe = []
    for row in versions:
        safe.append({k: row.get(k) for k in ("name", "state", "createTime", "destroyTime") if row.get(k) is not None})
    return {"state": "PASS", "versions": safe, "payload_accessed": False}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).isoformat()

    service, svc_meta = _cmd_json("gcloud", "run", "services", "describe", SERVICE, f"--project={PROJECT}", f"--region={REGION}", "--format=json")
    service = service if isinstance(service, dict) else {}
    url = _service_url(service)
    traffic = _serving_traffic(service)
    serving_revision = next(iter(traffic)) if len(traffic) == 1 and next(iter(traffic.values())) == 100 else ""
    revision: dict[str, Any] = {}
    rev_meta: dict[str, Any] = {"ok": False, "error": "serving_revision_not_single_100"}
    if serving_revision:
        obj, rev_meta = _cmd_json("gcloud", "run", "revisions", "describe", serving_revision, f"--project={PROJECT}", f"--region={REGION}", "--format=json")
        revision = obj if isinstance(obj, dict) else {}
    env = _safe_revision_env(revision)

    iam, iam_meta = _cmd_json("gcloud", "run", "services", "get-iam-policy", SERVICE, f"--project={PROJECT}", f"--region={REGION}", "--format=json")
    iam = iam if isinstance(iam, dict) else {}
    public_invoker = any(
        b.get("role") == "roles/run.invoker" and "allUsers" in (b.get("members") or [])
        for b in iam.get("bindings") or [] if isinstance(b, dict)
    )
    annotations = (service.get("metadata") or {}).get("annotations") or {}
    ingress = annotations.get("run.googleapis.com/ingress") or annotations.get("run.googleapis.com/ingress-status") or "unspecified"

    job, job_meta = _cmd_json("gcloud", "run", "jobs", "describe", ROTATION_JOB, f"--project={PROJECT}", f"--region={REGION}", "--format=json")
    scheduler, scheduler_meta = _cmd_json("gcloud", "scheduler", "jobs", "describe", ROTATION_SCHEDULER, f"--project={PROJECT}", f"--location={REGION}", "--format=json")
    executions, executions_meta = _cmd_json(
        "gcloud", "run", "jobs", "executions", "list", f"--job={ROTATION_JOB}", f"--project={PROJECT}", f"--region={REGION}",
        "--limit=20", "--sort-by=~metadata.creationTimestamp", "--format=json",
    )

    service_logs, service_logs_meta = _cmd_json(
        "gcloud", "logging", "read",
        f'resource.type="cloud_run_revision" AND resource.labels.service_name="{SERVICE}"',
        f"--project={PROJECT}", "--freshness=24h", "--limit=800", "--order=desc", "--format=json", timeout=120,
    )
    job_logs, job_logs_meta = _cmd_json(
        "gcloud", "logging", "read",
        f'resource.type="cloud_run_job" AND resource.labels.job_name="{ROTATION_JOB}"',
        f"--project={PROJECT}", "--freshness=7d", "--limit=500", "--order=desc", "--format=json", timeout=120,
    )

    session = requests.Session()
    endpoints: dict[str, Any] = {}
    tls = {"state": "NOT_PROVEN", "error": "service_url_missing"}
    if url.startswith("https://"):
        host = urlparse(url).hostname or ""
        tls = _tls(host) if host else tls
        for path in ("/api/health", "/api/broker/status", "/ui"):
            endpoints[path] = _endpoint(session, url, path, samples=5)

    sinks, sinks_meta = _cmd_json("gcloud", "logging", "sinks", "list", f"--project={PROJECT}", "--format=json")
    bq, bq_meta = _cmd_json("bq", "ls", f"--project_id={PROJECT}", "--format=json", timeout=60)

    adapters = {
        "elasticsearch": "CONFIGURED" if os.getenv("ELASTICSEARCH_URL") else "BLOCKED_NOT_CONFIGURED",
        "jaeger": "CONFIGURED" if os.getenv("JAEGER_ENDPOINT") else "BLOCKED_NOT_CONFIGURED",
        "grafana": "CONFIGURED" if os.getenv("GRAFANA_URL") else "BLOCKED_NOT_CONFIGURED",
        "powerbi": "CONFIGURED" if os.getenv("POWERBI_PUSH_URL") else "BLOCKED_NOT_CONFIGURED",
        "bigquery_forensic_dataset": "CONFIGURED" if os.getenv("BIGQUERY_AUDIT_DATASET") else "DISCOVERY_ONLY",
    }

    broker = endpoints.get("/api/broker/status") or {}
    health = endpoints.get("/api/health") or {}
    safety_failures = []
    if env.get("LIVE_TRADING_ENABLED") not in ("0", "false", "False", None): safety_failures.append("live_trading_enabled")
    if env.get("SYSTEM3_LIVE_TRADING_ALLOWED") not in ("0", "false", "False", None): safety_failures.append("system3_live_trading_allowed")
    if env.get("AUTO_EXECUTE_TRADES") not in ("0", "false", "False", None): safety_failures.append("auto_execute_trades")
    if broker.get("order_placement_allowed") is True: safety_failures.append("broker_order_placement_allowed")
    if broker.get("token_value_exposed") is True: safety_failures.append("broker_token_value_exposed")
    if not public_invoker: safety_failures.append("public_dashboard_invoker_missing")

    operational_failures = []
    if not svc_meta.get("ok") or not rev_meta.get("ok"): operational_failures.append("cloud_run_not_proven")
    if len(traffic) != 1 or list(traffic.values()) != [100]: operational_failures.append("serving_traffic_not_single_100")
    if health.get("state") != "PASS" or health.get("health_status") != "ok": operational_failures.append("health_not_ready")
    if broker.get("state") != "PASS" or broker.get("connected") is not True: operational_failures.append("broker_not_connected")
    if tls.get("state") != "PASS": operational_failures.append("tls_not_valid")
    if not job_meta.get("ok"): operational_failures.append("rotator_job_not_proven")
    if not scheduler_meta.get("ok"): operational_failures.append("rotator_scheduler_not_proven")

    serving_sha = env.get("DEPLOY_GIT_SHA")
    source_relation = "EXACT" if EXPECTED_SHA and serving_sha == EXPECTED_SHA else "RUNTIME_BEHIND_OR_NONDEPLOY_COMMIT"
    report = {
        "schema": "genesis-system3-full-cloud-audit-v1",
        "generated_at_utc": generated,
        "project": PROJECT,
        "region": REGION,
        "github_sha": EXPECTED_SHA,
        "serving_revision": serving_revision or None,
        "serving_deploy_git_sha": serving_sha,
        "source_relation": source_relation,
        "cloud_run": {
            "state": "PASS" if svc_meta.get("ok") and rev_meta.get("ok") else "FAIL",
            "service_url": url,
            "traffic": traffic,
            "ingress": ingress,
            "public_run_invoker": public_invoker,
            "firewall_assessment": "NOT_APPLICABLE_CLOUD_RUN; ingress/IAM audited instead",
            "safe_env": env,
            "iam_read_ok": iam_meta.get("ok"),
        },
        "tls": tls,
        "endpoints": endpoints,
        "rotator": {
            "job_read_ok": job_meta.get("ok"),
            "scheduler_read_ok": scheduler_meta.get("ok"),
            "execution_list_read_ok": executions_meta.get("ok"),
            "recent_executions": [
                {
                    "name": (x.get("metadata") or {}).get("name"),
                    "created": (x.get("metadata") or {}).get("creationTimestamp"),
                    "creator": ((x.get("metadata") or {}).get("annotations") or {}).get("run.googleapis.com/creator"),
                    "failedCount": (x.get("status") or {}).get("failedCount"),
                    "succeededCount": (x.get("status") or {}).get("succeededCount"),
                }
                for x in (executions or [])[:20] if isinstance(x, dict)
            ],
        },
        "logs": {
            "service_query_ok": service_logs_meta.get("ok"),
            "job_query_ok": job_logs_meta.get("ok"),
            "service": _log_findings(service_logs if isinstance(service_logs, list) else []),
            "rotator_job": _log_findings(job_logs if isinstance(job_logs, list) else []),
        },
        "secret_metadata": {name: _secret_metadata(name) for name in SECRET_NAMES},
        "durable_trail": {
            "logging_sinks_query_ok": sinks_meta.get("ok"),
            "logging_sinks": [
                {k: s.get(k) for k in ("name", "destination", "disabled") if k in s}
                for s in (sinks or []) if isinstance(s, dict)
            ],
            "bigquery_dataset_query_ok": bq_meta.get("ok"),
            "bigquery_datasets": [str(x.get("datasetReference", {}).get("datasetId")) for x in (bq or []) if isinstance(x, dict)],
            "github_artifact_is_not_permanent_storage": True,
            "external_adapters": adapters,
        },
        "safety": {
            "state": "PASS" if not safety_failures else "FAIL",
            "failures": safety_failures,
            "live_trading_enabled": False,
            "order_actions_performed": False,
            "secret_payloads_accessed": False,
            "secret_values_exposed": False,
        },
        "operational": {"state": "PASS" if not operational_failures else "FAIL", "failures": operational_failures},
    }
    report["state"] = "PASS" if report["safety"]["state"] == "PASS" and report["operational"]["state"] == "PASS" else "FAIL"
    (OUT / "full_cloud_audit.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Genesis System3 Full Cloud Audit", "",
        f"Overall: **{report['state']}**", f"Safety: **{report['safety']['state']}**", f"Operational: **{report['operational']['state']}**", "",
        f"- GitHub SHA: `{EXPECTED_SHA}`", f"- Serving SHA: `{serving_sha}`", f"- Serving revision: `{serving_revision}`",
        f"- Source relation: `{source_relation}`", f"- Broker connected: `{broker.get('connected')}`", f"- TLS days remaining: `{tls.get('days_remaining')}`",
        f"- Public Cloud Run invoker: `{public_invoker}`", f"- Ingress: `{ingress}`", "",
        "## External/durable adapters", "",
    ]
    lines += [f"- {k}: **{v}**" for k, v in adapters.items()]
    lines += ["", "No secret payload was read; no broker order/mutation endpoint was called.", ""]
    (OUT / "full_cloud_audit.md").write_text("\n".join(lines), encoding="utf-8")
    print("FULL_CLOUD_AUDIT " + json.dumps({
        "state": report["state"], "safety": report["safety"]["state"], "operational": report["operational"]["state"],
        "serving_revision": serving_revision, "broker_connected": broker.get("connected"), "tls_days": tls.get("days_remaining"),
    }, sort_keys=True))
    return 0 if report["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
