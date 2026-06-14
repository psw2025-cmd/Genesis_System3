"""
Genesis System3 — Dashboard Endpoint Coverage Proof
====================================================
Probes all known dashboard API endpoints and writes a coverage report to
  reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json

Used by the orchestrator's gate_dashboard_truth() gate.
Writes a proven=True result only if every required endpoint returns HTTP 2xx.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "reports" / "latest" / "dashboard_endpoint_coverage"
OUT.mkdir(parents=True, exist_ok=True)

BASE_URL = os.environ.get(
    "SYSTEM3_PUBLIC_BACKEND_URL",
    "https://genesis-system3-backend.onrender.com",
).rstrip("/")

REQUIRED_ENDPOINTS = [
    "/health",
    "/api/health",
    "/api/state",
    "/api/broker/status",
    "/docs",
]

OPTIONAL_ENDPOINTS = [
    "/",            # Root HTML — may timeout on Render free tier cold start
    "/api/gain_rank",
    "/api/accuracy_trend",
    "/api/system_health",
    "/api/broker/deps",
    "/api/status",
]

SAFETY_CHECKS = {
    "/api/health": {
        "live_allowed_must_be_false": lambda j: j.get("live_allowed") is not True,
    },
    "/api/broker/status": {
        "no_live_order_placement": lambda j: j.get("order_placement_allowed") is not True,
    },
    "/api/state": {
        "mode_not_live": lambda j: str(j.get("mode", "")).upper() != "LIVE",
    },
}


def fetch(url: str, timeout: int = 20) -> dict:
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "System3-EndpointCoverage/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(50000).decode("utf-8", errors="replace")
            ms = int((time.time() - start) * 1000)
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = None
            return {"url": url, "ok": True, "http": r.status, "latency_ms": ms, "json": parsed, "snippet": raw[:500]}
    except urllib.error.HTTPError as e:
        raw = e.read(10000).decode("utf-8", errors="replace") if e else ""
        return {"url": url, "ok": False, "http": e.code, "error": str(e), "json": None, "snippet": raw[:500]}
    except Exception as e:
        return {"url": url, "ok": False, "http": None, "error": str(e), "json": None, "snippet": ""}


def run_proof() -> dict:
    started = datetime.now(timezone.utc).isoformat()
    results = {}

    print(f"[DashboardCoverage] Probing {BASE_URL} ...")

    all_results = []
    for ep in REQUIRED_ENDPOINTS + OPTIONAL_ENDPOINTS:
        url = BASE_URL + ep
        r = fetch(url)
        r["endpoint"] = ep
        r["required"] = ep in REQUIRED_ENDPOINTS
        all_results.append(r)
        status = f"HTTP {r['http']}" if r["http"] else f"ERROR: {r.get('error','?')[:60]}"
        print(f"  {'REQ' if r['required'] else 'OPT'} {ep}: {status} ({r.get('latency_ms','?')}ms)")
        results[ep] = r

    # Required endpoint pass/fail
    required_ok = [r for r in all_results if r["required"] and r["ok"] and r.get("http") == 200]
    required_fail = [r for r in all_results if r["required"] and (not r["ok"] or r.get("http") != 200)]

    # Safety checks
    safety_violations = []
    safety_passed = []
    for ep, checks in SAFETY_CHECKS.items():
        r = results.get(ep, {})
        j = r.get("json") or {}
        for check_name, check_fn in checks.items():
            try:
                if not check_fn(j):
                    safety_violations.append(f"{ep}: {check_name} FAILED — json={str(j)[:200]}")
                else:
                    safety_passed.append(f"{ep}: {check_name} OK")
            except Exception as e:
                safety_violations.append(f"{ep}: {check_name} ERROR — {e}")

    # Parse broker/health state
    broker_json = results.get("/api/broker/status", {}).get("json") or {}
    health_json = results.get("/api/health", {}).get("json") or {}
    state_json = results.get("/api/state", {}).get("json") or {}

    all_required_pass = len(required_fail) == 0
    no_safety_violations = len(safety_violations) == 0
    proof_pass = all_required_pass and no_safety_violations

    summary = {
        "generated_utc": started,
        "base_url": BASE_URL,
        "gate": "dashboard_endpoint_coverage",
        "pass": proof_pass,
        "status": "PASS" if proof_pass else "FAIL",
        "required_endpoints_total": len(REQUIRED_ENDPOINTS),
        "required_endpoints_ok": len(required_ok),
        "required_endpoints_failed": len(required_fail),
        "optional_endpoints_total": len(OPTIONAL_ENDPOINTS),
        "optional_endpoints_ok": sum(1 for r in all_results if not r["required"] and r.get("http") == 200),
        "safety_checks_passed": safety_passed,
        "safety_violations": safety_violations,
        "all_required_endpoints_pass": all_required_pass,
        "no_safety_violations": no_safety_violations,
        "browser_visual_truth_proven": False,
        "api_db_report_reconciliation_proven": False,
        "endpoint_coverage_complete": proof_pass,
        "broker_connected": broker_json.get("connected"),
        "broker_error": broker_json.get("error"),
        "health_status": health_json.get("status"),
        "live_allowed": health_json.get("live_allowed"),
        "state_mode": state_json.get("mode"),
        "live_trading_enabled": False,
        "system3_live_trading_allowed": False,
        "endpoints": all_results,
        "blockers": [f"required endpoint failed: {r['url']}" for r in required_fail],
        "warnings": (
            (["browser_visual_truth_not_proven"] if True else []) +
            (["api_db_reconciliation_not_automated"] if True else []) +
            ([f"safety_violation: {v}" for v in safety_violations])
        ),
        "next_action": (
            "All required endpoints pass and no safety violations. Accumulate live proof." if proof_pass
            else f"Fix {len(required_fail)} required endpoint failures before proof can pass."
        ),
    }

    (OUT / "endpoint_coverage_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "endpoint_results.json").write_text(json.dumps(all_results, indent=2), encoding="utf-8")

    print(f"\n[DashboardCoverage] Result: {'PASS' if proof_pass else 'FAIL'}")
    print(f"  Required: {len(required_ok)}/{len(REQUIRED_ENDPOINTS)} OK")
    print(f"  Safety violations: {len(safety_violations)}")
    if required_fail:
        for r in required_fail:
            print(f"  FAIL {r['endpoint']}: HTTP {r.get('http')} {r.get('error','')}")
    print(f"  Report: {OUT / 'endpoint_coverage_summary.json'}")
    return summary


if __name__ == "__main__":
    result = run_proof()
    sys.exit(0 if result["pass"] else 1)
