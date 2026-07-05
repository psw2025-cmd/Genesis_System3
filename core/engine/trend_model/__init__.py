"""
Trend Model - Multi-timeframe trend detection
"""

from .trend_analyzer import compute_multi_timeframe_trend, compute_trend_features

__all__ = ["compute_trend_features", "compute_multi_timeframe_trend"]
