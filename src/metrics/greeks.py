"""
Greeks Calculator using Black-Scholes
"""

from typing import Dict, Optional

import numpy as np
from scipy.stats import norm

from src.metrics.iv_solver import black_scholes_price


def calculate_greeks(
    spot: float, strike: float, time_to_expiry: float, risk_free_rate: float, volatility: float, option_type: str
) -> Dict[str, float]:
    """
    Calculate all Greeks using Black-Scholes model.

    Args:
        spot: Current spot price
        strike: Strike price
        time_to_expiry: Time to expiry in years
        risk_free_rate: Risk-free rate (e.g., 0.06 for 6%)
        volatility: Annualized volatility (e.g., 0.20 for 20%)
        option_type: 'CE' or 'PE'

    Returns:
        dict with keys: delta, gamma, theta, vega, rho
    """
    if time_to_expiry <= 0:
        # Expired option
        return {
            "delta": 1.0 if (option_type == "CE" and spot > strike) or (option_type == "PE" and spot < strike) else 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "vega": 0.0,
            "rho": 0.0,
        }

    if volatility <= 0:
        # No volatility
        return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}

    S = spot
    K = strike
    T = time_to_expiry
    r = risk_free_rate
    sigma = volatility

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    # Delta
    if option_type == "CE":
        delta = norm.cdf(d1)
    else:  # PE
        delta = -norm.cdf(-d1)

    # Gamma (same for CE and PE)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))

    # Theta (per day, negative for time decay)
    if option_type == "CE":
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365.0
    else:  # PE
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365.0

    # Vega (same for CE and PE)
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100.0  # Per 1% change in IV

    # Rho (sensitivity to interest rate)
    if option_type == "CE":
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100.0  # Per 1% change in rate
    else:  # PE
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100.0

    return {"delta": float(delta), "gamma": float(gamma), "theta": float(theta), "vega": float(vega), "rho": float(rho)}


def calculate_greeks_from_market_price(
    spot: float, strike: float, time_to_expiry: float, risk_free_rate: float, market_price: float, option_type: str
) -> Optional[Dict[str, float]]:
    """
    Calculate Greeks from market price (solves IV first).

    Args:
        spot: Current spot price
        strike: Strike price
        time_to_expiry: Time to expiry in years
        risk_free_rate: Risk-free rate
        market_price: Observed market price
        option_type: 'CE' or 'PE'

    Returns:
        dict with keys: delta, gamma, theta, vega, rho, iv
        Returns None if IV solving fails
    """
    from src.metrics.iv_solver import solve_implied_volatility

    # Solve for IV
    iv = solve_implied_volatility(spot, strike, time_to_expiry, risk_free_rate, market_price, option_type)

    if iv is None:
        return None

    # Calculate Greeks with solved IV
    greeks = calculate_greeks(spot, strike, time_to_expiry, risk_free_rate, iv, option_type)
    greeks["iv"] = float(iv)

    return greeks
