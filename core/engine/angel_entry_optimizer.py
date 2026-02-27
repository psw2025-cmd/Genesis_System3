"""
Angel One Index Options - Entry Optimizer

Optimizes trade entry timing and price.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def optimize_entry_timing(df_signals: pd.DataFrame, lookback: int = 5) -> pd.DataFrame:
    """
    Optimize entry timing based on recent price action.

    Args:
        df_signals: DataFrame with price data
        lookback: Number of periods to analyze

    Returns:
        DataFrame with entry optimization columns
    """
    if df_signals.empty:
        return df_signals

    if lookback < 2:
        lookback = 2

    df = df_signals.copy()

    # Compute entry timing score
    if "ltp" in df.columns:
        df["entry_timing_score"] = (
            df["ltp"].rolling(window=lookback, min_periods=1).apply(lambda x: _compute_timing_score(x))
        )

    return df


def compute_optimal_entry_price(
    current_price: float,
    bid: float,
    ask: float,
) -> float:
    """
    Compute optimal entry price.

    Args:
        current_price: Current market price
        bid: Bid price
        ask: Ask price

    Returns:
        Optimal entry price
    """
    if ask < bid or current_price <= 0:
        return current_price

    # Prefer mid-price, but can adjust based on strategy
    mid_price = (bid + ask) / 2.0

    # If current price is close to mid, use current
    if abs(current_price - mid_price) / mid_price < 0.01:
        return current_price

    return mid_price


def suggest_entry_strategy(signal_row: pd.Series) -> str:
    """
    Suggest entry strategy.

    Returns: "MARKET", "LIMIT", "WAIT"
    """
    confidence = float(signal_row.get("pred_confidence", 0.0))
    score = abs(float(signal_row.get("expected_move_score", 0.0)))

    # High confidence + high score = market order
    if confidence >= 0.85 and score >= 0.30:
        return "MARKET"

    # Medium confidence = limit order
    if confidence >= 0.70:
        return "LIMIT"

    # Low confidence = wait
    return "WAIT"


def _compute_timing_score(price_series: pd.Series) -> float:
    """Compute entry timing score (0.0 to 1.0)."""
    if len(price_series) < 2:
        return 0.5

    # Simple: lower price = better entry (for long)
    recent = price_series.tail(3)
    if len(recent) < 2:
        return 0.5

    # Score based on price trend
    trend = (recent.iloc[-1] - recent.iloc[0]) / recent.iloc[0]
    score = 0.5 - trend * 10.0  # Lower trend = better entry
    return float(max(0.0, min(1.0, score)))


def main() -> None:
    """Test entry optimizer."""
    print("=== ANGEL ONE INDEX OPTIONS - ENTRY OPTIMIZER ===")
    df = pd.DataFrame(
        {
            "ltp": [100, 105, 102, 108, 110],
            "pred_confidence": [0.9, 0.8, 0.7, 0.85, 0.75],
            "expected_move_score": [0.4, 0.3, 0.2, 0.35, 0.25],
        }
    )
    result = optimize_entry_timing(df)
    print(result[["ltp", "entry_timing_score"]].to_string())


if __name__ == "__main__":
    main()
