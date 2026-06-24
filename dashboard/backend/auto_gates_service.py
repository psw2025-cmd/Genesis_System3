"""
Auto gates service — production-grade prediction/profit/lifecycle blocker truth for dashboard API.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
GATES_JSON = ROOT / "reports" / "latest" / "system3_auto_gates" / "summary.json"
FRICTION_JSON = ROOT / "reports" / "latest" / "friction_expectancy" / "summary.json"
VIABILITY_JSON = ROOT / "reports" / "latest" / "production_viability_bridge" / "latest.json"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _refresh_gates(max_age_sec: int = 300) -> None:
    if GATES_JSON.exists():
        age = datetime.now(timezone.utc).timestamp() - GATES_JSON.stat().st_mtime
        if age < max_age_sec:
            return
    script = ROOT / "scripts" / "system3_gate_evaluator.py"
    if script.exists():
        subprocess.run([sys.executable, str(script)], cwd=ROOT, capture_output=True, timeout=120)


def _proof_gates_from_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    gates = payload.get("gates") or {}
    mapping = [
        ("ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS", "ML Accuracy (Spearman ρ)"),
        ("POSITIVE_NET_EXPECTANCY_AFTER_COSTS", "Profit / Expectancy"),
        ("REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF", "Paper Lifecycle"),
        ("WEBSOCKET_TICK_HEALTH_PROVEN", "Tick / Data Freshness"),
        ("MODEL_ACCURACY_REPORT_PRESENT", "Model Accuracy Report"),
        ("OPTION_STRIKE_VISIBILITY_PROVEN", "Option Strike Visibility"),
        ("EQUITY_FO_ELIGIBILITY_PROVEN", "Equity F&O Eligibility"),
    ]
    out: List[Dict[str, Any]] = []
    for gid, label in mapping:
        g = gates.get(gid) or {}
        ok = bool(g.get("pass"))
        note = g.get("auto_action") or ""
        if gid == "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS":
            note = f"{g.get('days_recorded', 0)}/{g.get('days_required', 5)} days · ρ={g.get('latest_rho')} · need ≥{g.get('threshold', 0.7)}"
        elif gid == "POSITIVE_NET_EXPECTANCY_AFTER_COSTS":
            note = f"expectancy={g.get('net_expectancy_after_costs')} · win_rate={g.get('win_rate')}"
        elif gid == "REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF":
            note = "proven" if g.get("full_lifecycle_proven") else "market-session proof pending"
        out.append(
            {
                "name": label,
                "gate_id": gid,
                "status": "PASS" if ok else "PEND",
                "pass": ok,
                "note": note,
                "blocker_id": g.get("blocker_id"),
            }
        )
    return out


def build_auto_gates_report(refresh: bool = True) -> Dict[str, Any]:
    if refresh:
        _refresh_gates()
    payload = _read(GATES_JSON) or {}
    friction = _read(FRICTION_JSON) or {}
    viability = _read(VIABILITY_JSON) or {}

    proof_gates = _proof_gates_from_payload(payload)
    passing = sum(1 for p in proof_gates if p.get("pass"))
    total = len(proof_gates)

    return {
        "generated_utc": payload.get("generated_utc") or _utc(),
        "status": "ok",
        "source": "reports/latest/system3_auto_gates/summary.json",
        "runtime_driven": True,
        "gates": payload.get("gates") or {},
        "gates_passing": passing,
        "gates_total": total,
        "proof_gates": proof_gates,
        "open_blockers": payload.get("open_blockers") or [],
        "prediction_accuracy_blocked": payload.get("prediction_accuracy_blocked", True),
        "profit_blocked": payload.get("profit_blocked", True),
        "lifecycle_blocked": payload.get("lifecycle_blocked", True),
        "trade_ready": payload.get("trade_ready", False),
        "analyzer_ready": payload.get("analyzer_ready", False),
        "technical_gates_still_required": payload.get("technical_gates_still_required") or [],
        "recommended_auto_actions": payload.get("recommended_auto_actions") or [],
        "friction_expectancy": friction.get("evidence") or {},
        "strategy_quarantined": (viability.get("summary") or {}).get("strategy_quarantined_for_live", True),
        "production_live_ready": False,
        "live_trading_enabled": False,
        "permanent_safety": ["LIVE_TRADING_DISABLED_BY_DESIGN"],
    }
