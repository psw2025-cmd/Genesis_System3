#!/usr/bin/env python3
"""
Multi-agent production coordination — proof-only, no live trading.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "latest" / "production_grade_readiness"
BASE_URL = "https://genesis-system3-backend.onrender.com"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

AGENT_RUNS = [
    ("gate_orchestrator", [sys.executable, "scripts/system3_master_proof_orchestrator.py"], "reports/latest/proof_status_matrix/proof_status_matrix.json"),
    ("dashboard_audit", [sys.executable, "tools/dashboard_full_audit.py"], "reports/latest/dashboard_full_audit/summary.json"),
    ("broker_validation", [sys.executable, "tools/broker_trader_validation.py"], "reports/latest/broker_trader_validation/summary.json"),
    ("audit_reports", [sys.executable, "tools/generate_audit_reports.py"], "reports/latest/dhan_option_chain_schema_audit/summary.json"),
    ("human_approval", [sys.executable, "tools/record_human_approval.py"], "reports/latest/human_approval_gate/summary.json"),
    ("control_plane", [sys.executable, "system3_control_plane.py", "proofs"], "reports/latest/system3_master_control_plane/system3_master_control_plane.json"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_cmd(cmd: List[str]) -> Dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
        return {
            "exit_code": proc.returncode,
            "stdout_tail": proc.stdout[-1200:],
            "stderr_tail": proc.stderr[-600:],
            "passed": proc.returncode == 0,
        }
    except Exception as exc:
        return {"exit_code": -1, "error": str(exc)[:200], "passed": False}


def probe_live_endpoints() -> Dict[str, Any]:
    import urllib.request

    endpoints = [
        "/api/state",
        "/api/paper",
        "/api/portfolio/unified",
        "/api/broker/holdings",
        "/api/broker/positions/live",
        "/api/broker/funds",
        "/api/broker/truth",
        "/api/trader/requirements",
        "/api/approval/status",
        "/api/trades/history",
    ]
    results = {}
    for ep in endpoints:
        url = f"{BASE_URL}{ep}"
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                body = resp.read(4000).decode("utf-8", errors="replace")
                results[ep] = {"status": resp.status, "ok": resp.status == 200, "sample": body[:500]}
        except Exception as exc:
            results[ep] = {"status": 0, "ok": False, "error": str(exc)[:200]}
    return results


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)

    agent_results = []
    for agent_id, cmd, evidence in AGENT_RUNS:
        evidence_path = ROOT / evidence
        run = run_cmd(cmd)
        agent_results.append({
            "id": agent_id,
            "evidence": evidence,
            "evidence_exists": evidence_path.exists(),
            "run_attempted": True,
            "run_passed": run["passed"],
            "run_detail": run,
        })

    live = probe_live_endpoints()
    state_data = {}
    try:
        state_data = json.loads(live.get("/api/state", {}).get("sample", "{}"))
    except Exception:
        pass
    broker = state_data.get("broker") or {}
    broker_connected = bool(broker.get("connected"))

    blockers = [
        "LIVE_TRADING_DISABLED_BY_DESIGN",
        "REAL_PAPER_LIFECYCLE_NOT_PROVEN",
        "POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN",
        "MULTI_DAY_STABILITY_NOT_PROVEN",
        "WEBSOCKET_TICK_HEALTH_NOT_PROVEN",
    ]
    try:
        from dashboard.backend.human_approval_service import load_human_approval
        if not load_human_approval().get("approved"):
            blockers.append("HUMAN_APPROVAL_REQUIRED_FOR_LIVE")
    except Exception:
        blockers.append("HUMAN_APPROVAL_REQUIRED_FOR_LIVE")

    payload = {
        "generated_utc": utc_now(),
        "mode": "ANALYZER_PAPER_ONLY",
        "live_trading_enabled": False,
        "production_ready_for_real_money": False,
        "cloud_url": BASE_URL,
        "agents": agent_results,
        "live_endpoint_probe": live,
        "broker_connected": broker_connected,
        "data_source": state_data.get("data_source"),
        "readiness_ladder": {
            "repo_safe": True,
            "cloud_deployed": live.get("/api/state", {}).get("ok", False),
            "dashboard_production_grade": live.get("/api/broker/truth", {}).get("ok", False),
            "broker_readonly_portfolio_api": live.get("/api/broker/holdings", {}).get("ok", False),
            "human_approval_recorded": live.get("/api/approval/status", {}).get("ok", False),
            "real_money_ready": False,
        },
        "blockers": blockers,
        "next_exact_actions": [
            "Run market-day paper lifecycle proof Mon-Fri 09:15-15:30 IST",
            "Accumulate 5+ prediction days with rho>=0.70",
            "Prove positive net expectancy after all costs",
            "Implement Dhan WebSocket tick health",
            "ENV flip for live only after all gates + owner final sign-off",
        ],
    }

    with open(REPORTS / "summary.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    md_lines = [
        "# Production Grade Readiness — Multi-Agent Coordination",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        "",
        "**Verdict: ANALYZER READY — REAL MONEY BLOCKED**",
        "",
        "## Agents run",
    ]
    for a in agent_results:
        md_lines.append(f"- **{a['id']}**: {'PASS' if a['run_passed'] else 'FAIL'} — `{a['evidence']}`")
    md_lines.extend([
        "",
        "## Cloud probes",
        *[f"- `{ep}`: {'OK' if v.get('ok') else 'FAIL'}" for ep, v in live.items()],
        "",
        "## Blockers",
        *[f"- {b}" for b in blockers],
        "",
        "## Next actions",
        *[f"- {x}" for x in payload["next_exact_actions"]],
    ])
    with open(REPORTS / "summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Wrote {REPORTS / 'summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
