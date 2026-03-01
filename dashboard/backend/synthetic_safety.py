"""
Synthetic Data Safety - Ensures synthetic data is never used for live trading.
Auto-switch logic: when market closed + synthetic available -> data_source=synthetic, trading_blocked=True.
"""

from typing import Optional


def is_synthetic_safe_for_trading(data_source: Optional[str]) -> bool:
    """
    Returns False when data is synthetic - trading must be blocked.
    Only live/cached (with market open) data is safe for trading decisions.
    """
    if not data_source:
        return False
    ds = str(data_source).lower()
    return ds not in ("synthetic", "simulated", "mock", "demo")


def get_synthetic_safety_flags(data_source: Optional[str], market_is_open: bool) -> dict:
    """
    Get safety flags for UI and validation.
    """
    safe = is_synthetic_safe_for_trading(data_source)
    return {
        "trading_allowed": safe and market_is_open,
        "data_synthetic": not safe,
        "synthetic_safe": safe,
    }
