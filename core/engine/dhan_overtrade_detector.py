"""
Dhan Index Options - Over-Trade Detector

Detects excessive trading activity.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
EXEC_LOG_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_trades_exec_log.csv"


def detect_overtrading(
    exec_log: pd.DataFrame,
    time_window_min: int = 60,
) -> Dict[str, Any]:
    """
    Detect overtrading in execution log.

    Args:
        exec_log: DataFrame with execution log
        time_window_min: Time window in minutes

    Returns:
        Dict with overtrading detection results
    """
    if exec_log.empty:
        return {
            "is_overtrading": False,
            "trade_frequency": 0.0,
            "risk_level": "LOW",
            "recommendation": "NORMAL",
        }

    if time_window_min <= 0:
        time_window_min = 60

    # Parse timestamps
    if "ts_exec" in exec_log.columns:
        exec_log["ts_exec"] = pd.to_datetime(exec_log["ts_exec"], errors="coerce")
        exec_log = exec_log.dropna(subset=["ts_exec"])

        # Filter to time window
        cutoff = datetime.utcnow() - timedelta(minutes=time_window_min)
        recent = exec_log[exec_log["ts_exec"] >= cutoff]

        # Compute frequency
        trade_frequency = len(recent) / (time_window_min / 60.0)  # trades per hour
    else:
        trade_frequency = len(exec_log) / (time_window_min / 60.0)

    # Classify risk
    if trade_frequency >= 10:
        risk_level = "CRITICAL"
        recommendation = "STOP_TRADING"
    elif trade_frequency >= 5:
        risk_level = "HIGH"
        recommendation = "REDUCE_FREQUENCY"
    elif trade_frequency >= 3:
        risk_level = "MEDIUM"
        recommendation = "MONITOR"
    else:
        risk_level = "LOW"
        recommendation = "NORMAL"

    is_overtrading = risk_level in ["HIGH", "CRITICAL"]

    return {
        "is_overtrading": is_overtrading,
        "trade_frequency": float(trade_frequency),
        "risk_level": risk_level,
        "recommendation": recommendation,
    }


def compute_trade_frequency(
    trades: pd.DataFrame,
    window: int,
) -> float:
    """
    Compute trade frequency in trades per hour.

    Args:
        trades: DataFrame with trades
        window: Time window in minutes

    Returns:
        Trade frequency (trades per hour)
    """
    if trades.empty or window <= 0:
        return 0.0

    return len(trades) / (window / 60.0)


def check_overtrade_risk(
    underlying: str,
    recent_trades: int,
    limit: int,
) -> bool:
    """
    Check if overtrading risk exists for an underlying.

    Args:
        underlying: Underlying name
        recent_trades: Number of recent trades
        limit: Maximum allowed trades

    Returns:
        True if risk detected
    """
    if limit <= 0:
        return False

    return recent_trades >= limit * 0.8  # 80% of limit = risk


def main() -> None:
    """Test overtrade detector."""
    print("=== ANGEL ONE INDEX OPTIONS - OVERTRADE DETECTOR ===")
    # Test with sample data
    exec_log = pd.DataFrame(
        {
            "ts_exec": pd.date_range(start="2024-01-01", periods=10, freq="5min"),
            "underlying": ["NIFTY"] * 10,
        }
    )
    result = detect_overtrading(exec_log, time_window_min=60)
    print(f"Overtrading detection: {result}")


if __name__ == "__main__":
    main()
