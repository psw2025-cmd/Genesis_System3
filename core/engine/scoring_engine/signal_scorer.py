"""
Signal Scorer - Combine all signals into final score
"""

from typing import Dict

import numpy as np
import pandas as pd


def compute_final_score(df: pd.DataFrame, weights: Dict[str, float] | None = None) -> pd.DataFrame:
    """
    Compute final score by combining all signal components.

    Args:
        df: DataFrame with all signal components
        weights: Optional weights for each component

    Returns:
        DataFrame with final_score column
    """
    if df.empty:
        return df

    df = df.copy()

    # Default weights (rebalance so AI does not dominate)
    if weights is None:
        weights = {
            "greeks_score": 0.20,
            "trend_score": 0.20,
            "volatility_score": 0.15,
            "breakout_score": 0.15,
            "momentum_score": 0.15,
            "ai_score": 0.15,
        }

    # Compute component scores if not present
    if "greeks_score" not in df.columns:
        # Combine Greeks into score
        if "delta" in df.columns:
            # For CE: positive delta = bullish, for PE: negative delta = bullish
            delta_score = df["delta"].copy().fillna(0.0)
            if "side" in df.columns:
                # For PE, invert delta (PE benefits from price going down)
                delta_score = delta_score.where(df["side"] == "CE", -delta_score)
            # Normalize delta to -1 to +1 range (delta is typically 0 to 1 for CE, -1 to 0 for PE)
            # Scale it to make it more meaningful
            df["greeks_score"] = (delta_score * 2.0 - 1.0).clip(-1.0, 1.0).fillna(0.0)
        else:
            df["greeks_score"] = 0.0

    if "trend_score" not in df.columns:
        if "multi_tf_trend_score" in df.columns:
            df["trend_score"] = df["multi_tf_trend_score"].fillna(0.0)
        else:
            df["trend_score"] = 0.0

    if "volatility_score" not in df.columns:
        if "volatility_score" in df.columns:
            df["volatility_score"] = df["volatility_score"].fillna(0.0)
        else:
            df["volatility_score"] = 0.0

    if "breakout_score" not in df.columns:
        if "breakout_score" in df.columns:
            df["breakout_score"] = df["breakout_score"].fillna(0.0)
        else:
            df["breakout_score"] = 0.0

    if "momentum_score" not in df.columns:
        if "momentum_score" in df.columns:
            df["momentum_score"] = df["momentum_score"].fillna(0.0)
        else:
            df["momentum_score"] = 0.0

    if "ai_score" not in df.columns:
        # Use expected_move_score if available
        if "expected_move_score" in df.columns:
            df["ai_score"] = df["expected_move_score"].fillna(0.0)
        else:
            df["ai_score"] = 0.0

    # Ensure all component scores are numeric and filled
    for col in ["greeks_score", "trend_score", "volatility_score", "breakout_score", "momentum_score", "ai_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        else:
            df[col] = 0.0

    # Compute weighted final score
    base_score = (
        df["greeks_score"] * weights["greeks_score"]
        + df["trend_score"] * weights["trend_score"]
        + df["volatility_score"] * weights["volatility_score"]
        + df["breakout_score"] * weights["breakout_score"]
        + df["momentum_score"] * weights["momentum_score"]
        + df["ai_score"] * weights["ai_score"]
    )

    # Amplify score when multiple components agree (signal reinforcement)
    # Only amplify if we have non-zero components
    component_signs = pd.DataFrame(
        {
            "greeks": np.sign(df["greeks_score"]),
            "trend": np.sign(df["trend_score"]),
            "volatility": np.sign(df["volatility_score"]),
            "breakout": np.sign(df["breakout_score"]),
            "momentum": np.sign(df["momentum_score"]),
            "ai": np.sign(df["ai_score"]),
        }
    )

    # Count how many components agree (same sign, excluding zeros)
    non_zero_mask = (
        (df["greeks_score"].abs() > 0.001)
        | (df["trend_score"].abs() > 0.001)
        | (df["volatility_score"].abs() > 0.001)
        | (df["breakout_score"].abs() > 0.001)
        | (df["momentum_score"].abs() > 0.001)
        | (df["ai_score"].abs() > 0.001)
    )

    agreement_count = pd.Series([0] * len(df), index=df.index)
    if non_zero_mask.any():
        # Count agreements only for non-zero components
        for idx in df[non_zero_mask].index:
            signs = component_signs.loc[idx]
            # Count how many have the same sign as the first non-zero
            first_non_zero = None
            for col in component_signs.columns:
                if abs(df.loc[idx, col.replace("_sign", "_score").replace("greeks", "greeks_score")]) > 0.001:
                    first_non_zero = signs[col]
                    break
            if first_non_zero is not None:
                agreement_count.loc[idx] = (signs == first_non_zero).sum() - 1

    # Amplification factor: more agreement = stronger signal
    amplification = 1.0 + (agreement_count >= 3) * 0.5 + (agreement_count >= 4) * 0.5 + (agreement_count >= 5) * 0.5

    final_score = base_score * amplification

    # Ensure score is never exactly zero unless all components are zero
    all_zero_mask = (
        (df["greeks_score"].abs() < 0.001)
        & (df["trend_score"].abs() < 0.001)
        & (df["volatility_score"].abs() < 0.001)
        & (df["breakout_score"].abs() < 0.001)
        & (df["momentum_score"].abs() < 0.001)
        & (df["ai_score"].abs() < 0.001)
    )

    # For rows where not all components are zero, ensure final_score reflects that
    not_all_zero = ~all_zero_mask
    if not_all_zero.any():
        # Recompute for non-zero rows to ensure they get non-zero scores
        base_score_nonzero = (
            df.loc[not_all_zero, "greeks_score"] * weights["greeks_score"]
            + df.loc[not_all_zero, "trend_score"] * weights["trend_score"]
            + df.loc[not_all_zero, "volatility_score"] * weights["volatility_score"]
            + df.loc[not_all_zero, "breakout_score"] * weights["breakout_score"]
            + df.loc[not_all_zero, "momentum_score"] * weights["momentum_score"]
            + df.loc[not_all_zero, "ai_score"] * weights["ai_score"]
        )
        # Apply amplification
        amp_nonzero = amplification[not_all_zero]
        final_score_nonzero = (base_score_nonzero * amp_nonzero).clip(-1.0, 1.0)
        # Ensure minimum magnitude if any component is non-zero
        min_magnitude = 0.01
        final_score_nonzero = final_score_nonzero.where(
            final_score_nonzero.abs() >= min_magnitude, np.sign(final_score_nonzero) * min_magnitude
        )
        final_score.loc[not_all_zero] = final_score_nonzero.values

    # For all-zero rows, keep score at 0
    final_score.loc[all_zero_mask] = 0.0

    # Final clipping
    final_score = final_score.clip(-1.0, 1.0)

    df["final_score"] = final_score.values

    return df


def generate_signals(
    df: pd.DataFrame,
    buy_threshold: float = 0.40,
    sell_threshold: float = -0.40,
    thresholds_by_underlying: dict | None = None,
) -> pd.DataFrame:
    """
    Generate BUY/SELL/HOLD signals from final score.

    Args:
        df: DataFrame with final_score
        buy_threshold: Default threshold for BUY signal (used if thresholds_by_underlying not provided)
        sell_threshold: Default threshold for SELL signal (used if thresholds_by_underlying not provided)
        thresholds_by_underlying: Optional dict mapping underlying -> {"buy": float, "sell": float}

    Returns:
        DataFrame with signal column
    """
    if df.empty or "final_score" not in df.columns:
        return df

    # INSTRUMENTATION: Log threshold configuration
    import sys
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from core.utils.logger import logger

    logger.info(f"  generate_signals: default thresholds [buy={buy_threshold:.4f}, sell={sell_threshold:.4f}]")
    if thresholds_by_underlying:
        default_thresh = thresholds_by_underlying.get("default", {})
        logger.info(
            f"  generate_signals: using per-underlying thresholds [buy={default_thresh.get('buy', buy_threshold):.4f}, sell={default_thresh.get('sell', sell_threshold):.4f}]"
        )

    df = df.copy()

    score = pd.to_numeric(df["final_score"], errors="coerce").fillna(0.0)

    # Build per-row thresholds
    buy_thr_series = pd.Series(buy_threshold, index=df.index)
    sell_thr_series = pd.Series(sell_threshold, index=df.index)

    # Apply per-underlying thresholds if provided
    if thresholds_by_underlying and "underlying" in df.columns:
        for idx, row in df.iterrows():
            underlying = row.get("underlying", "")
            if underlying in thresholds_by_underlying:
                thresholds = thresholds_by_underlying[underlying]
                buy_thr_series.loc[idx] = thresholds.get("buy", buy_threshold)
                sell_thr_series.loc[idx] = thresholds.get("sell", sell_threshold)
            else:
                # Fallback to default
                default_thresh = thresholds_by_underlying.get("default", {})
                buy_thr_series.loc[idx] = default_thresh.get("buy", buy_threshold)
                sell_thr_series.loc[idx] = default_thresh.get("sell", sell_threshold)

    # Optional dynamic thresholds based on volatility regime / IV rank
    if "iv_rank" in df.columns:
        # Higher IV rank → slightly wider thresholds, lower IV → slightly tighter
        ivr = pd.to_numeric(df["iv_rank"], errors="coerce").fillna(50.0) / 100.0
        factor = 0.8 + 0.4 * ivr  # 0.8x to 1.2x
        buy_thr_series = buy_thr_series * factor
        sell_thr_series = sell_thr_series * factor

    # Generate signals with (possibly) row-wise thresholds
    def get_signal(row):
        s = row["final_score"]
        bt = row["_buy_thr"]
        st = row["_sell_thr"]
        if s > bt:
            return "BUY"
        elif s < st:
            return "SELL"
        else:
            return "HOLD"

    df["_buy_thr"] = buy_thr_series
    df["_sell_thr"] = sell_thr_series
    df["signal"] = df.apply(get_signal, axis=1)
    df = df.drop(columns=["_buy_thr", "_sell_thr"])

    # INSTRUMENTATION: Log signal generation results
    buy_count = len(df[df["signal"] == "BUY"])
    sell_count = len(df[df["signal"] == "SELL"])
    hold_count = len(df[df["signal"] == "HOLD"])
    logger.info(f"  generate_signals: AFTER threshold filter [BUY={buy_count}, SELL={sell_count}, HOLD={hold_count}]")

    if buy_count + sell_count == 0:
        score_min = df["final_score"].min()
        score_max = df["final_score"].max()
        score_mean = df["final_score"].mean()
        logger.warning(
            f"  ⚠️  NO ACTION SIGNALS: final_score range=[{score_min:.4f}, {score_max:.4f}], mean={score_mean:.4f}"
        )
        logger.warning(f"      Thresholds may be too strict. Check thresholds_by_underlying or adjust defaults.")

    # Signal strength (absolute score)
    df["signal_strength"] = np.abs(score).values

    # Ensure we have non-zero scores for BUY/SELL
    # If signal is BUY/SELL but score is near zero, adjust slightly
    buy_mask = df["signal"] == "BUY"
    sell_mask = df["signal"] == "SELL"

    # Use actual thresholds from series for adjustment
    if buy_mask.any():
        buy_thr_val = buy_thr_series[buy_mask].iloc[0] if buy_mask.any() else buy_threshold
        df.loc[buy_mask & (df["final_score"] <= 0), "final_score"] = buy_thr_val + 0.01
    if sell_mask.any():
        sell_thr_val = sell_thr_series[sell_mask].iloc[0] if sell_mask.any() else sell_threshold
        df.loc[sell_mask & (df["final_score"] >= 0), "final_score"] = sell_thr_val - 0.01

    return df
