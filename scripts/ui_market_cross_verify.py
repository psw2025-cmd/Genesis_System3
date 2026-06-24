#!/usr/bin/env python3
"""
UI + market cross-verify — polls cloud dashboard APIs and NSE market status.

Outputs:
  reports/latest/ui_market_cross_verify/summary.json
  reports/latest/ui_market_cross_verify/summary.md

Run during market hours for continuous tracking.
"""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "ui_market_cross_verify"
CLOUD = os.environ.get(
    "SYSTEM3_API_BASE",
    "https://genesis-system3-backend.onrender.com",
).rstrip("/")

ENDPOINTS = [
    "/api/state",
    "/api/auto_gates",
    "/api/accuracy_trend",
    "/api/gain_rank",
    "/api/scanner/top_contract_gainers",
    "/api/scanner/equity_options",
    "/api/paper",
    "/api/portfolio/unified",
    "/api/chain/NIFTY",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _ist_market_open() -> Dict[str, Any]:
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    wd = now.weekday() < 5
    mins = now.hour * 60 + now.minute
    open_m = 9 * 60 + 15
    close_m = 15 * 60 + 30
    is_open = wd and open_m <= mins < close_m
    return {
        "ist": now.isoformat(),
        "weekday": now.strftime("%A"),
        "is_open": is_open,
        "minutes_to_close": max(0, close_m - mins) if is_open else None,
    }


def _fetch(url: str, timeout: int = 90) -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read(500_000).decode("utf-8", errors="replace")
            data = json.loads(body) if body.startswith("{") or body.startswith("[") else {}
            return {"ok": resp.status == 200, "status": resp.status, "data": data}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def _issues(results: Dict[str, Any], market: Dict[str, Any]) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    state = results.get("/api/state", {}).get("data") or {}
    gates = results.get("/api/auto_gates", {}).get("data") or {}
    cloud_market = (state.get("market") or {}).get("is_open")
    if market["is_open"] != cloud_market and cloud_market is not None:
        issues.append({
            "id": "MARKET_OPEN_MISMATCH",
            "severity": "HIGH",
            "detail": f"local_ist={market['is_open']} cloud={cloud_market}",
        })
    if not (state.get("broker") or {}).get("connected"):
        issues.append({"id": "BROKER_DISCONNECTED", "severity": "HIGH", "detail": "Cloud broker not connected"})
    if not gates.get("gates"):
        issues.append({"id": "AUTO_GATES_EMPTY", "severity": "HIGH", "detail": "auto_gates returned empty gate map"})
    if gates.get("gates_passing", 0) == 0 and gates.get("gates_total", 0) > 0:
        issues.append({
            "id": "ALL_GATES_PENDING",
            "severity": "MEDIUM",
            "detail": f"0/{gates.get('gates_total')} gates passing",
        })
    acc = results.get("/api/accuracy_trend", {}).get("data") or {}
    if acc.get("status") == "ok" and not acc.get("trend"):
        issues.append({"id": "NO_ACCURACY_HISTORY", "severity": "MEDIUM", "detail": "accuracy_trend empty"})
    for ep, r in results.items():
        if not r.get("ok"):
            issues.append({"id": "ENDPOINT_FAIL", "severity": "HIGH", "detail": f"{ep} failed: {r.get('error','')}"})
    return issues


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    market = _ist_market_open()
    results: Dict[str, Any] = {}
    for ep in ENDPOINTS:
        timeout = 120 if "/api/chain/" in ep else 90
        results[ep] = _fetch(f"{CLOUD}{ep}", timeout=timeout)

    issues = _issues(results, market)
    payload = {
        "generated_utc": _utc(),
        "cloud_url": CLOUD,
        "market": market,
        "endpoints": {k: {"ok": v.get("ok"), "error": v.get("error")} for k, v in results.items()},
        "auto_gates_passing": (results.get("/api/auto_gates", {}).get("data") or {}).get("gates_passing"),
        "auto_gates_total": (results.get("/api/auto_gates", {}).get("data") or {}).get("gates_total"),
        "issues": issues,
        "issue_count": len(issues),
        "pass": len(issues) == 0,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# UI Market Cross Verify",
        "",
        f"IST market open: **{market['is_open']}**",
        f"Issues: **{len(issues)}**",
        "",
    ]
    for i in issues:
        lines.append(f"- [{i['severity']}] {i['id']}: {i['detail']}")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"pass": payload["pass"], "issues": len(issues)}, indent=2))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
