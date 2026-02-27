"""
Angel One Index Options - Synthetic IV Estimator Refinement

Estimates implied volatility from option prices.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from math import log, sqrt, exp


def estimate_synthetic_iv(
    ltp: float,
    spot: float,
    strike: float,
    time_to_expiry: float,
    option_type: str,
) -> float:
    """
    Estimate synthetic IV from option price.

    Args:
        ltp: Last traded price (option premium)
        spot: Current spot price
        strike: Strike price
        time_to_expiry: Time to expiry in years
        option_type: "CE" or "PE"

    Returns:
        Estimated IV as decimal (e.g., 0.20 for 20%)
    """
    if ltp <= 0 or spot <= 0 or strike <= 0 or time_to_expiry <= 0:
        return 0.0

    if option_type not in ["CE", "PE"]:
        return 0.0

    # Simplified IV estimation using Black-Scholes approximation
    # This is a placeholder - real IV calculation requires iterative solving

    moneyness = (spot - strike) / strike
    intrinsic = max(0, spot - strike) if option_type == "CE" else max(0, strike - spot)
    time_value = ltp - intrinsic

    if time_value <= 0 or time_to_expiry <= 0:
        return 0.0

    # Rough IV estimate: time_value / (spot * sqrt(time))
    iv_estimate = time_value / (spot * sqrt(time_to_expiry))
    iv_estimate = min(5.0, max(0.01, iv_estimate))  # Clamp to reasonable range

    return float(iv_estimate)


def refine_iv_estimate(df_signals: pd.DataFrame) -> pd.DataFrame:
    """
    Refine IV estimates for all signals.

    Args:
        df_signals: DataFrame with ltp, spot, strike, expiry data

    Returns:
        DataFrame with synthetic_iv column
    """
    if df_signals.empty:
        return df_signals

    df = df_signals.copy()

    required = ["ltp", "spot", "strike"]
    if not all(col in df.columns for col in required):
        df["synthetic_iv"] = 0.0
        return df

    # Default time to expiry (assume 1 day = 1/365 years)
    time_to_expiry = df.get("time_to_expiry", pd.Series([1.0 / 365.0] * len(df)))

    iv_values = []
    for _, row in df.iterrows():
        ltp = float(row.get("ltp", 0.0))
        spot = float(row.get("spot", 0.0))
        strike = float(row.get("strike", 0.0))
        tte = float(row.get("time_to_expiry", time_to_expiry.iloc[0] if len(time_to_expiry) > 0 else 1.0 / 365.0))
        opt_type = row.get("side", "CE")

        iv = estimate_synthetic_iv(ltp, spot, strike, tte, opt_type)
        iv_values.append(iv)

    df["synthetic_iv"] = iv_values

    # Compute IV rank and percentile
    if len(iv_values) > 1:
        iv_series = pd.Series(iv_values)
        df["iv_rank"] = iv_series.rank(pct=True) * 100.0
        df["iv_percentile"] = iv_series.quantile([0.25, 0.5, 0.75]).apply(
            lambda x: (
                "LOW" if iv_series.iloc[-1] < x.iloc[0] else "MEDIUM" if iv_series.iloc[-1] < x.iloc[1] else "HIGH"
            )
        )
    else:
        df["iv_rank"] = 50.0
        df["iv_percentile"] = "MEDIUM"

    return df


def compute_iv_rank(iv: float, iv_history: pd.Series) -> float:
    """
    Compute IV percentile rank.

    Args:
        iv: Current IV value
        iv_history: Historical IV values

    Returns:
        Percentile rank (0.0 to 100.0)
    """
    if len(iv_history) == 0:
        return 50.0

    rank = (iv_history < iv).sum() / len(iv_history) * 100.0
    return float(rank)


def main() -> None:
    """Test IV estimator."""
    print("=== ANGEL ONE INDEX OPTIONS - IV ESTIMATOR ===")
    df = pd.DataFrame(
        {
            "ltp": [100, 105, 110],
            "spot": [22000, 22100, 22200],
            "strike": [22000, 22100, 22200],
            "side": ["CE", "CE", "CE"],
            "time_to_expiry": [1.0 / 365.0] * 3,
        }
    )
    result = refine_iv_estimate(df)
    print(result[["ltp", "spot", "synthetic_iv", "iv_rank"]].to_string())


if __name__ == "__main__":
    main()
