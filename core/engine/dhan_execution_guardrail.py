"""
Dhan Index Options - Execution Guardrail

Validates execution requests before order placement.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
EXEC_LOG_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_trades_exec_log.csv"


def validate_execution_request(
    trade_row: pd.Series,
    current_market: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Validate execution request before order placement.

    Args:
        trade_row: Trade row with entry details
        current_market: Current market data

    Returns:
        Dict with validation results
    """
    validation_checks = {}

    # Check price slippage
    entry_price = float(trade_row.get("entry_price", 0.0))
    if not current_market.empty and "ltp" in current_market.columns:
        current_price = float(current_market["ltp"].iloc[-1])
        slippage_check = check_price_slippage(entry_price, current_price, max_slippage_pct=2.0)
        validation_checks["slippage_check"] = slippage_check
    else:
        validation_checks["slippage_check"] = True  # Pass if no market data

    # Check execution limits
    underlying = trade_row.get("underlying", "")
    if underlying:
        daily_count = _get_daily_trade_count(underlying)
        limit_check = enforce_execution_limits(underlying, daily_count, limit=5)
        validation_checks["limit_check"] = limit_check
    else:
        validation_checks["limit_check"] = True

    # All checks must pass
    execution_allowed = all(validation_checks.values())

    return {
        "execution_allowed": execution_allowed,
        "validation_checks": validation_checks,
        "slippage_check": validation_checks.get("slippage_check", True),
        "limit_check": validation_checks.get("limit_check", True),
    }


def check_price_slippage(
    entry_price: float,
    current_price: float,
    max_slippage_pct: float = 2.0,
) -> bool:
    """
    Check if price slippage is acceptable.

    Args:
        entry_price: Planned entry price
        current_price: Current market price
        max_slippage_pct: Maximum allowed slippage percentage

    Returns:
        True if slippage is acceptable
    """
    if entry_price <= 0 or current_price <= 0 or max_slippage_pct <= 0:
        return False

    slippage_pct = abs(current_price - entry_price) / entry_price * 100.0
    return slippage_pct <= max_slippage_pct


def enforce_execution_limits(
    underlying: str,
    daily_count: int,
    limit: int,
) -> bool:
    """
    Enforce daily execution limits.

    Args:
        underlying: Underlying name
        daily_count: Current daily trade count
        limit: Maximum allowed trades

    Returns:
        True if within limits
    """
    if limit <= 0:
        return True

    return daily_count < limit


def _get_daily_trade_count(underlying: str) -> int:
    """Get daily trade count for an underlying."""
    if not EXEC_LOG_CSV.exists():
        return 0

    try:
        exec_log = pd.read_csv(EXEC_LOG_CSV)
        if exec_log.empty:
            return 0

        if "ts_exec" in exec_log.columns:
            exec_log["ts_exec"] = pd.to_datetime(exec_log["ts_exec"], errors="coerce")
            today = datetime.utcnow().date()
            exec_log["date"] = exec_log["ts_exec"].dt.date
            today_trades = exec_log[(exec_log["date"] == today) & (exec_log["underlying"] == underlying)]
            return len(today_trades)

        return 0
    except Exception:
        return 0


def main() -> None:
    """Test execution guardrail."""
    print("=== ANGEL ONE INDEX OPTIONS - EXECUTION GUARDRAIL ===")
    trade_row = pd.Series(
        {
            "entry_price": 100.0,
            "underlying": "NIFTY",
        }
    )
    current_market = pd.DataFrame(
        {
            "ltp": [101.0],
        }
    )
    result = validate_execution_request(trade_row, current_market)
    print(f"Execution validation: {result}")


if __name__ == "__main__":
    main()
