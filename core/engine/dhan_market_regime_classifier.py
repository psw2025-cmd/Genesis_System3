"""
Dhan Index Options - Market Regime Classifier - UPGRADED

Classifies current market regime (trending, ranging, volatile, etc.).

UPGRADED FEATURES:
- Strategy switching based on regime
- Multiple trading strategies (momentum, mean reversion, breakout, volatility)
- Automatic strategy selection and parameter adjustment
- Enhanced regime classification with more granular detection
"""

from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


class TradingStrategy(Enum):
    """Available trading strategies."""

    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    VOLATILITY = "volatility"
    TREND_FOLLOWING = "trend_following"
    RANGE_TRADING = "range_trading"


class StrategySwitcher:
    """Manages strategy switching based on market regime."""

    # Regime to strategy mapping
    REGIME_STRATEGY_MAP = {
        "TRENDING_UP": TradingStrategy.MOMENTUM,
        "TRENDING_DOWN": TradingStrategy.MOMENTUM,
        "RANGING": TradingStrategy.MEAN_REVERSION,
        "VOLATILE": TradingStrategy.VOLATILITY,
        "CALM": TradingStrategy.RANGE_TRADING,
        "BREAKOUT_UP": TradingStrategy.BREAKOUT,
        "BREAKOUT_DOWN": TradingStrategy.BREAKOUT,
    }

    # Strategy configurations
    STRATEGY_CONFIGS = {
        TradingStrategy.MOMENTUM: {
            "entry_threshold": 0.7,
            "exit_threshold": 0.3,
            "position_size_multiplier": 1.2,
            "stoploss_pct": 3.0,
            "target_pct": 8.0,
            "hold_duration_min": 15,
        },
        TradingStrategy.MEAN_REVERSION: {
            "entry_threshold": 0.6,
            "exit_threshold": 0.4,
            "position_size_multiplier": 0.8,
            "stoploss_pct": 2.5,
            "target_pct": 5.0,
            "hold_duration_min": 30,
        },
        TradingStrategy.BREAKOUT: {
            "entry_threshold": 0.75,
            "exit_threshold": 0.25,
            "position_size_multiplier": 1.5,
            "stoploss_pct": 4.0,
            "target_pct": 12.0,
            "hold_duration_min": 10,
        },
        TradingStrategy.VOLATILITY: {
            "entry_threshold": 0.65,
            "exit_threshold": 0.35,
            "position_size_multiplier": 1.0,
            "stoploss_pct": 5.0,
            "target_pct": 10.0,
            "hold_duration_min": 20,
        },
        TradingStrategy.TREND_FOLLOWING: {
            "entry_threshold": 0.7,
            "exit_threshold": 0.3,
            "position_size_multiplier": 1.3,
            "stoploss_pct": 3.5,
            "target_pct": 9.0,
            "hold_duration_min": 25,
        },
        TradingStrategy.RANGE_TRADING: {
            "entry_threshold": 0.55,
            "exit_threshold": 0.45,
            "position_size_multiplier": 0.9,
            "stoploss_pct": 2.0,
            "target_pct": 4.0,
            "hold_duration_min": 45,
        },
    }

    @classmethod
    def get_strategy_for_regime(cls, regime: str) -> TradingStrategy:
        """Get recommended strategy for a given regime."""
        return cls.REGIME_STRATEGY_MAP.get(regime, TradingStrategy.MEAN_REVERSION)

    @classmethod
    def get_strategy_config(cls, strategy: TradingStrategy, regime: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for a strategy, adjusted for regime if provided."""
        config = cls.STRATEGY_CONFIGS.get(strategy, cls.STRATEGY_CONFIGS[TradingStrategy.MEAN_REVERSION]).copy()

        # Adjust for regime if provided
        if regime:
            if regime == "VOLATILE":
                config["stoploss_pct"] *= 1.5
                config["target_pct"] *= 1.2
            elif regime == "CALM":
                config["stoploss_pct"] *= 0.8
                config["target_pct"] *= 0.9
            elif regime in ["TRENDING_UP", "TRENDING_DOWN"]:
                config["target_pct"] *= 1.1
                config["position_size_multiplier"] *= 1.1

        return config

    @classmethod
    def switch_strategy(cls, current_regime: str, previous_regime: Optional[str] = None) -> Dict[str, Any]:
        """
        Switch strategy based on regime change.

        Returns:
            Dict with new strategy, config, and switch reason
        """
        new_strategy = cls.get_strategy_for_regime(current_regime)
        config = cls.get_strategy_config(new_strategy, current_regime)

        result = {
            "strategy": new_strategy.value,
            "config": config,
            "regime": current_regime,
            "switched": previous_regime != current_regime if previous_regime else True,
        }

        if previous_regime and previous_regime != current_regime:
            old_strategy = cls.get_strategy_for_regime(previous_regime)
            result["previous_strategy"] = old_strategy.value
            result["switch_reason"] = f"Regime changed from {previous_regime} to {current_regime}"

        return result


def classify_market_regime(df_signals: pd.DataFrame) -> str:
    """
    Classify current market regime.

    Returns: "TRENDING_UP", "TRENDING_DOWN", "RANGING", "VOLATILE", "CALM"
    """
    if df_signals.empty or "spot" not in df_signals.columns:
        return "RANGING"

    spot = df_signals["spot"].dropna()
    if len(spot) < 5:
        return "RANGING"

    # Compute regime features
    features = compute_regime_features(spot, spot.rolling(5).std())

    # Classify based on features
    trend = features.get("trend", 0.0)
    volatility = features.get("volatility", 0.0)
    price_range = features.get("range", 0.0)

    # Enhanced classification with breakout detection
    if len(spot) >= 20:
        recent_high = spot.tail(20).max()
        recent_low = spot.tail(20).min()
        current_price = spot.iloc[-1]

        # Breakout detection
        if current_price > recent_high * 1.01:  # 1% above recent high
            return "BREAKOUT_UP"
        elif current_price < recent_low * 0.99:  # 1% below recent low
            return "BREAKOUT_DOWN"

    # Volatility-based classification
    if volatility > 200:
        return "VOLATILE"
    elif volatility < 50:
        return "CALM"

    # Trend-based classification
    if trend > 0.1:
        return "TRENDING_UP"
    elif trend < -0.1:
        return "TRENDING_DOWN"

    # Range-based classification
    if price_range < 0.02:  # Very tight range
        return "RANGING"
    else:
        return "RANGING"


def compute_regime_features(
    spot_series: pd.Series,
    vol_series: pd.Series,
) -> Dict[str, float]:
    """
    Compute features for regime classification.

    Args:
        spot_series: Series of spot prices
        vol_series: Series of volatility values

    Returns:
        Dict with regime features
    """
    if len(spot_series) < 2:
        return {
            "trend": 0.0,
            "volatility": 0.0,
            "range": 0.0,
        }

    # Trend: slope of price
    x = np.arange(len(spot_series))
    y = spot_series.values
    trend = np.polyfit(x, y, 1)[0] / spot_series.mean() if spot_series.mean() > 0 else 0.0

    # Volatility: average volatility
    volatility = vol_series.mean() if len(vol_series) > 0 else spot_series.std()

    # Range: price range
    price_range = (spot_series.max() - spot_series.min()) / spot_series.mean() if spot_series.mean() > 0 else 0.0

    return {
        "trend": float(trend),
        "volatility": float(volatility),
        "range": float(price_range),
    }


def adjust_strategy_for_regime(
    regime: str,
    current_strategy: Optional[Dict[str, Any]] = None,
    previous_regime: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Adjust or switch trading strategy based on market regime.

    Args:
        regime: Current market regime
        current_strategy: Current strategy parameters (optional)
        previous_regime: Previous regime for switch detection (optional)

    Returns:
        Adjusted or switched strategy configuration
    """
    # Use strategy switcher to get new strategy
    switch_result = StrategySwitcher.switch_strategy(regime, previous_regime)

    # If current strategy provided, merge with new config
    if current_strategy:
        adjusted = current_strategy.copy()
        adjusted.update(switch_result["config"])
        adjusted["strategy"] = switch_result["strategy"]
        adjusted["regime"] = switch_result["regime"]
    else:
        adjusted = switch_result["config"].copy()
        adjusted["strategy"] = switch_result["strategy"]
        adjusted["regime"] = switch_result["regime"]

    adjusted["strategy_switched"] = switch_result["switched"]
    if "switch_reason" in switch_result:
        adjusted["switch_reason"] = switch_result["switch_reason"]

    return adjusted


def get_optimal_strategy_for_regime(regime: str) -> Dict[str, Any]:
    """
    Get optimal strategy configuration for a given regime.

    Args:
        regime: Current market regime

    Returns:
        Complete strategy configuration
    """
    strategy = StrategySwitcher.get_strategy_for_regime(regime)
    config = StrategySwitcher.get_strategy_config(strategy, regime)

    return {"strategy": strategy.value, "regime": regime, **config}


def main() -> None:
    """Test market regime classifier."""
    print("=== ANGEL ONE INDEX OPTIONS - MARKET REGIME CLASSIFIER ===")
    df = pd.DataFrame(
        {
            "spot": [22000, 22100, 22200, 22300, 22400],
        }
    )
    regime = classify_market_regime(df)
    print(f"Market regime: {regime}")


if __name__ == "__main__":
    main()
