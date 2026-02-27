"""
Greeks Calculator - Compute delta, gamma, theta, vega for options
"""

import numpy as np
import pandas as pd
from typing import Dict, Any
from math import log, sqrt, exp

try:
    from scipy.stats import norm

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

    # Fallback to approximate normal CDF
    def norm_cdf(x):
        """Approximate normal CDF using error function."""
        return 0.5 * (1 + np.sign(x) * (1 - np.exp(-2 * x * x / np.pi)))

    def norm_pdf(x):
        """Approximate normal PDF."""
        return np.exp(-0.5 * x * x) / np.sqrt(2 * np.pi)

    class norm:
        @staticmethod
        def cdf(x):
            return norm_cdf(x)

        @staticmethod
        def pdf(x):
            return norm_pdf(x)


def black_scholes_price(
    spot: float, strike: float, time_to_expiry: float, risk_free_rate: float, volatility: float, option_type: str
) -> float:
    """
    Black-Scholes option pricing.

    Args:
        spot: Current spot price
        strike: Strike price
        time_to_expiry: Time to expiry in years
        risk_free_rate: Risk-free rate (default 0.06 for 6%)
        volatility: Implied volatility (decimal, e.g., 0.20 for 20%)
        option_type: "CE" or "PE"

    Returns:
        Option price
    """
    if time_to_expiry <= 0 or volatility <= 0 or spot <= 0 or strike <= 0:
        return 0.0

    S = spot
    K = strike
    T = time_to_expiry
    r = risk_free_rate
    sigma = volatility

    d1 = (log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    if option_type == "CE":
        price = S * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)
    else:  # PE
        price = K * exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return max(0.0, price)


def compute_greeks(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    option_type: str,
    option_price: float = None,
) -> Dict[str, float]:
    """
    Compute all Greeks for an option.

    Args:
        spot: Current spot price
        strike: Strike price
        time_to_expiry: Time to expiry in years
        risk_free_rate: Risk-free rate (default 0.06)
        volatility: Implied volatility (decimal)
        option_type: "CE" or "PE"
        option_price: Option price (if None, computed via BS)

    Returns:
        Dict with delta, gamma, theta, vega
    """
    if time_to_expiry <= 0 or volatility <= 0 or spot <= 0 or strike <= 0:
        return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}

    S = spot
    K = strike
    T = time_to_expiry
    r = risk_free_rate
    sigma = volatility

    d1 = (log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    # Delta
    if option_type == "CE":
        delta = norm.cdf(d1)
    else:  # PE
        delta = -norm.cdf(-d1)

    # Gamma (same for CE and PE)
    gamma = norm.pdf(d1) / (S * sigma * sqrt(T))
    if not np.isfinite(gamma):
        gamma = 0.0

    # Theta (per day, negative for time decay)
    if option_type == "CE":
        theta = (-(S * norm.pdf(d1) * sigma) / (2 * sqrt(T)) - r * K * exp(-r * T) * norm.cdf(d2)) / 365.0
    else:  # PE
        theta = (-(S * norm.pdf(d1) * sigma) / (2 * sqrt(T)) + r * K * exp(-r * T) * norm.cdf(-d2)) / 365.0

    if not np.isfinite(theta):
        theta = 0.0

    # Vega (per 1% change in volatility)
    vega = S * norm.pdf(d1) * sqrt(T) / 100.0
    if not np.isfinite(vega):
        vega = 0.0

    return {"delta": float(delta), "gamma": float(gamma), "theta": float(theta), "vega": float(vega)}


def compute_greeks_for_df(df: pd.DataFrame, risk_free_rate: float = 0.06) -> pd.DataFrame:
    """
    Compute Greeks for all rows in DataFrame.

    Required columns: spot, strike, ltp, side, expiry (or time_to_expiry)

    Args:
        df: DataFrame with option data
        risk_free_rate: Risk-free rate (default 0.06)

    Returns:
        DataFrame with added columns: delta, gamma, theta, vega, iv_estimate
    """
    if df.empty:
        return df

    df = df.copy()

    # Ensure required columns exist
    required = ["spot", "strike", "ltp", "side"]
    for col in required:
        if col not in df.columns:
            df[col] = 0.0

    # Compute time to expiry
    if "time_to_expiry" not in df.columns:
        if "expiry" in df.columns:
            from datetime import datetime, date

            today = date.today()

            def parse_expiry(exp_str):
                try:
                    # Try common formats
                    for fmt in ["%d%b%Y", "%d-%b-%Y", "%Y-%m-%d", "%d/%m/%Y"]:
                        try:
                            exp_date = datetime.strptime(str(exp_str), fmt).date()
                            days = (exp_date - today).days
                            return max(1.0 / 365.0, days / 365.0)
                        except:
                            continue
                    return 1.0 / 365.0  # Default to 1 day
                except:
                    return 1.0 / 365.0

            df["time_to_expiry"] = df["expiry"].apply(parse_expiry)
        else:
            df["time_to_expiry"] = 1.0 / 365.0  # Default 1 day

    # Estimate IV if not present
    if "iv" not in df.columns and "implied_volatility" not in df.columns:
        from core.engine.angel_iv_estimator import estimate_synthetic_iv

        iv_values = []
        for _, row in df.iterrows():
            iv = estimate_synthetic_iv(
                float(row.get("ltp", 0.0)),
                float(row.get("spot", 0.0)),
                float(row.get("strike", 0.0)),
                float(row.get("time_to_expiry", 1.0 / 365.0)),
                str(row.get("side", "CE")),
            )
            iv_values.append(iv)
        df["iv_estimate"] = iv_values
        df["iv"] = df["iv_estimate"]
    elif "iv" not in df.columns:
        df["iv"] = df["implied_volatility"]

    # Compute Greeks
    deltas = []
    gammas = []
    thetas = []
    vegas = []

    for _, row in df.iterrows():
        spot = float(row.get("spot", 0.0))
        strike = float(row.get("strike", 0.0))
        tte = float(row.get("time_to_expiry", 1.0 / 365.0))
        iv = float(row.get("iv", 0.0))
        opt_type = str(row.get("side", "CE"))

        if spot > 0 and strike > 0 and tte > 0 and iv > 0:
            greeks = compute_greeks(spot, strike, tte, risk_free_rate, iv, opt_type)
            deltas.append(greeks["delta"])
            gammas.append(greeks["gamma"])
            thetas.append(greeks["theta"])
            vegas.append(greeks["vega"])
        else:
            deltas.append(0.0)
            gammas.append(0.0)
            thetas.append(0.0)
            vegas.append(0.0)

    df["delta"] = deltas
    df["gamma"] = gammas
    df["theta"] = thetas
    df["vega"] = vegas

    return df
