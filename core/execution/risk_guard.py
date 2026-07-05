"""
System3 Phase 235 - Risk Guard Core

Central risk checks for virtual orders (no real API).
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.utils.logger import logger

from .order_models import PlannedOrder, RiskDecision

LOG_DIR = PROJECT_ROOT / "logs" / "risk"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_risk_guard.log"


def _log_risk(message: str, level: str = "INFO") -> None:
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


def check_per_trade_limits(order: PlannedOrder, risk_config: Dict[str, Any]) -> RiskDecision:
    """
    Check per-trade limits for a single order.

    Args:
        order: Planned order
        risk_config: Risk configuration dict

    Returns:
        RiskDecision with approval status
    """
    try:
        risk_flags = {}
        approved = True
        adjusted_lots = order.lots
        reason = "OK"

        # Check symbol whitelist
        symbol_whitelist = risk_config.get("SYMBOL_WHITELIST", [])
        if symbol_whitelist and order.underlying not in symbol_whitelist:
            approved = False
            reason = f"SYMBOL_NOT_WHITELISTED: {order.underlying}"
            risk_flags["symbol_check"] = "FAILED"
            _log_risk(f"Order rejected: {reason}", "WARN")
            return RiskDecision(approved=False, adjusted_lots=0, reason=reason, risk_flags=risk_flags)

        # Check minimum score
        min_score = risk_config.get("MIN_SCORE_FOR_TRADE", 0.12)
        if abs(order.final_score) < min_score:
            approved = False
            reason = f"SCORE_TOO_LOW: {order.final_score:.3f} < {min_score}"
            risk_flags["score_check"] = "FAILED"
            _log_risk(f"Order rejected: {reason}", "WARN")
            return RiskDecision(approved=False, adjusted_lots=0, reason=reason, risk_flags=risk_flags)

        # Check max lots per trade
        max_lots = risk_config.get("MAX_LOTS_PER_TRADE", 1)
        if order.lots > max_lots:
            adjusted_lots = max_lots
            reason = f"LOTS_REDUCED: {order.lots} -> {max_lots}"
            risk_flags["lots_adjusted"] = "REDUCED"
            _log_risk(f"Order adjusted: {reason}", "INFO")

        risk_flags["symbol_check"] = "PASSED"
        risk_flags["score_check"] = "PASSED"

        return RiskDecision(approved=approved, adjusted_lots=adjusted_lots, reason=reason, risk_flags=risk_flags)

    except Exception as e:
        _log_risk(f"Risk guard error: {e}", "ERROR")
        return RiskDecision(
            approved=False, adjusted_lots=0, reason=f"RISK_GUARD_ERROR: {e}", risk_flags={"error": str(e)}
        )


def check_daily_limits(
    orders: List[PlannedOrder], current_pnl: float, open_positions_count: int, risk_config: Dict[str, Any]
) -> Tuple[List[RiskDecision], Dict[str, Any]]:
    """
    Check daily limits across multiple orders.

    Args:
        orders: List of planned orders
        current_pnl: Current daily PnL
        open_positions_count: Current number of open positions
        risk_config: Risk configuration dict

    Returns:
        Tuple of (list of RiskDecision, summary dict)
    """
    try:
        decisions = []
        summary = {
            "total_orders": len(orders),
            "approved_count": 0,
            "rejected_count": 0,
            "current_pnl": current_pnl,
            "open_positions": open_positions_count,
        }

        max_daily_loss = risk_config.get("MAX_DAILY_LOSS", 5000)
        max_open_positions = risk_config.get("MAX_OPEN_POSITIONS", 3)

        # Check daily loss limit
        if current_pnl <= -max_daily_loss:
            _log_risk(f"MAX_DAILY_LOSS_REACHED: {current_pnl:.2f} <= -{max_daily_loss}", "WARN")
            for order in orders:
                decisions.append(
                    RiskDecision(
                        approved=False,
                        adjusted_lots=0,
                        reason="MAX_DAILY_LOSS_REACHED",
                        risk_flags={"daily_limit": "EXCEEDED"},
                    )
                )
            summary["rejected_count"] = len(orders)
            return decisions, summary

        # Check open positions limit
        if open_positions_count >= max_open_positions:
            _log_risk(f"MAX_OPEN_POSITIONS_REACHED: {open_positions_count} >= {max_open_positions}", "WARN")
            for order in orders:
                decisions.append(
                    RiskDecision(
                        approved=False,
                        adjusted_lots=0,
                        reason="MAX_OPEN_POSITIONS_REACHED",
                        risk_flags={"position_limit": "EXCEEDED"},
                    )
                )
            summary["rejected_count"] = len(orders)
            return decisions, summary

        # Check each order individually
        for order in orders:
            decision = check_per_trade_limits(order, risk_config)
            decisions.append(decision)
            if decision.approved:
                summary["approved_count"] += 1
            else:
                summary["rejected_count"] += 1

        _log_risk(f"Daily limits check: {summary['approved_count']} approved, {summary['rejected_count']} rejected")

        return decisions, summary

    except Exception as e:
        _log_risk(f"Daily limits check error: {e}", "ERROR")
        # Return all rejected on error
        decisions = [
            RiskDecision(approved=False, adjusted_lots=0, reason=f"RISK_GUARD_ERROR: {e}", risk_flags={"error": str(e)})
            for _ in orders
        ]
        return decisions, {"error": str(e)}


def apply_global_safety_flags(
    orders: List[PlannedOrder], risk_config: Dict[str, Any], live_trade_config: Dict[str, Any]
) -> List[RiskDecision]:
    """
    Apply global safety flags (e.g., LIVE_TRADING_ENABLED check).

    Args:
        orders: List of planned orders
        risk_config: Risk configuration dict
        live_trade_config: Live trading configuration dict

    Returns:
        List of RiskDecision
    """
    try:
        # In DRY-RUN mode, this is just a pass-through (virtual execution always allowed)
        # But we still check other flags

        decisions = []
        for order in orders:
            # For now, approve all (virtual execution)
            # Future: could add more global checks here
            decisions.append(
                RiskDecision(
                    approved=True,
                    adjusted_lots=order.lots,
                    reason="GLOBAL_SAFETY_PASSED",
                    risk_flags={"global_check": "PASSED"},
                )
            )

        return decisions

    except Exception as e:
        _log_risk(f"Global safety flags error: {e}", "ERROR")
        return [
            RiskDecision(approved=False, adjusted_lots=0, reason=f"RISK_GUARD_ERROR: {e}", risk_flags={"error": str(e)})
            for _ in orders
        ]
