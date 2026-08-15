#!/usr/bin/env python3
"""Bounded exact-contract verifier for the public scheduler health endpoint.

The verifier intentionally derives every expected scheduler count from the
production scheduler contract.  A newly added lane therefore cannot remain
invisible behind a stale literal such as `total == 9`.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

from dashboard.backend.scheduler_contract import coverage_expectations


def verify_payload(body: dict, *, http_status: int = 200) -> dict:
    coverage = body.get("coverage") if isinstance(body.get("coverage"), dict) else {}
    observability = body.get("observability") if isinstance(body.get("observability"), dict) else {}
    expected = coverage_expectations()
    checks = {
        "http_ok": int(http_status) == 200,
        "healthy": body.get("healthy") is True,
        "contract_matched": coverage.get("contract_matched") is True,
        "expected_total": coverage.get("expected_total") == expected["expected_total"],
        "total_matches_expected": coverage.get("total") == expected["expected_total"],
        "workload_matches_expected": coverage.get("workload") == expected["expected_workload"],
        "control_matches_expected": coverage.get("control") == expected["expected_control"],
        "enabled_matches_expected": coverage.get("enabled") == expected["expected_enabled"],
        "paused_matches_expected": coverage.get("paused") == expected["expected_paused"],
        "live_off": body.get("live_trading_enabled") is not True,
        "alert_none": observability.get("alert_severity") in {None, "none"},
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "coverage": coverage,
        "expected": expected,
        "observability": observability,
    }


def main() -> int:
    os.environ["LIVE_TRADING_ENABLED"] = "0"
    os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
    os.environ["AUTO_EXECUTE_TRADES"] = "0"
    base = (os.environ.get("SYSTEM3_SERVICE_URL") or "").strip().rstrip("/")
    if not base:
        print(json.dumps({"status": "FAIL", "reason": "SYSTEM3_SERVICE_URL_REQUIRED"}), file=sys.stderr)
        return 2
    pass_no = int(os.environ.get("SYSTEM3_VERIFY_PASS", "1") or "1")
    url = f"{base}/api/scheduler/health?refresh=true"
    req = urllib.request.Request(url, headers={"User-Agent": "genesis-system3-control-plane-verify-v2"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            http_status = int(getattr(resp, "status", 200) or 200)
    except urllib.error.HTTPError as exc:
        print(json.dumps({"status": "FAIL", "pass_number": pass_no, "reason": f"HTTP_{exc.code}"}), file=sys.stderr)
        return 1
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "pass_number": pass_no, "reason": type(exc).__name__}), file=sys.stderr)
        return 1

    result = verify_payload(body, http_status=http_status)
    proof = {
        "status": "PASS" if result["ok"] else "FAIL",
        "pass_number": pass_no,
        "service_url": base,
        "checks": result["checks"],
        "expected": result["expected"],
        "coverage": {
            key: result["coverage"].get(key)
            for key in (
                "total", "workload", "control", "enabled", "paused",
                "expected_total", "expected_workload", "expected_control",
                "expected_enabled", "expected_paused", "contract_matched",
            )
        },
        "evidence_version": body.get("evidence_version"),
        "evidence_sha256": body.get("evidence_sha256"),
        "observability": result["observability"],
        "deploy_git_sha": body.get("deploy_git_sha") or os.environ.get("DEPLOY_GIT_SHA"),
        "live_trading_enabled": False,
    }
    print(json.dumps(proof, sort_keys=True, default=str))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
