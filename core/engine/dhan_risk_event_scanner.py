"""
Dhan Index Options - Risk Event Scanner

Scans for risk events including big index moves.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def scan_risk_events(
    df_signals: pd.DataFrame,
    threshold_pct: float = 1.0,
) -> pd.DataFrame:
    """
    Scan for risk events in signals DataFrame.

    Args:
        df_signals: DataFrame with spot/price data
        threshold_pct: Percentage threshold for big moves

    Returns:
        DataFrame with risk event columns
    """
    if df_signals.empty:
        return df_signals

    if threshold_pct <= 0:
        threshold_pct = 1.0

    df = df_signals.copy()

    # Compute spot changes
    if "spot" in df.columns:
        df["spot_change_pct"] = df["spot"].pct_change() * 100.0
        df["big_move_detected"] = df["spot_change_pct"].apply(lambda x: detect_big_move(x, threshold_pct))

    # Classify risk level
    df["risk_level"] = df.apply(
        lambda row: classify_risk_level_single(row, threshold_pct),
        axis=1,
    )

    # Risk event flag
    df["risk_event_flag"] = df["risk_level"].isin(["HIGH", "CRITICAL"])

    return df


def detect_big_move(spot_change_pct: float, threshold: float) -> bool:
    """
    Detect if a big move occurred.

    Args:
        spot_change_pct: Percentage change in spot
        threshold: Threshold percentage

    Returns:
        True if big move detected
    """
    if pd.isna(spot_change_pct):
        return False

    return abs(spot_change_pct) >= threshold


def classify_risk_level(df: pd.DataFrame) -> str:
    """
    Classify overall risk level.

    Returns: "LOW", "MEDIUM", "HIGH", "CRITICAL"
    """
    if df.empty:
        return "LOW"

    if "risk_level" in df.columns:
        levels = df["risk_level"].value_counts()
        if "CRITICAL" in levels.index:
            return "CRITICAL"
        elif "HIGH" in levels.index:
            return "HIGH"
        elif "MEDIUM" in levels.index:
            return "MEDIUM"
        else:
            return "LOW"

    return "LOW"


def classify_risk_level_single(row: pd.Series, threshold: float) -> str:
    """Classify risk level for a single row."""
    change_pct = abs(row.get("spot_change_pct", 0.0))

    if change_pct >= threshold * 3.0:
        return "CRITICAL"
    elif change_pct >= threshold * 2.0:
        return "HIGH"
    elif change_pct >= threshold:
        return "MEDIUM"
    else:
        return "LOW"


def main() -> None:
    """Test risk event scanner."""
    print("=== ANGEL ONE INDEX OPTIONS - RISK EVENT SCANNER ===")
    df = pd.DataFrame(
        {
            "spot": [22000, 22220, 22050, 22300, 22000],
        }
    )
    result = scan_risk_events(df, threshold_pct=1.0)
    print(result[["spot", "spot_change_pct", "big_move_detected", "risk_level"]].to_string())


if __name__ == "__main__":
    main()
