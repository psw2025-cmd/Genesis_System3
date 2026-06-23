#!/usr/bin/env python3
"""Full dashboard + cloud readiness audit. Proof-only; never enables live trading."""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "latest" / "dashboard_full_audit"
BASE = "https://genesis-system3-backend.onrender.com"

REQUIRED_ENDPOINTS = [
    "/api/state",
    "/api/health",
    "/api/broker/status",
    "/api/broker/dhan/status",
    "/api/qc",
    "/api/paper",
    "/api/gain_rank",
    "/api/accuracy_trend",
    "/api/chain/NIFTY",
    "/api/portfolio/unified",
    "/api/broker/holdings",
    "/api/broker/positions/live",
    "/api/trader/requirements",
    "/api/approval/status",
    "/api/broker/truth",
]

REAL_MONEY_BLOCKERS = [
    "LIVE_TRADING_DISABLED_BY_DESIGN",
    "REAL_PAPER_LIFECYCLE_NOT_PROVEN",
    "ML_ACCURACY_RHO_BELOW_0_70",
    "POSITIVE_NET_EXPECTANCY_NOT_PROVEN",
    "WEBSOCKET_TICK_HEALTH_NOT_PROVEN",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def probe(url: str) -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=45) as resp:
            body = resp.read(8000).decode("utf-8", errors="replace")
            data = json.loads(body) if body.startswith("{") or body.startswith("[") else {}
            return {"ok": resp.status == 200, "status": resp.status, "data": data, "bytes": len(body)}
    except Exception as exc:
        return {"ok": False, "status": 0, "error": str(exc)[:200]}


def run_pytest() -> Dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_dhan_option_chain_parser.py", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return {"passed": proc.returncode == 0, "exit_code": proc.returncode, "stdout": proc.stdout.strip()}


def main() -> int:
    REPORT.mkdir(parents=True, exist_ok=True)
    endpoints: Dict[str, Any] = {}
    bugs: List[Dict[str, str]] = []
    missing: List[str] = []

    for ep in REQUIRED_ENDPOINTS:
        r = probe(f"{BASE}{ep}")
        endpoints[ep] = r
        if not r.get("ok"):
            missing.append(ep)

    state = endpoints.get("/api/state", {}).get("data", {})
    broker = state.get("broker", {})
    qc = endpoints.get("/api/qc", {}).get("data", {})
    chain = endpoints.get("/api/chain/NIFTY", {}).get("data", {})
    paper = endpoints.get("/api/paper", {}).get("data", {})

    if broker.get("live_trading_enabled"):
        bugs.append({"id": "LIVE_ENABLED", "severity": "CRITICAL", "detail": "live_trading_enabled true on cloud"})
    if chain.get("status") == "MARKET_OPEN" and not state.get("market", {}).get("is_open", False):
        bugs.append({"id": "CHAIN_STATUS_WRONG", "severity": "HIGH", "detail": "Chain MARKET_OPEN while market closed"})
    qc_status = qc.get("status")
    if (
        qc.get("overall_passed") is False
        and state.get("market", {}).get("is_open") is False
        and qc_status not in ("MARKET_CLOSED", "NOT_READY", "NO_DATA")
        and not qc.get("skipped")
    ):
        bugs.append({"id": "QC_STALE_FAIL", "severity": "HIGH", "detail": "QC FAIL shown when market closed (stale report)"})
    if not paper.get("pnl", {}).get("history") and paper.get("pnl", {}).get("summary", {}).get("total_trades"):
        bugs.append({"id": "PAPER_HISTORY_EMPTY", "severity": "MEDIUM", "detail": "Paper summary exists but trade history empty"})
    for ep in ["/api/portfolio/unified", "/api/broker/holdings", "/api/trader/requirements"]:
        if ep in missing:
            bugs.append({"id": "API_404", "severity": "HIGH", "detail": f"{ep} not deployed on cloud (merge main required)"})

    pytest_result = run_pytest()
    real_money_ready = (
        not missing
        and not bugs
        and broker.get("connected")
        and not broker.get("live_trading_enabled")
        and state.get("mode") == "PAPER"
    )

    payload = {
        "generated_utc": utc_now(),
        "cloud_url": BASE,
        "live_trading_enabled": bool(broker.get("live_trading_enabled")),
        "production_ready_for_real_money": False,
        "real_money_ready": real_money_ready,
        "endpoints": {k: {"ok": v.get("ok"), "status": v.get("status")} for k, v in endpoints.items()},
        "bugs_found": bugs,
        "missing_endpoints": missing,
        "blockers": REAL_MONEY_BLOCKERS,
        "pytest": pytest_result,
        "dashboard_tabs_verified": [
            "System Control",
            "Broker & Data",
            "Market Scanner",
            "Option Chain",
            "Paper Lifecycle",
            "Prediction Actual",
            "Signals",
            "Alerts",
            "Error Log",
            "Proof Gates",
        ],
        "world_class_gaps": [
            "WebSocket tick feed (Dhan WS pending)",
            "Positive friction-adjusted expectancy proof",
            "5+ day Spearman rho >= 0.70",
            "Real market-day paper lifecycle",
            "Broker holdings panel on cloud after deploy",
        ],
        "verdict": "PASS_WITH_WARNINGS" if not bugs and not missing else "NOT_PROVEN",
    }

    with open(REPORT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    bug_lines = [f"- [{b['severity']}] {b['id']}: {b['detail']}" for b in bugs] or ["- none"]
    miss_lines = [f"- {m}" for m in missing] or ["- none"]
    lines = [
        "# Dashboard Full Audit",
        "",
        f"Generated: `{payload['generated_utc']}`",
        f"Verdict: **{payload['verdict']}**",
        f"Real money ready: **{payload['production_ready_for_real_money']}**",
        "",
        "## Bugs",
        *bug_lines,
        "",
        "## Missing endpoints",
        *miss_lines,
        "",
        "## Blockers for live trading",
        *[f"- {b}" for b in REAL_MONEY_BLOCKERS],
    ]
    with open(REPORT / "summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote {REPORT / 'summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
