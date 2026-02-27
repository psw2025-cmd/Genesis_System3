"""
System3 Phase 236 - Virtual Execution Engine

Convert signals + thresholds into virtual orders and log them.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.utils.logger import logger
from .order_models import PlannedOrder, RiskDecision
from .risk_guard import check_per_trade_limits, check_daily_limits, apply_global_safety_flags

LOG_DIR = PROJECT_ROOT / "logs" / "execution"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_virtual_execution.log"

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)
VIRTUAL_ORDERS_CSV = STORAGE_LIVE / "angel_virtual_orders.csv"


def _log_execution(message: str, level: str = "INFO") -> None:
    """Log to both logger and file."""
    log_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}"
    # Use standard logger methods
    import logging

    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, message)
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except Exception:
        pass


def plan_orders_from_signals(
    signals_df: pd.DataFrame, thresholds_by_underlying: Dict[str, Dict[str, float]], live_trade_config: Dict[str, Any]
) -> List[PlannedOrder]:
    """
    Convert signals DataFrame to planned orders.

    Args:
        signals_df: DataFrame with signals (must have: ts, underlying, strike, side, option_type, expiry, ltp, final_score, ai_score)
        thresholds_by_underlying: Thresholds dict from threshold_loader
        live_trade_config: Live trading config

    Returns:
        List of PlannedOrder objects
    """
    planned_orders = []

    if signals_df.empty:
        return planned_orders

    try:
        # Filter to BUY/SELL only (ignore HOLD)
        action_signals = signals_df[signals_df["signal"].isin(["BUY", "SELL"])].copy()

        if action_signals.empty:
            _log_execution("No BUY/SELL signals to convert to orders")
            return planned_orders

        # Get snapshot_id if available (use row index as fallback)
        snapshot_id = 0
        if "snapshot_id" in action_signals.columns:
            snapshot_id = action_signals["snapshot_id"].iloc[0] if len(action_signals) > 0 else 0

        for idx, row in action_signals.iterrows():
            try:
                # Extract required fields
                ts = str(row.get("ts", datetime.now().isoformat()))
                underlying = str(row.get("underlying", ""))
                strike = float(row.get("strike", 0.0))
                side = str(row.get("signal", "HOLD"))  # BUY or SELL
                option_type = str(row.get("side", "CE"))  # CE or PE
                expiry = str(row.get("expiry", ""))
                ltp = float(row.get("ltp", 0.0))
                final_score = float(row.get("final_score", 0.0))
                ai_score = float(row.get("ai_score", 0.0))

                # Skip if missing critical fields
                if not underlying or strike == 0.0 or ltp == 0.0:
                    continue

                # Determine lots (default 1, or from config)
                lots = live_trade_config.get("MAX_LOTS_PER_TRADE", 1)

                # Build reason
                reason = f"Signal: {side}, Score: {final_score:.3f}"

                order = PlannedOrder(
                    ts=ts,
                    underlying=underlying,
                    strike=strike,
                    option_type=option_type,
                    side=side,
                    expiry=expiry,
                    ltp=ltp,
                    final_score=final_score,
                    ai_score=ai_score,
                    lots=lots,
                    reason=reason,
                    snapshot_id=snapshot_id,
                )

                planned_orders.append(order)

            except Exception as e:
                _log_execution(f"Error creating planned order from row {idx}: {e}", "WARN")
                continue

        _log_execution(f"Planned {len(planned_orders)} orders from {len(action_signals)} signals")

    except Exception as e:
        _log_execution(f"Error planning orders: {e}", "ERROR")

    return planned_orders


def run_risk_checks_on_orders(
    planned_orders: List[PlannedOrder],
    risk_config: Dict[str, Any],
    current_pnl: float = 0.0,
    open_positions_count: int = 0,
) -> List[RiskDecision]:
    """
    Run risk checks on planned orders.

    Args:
        planned_orders: List of planned orders
        risk_config: Risk configuration dict
        current_pnl: Current daily PnL
        open_positions_count: Current number of open positions

    Returns:
        List of RiskDecision objects
    """
    if not planned_orders:
        return []

    try:
        # Check daily limits first
        decisions, summary = check_daily_limits(planned_orders, current_pnl, open_positions_count, risk_config)

        # If all rejected by daily limits, return early
        if all(not d.approved for d in decisions):
            return decisions

        # Apply global safety flags
        global_decisions = apply_global_safety_flags(planned_orders, risk_config, risk_config)

        # Combine decisions (global can override)
        final_decisions = []
        for daily_decision, global_decision in zip(decisions, global_decisions):
            if not daily_decision.approved:
                final_decisions.append(daily_decision)
            elif not global_decision.approved:
                final_decisions.append(global_decision)
            else:
                # Both approved, use daily decision (has adjusted_lots)
                final_decisions.append(daily_decision)

        return final_decisions

    except Exception as e:
        _log_execution(f"Error running risk checks: {e}", "ERROR")
        return [
            RiskDecision(approved=False, adjusted_lots=0, reason=f"RISK_CHECK_ERROR: {e}", risk_flags={"error": str(e)})
            for _ in planned_orders
        ]


def log_virtual_orders(
    planned_orders: List[PlannedOrder], risk_decisions: List[RiskDecision], csv_path: Path = None
) -> None:
    """
    Log virtual orders to CSV file.

    Args:
        planned_orders: List of planned orders
        risk_decisions: List of risk decisions (aligned with orders)
        csv_path: Optional path to CSV file
    """
    if csv_path is None:
        csv_path = VIRTUAL_ORDERS_CSV

    if not planned_orders:
        return

    try:
        # Build DataFrame
        rows = []
        for order, decision in zip(planned_orders, risk_decisions):
            row = {
                "ts": order.ts,
                "underlying": order.underlying,
                "strike": order.strike,
                "option_type": order.option_type,
                "side": order.side,
                "expiry": order.expiry,
                "ltp": order.ltp,
                "final_score": order.final_score,
                "ai_score": order.ai_score,
                "lots": order.lots,
                "approved": decision.approved,
                "adjusted_lots": decision.adjusted_lots,
                "risk_reason": decision.reason,
                "risk_flags_json": json.dumps(decision.risk_flags),
                "snapshot_id": order.snapshot_id,
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # Append to CSV
        write_header = not csv_path.exists()
        df.to_csv(csv_path, mode="a", header=write_header, index=False, encoding="utf-8")

        approved_count = sum(1 for d in risk_decisions if d.approved)
        _log_execution(f"Logged {len(planned_orders)} virtual orders ({approved_count} approved) to {csv_path}")

    except Exception as e:
        _log_execution(f"Error logging virtual orders: {e}", "ERROR")
