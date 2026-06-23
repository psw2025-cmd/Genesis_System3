#!/usr/bin/env python3
"""
Multi-agent production coordination — proof-only, no live trading.

Coordinates existing agents/runners and publishes a single readiness report.
Does NOT enable live trading or place broker orders.
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

AGENTS = [
    {
        "id": "gate_orchestrator",
        "role": "8-gate proof matrix",
        "runner": "scripts/system3_master_proof_orchestrator.py",
        "output": "reports/latest/proof_status_matrix/proof_status_matrix.json",
    },
    {
        "id": "truth_bridge",
        "role": "Live cloud API truth",
        "runner": "tools/run_truth_bridge_powershell.bat",
        "output": "reports/latest/system3_truth_bridge/summary.json",
    },
    {
        "id": "dhan_schema_audit",
        "role": "Dhan option-chain schema",
        "runner": "tools/generate_audit_reports.py",
        "output": "reports/latest/dhan_option_chain_schema_audit/summary.json",
    },
    {
        "id": "dashboard_browser",
        "role": "Playwright UI proof",
        "runner": "tools/run_dashboard_proof.bat",
        "output": "reports/latest/dashboard_browser_proof/summary.json",
    },
    {
        "id": "geni_orchestrator",
        "role": "Internal task coordination (AUTO_EXECUTE_REAL_TRADES=False)",
        "runner": None,
        "output": "core/geni/geni_config.py",
    },
    {
        "id": "control_plane",
        "role": "Repo authority + master control",
        "runner": "system3_control_plane.py",
        "output": "reports/latest/system3_master_control_plane/system3_master_control_plane.json",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_cmd(cmd: List[str], cwd: Path) -> Dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
        return {
            "exit_code": proc.returncode,
            "stdout_tail": proc.stdout[-1500:],
            "stderr_tail": proc.stderr[-800:],
            "passed": proc.returncode == 0,
        }
    except Exception as exc:
        return {"exit_code": -1, "error": str(exc), "passed": False}


def probe_live_endpoints() -> Dict[str, Any]:
    import urllib.request

    endpoints = [
        "/api/state",
        "/api/paper",
        "/api/portfolio/unified",
        "/api/broker/holdings",
        "/api/broker/positions/live",
        "/api/trades/history",
    ]
    results = {}
    for ep in endpoints:
        url = f"{BASE_URL}{ep}"
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                body = resp.read(4000).decode("utf-8", errors="replace")
                results[ep] = {"status": resp.status, "ok": resp.status == 200, "sample": body[:500]}
        except Exception as exc:
            results[ep] = {"status": 0, "ok": False, "error": str(exc)[:200]}
    return results


def load_json(path: Path) -> Dict[str, Any]:
    if path.exists():
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    return {}


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)

    agent_results = []
    for agent in AGENTS:
        evidence_path = ROOT / agent["output"] if agent["output"] else None
        result = {
            "id": agent["id"],
            "role": agent["role"],
            "evidence": agent["output"],
            "evidence_exists": evidence_path.exists() if evidence_path else False,
            "run_attempted": False,
            "run_passed": None,
        }
        if agent["runner"] and agent["runner"].endswith(".py"):
            py = ROOT / agent["runner"]
            if py.exists():
                result["run_attempted"] = True
                run = run_cmd([sys.executable, str(py)], ROOT)
                result["run_passed"] = run["passed"]
                result["run_detail"] = run
        agent_results.append(result)

    live = probe_live_endpoints()
    truth = load_json(ROOT / "reports/latest/system3_truth_bridge/latest.json")
    state = (truth.get("live") or {}).get("state", {}).get("data", {})
    broker = state.get("broker") or {}

    blockers = [
        "LIVE_TRADING_DISABLED_BY_DESIGN",
        "REAL_PAPER_LIFECYCLE_NOT_PROVEN",
        "POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN",
        "MULTI_DAY_STABILITY_NOT_PROVEN",
        "HUMAN_APPROVAL_REQUIRED_FOR_LIVE",
    ]
    if not broker.get("connected"):
        blockers.append("BROKER_NOT_CONNECTED")

    payload = {
        "generated_utc": utc_now(),
        "mode": "ANALYZER_PAPER_ONLY",
        "live_trading_enabled": False,
        "production_ready_for_real_money": False,
        "cloud_url": BASE_URL,
        "agents": agent_results,
        "live_endpoint_probe": live,
        "broker_connected": broker.get("connected"),
        "data_source": state.get("data_source"),
        "readiness_ladder": {
            "repo_safe": True,
            "cloud_deployed": live.get("/api/state", {}).get("ok", False),
            "dashboard_production_grade": live.get("/api/portfolio/unified", {}).get("ok", False),
            "broker_readonly_portfolio_api": live.get("/api/broker/holdings", {}).get("ok", False),
            "real_money_ready": False,
        },
        "blockers": blockers,
        "next_exact_actions": [
            "Deploy this branch to Render (portfolio unified API + dashboard panel)",
            "Run market-day paper lifecycle proof Mon-Fri 09:30-15:30 IST",
            "Prove positive net expectancy after brokerage/STT/slippage",
            "Accumulate 5+ prediction accuracy days with rho>=0.70",
            "Explicit human sign-off before LIVE_TRADING_ENABLED (never auto)",
        ],
    }

    with open(REPORTS / "summary.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    md_lines = [
        "# Production Grade Readiness — Multi-Agent Coordination",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        "",
        "**Verdict: NOT READY FOR REAL MONEY** (live trading remains disabled)",
        "",
        "## Agent coordination map",
    ]
    for a in agent_results:
        md_lines.append(f"- **{a['id']}** ({a['role']}) — evidence: `{a['evidence']}`")
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
