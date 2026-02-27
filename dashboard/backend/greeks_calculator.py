"""
Greeks Calculator
Calculates option Greeks using Black-Scholes model
"""

import math
from typing import Dict, Optional
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


def calculate_greeks(
    spot_price: float,
    strike_price: float,
    time_to_expiry_days: float,
    risk_free_rate: float = 0.06,  # 6% annual
    implied_vol: Optional[float] = None,
    option_type: str = "CE",  # CE or PE
) -> Dict[str, Optional[float]]:
    """
    Calculate option Greeks using Black-Scholes

    Args:
        spot_price: Current spot price
        strike_price: Strike price
        time_to_expiry_days: Days to expiry
        risk_free_rate: Risk-free rate (annual)
        implied_vol: Implied volatility (0.01 to 2.5, i.e., 1% to 250%)
        option_type: "CE" (Call) or "PE" (Put)

    Returns:
        {
            "delta": float | None,
            "gamma": float | None,
            "theta": float | None,
            "vega": float | None,
            "available": bool
        }
    """
    if not implied_vol or implied_vol <= 0 or implied_vol > 2.5:
        return {"delta": None, "gamma": None, "theta": None, "vega": None, "available": False}

    if time_to_expiry_days <= 0:
        return {"delta": None, "gamma": None, "theta": None, "vega": None, "available": False}

    if spot_price <= 0 or strike_price <= 0:
        return {"delta": None, "gamma": None, "theta": None, "vega": None, "available": False}

    try:
        S = spot_price
        K = strike_price
        T = time_to_expiry_days / 365.0  # Convert to years
        r = risk_free_rate
        sigma = implied_vol

        # Calculate d1 and d2
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        # Standard normal CDF approximation
        def norm_cdf(x):
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))

        def norm_pdf(x):
            return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)

        N_d1 = norm_cdf(d1)
        N_d2 = norm_cdf(d2)
        n_d1 = norm_pdf(d1)

        if option_type.upper() == "CE":
            # Call option
            delta = N_d1
            theta = (-(S * n_d1 * sigma) / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * N_d2) / 365.0
        else:
            # Put option
            delta = N_d1 - 1
            theta = (-(S * n_d1 * sigma) / (2 * math.sqrt(T)) + r * K * math.exp(-r * T) * (1 - N_d2)) / 365.0

        gamma = n_d1 / (S * sigma * math.sqrt(T))
        vega = S * n_d1 * math.sqrt(T) / 100.0  # Per 1% change in vol

        return {
            "delta": round(delta, 4),
            "gamma": round(gamma, 6),
            "theta": round(theta, 2),
            "vega": round(vega, 2),
            "available": True,
        }
    except Exception as e:
        print(f"Error calculating Greeks: {e}")
        return {"delta": None, "gamma": None, "theta": None, "vega": None, "available": False}


def calculate_portfolio_greeks(positions: list) -> Dict[str, float]:
    """
    Calculate portfolio-level Greeks by summing position Greeks

    Args:
        positions: List of positions with greeks

    Returns:
        {
            "delta": float,
            "gamma": float,
            "theta": float,
            "vega": float
        }
    """
    portfolio = {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}

    for pos in positions:
        greeks = pos.get("greeks", {})
        qty = pos.get("qty", 0)

        if greeks.get("available", False):
            portfolio["delta"] += (greeks.get("delta", 0) or 0) * qty
            portfolio["gamma"] += (greeks.get("gamma", 0) or 0) * qty
            portfolio["theta"] += (greeks.get("theta", 0) or 0) * qty
            portfolio["vega"] += (greeks.get("vega", 0) or 0) * qty

    return portfolio
