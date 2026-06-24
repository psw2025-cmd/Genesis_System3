"""
Auto gates service — production-grade prediction/profit/lifecycle blocker truth for dashboard API.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
GATES_JSON = ROOT / "reports" / "latest" / "system3_auto_gates" / "summary.json"
FRICTION_JSON = ROOT / "reports" / "latest" / "friction_expectancy" / "summary.json"
VIABILITY_JSON = ROOT / "reports" / "latest" / "production_viability_bridge" / "latest.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _evaluate_inline(live_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    from scripts.runtime_gate_proofs import ensure_runtime_proofs
    from scripts.system3_gate_evaluator import evaluate_all, write_reports

    try:
        ensure_runtime_proofs(ROOT, live_state=live_state)
    except Exception:
        pass
    payload = evaluate_all(ROOT, live_state=live_state)
    try:
        write_reports(ROOT, payload)
    except Exception:
        pass
    return payload


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
        if gid == "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS":
            note = f"{g.get('days_recorded', 0)}/{g.get('days_required', 5)} days · ρ={g.get('latest_rho')} · need ≥{g.get('threshold', 0.7)}"
        elif gid == "POSITIVE_NET_EXPECTANCY_AFTER_COSTS":
            note = f"expectancy={g.get('net_expectancy_after_costs')} · win_rate={g.get('win_rate')}"
        elif gid == "REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF":
            note = "proven" if g.get("full_lifecycle_proven") else "market-session proof pending"
        elif gid == "WEBSOCKET_TICK_HEALTH_PROVEN":
            note = f"tick_age={g.get('last_tick_age_sec')}s refresh={g.get('refresh_interval_sec')}s"
        else:
            note = g.get("auto_action") or ""
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


def build_auto_gates_report(
    refresh: bool = True,
    live_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if refresh or not GATES_JSON.exists():
        try:
            payload = _evaluate_inline(live_state)
        except Exception:
            payload = _read(GATES_JSON) or {}
    else:
        age = datetime.now(timezone.utc).timestamp() - GATES_JSON.stat().st_mtime
        if age > 300:
            try:
                payload = _evaluate_inline(live_state)
            except Exception:
                payload = _read(GATES_JSON) or {}
        else:
            payload = _read(GATES_JSON) or {}

    if not payload.get("gates"):
        try:
            payload = _evaluate_inline(live_state)
        except Exception:
            pass

    friction = _read(FRICTION_JSON) or {}
    viability = _read(VIABILITY_JSON) or {}
    proof_gates = _proof_gates_from_payload(payload)
    passing = payload.get("gates_passing")
    if passing is None:
        passing = sum(1 for p in proof_gates if p.get("pass"))

    market = (live_state or {}).get("market") or {}
    return {
        "generated_utc": payload.get("generated_utc") or _utc(),
        "status": "ok",
        "source": "inline_gate_evaluator",
        "runtime_driven": True,
        "market_open": market.get("is_open"),
        "market_reason": market.get("reason"),
        "broker_connected": (live_state or {}).get("broker", {}).get("connected"),
        "gates": payload.get("gates") or {},
        "gates_passing": passing,
        "gates_total": payload.get("gates_total") or len(proof_gates),
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
