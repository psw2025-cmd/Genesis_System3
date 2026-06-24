#!/usr/bin/env python3
"""
Evaluate prediction-accuracy, profit, and lifecycle gates from on-disk proof artifacts.

Outputs:
  reports/latest/system3_auto_gates/summary.json
  reports/latest/system3_auto_gates/summary.md

Read-only except optional sync of human_approval technical gates (--sync-gates).
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "system3_auto_gates"
SPEARMAN_THRESHOLD = 0.70
SPEARMAN_DAYS_REQUIRED = 5
HUMAN_GATE_PATH = ROOT / "config" / "human_approval_gate.json"

GATE_IDS = [
    "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS",
    "POSITIVE_NET_EXPECTANCY_AFTER_COSTS",
    "REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF",
    "WEBSOCKET_TICK_HEALTH_PROVEN",
    "MODEL_ACCURACY_REPORT_PRESENT",
    "OPTION_STRIKE_VISIBILITY_PROVEN",
    "EQUITY_FO_ELIGIBILITY_PROVEN",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _spearman_from_validation(data: Dict[str, Any]) -> Optional[float]:
    for key in ("rank_correlation_spearman", "spearman_correlation", "spearman_rho", "rho"):
        val = data.get(key)
        if val is not None:
            try:
                return float(val)
            except (TypeError, ValueError):
                pass
    return None


def load_spearman_days(root: Path) -> Tuple[List[Dict[str, Any]], int, Optional[float]]:
    mv_dir = root / "state" / "market_validations"
    days: List[Dict[str, Any]] = []
    if not mv_dir.exists():
        return days, 0, None
    for path in sorted(mv_dir.glob("*.json")):
        data = _read_json(path)
        if not data:
            continue
        rho = _spearman_from_validation(data)
        if rho is None:
            continue
        days.append({
            "date": data.get("date") or path.stem.replace("market_validation_", ""),
            "rho": round(rho, 4),
            "hit_rate": data.get("hit_rate"),
            "status": data.get("status"),
            "pass": rho >= SPEARMAN_THRESHOLD,
        })
    passing = sum(1 for d in days if d["pass"])
    latest_rho = days[-1]["rho"] if days else None
    return days, passing, latest_rho


def eval_spearman_gate(root: Path) -> Dict[str, Any]:
    days, passing, latest = load_spearman_days(root)
    consecutive_pass = 0
    for d in reversed(days):
        if d["pass"]:
            consecutive_pass += 1
        else:
            break
    ok = passing >= SPEARMAN_DAYS_REQUIRED
    return {
        "gate_id": "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS",
        "pass": ok,
        "days_recorded": len(days),
        "days_passing_threshold": passing,
        "days_required": SPEARMAN_DAYS_REQUIRED,
        "threshold": SPEARMAN_THRESHOLD,
        "latest_rho": latest,
        "consecutive_pass_days": consecutive_pass,
        "blocker_id": None if ok else "SYS3-BLK-005",
        "auto_action": "Run daily_gain_validate at 15:35 IST weekdays; auto_retrain if rho<0.40 x3 days",
        "days": days[-14:],
    }


def eval_expectancy_gate(root: Path) -> Dict[str, Any]:
    path = root / "reports" / "latest" / "friction_expectancy" / "summary.json"
    data = _read_json(path) or {}
    ev = data.get("evidence") or {}
    net = ev.get("net_expectancy_after_costs")
    try:
        net_f = float(net) if net is not None else None
    except (TypeError, ValueError):
        net_f = None
    ok = data.get("pass") is True and net_f is not None and net_f > 0
    return {
        "gate_id": "POSITIVE_NET_EXPECTANCY_AFTER_COSTS",
        "pass": ok,
        "report_exists": path.exists(),
        "net_expectancy_after_costs": net_f,
        "win_rate": ev.get("win_rate"),
        "trade_count": ev.get("trade_count"),
        "blocker_id": None if ok else "PROFIT_BLOCKER",
        "auto_action": "Run scripts/system3_friction_expectancy_proof.py after paper trades accumulate",
    }


def eval_lifecycle_gate(root: Path, live_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    path = root / "reports" / "latest" / "analyzer_paper_lifecycle_proof" / "summary.json"
    data = _read_json(path) or {}
    ev = data.get("evidence") or {}
    broker_connected = ev.get("lifecycle_proof_broker_not_connected") is not True
    if live_state:
        broker_connected = bool((live_state.get("broker") or {}).get("connected"))
    full_proven = ev.get("full_lifecycle_proven") is True
    if not full_proven and live_state and broker_connected:
        positions = live_state.get("positions") or []
        if positions and all(
            isinstance(p, dict) and p.get("strike") and p.get("entry_price") and p.get("position_id")
            for p in positions
        ):
            full_proven = True
    ok = (
        (data.get("pass") is True or full_proven)
        and full_proven
        and ev.get("lifecycle_proof_dry_run") is not True
        and broker_connected
    )
    market_open = bool((live_state or {}).get("market", {}).get("is_open"))
    return {
        "gate_id": "REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF",
        "pass": ok,
        "report_exists": path.exists(),
        "full_lifecycle_proven": full_proven,
        "broker_connected": broker_connected,
        "market_open": market_open,
        "blocker_id": None if ok else "SYS3-BLK-008",
        "auto_action": "Run scripts/paper_lifecycle_proof.py during market hours with broker connected",
    }


def eval_tick_health_gate(root: Path, live_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    path = root / "reports" / "latest" / "websocket_tick_health" / "summary.json"
    data = _read_json(path) or {}
    ev = data.get("evidence") or {}
    tick_age = ev.get("last_tick_age_sec")
    refresh = ev.get("refresh_interval_sec")
    broker_ok = ev.get("broker_connected")
    if live_state:
        tick_age = live_state.get("last_tick_age_sec") or (live_state.get("tick_health") or {}).get("last_tick_age_sec") or tick_age
        refresh = live_state.get("refresh_interval") or (live_state.get("tick_health") or {}).get("refresh_interval_sec") or refresh
        broker_ok = (live_state.get("broker") or {}).get("connected") if broker_ok is None else broker_ok
    rest_ok = refresh is not None and float(refresh) <= 10
    ok = data.get("pass") is True or (
        rest_ok and broker_ok and tick_age is not None and float(tick_age) <= 15
    )
    return {
        "gate_id": "WEBSOCKET_TICK_HEALTH_PROVEN",
        "pass": ok,
        "report_exists": path.exists(),
        "last_tick_age_sec": tick_age,
        "refresh_interval_sec": refresh,
        "blocker_id": None if ok else "TICK_HEALTH_BLOCKER",
        "auto_action": "REST poll ≤10s counts for analyzer; WebSocket stream for live execution",
    }


def eval_model_accuracy_report(root: Path) -> Dict[str, Any]:
    path = root / "reports" / "latest" / "model_accuracy_report.json"
    data = _read_json(path) or {}
    summary = data.get("summary") or {}
    rows = summary.get("rows", 0)
    try:
        rows = int(rows)
    except (TypeError, ValueError):
        rows = 0
    ok = path.exists() and rows > 0
    spearman_days, passing, _ = load_spearman_days(root)
    return {
        "gate_id": "MODEL_ACCURACY_REPORT_PRESENT",
        "pass": ok,
        "report_exists": path.exists(),
        "rows": rows,
        "validation_days": len(spearman_days),
        "spearman_days_passing": passing,
        "blocker_id": None if ok else "SYS3-BLK-005",
        "auto_action": "Run scripts/system3_model_accuracy_tracker.py --api-base $CLOUD",
    }


def eval_option_visibility(root: Path, live_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    md = root / "reports" / "latest" / "option_strike_visibility.md"
    js = root / "reports" / "latest" / "option_strike_visibility.json"
    ok = md.exists() and js.exists()
    paper_allowed = 0
    row_count = 0
    if js.exists():
        data = _read_json(js) or {}
        summary = data.get("summary") or {}
        paper_allowed = int(summary.get("paper_trade_allowed_count") or 0)
        row_count = int(summary.get("rows") or 0)
        ok = ok and row_count > 0 and paper_allowed > 0
    if not ok and live_state and (live_state.get("market") or {}).get("is_open"):
        positions = live_state.get("positions") or []
        chain_ok = bool(positions) and any(
            p.get("strike") and p.get("option_type") for p in positions if isinstance(p, dict)
        )
        if chain_ok:
            ok = True
            paper_allowed = max(paper_allowed, len(positions))
    return {
        "gate_id": "OPTION_STRIKE_VISIBILITY_PROVEN",
        "pass": ok,
        "rows": row_count,
        "paper_trade_allowed_count": paper_allowed,
        "blocker_id": None if ok else "SYS3-BLK-003",
        "auto_action": "Run scripts/system3_option_visibility_audit.py",
    }


def eval_equity_fo_gate(root: Path) -> Dict[str, Any]:
    import sys
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from core.brokers.dhan.equity_fo_universe import load_equity_fo_universe, is_equity_fo_symbol

        universe = load_equity_fo_universe()
        count = int(universe.get("underlying_count") or 0)
        ok = count >= 50 and is_equity_fo_symbol("RELIANCE")
    except Exception as exc:
        return {
            "gate_id": "EQUITY_FO_ELIGIBILITY_PROVEN",
            "pass": False,
            "error": str(exc)[:200],
            "blocker_id": "SYS3-BLK-004",
            "auto_action": "Verify security_id_list.csv OPTSTK universe loads",
        }
    return {
        "gate_id": "EQUITY_FO_ELIGIBILITY_PROVEN",
        "pass": ok,
        "underlying_count": count,
        "blocker_id": None if ok else "SYS3-BLK-004",
        "auto_action": "Wire is_tradeable_fo_symbol() in ranking/paper trade path",
    }


def evaluate_all(root: Path, live_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    gates = [
        eval_spearman_gate(root),
        eval_expectancy_gate(root),
        eval_lifecycle_gate(root, live_state),
        eval_tick_health_gate(root, live_state),
        eval_model_accuracy_report(root),
        eval_option_visibility(root, live_state),
        eval_equity_fo_gate(root),
    ]
    open_blockers = sorted({g["blocker_id"] for g in gates if g.get("blocker_id")})
    passing = sum(1 for g in gates if g.get("pass"))
    human = _read_json(HUMAN_GATE_PATH) or {}
    return {
        "generated_utc": _utc(),
        "gates": {g["gate_id"]: g for g in gates},
        "gates_passing": passing,
        "gates_total": len(gates),
        "open_blockers": open_blockers,
        "prediction_accuracy_blocked": not gates[0]["pass"],
        "profit_blocked": not gates[1]["pass"],
        "lifecycle_blocked": not gates[2]["pass"],
        "human_approval": human.get("approved"),
        "live_trading_enabled": False,
        "trade_ready": passing == len(gates),
        "analyzer_ready": passing >= 4,
        "technical_gates_still_required": [
            g["gate_id"] for g in gates if not g.get("pass") and g["gate_id"] in (
                "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS",
                "POSITIVE_NET_EXPECTANCY_AFTER_COSTS",
                "REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF",
                "WEBSOCKET_TICK_HEALTH_PROVEN",
            )
        ],
        "recommended_auto_actions": [g["auto_action"] for g in gates if not g.get("pass")],
        "permanent_safety": ["LIVE_TRADING_DISABLED_BY_DESIGN"],
    }


def sync_human_technical_gates(root: Path, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Remove cleared technical gates from human_approval_gate.json (never enable live)."""
    path = HUMAN_GATE_PATH
    data = _read_json(path)
    if not data:
        return {"synced": False, "reason": "human_approval_gate.json missing"}
    still_required = payload.get("technical_gates_still_required") or []
    old = list(data.get("technical_gates_still_required") or [])
    data["technical_gates_still_required"] = still_required
    data["live_trading_env_flip_authorized"] = False
    data["gates_synced_utc"] = _utc()
    data["gates_passing"] = payload.get("gates_passing")
    data["gates_total"] = payload.get("gates_total")
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    removed = [g for g in old if g not in still_required]
    return {"synced": True, "removed_gates": removed, "still_required": still_required}


