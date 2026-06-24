#!/usr/bin/env python3
"""
System3 Full Auto Coordinator — prediction accuracy + profit blockers + AI agent coordination.

Runs all automatable proofs, tests, gate evaluation, and remediation without human input.
Does NOT enable live trading or modify secrets/.env.

Usage:
  python tools/system3_auto_coordinator.py
  python tools/system3_auto_coordinator.py --full
  python tools/system3_auto_coordinator.py --api-base https://genesis-system3-backend.onrender.com

Outputs:
  reports/latest/system3_auto_coordinator/summary.json
  reports/latest/system3_auto_coordinator/summary.md
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "system3_auto_coordinator"
DEFAULT_CLOUD = "https://genesis-system3-backend.onrender.com"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _run(cmd: Sequence[str], timeout: int = 600, env: Optional[dict] = None) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            list(cmd),
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return {
            "cmd": list(cmd),
            "passed": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-2000:],
            "stderr_tail": (proc.stderr or "")[-800:],
        }
    except Exception as exc:
        return {"cmd": list(cmd), "passed": False, "exit_code": -1, "error": str(exc)[:300]}


def _market_session_open() -> bool:
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    if now.weekday() >= 5:
        return False
    minutes = now.hour * 60 + now.minute
    return 9 * 60 + 15 <= minutes <= 15 * 60 + 30


def _missing(path: str) -> bool:
    return not (ROOT / path).exists()


def _plan_auto_actions(api_base: str, full: bool) -> List[Tuple[str, List[str]]]:
    actions: List[Tuple[str, List[str]]] = []
    py = sys.executable

    if _missing("reports/latest/markdown_inventory.json"):
        actions.append(("markdown_inventory", [py, "scripts/system3_markdown_inventory.py"]))

    if _missing("reports/latest/markdown_inventory.json") or _missing("reports/latest/model_accuracy_report.json"):
        actions.append(("control_plane", [py, "scripts/system3_control_plane_runner.py", "--api-base", api_base]))

    if _missing("reports/latest/model_accuracy_report.json"):
        actions.append(("model_accuracy", [py, "scripts/system3_model_accuracy_tracker.py", "--api-base", api_base]))

    if _missing("reports/latest/option_strike_visibility.json"):
        actions.append(("option_visibility", [py, "scripts/system3_option_visibility_audit.py", "--api-base", api_base]))

    actions.append(("friction_expectancy", [py, "scripts/system3_friction_expectancy_proof.py"]))
    actions.append(("websocket_tick_health", [py, "scripts/websocket_tick_health_proof.py"]))

    if (ROOT / "state" / "retrain_signal.json").exists():
        actions.append(("auto_retrain", [py, "scripts/auto_retrain.py"]))

    if _market_session_open():
        actions.append(("paper_lifecycle", [py, "scripts/paper_lifecycle_proof.py"]))

    actions.append(("model_to_trade_gap", [py, "scripts/system3_model_to_trade_gap_proof.py"]))
    actions.append(("post_market_pipeline", [py, "scripts/system3_post_market_auto_pipeline.py"]))
    actions.append(("blocker_finder", [py, "scripts/system3_blocker_finder.py", "--api-base", api_base]))
    actions.append(("viability_bridge", [py, "scripts/system3_production_viability_bridge.py"]))
    actions.append(("local_review", [py, "tools/local_code_review.py"]))
    actions.append(("pytest", [py, "-m", "pytest", "tests/", "-q", "--tb=no"]))

    if full:
        actions.extend([
            ("master_orchestrator", [py, "scripts/system3_master_proof_orchestrator.py"]),
            ("dashboard_audit", [py, "tools/dashboard_full_audit.py"]),
            ("broker_validation", [py, "tools/broker_trader_validation.py"]),
        ])
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description="System3 full auto coordinator")
    parser.add_argument("--full", action="store_true", help="Run extended proof pack")
    parser.add_argument("--api-base", default=os.environ.get("SYSTEM3_API_BASE", DEFAULT_CLOUD))
    args = parser.parse_args()
    api_base = args.api_base.rstrip("/")

    OUT.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["SYSTEM3_API_BASE"] = api_base
    env.setdefault("LIVE_TRADING_ENABLED", "0")
    env.setdefault("SYSTEM3_LIVE_TRADING_ALLOWED", "0")

    agent_results: List[Dict[str, Any]] = []
    for name, cmd in _plan_auto_actions(api_base, args.full):
        result = _run(cmd, env=env)
        result["agent"] = name
        agent_results.append(result)
        print(f"[{'PASS' if result['passed'] else 'FAIL'}] {name}")

    gates_path = ROOT / "reports" / "latest" / "system3_auto_gates" / "summary.json"
    gates: Dict[str, Any] = {}
    if gates_path.exists():
        try:
            gates = json.loads(gates_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    agents_passed = sum(1 for a in agent_results if a.get("passed"))
    critical_fail = [
        a for a in agent_results
        if not a.get("passed") and a.get("agent") in ("pytest", "blocker_finder", "model_accuracy")
    ]
    payload = {
        "generated_utc": _utc(),
        "mode": "FULL_AUTO_COORDINATION",
        "api_base": api_base,
        "market_session_open": _market_session_open(),
        "live_trading_enabled": False,
        "agents": agent_results,
        "agents_passed": agents_passed,
        "agents_total": len(agent_results),
        "gates": gates,
        "prediction_accuracy_blocked": gates.get("prediction_accuracy_blocked", True),
        "profit_blocked": gates.get("profit_blocked", True),
        "lifecycle_blocked": gates.get("lifecycle_blocked", True),
        "trade_ready": gates.get("trade_ready", False),
        "analyzer_ready": gates.get("analyzer_ready", False),
        "open_blockers": gates.get("open_blockers", []),
        "technical_gates_still_required": gates.get("technical_gates_still_required", []),
        "verdict": (
            "AUTO_COORDINATION_COMPLETE_ANALYZER_READY"
            if gates.get("analyzer_ready")
            else "AUTO_COORDINATION_COMPLETE_PROOFS_PENDING"
        ),
        "human_required": [],
        "permanent_safety": ["LIVE_TRADING_DISABLED_BY_DESIGN"],
    }
    if not _market_session_open():
        payload["human_required"] = []  # no human — market session tasks auto-scheduled
        payload["market_session_auto_scheduled"] = [
            "daily_gain_validate 15:35 IST",
            "paper_lifecycle_proof 09:30 IST",
        ]

    (OUT / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# System3 Auto Coordinator",
        "",
        f"Generated: `{payload['generated_utc']}`",
        f"Verdict: **{payload['verdict']}**",
        f"Agents: **{agents_passed}/{len(agent_results)}** PASS",
        f"Gates: **{gates.get('gates_passing', 0)}/{gates.get('gates_total', 0)}**",
        "",
        "## Prediction / Profit blockers",
        f"- Prediction accuracy blocked: `{payload['prediction_accuracy_blocked']}`",
        f"- Profit blocked: `{payload['profit_blocked']}`",
        f"- Lifecycle blocked: `{payload['lifecycle_blocked']}`",
        "",
        "## Agents",
    ]
    for a in agent_results:
        lines.append(f"- **{a['agent']}**: {'PASS' if a.get('passed') else 'FAIL'}")
    lines.extend(["", "## Open blockers", ""])
    for b in payload.get("open_blockers") or []:
        lines.append(f"- `{b}`")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT / 'summary.md'}")
    return 0 if not critical_fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
