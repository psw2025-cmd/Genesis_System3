"""
Trader requirements API — maps validated broker + paper data to trader audit fields.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _status_from_field(field: Dict[str, Any]) -> str:
    if not field:
        return "NOT_FOUND"
    if field.get("valid"):
        return "PASS"
    st = field.get("status", "NOT_FOUND")
    if st == "BROKER_OFFLINE":
        return "BROKER_OFFLINE"
    if st in ("API_FAILED", "NOT_FOUND", "EMPTY", "INVALID_TYPE"):
        return "NOT_FOUND"
    return "PASS_WITH_WARNINGS"


def build_trader_requirements_report(outputs_dir: Path) -> Dict[str, Any]:
    try:
        from dashboard.backend.broker_truth_validator import build_broker_truth_report
        from dashboard.backend.portfolio_truth_service import build_unified_portfolio
    except ImportError:
        from broker_truth_validator import build_broker_truth_report
        from portfolio_truth_service import build_unified_portfolio

    broker_truth = build_broker_truth_report()
    unified = build_unified_portfolio(outputs_dir)
    tf = broker_truth.get("trader_fields") or {}

    paper = unified.get("paper") or {}
    summary = paper.get("summary") or {}
    trades = unified.get("trade_history") or []
    holdings_rows = broker_truth.get("holdings", {}).get("rows") or []
    positions_rows = broker_truth.get("positions", {}).get("rows") or []
    funds = broker_truth.get("funds", {}).get("normalized") or {}

    has_summary = bool(summary.get("total_trades"))
    has_trades = bool(trades)
    broker_connected = broker_truth.get("broker_connected", False)

    portfolio = {
        "total_invested": _status_from_field(tf.get("holdings_total_value")),
        "current_value": _status_from_field(tf.get("holdings_total_value")),
        "gross_pnl": _status_from_field(tf.get("positions_unrealized_pnl")) if positions_rows else (
            "PASS_WITH_WARNINGS" if has_summary else "NOT_FOUND"
        ),
        "net_pnl": "PASS_WITH_WARNINGS" if has_summary else "NOT_FOUND",
        "cash_available": _status_from_field(tf.get("cash_available")),
        "open_positions": (
            "PASS" if positions_rows or paper.get("open_positions") else (
                "BROKER_OFFLINE" if not broker_connected else "PASS"
            )
        ),
        "win_rate": "PASS_WITH_WARNINGS" if "win_rate" in summary else "NOT_FOUND",
        "max_loss_position": "NOT_FOUND",
        "utilized_margin": _status_from_field(tf.get("utilized_margin")),
        "holdings_count": _status_from_field(tf.get("holdings_count")),
        "positions_count": _status_from_field(tf.get("positions_count")),
    }

    trade_fields = [
        "trade_id", "timestamp_ist", "symbol", "entry_price", "exit_price",
        "gross_pnl", "net_pnl", "charges_breakdown", "duration_minutes",
        "exit_reason", "source", "Greeks_at_entry", "Greeks_at_exit",
        "slippage_realized", "market_condition_at_entry",
    ]
    trade_history_map: Dict[str, str] = {}
    sample = trades[0] if trades else {}
    key_map = {
        "trade_id": "position_id",
        "timestamp_ist": "time_ist",
        "symbol": "underlying",
        "gross_pnl": "realized_pnl",
        "net_pnl": "realized_pnl",
    }
    for field in trade_fields:
        src_key = key_map.get(field, field)
        if field == "source":
            trade_history_map[field] = "PASS" if sample.get("data_source") or has_trades else "NOT_FOUND"
        else:
            trade_history_map[field] = (
                "PASS" if src_key in sample else ("PASS_WITH_WARNINGS" if has_summary else "NOT_FOUND")
            )

    live_fields = [
        "position_id", "symbol", "strike", "entry_price", "current_ltp",
        "unrealized_pnl", "Greeks_now", "Greeks_change_since_entry",
        "iv_change", "stoploss", "target", "risk_reward_ratio", "days_to_expiry",
    ]
    live_positions_map: Dict[str, str] = {}
    psample = positions_rows[0] if positions_rows else {}
    for field in live_fields:
        if field == "symbol" and psample.get("symbol"):
            live_positions_map[field] = "PASS"
        elif field == "current_ltp" and psample.get("ltp") is not None:
            live_positions_map[field] = "PASS"
        elif field == "unrealized_pnl" and psample.get("unrealized_pnl") is not None:
            live_positions_map[field] = "PASS"
        elif field in ("net_qty",) and psample.get("net_qty") is not None:
            live_positions_map[field] = "PASS"
        elif not broker_connected:
            live_positions_map[field] = "BROKER_OFFLINE"
        elif positions_rows:
            live_positions_map[field] = "PASS_WITH_WARNINGS"
        else:
            live_positions_map[field] = "NOT_FOUND"

    prediction = {k: "NOT_FOUND" for k in [
        "prediction_timestamp", "predicted_top_3", "actual_top_3",
        "accuracy_pct", "ranking_correlation", "market_result_proof",
    ]}

    counts: Dict[str, int] = {}
    for group in [portfolio, trade_history_map, live_positions_map, prediction]:
        for v in group.values():
            counts[v] = counts.get(v, 0) + 1

    broker_val = broker_truth.get("validation") or {}
    overall = broker_val.get("overall", "NOT_VALID")
    if overall == "VALID" and counts.get("PASS", 0) >= 8:
        overall_status = "PASS"
    elif overall in ("VALID", "PASS_WITH_WARNINGS"):
        overall_status = "PASS_WITH_WARNINGS"
    elif not broker_connected:
        overall_status = "BROKER_OFFLINE"
    else:
        overall_status = "NOT_PROVEN"

    return {
        "status": overall_status,
        "live_trading_enabled": False,
        "production_ready_for_real_money": False,
        "data_transparency": unified.get("data_transparency"),
        "broker_validation": broker_val,
        "broker_data_source": broker_truth.get("data_source"),
        "portfolio": portfolio,
        "trade_history": trade_history_map,
        "live_positions": live_positions_map,
        "prediction_vs_market": prediction,
        "evidence": {
            "paper_summary": summary,
            "trade_history_count": len(trades),
            "broker_holdings_count": len(holdings_rows),
            "broker_positions_count": len(positions_rows),
            "funds_available": funds.get("available_balance"),
            "validation_pct": broker_val.get("valid_pct"),
        },
        "blockers": unified.get("blockers", []),
        "next_actions": unified.get("next_actions", []),
    }