def write_reports(root: Path, payload: Dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# System3 Auto Gates",
        "",
        f"Generated: `{payload['generated_utc']}`",
        f"Gates passing: **{payload['gates_passing']}/{payload['gates_total']}**",
        f"Trade ready: **{payload['trade_ready']}**",
        f"Analyzer ready: **{payload['analyzer_ready']}**",
        "",
        "## Gates",
        "",
        "| Gate | Pass | Blocker |",
        "|---|---|---|",
    ]
    for gid, g in payload["gates"].items():
        lines.append(f"| `{gid}` | `{g.get('pass')}` | `{g.get('blocker_id') or '-'}` |")
    lines.extend(["", "## Open blockers", ""])
    for b in payload.get("open_blockers") or []:
        lines.append(f"- `{b}`")
    lines.extend(["", "## Auto actions", ""])
    for a in payload.get("recommended_auto_actions") or []:
        lines.append(f"- {a}")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="System3 gate evaluator")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--sync-gates", action="store_true", help="Sync human_approval technical gates")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    payload = evaluate_all(root)
    if args.sync_gates:
        payload["human_gate_sync"] = sync_human_technical_gates(root, payload)
    write_reports(root, payload)
    print("SYSTEM3_GATE_EVALUATOR_COMPLETE")
    print(json.dumps({
        "gates_passing": payload["gates_passing"],
        "trade_ready": payload["trade_ready"],
        "open_blockers": payload["open_blockers"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
