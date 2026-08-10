#!/usr/bin/env python3
"""Create sanitized, read-only Genesis_System3 Google Cloud runtime evidence."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import statistics
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.getenv("GCP_REGION", "asia-south1")
SERVICE = os.getenv("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
ROTATION_JOB = os.getenv("DHAN_ROTATION_JOB", "genesis-system3-dhan-token-rotate")
SCHEDULER = os.getenv("DHAN_ROTATION_SCHEDULER", "genesis-system3-dhan-token-rotate-daily")
EXPECTED_SHA = os.getenv("GITHUB_SHA", "").strip()
OUT = Path(os.getenv("SYSTEM3_GCP_EVIDENCE_DIR", "reports/latest/gcp_runtime_lock"))
SAFE_ENV = {
    "SYSTEM3_MODE", "ANALYZE_MODE", "LIVE_TRADING_ENABLED",
    "SYSTEM3_LIVE_TRADING_ALLOWED", "AUTO_EXECUTE_TRADES", "REQUIRE_API_KEY",
    "SYSTEM3_STATE_BACKEND", "SYSTEM3_REAL_ONLY", "CLOUD_PAPER_ENGINE",
    "DHAN_TOKEN_SOURCE", "DHAN_ACCESS_TOKEN_SECRET_ID", "DHAN_TOKEN_CACHE_TTL_S",
    "DHAN_TOKEN_ROTATION_JOB", "DHAN_TOKEN_ROTATION_SCHEDULE", "DEPLOY_GIT_SHA",
    "SYSTEM3_DEPLOY_TARGET", "MEM_WARN_MB", "MEM_GC_MB", "MEM_LIMIT_MB",
}
SECRETS = ("system3-dhan-client-id", "dhan-access-token", "dhan-pin", "dhan-totp-secret")
# Env var names that must only ever arrive via Secret Manager (valueFrom). If one of
# these shows up with a plain `value` instead, that is a plaintext-secret leak.
SECRET_BACKED_ENV_NAMES = {"API_KEY", "WORKER_PUSH_TOKEN"}
REDACT = re.compile(
    r"(?i)(bearer\s+[a-z0-9._~+\-/]+=*|authorization\s*[:=]\s*\S+|"
    r"(?:token|secret|password|pin|totp|api[_-]?key)\s*[:=]\s*[^\s,;]+)"
)


def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso(value: dt.datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def run_json(args: list[str], timeout: int = 90) -> tuple[Any, dict[str, Any]]:
    proc = subprocess.run(args, text=True, capture_output=True, timeout=timeout, check=False)
    meta = {"ok": proc.returncode == 0, "returncode": proc.returncode,
            "command": " ".join(args[:4]) + (" ..." if len(args) > 4 else "")}
    if proc.returncode:
        meta["error"] = REDACT.sub("[REDACTED]", (proc.stderr or "")[:400]).strip()
        return None, meta
    try:
        return json.loads(proc.stdout or "null"), meta
    except json.JSONDecodeError as exc:
        meta.update(ok=False, error=f"invalid_json:{exc.msg}")
        return None, meta


def container(service: dict[str, Any]) -> dict[str, Any]:
    rows = (((service.get("spec") or {}).get("template") or {}).get("spec") or {}).get("containers") or []
    if not rows:
        rows = (service.get("template") or {}).get("containers") or []
    return rows[0] if rows else {}


def safe_env(service: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    env: dict[str, Any] = {}
    secret_refs: list[str] = []
    plaintext_secret_names: list[str] = []
    for row in container(service).get("env") or []:
        name = str(row.get("name") or "")
        if not name:
            continue
        if "valueFrom" in row:
            secret_refs.append(name)
        elif name in SAFE_ENV:
            env[name] = row.get("value")
        elif name in SECRET_BACKED_ENV_NAMES:
            # Present with a plain value instead of a Secret Manager valueFrom
            # reference: the value itself is never captured, only the fact of the leak.
            plaintext_secret_names.append(name)
    return env, sorted(secret_refs), sorted(plaintext_secret_names)


def is_off(value: Any) -> bool:
    return str(value).strip().lower() in {"0", "false", "no", "off"}


def is_on(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def evaluate_safety(env: dict[str, Any], secret_refs: list[str],
                     plaintext_secret_names: list[str]) -> dict[str, Any]:
    # api_key_required / api_key_mounted TRUE is the secure state: dashboard auth is
    # enforced and the key comes from Secret Manager (valueFrom), not a plain env value.
    return {"analyze_mode": is_on(env.get("ANALYZE_MODE")),
            "live_trading_enabled": not is_off(env.get("LIVE_TRADING_ENABLED")),
            "system3_live_trading_allowed": not is_off(env.get("SYSTEM3_LIVE_TRADING_ALLOWED")),
            "auto_execute_trades": not is_off(env.get("AUTO_EXECUTE_TRADES")),
            "api_key_required": not is_off(env.get("REQUIRE_API_KEY")),
            "api_key_mounted": "API_KEY" in secret_refs,
            "api_key_plaintext_exposed": "API_KEY" in plaintext_secret_names,
            "secret_payloads_exposed": False}


def safety_passes(safety: dict[str, Any]) -> bool:
    return (safety["analyze_mode"]
            and not safety["live_trading_enabled"]
            and not safety["system3_live_trading_allowed"]
            and not safety["auto_execute_trades"]
            and safety["api_key_required"]
            and safety["api_key_mounted"]
            and not safety["api_key_plaintext_exposed"])


def safety_blockers(safety: dict[str, Any]) -> list[str]:
    blockers = []
    if not safety["analyze_mode"]:
        blockers.append("Analyzer mode is not enabled.")
    if any(safety[k] for k in ("live_trading_enabled", "system3_live_trading_allowed", "auto_execute_trades")):
        blockers.append("Live-trading-off invariants are not proven.")
    if not safety["api_key_required"]:
        blockers.append("Dashboard API key authentication is missing or disabled (REQUIRE_API_KEY is not enforced).")
    if not safety["api_key_mounted"]:
        blockers.append("Dashboard API key is not mounted from Secret Manager.")
    if safety["api_key_plaintext_exposed"]:
        blockers.append("Dashboard API key is present as a plaintext environment value instead of a Secret Manager reference.")
    return blockers


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    return round(values[max(0, min(len(values) - 1, math.ceil(q * len(values)) - 1))], 3)


def latency_ms(value: Any) -> float | None:
    try:
        text = str(value)
        return float(text[:-1]) * 1000 if text.endswith("s") else float(text)
    except (TypeError, ValueError):
        return None


def log_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    statuses: dict[str, int] = {}
    latencies: list[float] = []
    severity: dict[str, int] = {}
    categories = {k: 0 for k in (
        "startup", "crash_or_restart", "out_of_memory", "dhan_auth",
        "option_chain", "firestore", "scheduler_or_worker", "unhandled_exception"
    )}
    latest_health = None
    for entry in entries:
        sev = str(entry.get("severity") or "DEFAULT").upper()
        severity[sev] = severity.get(sev, 0) + 1
        req = entry.get("httpRequest") or {}
        status = req.get("status")
        if status is not None:
            statuses[str(status)] = statuses.get(str(status), 0) + 1
        ms = latency_ms(req.get("latency"))
        if ms is not None:
            latencies.append(ms)
        if "/api/health" in str(req.get("requestUrl") or "") and int(status or 0) < 400:
            latest_health = max(str(entry.get("timestamp") or ""), latest_health or "")
        payload = entry.get("textPayload") or entry.get("jsonPayload") or entry.get("protoPayload") or ""
        text = payload if isinstance(payload, str) else json.dumps(payload, sort_keys=True, default=str)
        low = REDACT.sub("[REDACTED]", text).lower()
        checks = {
            "startup": ("startup", "uvicorn running", "application startup"),
            "crash_or_restart": ("container terminated", "crash", "restarting", "exit code"),
            "out_of_memory": ("out of memory", "memory limit exceeded", "killed process"),
            "dhan_auth": ("invalid token", "unauthorized", "token expired"),
            "option_chain": ("option chain", "option_chain", "/api/chain/"),
            "firestore": ("firestore",),
            "scheduler_or_worker": ("scheduler", "worker push", "rotation job"),
            "unhandled_exception": ("traceback", "unhandled exception", "exception:"),
        }
        for name, needles in checks.items():
            if any(x in low for x in needles) and (name != "dhan_auth" or "dhan" in low):
                categories[name] += 1
    return {
        "entries_examined": len(entries), "severity_counts": severity,
        "http_status_counts": statuses,
        "http_4xx_count": sum(v for k, v in statuses.items() if k.startswith("4")),
        "http_5xx_count": sum(v for k, v in statuses.items() if k.startswith("5")),
        "latency_sample_count": len(latencies), "p50_latency_ms": quantile(latencies, .50),
        "p95_latency_ms": quantile(latencies, .95), "p99_latency_ms": quantile(latencies, .99),
        "latest_successful_health_request": latest_health, "category_counts": categories,
        "raw_log_payloads_exposed": False,
    }


def access_token() -> str | None:
    proc = subprocess.run(["gcloud", "auth", "print-access-token"], text=True,
                          capture_output=True, timeout=30, check=False)
    return proc.stdout.strip() if proc.returncode == 0 else None


def metric(metric_type: str, start: str, end: str) -> dict[str, Any]:
    token = access_token()
    if not token:
        return {"ok": False, "error": "access_token_unavailable"}
    flt = (f'metric.type="{metric_type}" AND resource.type="cloud_run_revision" '
           f'AND resource.labels.service_name="{SERVICE}"')
    query = urllib.parse.urlencode({"filter": flt, "interval.startTime": start,
                                    "interval.endTime": end, "view": "FULL", "pageSize": "100"})
    req = urllib.request.Request(
        f"https://monitoring.googleapis.com/v3/projects/{PROJECT}/timeSeries?{query}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode())
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__}
    numeric: list[float] = []
    means: list[float] = []
    count = 0
    latest = ""
    for series in data.get("timeSeries") or []:
        for point in series.get("points") or []:
            latest = max(latest, str((point.get("interval") or {}).get("endTime") or ""))
            value = point.get("value") or {}
            for key in ("doubleValue", "int64Value"):
                try:
                    if key in value:
                        numeric.append(float(value[key]))
                except (TypeError, ValueError):
                    pass
            dist = value.get("distributionValue") or {}
            if dist:
                count += int(dist.get("count") or 0)
                try:
                    means.append(float(dist.get("mean")))
                except (TypeError, ValueError):
                    pass
    return {"ok": True, "series_count": len(data.get("timeSeries") or []),
            "point_count": len(numeric) + len(means),
            "sum": round(sum(numeric), 6) if numeric else None,
            "max": round(max(numeric), 6) if numeric else None,
            "distribution_count": count or None,
            "distribution_mean": round(statistics.fmean(means), 6) if means else None,
            "latest_point_time": latest or None}


def endpoint_summary(path: str, body: Any) -> dict[str, Any]:
    if not isinstance(body, dict):
        return {"json_object": False}
    if path == "/api/auth/status":
        return {k: body.get(k) for k in ("required", "configured", "authenticated", "mode")}
    if path == "/api/health":
        return {k: body.get(k) for k in ("status", "service", "mode", "timestamp", "version")}
    if path == "/api/state":
        broker = body.get("broker") if isinstance(body.get("broker"), dict) else {}
        return {"mode": body.get("mode"), "data_source": body.get("data_source"),
                "state_version": body.get("state_version"),
                "positions_count": len(body.get("positions") or []) if isinstance(body.get("positions"), list) else None,
                "broker_connected": broker.get("connected"),
                "updated_at": body.get("updated_at") or body.get("timestamp")}
    if path == "/api/broker/status":
        proof = body.get("token_proof") if isinstance(body.get("token_proof"), dict) else {}
        return {"connected": body.get("connected"), "latency_ms": body.get("latency_ms"),
                "error_present": bool(body.get("error")), "token_source": proof.get("source"),
                "secret_version": proof.get("secret_version"), "loaded_at_utc": proof.get("loaded_at_utc"),
                "expires_at_utc": proof.get("expires_at_utc"), "hours_remaining": proof.get("hours_remaining"),
                "token_value_exposed": proof.get("token_value_exposed"),
                "live_trading_enabled": body.get("live_trading_enabled"),
                "order_placement_allowed": body.get("order_placement_allowed")}
    if path.startswith("/api/chain/"):
        rows = body.get("contracts") or body.get("data") or body.get("rows")
        return {"symbol": body.get("symbol") or path.rsplit("/", 1)[-1],
                "source": body.get("source") or body.get("data_source"),
                "source_priority": body.get("source_priority"), "stale": body.get("stale"),
                "fetched_at_utc": body.get("fetched_at_utc") or body.get("timestamp"),
                "contract_count": len(rows) if isinstance(rows, list) else body.get("contract_count"),
                "spot_available": body.get("spot") is not None}
    if path == "/api/scanner/top_contract_gainers":
        rows = body.get("results") or body.get("contracts") or body.get("data")
        return {"status": body.get("status"), "source": body.get("source") or body.get("data_source"),
                "timestamp": body.get("timestamp") or body.get("generated_at"),
                "result_count": len(rows) if isinstance(rows, list) else body.get("count")}
    if path in {"/api/pnl", "/api/trades/today", "/api/paper"}:
        return {"status": body.get("status"), "data_source": body.get("data_source") or body.get("source"),
                "history_count": len(body.get("history") or []) if isinstance(body.get("history"), list) else None,
                "trades_count": len(body.get("trades") or []) if isinstance(body.get("trades"), list) else None,
                "orders_count": len(body.get("orders") or []) if isinstance(body.get("orders"), list) else None,
                "positions_count": len(body.get("positions") or []) if isinstance(body.get("positions"), list) else None,
                "timestamp": body.get("timestamp") or body.get("updated_at"),
                "financial_values_exposed": False}
    if path == "/api/auto_gates":
        gates = body.get("proof_gates") or body.get("gates") or []
        values = list(gates.values()) if isinstance(gates, dict) else gates if isinstance(gates, list) else []
        return {"status": body.get("status") or body.get("verdict"),
                "production_grade_claim_allowed": body.get("production_grade_claim_allowed"),
                "trade_ready": body.get("trade_ready"), "gate_count": len(values),
                "passed_gate_count": sum(1 for g in values if isinstance(g, dict) and (g.get("pass") or g.get("ok")))}
    if path == "/api/ml/performance":
        return {"status": body.get("status"), "days_recorded": body.get("days_recorded") or body.get("validation_days"),
                "latest_rho": body.get("latest_rho") or body.get("spearman_rho"),
                "model_ready": body.get("model_ready") or body.get("ready"),
                "timestamp": body.get("timestamp") or body.get("updated_at")}
    return {k: body.get(k) for k in ("status", "mode", "source", "timestamp") if k in body}


def fetch_endpoint(base: str, path: str) -> dict[str, Any]:
    req = urllib.request.Request(base.rstrip("/") + path,
                                 headers={"Accept": "application/json", "User-Agent": "System3Evidence/1.0"})
    started = now(); status = None; raw = b""; error = None
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            status = int(response.status); raw = response.read(5_000_000)
    except urllib.error.HTTPError as exc:
        status = int(exc.code); raw = exc.read(1_000_000); error = f"HTTP_{exc.code}"
    except Exception as exc:
        error = type(exc).__name__
    try:
        body = json.loads(raw.decode("utf-8", "replace")) if raw else None
    except json.JSONDecodeError:
        body = None
    return {"http_status": status, "ok": bool(status and 200 <= status < 300),
            "latency_ms": round((now() - started).total_seconds() * 1000, 1),
            "content_sha256": hashlib.sha256(raw).hexdigest() if raw else None,
            "json_valid": body is not None, "summary": endpoint_summary(path, body) if body is not None else {},
            "error": error, "raw_response_exposed": False}


def secret_metadata(name: str) -> dict[str, Any]:
    secret, describe = run_json(["gcloud", "secrets", "describe", name,
                                 f"--project={PROJECT}", "--format=json"])
    versions, query = run_json(["gcloud", "secrets", "versions", "list", name,
                                f"--project={PROJECT}", "--filter=state=enabled",
                                "--sort-by=~createTime", "--limit=5", "--format=json"])
    rows = versions if isinstance(versions, list) else []
    latest = rows[0] if rows else {}
    return {"exists": isinstance(secret, dict), "describe": describe,
            "enabled_version_count_observed": len(rows),
            "latest_enabled_version": str(latest.get("name") or "").rsplit("/", 1)[-1] or None,
            "latest_enabled_created_at": latest.get("createTime"), "versions_query": query,
            "payload_accessed": False}


def markdown(report: dict[str, Any]) -> str:
    lines = ["# Genesis_System3 GCP Runtime Lock", "",
             f"- Generated: `{report['generated_at_utc']}`", f"- Project: `{PROJECT}`",
             f"- Service: `{SERVICE}`", f"- Revision: `{report['cloud_run'].get('latest_ready_revision')}`",
             f"- Repository SHA: `{report.get('repository_commit') or 'UNKNOWN'}`",
             f"- Deployed SHA: `{report.get('deployed_commit') or 'UNKNOWN'}`",
             f"- Verdict: **{report['lock_result']}**", "", "## Safety", ""]
    lines += [f"- `{k}`: `{v}`" for k, v in report["safety"].items()]
    lines += ["", "## Blockers", ""]
    lines += [f"- {x}" for x in report["blockers"]] or ["- None for the achieved lock level."]
    lines += ["", "Secret payloads, raw endpoint bodies and authorization values are not included.", ""]
    return "\n".join(lines)


def collect() -> dict[str, Any]:
    end_dt = now(); start = iso(end_dt - dt.timedelta(hours=24)); end = iso(end_dt)
    commands: dict[str, Any] = {}
    service, commands["service"] = run_json(["gcloud", "run", "services", "describe", SERVICE,
                                               f"--project={PROJECT}", f"--region={REGION}", "--format=json"])
    service = service if isinstance(service, dict) else {}
    env, secret_refs, plaintext_secret_names = safe_env(service); c0 = container(service)
    revision = str(((service.get("status") or {}).get("latestReadyRevisionName"))
                   or service.get("latestReadyRevision") or "").rsplit("/", 1)[-1]
    url = ((service.get("status") or {}).get("url")) or service.get("uri") or ""
    iam, commands["iam"] = run_json(["gcloud", "run", "services", "get-iam-policy", SERVICE,
                                      f"--project={PROJECT}", f"--region={REGION}", "--format=json"])
    public = any(b.get("role") == "roles/run.invoker" and "allUsers" in (b.get("members") or [])
                 for b in (iam or {}).get("bindings", []))
    scheduler, commands["scheduler"] = run_json(["gcloud", "scheduler", "jobs", "describe", SCHEDULER,
                                                  f"--project={PROJECT}", f"--location={REGION}", "--format=json"])
    executions, commands["executions"] = run_json(["gcloud", "run", "jobs", "executions", "list",
                                                    f"--job={ROTATION_JOB}", f"--project={PROJECT}",
                                                    f"--region={REGION}", "--limit=5", "--format=json"])
    flt = (f'resource.type="cloud_run_revision" AND resource.labels.service_name="{SERVICE}" '
           f'AND timestamp>="{start}"')
    logs, commands["logs"] = run_json(["gcloud", "logging", "read", flt, f"--project={PROJECT}",
                                       "--limit=500", "--order=desc", "--format=json"], 120)
    paths = ["/api/auth/status", "/api/health", "/api/state", "/api/broker/status",
             "/api/chain/NIFTY", "/api/chain/BANKNIFTY", "/api/chain/FINNIFTY",
             "/api/chain/MIDCPNIFTY", "/api/scanner/top_contract_gainers", "/api/pnl",
             "/api/trades/today", "/api/paper", "/api/auto_gates", "/api/ml/performance"]
    endpoints = {p: fetch_endpoint(url, p) for p in paths} if url else {}
    chains = {s: endpoints.get(f"/api/chain/{s}", {}) for s in
              ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")}
    deployed_sha = str(env.get("DEPLOY_GIT_SHA") or "")
    source_match = bool(EXPECTED_SHA and deployed_sha and EXPECTED_SHA == deployed_sha)
    safety = evaluate_safety(env, secret_refs, plaintext_secret_names)
    safety_pass = safety_passes(safety)
    broker = endpoints.get("/api/broker/status", {}).get("summary", {})
    broker_ready = bool(broker.get("connected") and broker.get("token_source") == "GCP_SECRET_MANAGER_DYNAMIC"
                        and broker.get("token_value_exposed") is False
                        and broker.get("live_trading_enabled") is False
                        and broker.get("order_placement_allowed") is False)
    chains_ready = all(v.get("ok") and not v.get("summary", {}).get("stale")
                       and int(v.get("summary", {}).get("contract_count") or 0) > 0 for v in chains.values())
    health_ok = bool(endpoints.get("/api/health", {}).get("ok"))
    blockers = []
    if not commands["service"]["ok"]: blockers.append("Cloud Run service could not be read.")
    if not revision: blockers.append("Latest ready Cloud Run revision is unavailable.")
    if not source_match: blockers.append("GitHub SHA and deployed DEPLOY_GIT_SHA are missing or different.")
    blockers += safety_blockers(safety)
    if not health_ok: blockers.append("Public /api/health proof failed.")
    if not broker_ready: blockers.append("Dhan read-only broker proof is not ready.")
    if not chains_ready: blockers.append("All four required option chains are not fresh and populated.")
    if not commands["scheduler"]["ok"]: blockers.append("Token scheduler metadata is unavailable.")
    deployment_locked = bool(revision and source_match and safety_pass and health_ok)
    result = "ANALYZER_LOCKED" if deployment_locked and broker_ready and chains_ready else \
             "DEPLOYMENT_LOCKED" if deployment_locked else "PRODUCTION_BLOCKED"
    template = (service.get("spec") or {}).get("template") or service.get("template") or {}
    service_account = ((((service.get("spec") or {}).get("template") or {}).get("spec") or {}).get("serviceAccountName")
                       or template.get("serviceAccount"))
    return {"schema_version": 1, "generated_at_utc": iso(end_dt), "project_id": PROJECT,
            "region": REGION, "service": SERVICE, "repository_commit": EXPECTED_SHA or None,
            "deployed_commit": deployed_sha or None, "source_matches_deployment": source_match,
            "cloud_run": {"latest_ready_revision": revision or None, "service_url": url or None,
                          "image": c0.get("image"), "service_account": service_account,
                          "resources": c0.get("resources") or {}, "scaling": template.get("scaling") or {},
                          "public_invoker": public, "safe_environment": env,
                          "mounted_secret_environment_names": secret_refs,
                          "plaintext_secret_environment_names_detected": plaintext_secret_names},
            "safety": safety,
            "scheduler": {"name": (scheduler or {}).get("name") if isinstance(scheduler, dict) else None,
                          "state": (scheduler or {}).get("state") if isinstance(scheduler, dict) else None,
                          "schedule": (scheduler or {}).get("schedule") if isinstance(scheduler, dict) else None,
                          "time_zone": (scheduler or {}).get("timeZone") if isinstance(scheduler, dict) else None,
                          "last_attempt_time": (scheduler or {}).get("lastAttemptTime") if isinstance(scheduler, dict) else None,
                          "recent_rotation_executions": executions if isinstance(executions, list) else []},
            "secret_metadata": {name: secret_metadata(name) for name in SECRETS},
            "logs_24h": log_summary(logs if isinstance(logs, list) else []),
            "monitoring_24h": {"request_count": metric("run.googleapis.com/request_count", start, end),
                               "cpu_utilization": metric("run.googleapis.com/container/cpu/utilizations", start, end),
                               "memory_utilization": metric("run.googleapis.com/container/memory/utilizations", start, end),
                               "instance_count": metric("run.googleapis.com/container/instance_count", start, end)},
            "endpoints": endpoints, "option_chains": chains,
            "broker_read_only_ready": broker_ready, "all_required_chains_ready": chains_ready,
            "commands": commands, "blockers": blockers, "lock_result": result,
            "production_grade_claim_allowed": False, "secret_values_exposed": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(); OUT.mkdir(parents=True, exist_ok=True)
    report = collect()
    (OUT / "gcp_runtime_lock.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (OUT / "gcp_runtime_lock.md").write_text(markdown(report))
    print(json.dumps({"report": str(OUT / "gcp_runtime_lock.json"),
                      "lock_result": report["lock_result"],
                      "source_matches_deployment": report["source_matches_deployment"],
                      "blocker_count": len(report["blockers"]),
                      "production_grade_claim_allowed": False}, sort_keys=True))
    return 2 if args.strict and report["lock_result"] == "PRODUCTION_BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
