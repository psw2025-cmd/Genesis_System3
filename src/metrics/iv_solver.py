"""
Implied Volatility Solver using Black-Scholes
Newton-Raphson with bisection fallback
"""
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
from typing import Optional
import math


def black_scholes_price(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    option_type: str
) -> float:
    """
    Calculate Black-Scholes option price.
    
    Args:
        spot: Current spot price
        strike: Strike price
        time_to_expiry: Time to expiry in years
        risk_free_rate: Risk-free rate (e.g., 0.06 for 6%)
        volatility: Annualized volatility (e.g., 0.20 for 20%)
        option_type: 'CE' or 'PE'
    
    Returns:
        Option price
    """
    if time_to_expiry <= 0:
        return max(0, spot - strike) if option_type == 'CE' else max(0, strike - spot)
    
    if volatility <= 0:
        # Intrinsic value only
        if option_type == 'CE':
            return max(0, spot - strike)
        else:
            return max(0, strike - spot)
    
    S = spot
    K = strike
    T = time_to_expiry
    r = risk_free_rate
    sigma = volatility
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == 'CE':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:  # PE
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return max(0, price)


def black_scholes_vega(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float
) -> float:
    """
    Calculate Vega (sensitivity to volatility).
    
    Args:
        spot: Current spot price
        strike: Strike price
        time_to_expiry: Time to expiry in years
        risk_free_rate: Risk-free rate
        volatility: Annualized volatility
    
    Returns:
        Vega value
    """
    if time_to_expiry <= 0 or volatility <= 0:
        return 0.0
    
    S = spot
    K = strike
    T = time_to_expiry
    r = risk_free_rate
    sigma = volatility
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T)
    
    return vega


def solve_iv_newton_raphson(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    market_price: float,
    option_type: str,
    max_iterations: int = 100,
    tolerance: float = 1e-6,
    initial_guess: float = 0.2
) -> Optional[float]:
    """
    Solve for implied volatility using Newton-Raphson method.
    
    Args:
        spot: Current spot price
        strike: Strike price
        time_to_expiry: Time to expiry in years
        risk_free_rate: Risk-free rate
        market_price: Observed market price
        option_type: 'CE' or 'PE'
        max_iterations: Maximum iterations
        tolerance: Convergence tolerance
        initial_guess: Initial volatility guess (e.g., 0.2 for 20%)
    
    Returns:
        Implied volatility or None if failed
    """
    if time_to_expiry <= 0 or market_price <= 0:
        return None
    
    # Intrinsic value check
    if option_type == 'CE':
        intrinsic = max(0, spot - strike)
    else:
        intrinsic = max(0, strike - spot)
    
    if market_price < intrinsic:
        # Market price below intrinsic - invalid
        return None
    
    sigma = initial_guess
    
    for i in range(max_iterations):
        price = black_scholes_price(spot, strike, time_to_expiry, risk_free_rate, sigma, option_type)
        vega = black_scholes_vega(spot, strike, time_to_expiry, risk_free_rate, sigma)
        
        if abs(vega) < 1e-10:
            # Vega too small, switch to bisection
            break
        
        error = price - market_price
        if abs(error) < tolerance:
            return max(0, sigma)  # Ensure non-negative
        
        # Newton-Raphson update
        sigma_new = sigma - error / vega
        
        # Bounds check
        if sigma_new < 0:
            sigma_new = 0.01
        elif sigma_new > 5.0:  # 500% max
            sigma_new = 5.0
        
        if abs(sigma_new - sigma) < tolerance:
            return max(0, sigma_new)
        
        sigma = sigma_new
    
    # Fallback to bisection
    return solve_iv_bisection(
        spot, strike, time_to_expiry, risk_free_rate, market_price, option_type
    )


def solve_iv_bisection(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    market_price: float,
    option_type: str,
    low: float = 0.001,
    high: float = 5.0,
    max_iterations: int = 100,
    tolerance: float = 1e-6
) -> Optional[float]:
    """
    Solve for implied volatility using bisection method (fallback).
    
    Args:
        spot: Current spot price
        strike: Strike price
        time_to_expiry: Time to expiry in years
        risk_free_rate: Risk-free rate
        market_price: Observed market price
        option_type: 'CE' or 'PE'
        low: Lower bound for volatility
        high: Upper bound for volatility
        max_iterations: Maximum iterations
        tolerance: Convergence tolerance
    
    Returns:
        Implied volatility or None if failed
    """
    if time_to_expiry <= 0 or market_price <= 0:
        return None
    
    def price_diff(sigma):
        price = black_scholes_price(spot, strike, time_to_expiry, risk_free_rate, sigma, option_type)
        return price - market_price
    
    # Check bounds
    low_price = black_scholes_price(spot, strike, time_to_expiry, risk_free_rate, low, option_type)
    high_price = black_scholes_price(spot, strike, time_to_expiry, risk_free_rate, high, option_type)
    
    if low_price > market_price or high_price < market_price:
        # Market price outside bounds
        return None
    
    try:
        # Use scipy's brentq (robust root finder)
        iv = brentq(price_diff, low, high, maxiter=max_iterations, xtol=tolerance)
        return max(0, iv)
    except:
        # Fallback manual bisection
        for i in range(max_iterations):
            mid = (low + high) / 2.0
            mid_price = black_scholes_price(spot, strike, time_to_expiry, risk_free_rate, mid, option_type)
            
            if abs(mid_price - market_price) < tolerance:
                return max(0, mid)
            
            if mid_price < market_price:
                low = mid
            else:
                high = mid
            
            if (high - low) < tolerance:
                return max(0, (low + high) / 2.0)
    
    return None


def solve_implied_volatility(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    market_price: float,
    option_type: str,
    method: str = "newton"
) -> Optional[float]:
    """
    Solve for implied volatility (main entry point).
    
    Args:
        spot: Current spot price
        strike: Strike price
        time_to_expiry: Time to expiry in years
        risk_free_rate: Risk-free rate (default: 0.06 for 6%)
        market_price: Observed market price
        option_type: 'CE' or 'PE'
        method: 'newton' (default) or 'bisection'
    
    Returns:
        Implied volatility (0.0 to 5.0) or None if failed
    """
    if method == "newton":
        return solve_iv_newton_raphson(
            spot, strike, time_to_expiry, risk_free_rate, market_price, option_type
        )
    else:
        return solve_iv_bisection(
            spot, strike, time_to_expiry, risk_free_rate, market_price, option_type
        )
