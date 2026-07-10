#!/usr/bin/env python3
"""
Cloud runtime check for Genesis System3 Render deployment.

Purpose:
- Collect the exact live facts usually requested manually in chat.
- Save latest proof to reports/latest/cloud_runtime_check/.
- Analyzer/paper safety only. This script never sends broker secrets and never
  calls order-placement endpoints.

Stdlib-only so it can run in GitHub Actions without extra dependencies.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

DEFAULT_BASE_URL = "https://genesis-system3-backend.onrender.com"
REPORT_DIR = Path("reports/latest/cloud_runtime_check")

SECRET_KEY_RE = re.compile(
    r"(token|secret|password|passwd|pwd|pin|totp|api[_-]?key|access[_-]?token|authorization)",
    re.IGNORECASE,
)
SECRET_VALUE_RE = re.compile(r"([A-Za-z0-9_\-]{16,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}|[A-Za-z0-9_\-]{32,})")

ENDPOINTS: List[Tuple[str, str]] = [
    ("deploy_info", "/api/deploy/info"),
    ("health", "/api/health"),
    ("memory_before", "/api/memory"),
    ("broker_status", "/api/broker/status"),
    ("broker_dhan_status", "/api/broker/dhan/status"),
    ("broker_deps", "/api/broker/deps"),
    ("scheduler_health", "/api/scheduler/health"),
    ("portfolio_unified", "/api/portfolio/unified"),
    ("memory_after_portfolio", "/api/memory"),
    ("chain_nifty", "/api/chain/NIFTY"),
    ("memory_after_chain", "/api/memory"),
    ("underlyings", "/api/underlyings"),
    ("state", "/api/state"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for key, value in obj.items():
            if SECRET_KEY_RE.search(str(key)):
                if isinstance(value, bool):
                    out[key] = value
                elif value in (None, "", 0, "0"):
                    out[key] = value
                elif str(key).lower().endswith(("_present", "present")):
                    out[key] = bool(value)
                elif "length" in str(key).lower() or "status" in str(key).lower():
                    out[key] = value
                else:
                    out[key] = "[REDACTED]"
            else:
                out[key] = redact(value)
        return out
    if isinstance(obj, list):
        return [redact(x) for x in obj[:250]]
    if isinstance(obj, str):
        return SECRET_VALUE_RE.sub("[REDACTED]", obj)
    return obj


def _headers(api_key: str) -> Dict[str, str]:
    headers = {"User-Agent": "Genesis-System3-Cloud-Runtime-Check/1.2"}
    if api_key:
        headers["X-API-Key"] = api_key
    return headers


def _new_result(url: str, path: str) -> Dict[str, Any]:
    return {
        "url_path": path,
        "url": url,
        "ok": False,
        "status_code": None,
        "latency_ms": None,
        "json": None,
        "text_preview": None,
        "error": None,
        "attempts": 0,
    }


def fetch_json(base_url: str, path: str, timeout_s: float, api_key: str) -> Dict[str, Any]:
    url = base_url.rstrip("/") + path
    result = _new_result(url, path)
    retry_statuses = {0, 429, 502, 503, 504}
    backoffs = [0.0, 5.0, 12.0, 25.0]
    last_started = time.perf_counter()
    for attempt, sleep_s in enumerate(backoffs, start=1):
        if sleep_s:
            time.sleep(sleep_s)
        last_started = time.perf_counter()
        result["attempts"] = attempt
        try:
            req = urllib.request.Request(url, headers=_headers(api_key))
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                raw = resp.read(1_000_000)
                text = raw.decode("utf-8", errors="replace")
                result["status_code"] = getattr(resp, "status", None)
                result["latency_ms"] = round((time.perf_counter() - last_started) * 1000, 1)
                result["ok"] = 200 <= int(result["status_code"] or 0) < 400
                result["error"] = None
                try:
                    result["json"] = redact(json.loads(text))
                    result["text_preview"] = None
                except Exception:
                    result["json"] = None
                    result["text_preview"] = redact(text[:1000])
                return result
        except urllib.error.HTTPError as exc:
            result["status_code"] = exc.code
            result["latency_ms"] = round((time.perf_counter() - last_started) * 1000, 1)
            try:
                text = exc.read(4000).decode("utf-8", errors="replace")
            except Exception:
                text = ""
            result["text_preview"] = redact(text[:1000])
            result["error"] = f"HTTPError: {exc.code}"
            if exc.code not in retry_statuses or attempt == len(backoffs):
                return result
        except Exception as exc:
            result["status_code"] = 0
            result["latency_ms"] = round((time.perf_counter() - last_started) * 1000, 1)
            result["error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
            if attempt == len(backoffs):
                return result
    return result


def walk_values(obj: Any, path: str = "") -> Iterable[Tuple[str, Any]]:
    if isinstance(obj, dict):
        for key, value in obj.items():
            next_path = f"{path}.{key}" if path else str(key)
            yield next_path, value
            yield from walk_values(value, next_path)
    elif isinstance(obj, list):
        for idx, value in enumerate(obj[:100]):
            next_path = f"{path}[{idx}]"
            yield next_path, value
            yield from walk_values(value, next_path)


def get_json(results: Dict[str, Any], name: str) -> Any:
    item = results.get(name) or {}
    return item.get("json")


def memory_status(mem: Any) -> Dict[str, Any]:
    if not isinstance(mem, dict):
        return {"available": False}
    rss = mem.get("rss_mb") or mem.get("used_mb") or (mem.get("memory") or {}).get("used_mb")
    pct = mem.get("pct_used") or mem.get("percent") or (mem.get("memory") or {}).get("percent")
    status = mem.get("status") or "UNKNOWN"
    return {"available": True, "rss_mb": rss, "pct_used": pct, "status": status, "raw": mem}


def analyze(base_url: str, results: Dict[str, Any], expected_commit: str) -> Dict[str, Any]:
    alerts: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []
    passed: List[str] = []

    def alert(level: str, key: str, message: str) -> None:
        target = alerts if level == "CRITICAL" else warnings
        target.append({"level": level, "key": key, "message": message})

    for name, item in results.items():
        if not item.get("ok"):
            alert("WARNING", f"endpoint_{name}", f"{name} failed: {item.get('status_code')} {item.get('error')} attempts={item.get('attempts')}")
        else:
            passed.append(f"endpoint_{name}")

    deploy = get_json(results, "deploy_info") or {}
    deployed_sha = str(deploy.get("git_sha") or "")
    if expected_commit and deployed_sha and not deployed_sha.startswith(expected_commit[:7]):
        alert("WARNING", "deploy_commit_mismatch", f"Render git_sha={deployed_sha[:12]} expected={expected_commit[:12]}")
    elif deployed_sha:
        passed.append("deploy_commit_visible")

    broker = get_json(results, "broker_status") or {}
    if isinstance(broker, dict) and broker.get("connected") is True:
        passed.append("broker_connected")
    else:
        alert("WARNING", "broker_not_connected", f"broker status not connected: {broker.get('error') if isinstance(broker, dict) else broker}")

    scheduler = get_json(results, "scheduler_health") or {}
    if isinstance(scheduler, dict):
        if scheduler.get("healthy") is True:
            passed.append("scheduler_healthy")
        elif scheduler.get("received") is True:
            alert("WARNING", "scheduler_not_healthy", f"worker push received but unhealthy: {scheduler.get('unhealthy_reasons')}")
        else:
            alert("WARNING", "scheduler_no_worker_push", "worker scheduler health has not been received")

    chain = get_json(results, "chain_nifty") or {}
    if isinstance(chain, dict):
        contracts = int(chain.get("total_contracts") or len(chain.get("contracts") or []))
        source = chain.get("data_source") or chain.get("source")
        if contracts > 0:
            passed.append("chain_nifty_has_contracts")
        else:
            alert("WARNING", "chain_nifty_empty", f"NIFTY chain empty/status={chain.get('status')} source={source}")
        if contracts > 250:
            alert("WARNING", "chain_payload_large", f"NIFTY chain has {contracts} contracts; target <=250 on 512MB Render")
        if chain.get("limited_for_web") is True:
            passed.append("chain_limited_for_web")

    portfolio = get_json(results, "portfolio_unified") or {}
    if isinstance(portfolio, dict):
        broker_obj = portfolio.get("broker") or {}
        if broker_obj.get("details_mode") == "skipped_for_render_memory":
            passed.append("portfolio_broker_details_skipped_for_memory")
        if portfolio.get("order_placement_allowed") is False and portfolio.get("live_trading_enabled") is False:
            passed.append("portfolio_live_disabled")

    for endpoint_name, item in results.items():
        payload = item.get("json")
        for p, v in walk_values(payload):
            lower = p.lower()
            if lower.endswith("live_allowed") and v is True:
                alert("CRITICAL", "live_allowed_true", f"{endpoint_name}:{p}=true")
            if lower.endswith("live_trading_enabled") and v not in (False, 0, "0", "false", "False", None):
                alert("CRITICAL", "live_trading_enabled_not_false", f"{endpoint_name}:{p}={v}")
            if lower.endswith("order_placement_allowed") and v not in (False, 0, "0", "false", "False", None):
                alert("CRITICAL", "order_placement_allowed_not_false", f"{endpoint_name}:{p}={v}")

    mem_before = memory_status(get_json(results, "memory_before"))
    mem_after_portfolio = memory_status(get_json(results, "memory_after_portfolio"))
    mem_after_chain = memory_status(get_json(results, "memory_after_chain"))
    for key, mem in [("memory_before", mem_before), ("memory_after_portfolio", mem_after_portfolio), ("memory_after_chain", mem_after_chain)]:
        rss = mem.get("rss_mb")
        try:
            if rss is not None and float(rss) >= 420:
                alert("WARNING", key, f"RSS high: {rss}MB")
            elif rss is not None:
                passed.append(f"{key}_below_420mb")
        except Exception:
            pass

    verdict = "PASS"
    if alerts:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "WARN"

    return {
        "verdict": verdict,
        "base_url": base_url,
        "expected_commit": expected_commit,
        "deployed_commit": deployed_sha,
        "passed": sorted(set(passed)),
        "warnings": warnings,
        "alerts": alerts,
        "memory": {"before": mem_before, "after_portfolio": mem_after_portfolio, "after_chain": mem_after_chain},
        "key_facts": {
            "broker_connected": bool(isinstance(broker, dict) and broker.get("connected") is True),
            "scheduler_received": bool(isinstance(scheduler, dict) and scheduler.get("received") is True),
            "scheduler_healthy": bool(isinstance(scheduler, dict) and scheduler.get("healthy") is True),
            "chain_nifty_contracts": int(chain.get("total_contracts") or len(chain.get("contracts") or [])) if isinstance(chain, dict) else 0,
            "portfolio_details_mode": ((portfolio.get("broker") or {}).get("details_mode") if isinstance(portfolio, dict) else None),
        },
    }


def write_reports(report: Dict[str, Any], results: Dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    full = {**report, "endpoints": results}
    (REPORT_DIR / "summary.json").write_text(json.dumps(full, indent=2, sort_keys=True), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Cloud Runtime Check\n")
    lines.append(f"- Generated UTC: `{report['generated_utc']}`")
    lines.append(f"- Verdict: **{report['verdict']}**")
    lines.append(f"- Base URL: `{report['base_url']}`")
    lines.append(f"- Expected commit: `{report.get('expected_commit') or 'unknown'}`")
    lines.append(f"- Deployed commit: `{report.get('deployed_commit') or 'unknown'}`")
    lines.append("")
    lines.append("## Key facts")
    for k, v in report.get("key_facts", {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Memory")
    for label, mem in report.get("memory", {}).items():
        lines.append(f"- `{label}`: rss=`{mem.get('rss_mb')}`, pct=`{mem.get('pct_used')}`, status=`{mem.get('status')}`")
    lines.append("")
    lines.append("## Alerts")
    if report.get("alerts"):
        for item in report["alerts"]:
            lines.append(f"- **{item['level']}** `{item['key']}` — {item['message']}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Warnings")
    if report.get("warnings"):
        for item in report["warnings"]:
            lines.append(f"- **{item['level']}** `{item['key']}` — {item['message']}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Endpoint status")
    for name, item in results.items():
        lines.append(f"- `{name}` `{item.get('url_path')}`: ok=`{item.get('ok')}`, status=`{item.get('status_code')}`, latency_ms=`{item.get('latency_ms')}`, attempts=`{item.get('attempts')}`")
    lines.append("")
    lines.append("## Safety")
    lines.append("- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.")
    lines.append("- Secret-looking keys/values are redacted before saving report files.")
    (REPORT_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.environ.get("CLOUD_RUNTIME_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("CLOUD_RUNTIME_TIMEOUT_S", "20")))
    parser.add_argument("--expected-commit", default=os.environ.get("GITHUB_SHA", ""))
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    generated_utc = utc_now()
    api_key = os.environ.get("DASHBOARD_API_KEY", "").strip() or os.environ.get("API_KEY", "").strip()
    results: Dict[str, Any] = {}

    for name, path in ENDPOINTS:
        results[name] = fetch_json(base_url, path, timeout_s=args.timeout, api_key=api_key)
        time.sleep(0.35)

    report = analyze(base_url, results, args.expected_commit)
    report["generated_utc"] = generated_utc
    report["script"] = "tools/cloud_runtime_check.py"
    write_reports(report, results)

    print(json.dumps({"generated_utc": generated_utc, "verdict": report["verdict"], "alerts": report["alerts"], "warnings": report["warnings"], "report_dir": str(REPORT_DIR)}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        (REPORT_DIR / "summary.json").write_text(json.dumps({"generated_utc": utc_now(), "verdict": "ERROR", "traceback": traceback.format_exc()}, indent=2), encoding="utf-8")
        raise
