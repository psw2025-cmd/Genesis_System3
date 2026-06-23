"""
Trader requirements API — maps available data to trader audit fields.

Never enables live trading. Marks NOT_FOUND when data truly absent.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _status(found: bool, blocked: bool = False, partial: bool = False) -> str:
    if blocked:
        return "BLOCKED_SECRET_REQUIRED"
    if found and partial:
        return "PASS_WITH_WARNINGS"
    if found:
        return "PASS"
    return "NOT_FOUND"


def build_trader_requirements_report(outputs_dir: Path) -> Dict[str, Any]:
    try:
        from dashboard.backend.portfolio_truth_service import build_unified_portfolio
    except ImportError:
        from portfolio_truth_service import build_unified_portfolio

    unified = build_unified_portfolio(outputs_dir)
    paper = unified.get("paper") or {}
    summary = paper.get("summary") or {}
    trades = unified.get("trade_history") or []
    broker_pos = unified.get("broker_positions") or []
    broker_hold = unified.get("broker_holdings") or []

    has_summary = bool(summary.get("total_trades"))
    has_trades = bool(trades)
    has_broker = bool(broker_pos or broker_hold)

    portfolio = {
        "total_invested": _status(False),
        "current_value": _status(False),
        "gross_pnl": _status(has_summary, partial=True),
        "net_pnl": _status(has_summary, partial=True),
        "cash_available": _status(False),
        "open_positions": _status(has_broker or bool(paper.get("open_positions"))),
        "win_rate": _status("win_rate" in summary, partial=True),
        "max_loss_position": _status(False),
    }

    trade_fields = [
        "trade_id", "timestamp_ist", "symbol", "entry_price", "exit_price",
        "gross_pnl", "net_pnl", "charges_breakdown", "duration_minutes",
        "exit_reason", "source", "Greeks_at_entry", "Greeks_at_exit",
        "slippage_realized", "market_condition_at_entry",
    ]
    trade_history = {}
    sample = trades[0] if trades else {}
    for field in trade_fields:
        key_map = {
            "trade_id": "position_id",
            "timestamp_ist": "time_ist",
            "symbol": "underlying",
            "gross_pnl": "realized_pnl",
            "net_pnl": "realized_pnl",
        }
        src_key = key_map.get(field, field)
        trade_history[field] = _status(src_key in sample if sample else False, partial=field in ("gross_pnl", "net_pnl") and has_summary)

    live_fields = [
        "position_id", "symbol", "strike", "entry_price", "current_ltp",
        "unrealized_pnl", "Greeks_now", "Greeks_change_since_entry",
        "iv_change", "stoploss", "target", "risk_reward_ratio", "days_to_expiry",
    ]
    live_positions = {}
    bsample = (broker_pos or broker_hold or [{}])[0] if (broker_pos or broker_hold) else {}
    for field in live_fields:
        key_map = {"symbol": "symbol", "current_ltp": "ltp", "unrealized_pnl": "pnl", "position_id": "symbol"}
        src_key = key_map.get(field, field)
        live_positions[field] = _status(src_key in bsample if bsample else False, partial=field in ("symbol", "current_ltp"))

    prediction = {k: "NOT_FOUND" for k in [
        "prediction_timestamp", "predicted_top_3", "actual_top_3",
        "accuracy_pct", "ranking_correlation", "market_result_proof",
    ]}

    counts: Dict[str, int] = {}
    for group in [portfolio, trade_history, live_positions, prediction]:
        for v in group.values():
            counts[v] = counts.get(v, 0) + 1

    if counts.get("PASS", 0) >= 5:
        overall = "PASS_WITH_WARNINGS"
    elif counts.get("NOT_FOUND", 0) > 20:
        overall = "NOT_PROVEN"
    else:
        overall = "PASS_WITH_WARNINGS"

    return {
        "status": overall,
        "live_trading_enabled": False,
        "production_ready_for_real_money": False,
        "data_transparency": unified.get("data_transparency"),
        "portfolio": portfolio,
        "trade_history": trade_history,
        "live_positions": live_positions,
        "prediction_vs_market": prediction,
        "evidence": {
            "paper_summary": summary,
            "trade_history_count": len(trades),
            "broker_positions_count": len(broker_pos),
            "broker_holdings_count": len(broker_hold),
        },
        "blockers": unified.get("blockers", []),
        "next_actions": unified.get("next_actions", []),
    }
