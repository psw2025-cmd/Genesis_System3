"""
Dhan Index Options - Breakout Prediction Engine

Predicts price breakouts above resistance or below support.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def predict_breakout(
    df_signals: pd.DataFrame,
    resistance: float,
    support: float,
) -> Dict[str, Any]:
    """
    Predict breakout probability and direction.

    Args:
        df_signals: DataFrame with price data
        resistance: Resistance level
        support: Support level

    Returns:
        Dict with breakout prediction details
    """
    if df_signals.empty or "spot" not in df_signals.columns:
        return {
            "breakout_probability": 0.0,
            "breakout_direction": "NONE",
            "breakout_signal": "NONE",
        }

    if resistance <= support:
        return {
            "breakout_probability": 0.0,
            "breakout_direction": "NONE",
            "breakout_signal": "INVALID_LEVELS",
        }

    current_price = float(df_signals["spot"].iloc[-1])
    volatility = df_signals["spot"].std() if len(df_signals) > 1 else 0.0

    # Compute probabilities
    prob_up = compute_breakout_probability(current_price, resistance, support, volatility, "UP")
    prob_down = compute_breakout_probability(current_price, resistance, support, volatility, "DOWN")

    if prob_up > prob_down and prob_up > 0.5:
        direction = "UP"
        probability = prob_up
    elif prob_down > prob_up and prob_down > 0.5:
        direction = "DOWN"
        probability = prob_down
    else:
        direction = "NONE"
        probability = max(prob_up, prob_down)

    return {
        "breakout_probability": float(probability),
        "breakout_direction": direction,
        "breakout_signal": direction if probability > 0.6 else "NONE",
    }


def compute_breakout_probability(
    price: float,
    resistance: float,
    support: float,
    volatility: float,
    direction: str,
) -> float:
    """
    Compute breakout probability for a direction.

    Args:
        price: Current price
        resistance: Resistance level
        support: Support level
        volatility: Price volatility
        direction: "UP" or "DOWN"

    Returns:
        Probability between 0.0 and 1.0
    """
    if price <= 0 or resistance <= support or volatility < 0:
        return 0.0

    if direction == "UP":
        distance = resistance - price
        if distance <= 0:
            return 0.0
        # Probability increases as price approaches resistance
        prob = min(1.0, distance / (resistance - support) * 2.0)
        # Adjust for volatility
        if volatility > 0:
            prob *= 1.0 + min(1.0, volatility / price)
    elif direction == "DOWN":
        distance = price - support
        if distance <= 0:
            return 0.0
        prob = min(1.0, distance / (resistance - support) * 2.0)
        if volatility > 0:
            prob *= 1.0 + min(1.0, volatility / price)
    else:
        return 0.0

    return float(min(1.0, max(0.0, prob)))


def detect_breakout_signal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect breakout signals for all rows.

    Args:
        df: DataFrame with spot data

    Returns:
        DataFrame with breakout_signal column
    """
    if df.empty or "spot" not in df.columns:
        return df

    df = df.copy()

    # Compute support/resistance from recent data
    window = min(20, len(df))
    if window < 5:
        df["breakout_signal"] = "NONE"
        return df

    recent = df["spot"].tail(window)
    resistance = recent.max()
    support = recent.min()

    # Detect breakout for each row
    signals = []
    for idx, row in df.iterrows():
        subset = df.loc[:idx].tail(window)
        if len(subset) < 2:
            signals.append("NONE")
            continue

        pred = predict_breakout(subset, resistance, support)
        signals.append(pred["breakout_signal"])

    df["breakout_signal"] = signals
    return df


def main() -> None:
    """Test breakout predictor."""
    print("=== ANGEL ONE INDEX OPTIONS - BREAKOUT PREDICTOR ===")
    df = pd.DataFrame(
        {
            "spot": [22000, 22100, 22200, 22300, 22400],
        }
    )
    result = predict_breakout(df, resistance=22500, support=21900)
    print(f"Breakout prediction: {result}")


if __name__ == "__main__":
    main()
