"""
Dhan Index Options - Trade Lifecycle Validator V2

Enhanced validation of complete trade lifecycle.
"""

import pandas as pd
from typing import Dict, Any, List
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIFECYCLE_LOG_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_trade_lifecycle_log.csv"


def validate_trade_lifecycle(trade_id: str, lifecycle_log: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate complete trade lifecycle.

    Args:
        trade_id: Unique trade identifier
        lifecycle_log: DataFrame with lifecycle events

    Returns:
        Dict with validation results
    """
    if lifecycle_log.empty:
        return {
            "valid": False,
            "missing_events": ["ALL"],
            "anomalies": ["No lifecycle data"],
            "completeness_score": 0.0,
        }

    # Filter events for this trade
    trade_events = lifecycle_log[lifecycle_log["trade_id"] == trade_id]

    if trade_events.empty:
        return {
            "valid": False,
            "missing_events": ["ALL"],
            "anomalies": [f"Trade {trade_id} not found"],
            "completeness_score": 0.0,
        }

    # Expected event sequence
    expected_events = ["SIGNAL_GENERATED", "TRADE_PLANNED", "TRADE_EXECUTED", "TRADE_EXITED", "PNL_COMPUTED"]
    actual_events = trade_events["event_type"].tolist()

    # Check completeness
    missing = [e for e in expected_events if e not in actual_events]
    completeness = (len(expected_events) - len(missing)) / len(expected_events)

    # Detect anomalies
    anomalies = detect_lifecycle_anomalies(trade_events.iloc[-1] if len(trade_events) > 0 else pd.Series())

    valid = len(missing) == 0 and len(anomalies) == 0

    return {
        "valid": valid,
        "missing_events": missing,
        "anomalies": anomalies,
        "completeness_score": float(completeness),
    }


def check_lifecycle_completeness(events: List[str]) -> bool:
    """
    Check if lifecycle is complete.

    Args:
        events: List of event types

    Returns:
        True if complete
    """
    required = ["SIGNAL_GENERATED", "TRADE_PLANNED", "TRADE_EXECUTED"]
    return all(e in events for e in required)


def detect_lifecycle_anomalies(trade_row: pd.Series) -> List[str]:
    """
    Detect anomalies in trade lifecycle.

    Args:
        trade_row: Trade row from lifecycle log

    Returns:
        List of anomaly descriptions
    """
    anomalies = []

    if trade_row.empty:
        return ["Empty trade row"]

    # Check for missing critical fields
    if "underlying" not in trade_row.index or pd.isna(trade_row.get("underlying")):
        anomalies.append("Missing underlying")

    if "strike" not in trade_row.index or pd.isna(trade_row.get("strike")):
        anomalies.append("Missing strike")

    # Check timestamp
    if "ts" in trade_row.index:
        try:
            from datetime import datetime

            ts = pd.to_datetime(trade_row["ts"])
            if ts > pd.Timestamp.now():
                anomalies.append("Future timestamp")
        except Exception:
            anomalies.append("Invalid timestamp")

    return anomalies


def main() -> None:
    """Test trade validator V2."""
    print("=== ANGEL ONE INDEX OPTIONS - TRADE VALIDATOR V2 ===")
    # Test with sample data
    lifecycle_log = pd.DataFrame(
        {
            "trade_id": ["TEST_1", "TEST_1"],
            "event_type": ["SIGNAL_GENERATED", "TRADE_PLANNED"],
            "underlying": ["NIFTY", "NIFTY"],
            "strike": [22000, 22000],
        }
    )
    result = validate_trade_lifecycle("TEST_1", lifecycle_log)
    print(f"Validation result: {result}")


if __name__ == "__main__":
    main()
