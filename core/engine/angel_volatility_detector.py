"""
Angel One Index Options - Real-Time Volatility Detection

Detects volatility regimes and shocks in real-time market data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def detect_volatility_regime(df_signals: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    Detect volatility regime from signals DataFrame.

    Args:
        df_signals: DataFrame with spot/ltp data
        window: Rolling window for volatility calculation

    Returns:
        DataFrame with added volatility regime columns
    """
    if df_signals.empty:
        return df_signals

    df = df_signals.copy()

    # Ensure window is valid
    if window < 3:
        window = 3

    # Compute rolling volatility
    if "spot" in df.columns:
        df["spot_volatility"] = df["spot"].rolling(window=window, min_periods=1).std()
        df["volatility_regime"] = df["spot_volatility"].apply(_classify_volatility_state)

    if "ltp" in df.columns:
        df["ltp_volatility"] = df["ltp"].rolling(window=window, min_periods=1).std()

    return df


def compute_volatility_shock(spot_series: pd.Series, threshold: float = 2.0) -> bool:
    """
    Detect volatility shock (sudden large move).

    Args:
        spot_series: Series of spot prices
        threshold: Standard deviation multiplier threshold

    Returns:
        True if volatility shock detected
    """
    if len(spot_series) < 2:
        return False

    if threshold <= 0:
        threshold = 2.0

    # Compute change
    changes = spot_series.pct_change().dropna()
    if len(changes) == 0:
        return False

    # Check if latest change exceeds threshold * std
    std = changes.std()
    mean = changes.mean()
    latest_change = abs(changes.iloc[-1])

    return latest_change > (mean + threshold * std)


def classify_volatility_state(df: pd.DataFrame) -> str:
    """
    Classify overall volatility state.

    Returns: "LOW", "NORMAL", "HIGH", "EXTREME"
    """
    if df.empty or "spot_volatility" not in df.columns:
        return "NORMAL"

    vol = df["spot_volatility"].dropna()
    if len(vol) == 0:
        return "NORMAL"

    vol_mean = vol.mean()
    vol_std = vol.std()

    if vol_mean < vol_std * 0.5:
        return "LOW"
    elif vol_mean < vol_std * 1.5:
        return "NORMAL"
    elif vol_mean < vol_std * 3.0:
        return "HIGH"
    else:
        return "EXTREME"


def _classify_volatility_state(vol_value: float) -> str:
    """Helper to classify single volatility value."""
    if pd.isna(vol_value) or vol_value <= 0:
        return "NORMAL"

    # Simple thresholds (can be tuned)
    if vol_value < 50:
        return "LOW"
    elif vol_value < 150:
        return "NORMAL"
    elif vol_value < 300:
        return "HIGH"
    else:
        return "EXTREME"


def main() -> None:
    """Test volatility detector."""
    print("=== ANGEL ONE INDEX OPTIONS - VOLATILITY DETECTOR ===")
    # Test with sample data
    df = pd.DataFrame(
        {
            "spot": [22000, 22100, 22050, 22200, 22150],
            "ltp": [100, 105, 102, 110, 108],
        }
    )
    result = detect_volatility_regime(df, window=3)
    print(result[["spot", "volatility_regime"]].to_string())


if __name__ == "__main__":
    main()
