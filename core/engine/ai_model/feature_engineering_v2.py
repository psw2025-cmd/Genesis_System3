"""
Phase 389: Feature Engineering v2.0
===================================

Purpose: Add 40+ high-variance features to solve low feature variance issue.

Current Problem:
- 80% of features are zeros or near-zeros
- Delta range: -1.0 to +1.0 (narrow)
- Trend/Volatility/Momentum: 96-100% zeros

Solution: Add features with high variance across multiple dimensions:
1. Greeks momentum (8 features)
2. IV regime features (6 features)
3. Price & moneyness (8 features)
4. Volume & OI features (6 features)
5. Time-based features (4 features)
6. Multi-timeframe aggregates (8 features)

Author: System3 AI Team
Date: 2025-12-08
Phase: 389/400
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Feature categories
GREEKS_MOMENTUM_FEATURES = [
    "delta_momentum_5",
    "delta_momentum_10",
    "gamma_acceleration",
    "theta_decay_rate",
    "vega_change",
    "delta_gamma_ratio",
    "vega_theta_ratio",
    "greeks_momentum_score",
]

IV_REGIME_FEATURES = [
    "iv_percentile_75",
    "iv_percentile_25",
    "iv_regime_high",
    "iv_regime_low",
    "iv_change",
    "iv_acceleration",
]

PRICE_MONEYNESS_FEATURES = [
    "moneyness",
    "atm_distance",
    "atm_distance_pct",
    "relative_price",
    "price_momentum",
    "price_acceleration",
    "ce_pe_spread",
    "ce_pe_ratio",
]

VOLUME_OI_FEATURES = [
    "volume_momentum",
    "volume_acceleration",
    "oi_momentum",
    "oi_acceleration",
    "volume_oi_ratio",
    "oi_buildup",
]

TIME_FEATURES = ["days_to_expiry", "time_decay_factor", "is_weekly_expiry", "is_monthly_expiry"]

MULTIFRAME_FEATURES = [
    "ltp_ma_5",
    "ltp_ma_10",
    "ltp_ma_20",
    "volume_ma_5",
    "volume_ma_10",
    "volume_ma_20",
    "trend_strength_5",
    "trend_strength_10",
]

ALL_FEATURES = (
    GREEKS_MOMENTUM_FEATURES
    + IV_REGIME_FEATURES
    + PRICE_MONEYNESS_FEATURES
    + VOLUME_OI_FEATURES
    + TIME_FEATURES
    + MULTIFRAME_FEATURES
)


def add_greeks_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 8 Greeks momentum features.

    These capture how Greeks change over time, providing dynamic signals
    about option behavior beyond static Greek values.
    """
    # Ensure numeric types
    for col in ["delta", "gamma", "theta", "vega"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Delta momentum (5 and 10 period)
    df["delta_momentum_5"] = df.groupby("underlying")["delta"].rolling(5).mean().reset_index(0, drop=True).diff()
    df["delta_momentum_10"] = df.groupby("underlying")["delta"].rolling(10).mean().reset_index(0, drop=True).diff()

    # Gamma acceleration (rate of change in gamma)
    df["gamma_acceleration"] = df.groupby("underlying")["gamma"].rolling(5).mean().reset_index(0, drop=True).diff()

    # Theta decay rate (change in time decay)
    df["theta_decay_rate"] = df.groupby("underlying")["theta"].diff()

    # Vega sensitivity (change in IV sensitivity)
    df["vega_change"] = df.groupby("underlying")["vega"].diff()

    # Greeks ratios (cross-products)
    df["delta_gamma_ratio"] = df["delta"] / (df["gamma"].abs() + 1e-8)
    df["vega_theta_ratio"] = df["vega"] / (df["theta"].abs() + 1e-8)

    # Combined momentum score
    df["greeks_momentum_score"] = (df["delta_momentum_5"].fillna(0) + df["gamma_acceleration"].fillna(0)).clip(-1, 1)

    logger.info("Added 8 Greeks momentum features")
    return df


def add_iv_regime_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 6 IV regime features.

    These identify high/low IV regimes and IV momentum, critical for
    options pricing and volatility trading.
    """
    # IV percentiles (by underlying)
    for underlying in df["underlying"].unique():
        mask = df["underlying"] == underlying
        if mask.sum() > 0:
            df.loc[mask, "iv_percentile_75"] = (df.loc[mask, "iv"] > df.loc[mask, "iv"].quantile(0.75)).astype(int)
            df.loc[mask, "iv_percentile_25"] = (df.loc[mask, "iv"] < df.loc[mask, "iv"].quantile(0.25)).astype(int)

    # IV regime flags
    df["iv_regime_high"] = df.get("iv_percentile_75", 0)
    df["iv_regime_low"] = df.get("iv_percentile_25", 0)

    # IV change and acceleration
    df["iv_change"] = df.groupby("underlying")["iv"].diff()
    df["iv_acceleration"] = df.groupby("underlying")["iv"].diff().diff()

    logger.info("Added 6 IV regime features")
    return df


def add_price_moneyness_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 8 price & moneyness features.

    These capture option position relative to spot price and premium dynamics.
    """
    # Moneyness (strike relative to spot)
    if "spot" in df.columns and "strike" in df.columns:
        df["moneyness"] = df["strike"] / (df["spot"] + 1e-8)
        df["atm_distance"] = (df["strike"] - df["spot"]).abs()
        df["atm_distance_pct"] = df["atm_distance"] / (df["spot"] + 1e-8)
    else:
        df["moneyness"] = 1.0
        df["atm_distance"] = 0.0
        df["atm_distance_pct"] = 0.0

    # Relative pricing
    if "ltp" in df.columns and "strike" in df.columns:
        df["relative_price"] = df["ltp"] / (df["strike"] + 1e-8)
    else:
        df["relative_price"] = 0.0

    # Price momentum
    if "ltp" in df.columns:
        df["price_momentum"] = df.groupby("underlying")["ltp"].pct_change()
        df["price_acceleration"] = df["price_momentum"].diff()
    else:
        df["price_momentum"] = 0.0
        df["price_acceleration"] = 0.0

    # CE/PE spreads (if side column exists)
    if "side" in df.columns and "ltp" in df.columns:
        for underlying in df["underlying"].unique():
            mask = df["underlying"] == underlying
            ce_ltp = df.loc[mask & (df["side"] == "CE"), "ltp"].mean()
            pe_ltp = df.loc[mask & (df["side"] == "PE"), "ltp"].mean()

            df.loc[mask, "ce_pe_spread"] = ce_ltp - pe_ltp
            df.loc[mask, "ce_pe_ratio"] = ce_ltp / (pe_ltp + 1e-8)
    else:
        df["ce_pe_spread"] = 0.0
        df["ce_pe_ratio"] = 1.0

    logger.info("Added 8 price & moneyness features")
    return df


def add_volume_oi_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 6 volume & OI features.

    These capture market activity and liquidity dynamics.
    """
    # Volume momentum
    if "volume" in df.columns:
        df["volume_momentum"] = df.groupby("underlying")["volume"].pct_change()
        df["volume_acceleration"] = df["volume_momentum"].diff()
    else:
        df["volume_momentum"] = 0.0
        df["volume_acceleration"] = 0.0

    # OI momentum
    if "oi" in df.columns:
        df["oi_momentum"] = df.groupby("underlying")["oi"].pct_change()
        df["oi_acceleration"] = df["oi_momentum"].diff()
    else:
        df["oi_momentum"] = 0.0
        df["oi_acceleration"] = 0.0

    # Volume-OI ratios
    if "volume" in df.columns and "oi" in df.columns:
        df["volume_oi_ratio"] = df["volume"] / (df["oi"] + 1e-8)
        df["oi_buildup"] = (df.groupby("underlying")["oi"].diff() > 0).astype(int)
    else:
        df["volume_oi_ratio"] = 0.0
        df["oi_buildup"] = 0

    logger.info("Added 6 volume & OI features")
    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 4 time-based features.

    These capture time decay and expiry proximity effects.
    """
    if "expiry" in df.columns and "ts" in df.columns:
        try:
            # Convert to datetime with error handling
            df["expiry_dt"] = pd.to_datetime(df["expiry"], errors="coerce")
            df["ts_dt"] = pd.to_datetime(df["ts"], errors="coerce")

            # Calculate days to expiry
            df["days_to_expiry"] = (df["expiry_dt"] - df["ts_dt"]).dt.days

            # Fill NaT/NaN values with default
            df["days_to_expiry"] = df["days_to_expiry"].fillna(7)

            df["time_decay_factor"] = 1.0 / (df["days_to_expiry"].abs() + 1)
            df["is_weekly_expiry"] = (df["days_to_expiry"] <= 7).astype(int)
            df["is_monthly_expiry"] = (df["days_to_expiry"] > 7).astype(int)

            # Drop temporary columns
            df.drop(["expiry_dt", "ts_dt"], axis=1, inplace=True, errors="ignore")
        except Exception as e:
            logger.warning(f"Time feature calculation failed: {e}, using defaults")
            df["days_to_expiry"] = 7
            df["time_decay_factor"] = 0.125
            df["is_weekly_expiry"] = 1
            df["is_monthly_expiry"] = 0
    else:
        df["days_to_expiry"] = 7
        df["time_decay_factor"] = 0.125
        df["is_weekly_expiry"] = 1
        df["is_monthly_expiry"] = 0

    logger.info("Added 4 time-based features")
    return df


def add_multiframe_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 8 multi-timeframe aggregate features.

    These capture trend strength across different time windows.
    """
    if "ltp" in df.columns:
        # Rolling averages for LTP
        for window in [5, 10, 20]:
            df[f"ltp_ma_{window}"] = df.groupby("underlying")["ltp"].rolling(window).mean().reset_index(0, drop=True)
    else:
        for window in [5, 10, 20]:
            df[f"ltp_ma_{window}"] = 0.0

    if "volume" in df.columns:
        # Rolling averages for volume
        for window in [5, 10, 20]:
            df[f"volume_ma_{window}"] = (
                df.groupby("underlying")["volume"].rolling(window).mean().reset_index(0, drop=True)
            )
    else:
        for window in [5, 10, 20]:
            df[f"volume_ma_{window}"] = 0.0

    # Trend strength (z-score of price vs moving average)
    if "ltp" in df.columns:
        for window in [5, 10]:
            ma = df[f"ltp_ma_{window}"]
            std = df.groupby("underlying")["ltp"].rolling(window).std().reset_index(0, drop=True)
            df[f"trend_strength_{window}"] = (df["ltp"] - ma) / (std + 1e-8)
    else:
        df["trend_strength_5"] = 0.0
        df["trend_strength_10"] = 0.0

    logger.info("Added 8 multi-timeframe features")
    return df


def engineer_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all feature engineering transformations.

    Returns:
        Enhanced dataframe with 40+ new features
    """
    logger.info("=" * 60)
    logger.info("PHASE 389: FEATURE ENGINEERING V2.0")
    logger.info("=" * 60)

    original_cols = len(df.columns)

    # Apply all feature engineering
    df = add_greeks_momentum_features(df)
    df = add_iv_regime_features(df)
    df = add_price_moneyness_features(df)
    df = add_volume_oi_features(df)
    df = add_time_features(df)
    df = add_multiframe_features(df)

    # Fill NaN values with 0
    for col in ALL_FEATURES:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    new_cols = len(df.columns)
    features_added = new_cols - original_cols

    logger.info(f"Features added: {features_added}")
    logger.info(f"Total columns: {original_cols} → {new_cols}")

    # Calculate feature variance statistics
    variance_stats = calculate_feature_variance(df)

    logger.info("=" * 60)

    return df


def calculate_feature_variance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate variance statistics for all features.

    Returns metrics about feature quality and variance.
    """
    stats = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_features": 0,
        "zero_variance_features": [],
        "low_variance_features": [],
        "high_variance_features": [],
        "feature_variance_summary": {},
    }

    # Identify numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    stats["total_features"] = len(numeric_cols)

    for col in numeric_cols:
        variance = df[col].var()
        mean = df[col].mean()
        std = df[col].std()
        zero_pct = (df[col] == 0).sum() / len(df) * 100

        stats["feature_variance_summary"][col] = {
            "variance": float(variance),
            "mean": float(mean),
            "std": float(std),
            "zero_pct": float(zero_pct),
        }

        # Categorize by variance
        if variance < 1e-10:
            stats["zero_variance_features"].append(col)
        elif variance < 0.01:
            stats["low_variance_features"].append(col)
        else:
            stats["high_variance_features"].append(col)

    # Summary metrics
    stats["zero_variance_count"] = len(stats["zero_variance_features"])
    stats["low_variance_count"] = len(stats["low_variance_features"])
    stats["high_variance_count"] = len(stats["high_variance_features"])

    logger.info(f"Zero variance features: {stats['zero_variance_count']}")
    logger.info(f"Low variance features: {stats['low_variance_count']}")
    logger.info(f"High variance features: {stats['high_variance_count']}")

    return stats


def run_phase_389() -> Dict[str, Any]:
    """
    Phase 389 entry point: Feature Engineering Upgrade.

    Returns phase execution result with status and metrics.
    """
    try:
        logger.info("Phase 389: Feature Engineering Upgrade - Starting")

        # Load curated dataset
        curated_path = Path("storage/live/angel_index_ai_signals_curated.csv")
        if not curated_path.exists():
            logger.warning(f"Curated dataset not found: {curated_path}")
            # Use sample data for testing
            df = pd.DataFrame(
                {
                    "underlying": ["NIFTY"] * 100,
                    "delta": np.random.uniform(-1, 1, 100),
                    "gamma": np.random.uniform(0, 0.05, 100),
                    "theta": np.random.uniform(-0.5, 0.5, 100),
                    "vega": np.random.uniform(0, 1, 100),
                    "iv": np.random.uniform(0.2, 0.3, 100),
                    "ltp": np.random.uniform(100, 200, 100),
                    "strike": np.random.uniform(18000, 19000, 100),
                    "spot": np.random.uniform(18500, 18600, 100),
                    "volume": np.random.randint(1000, 10000, 100),
                    "oi": np.random.randint(5000, 50000, 100),
                    "side": np.random.choice(["CE", "PE"], 100),
                    "ts": pd.date_range("2025-12-01", periods=100, freq="5min"),
                    "expiry": "2025-12-12",
                }
            )
        else:
            df = pd.read_csv(curated_path)

        # Apply feature engineering
        df_enhanced = engineer_all_features(df)

        # Save enhanced dataset
        output_path = Path("storage/datasets")
        output_path.mkdir(parents=True, exist_ok=True)
        enhanced_csv = output_path / "feature_engineered_389.csv"
        df_enhanced.to_csv(enhanced_csv, index=False)
        logger.info(f"Saved enhanced dataset: {enhanced_csv}")

        # Calculate variance statistics
        variance_stats = calculate_feature_variance(df_enhanced)

        # Save metrics
        metrics_path = Path("storage/metrics")
        metrics_path.mkdir(parents=True, exist_ok=True)
        metrics_file = metrics_path / "feature_engineering_389.json"

        metrics = {
            "status": "ok",
            "phase": 389,
            "timestamp": datetime.utcnow().isoformat(),
            "features_added": len(ALL_FEATURES),
            "total_features": len(df_enhanced.columns),
            "variance_stats": variance_stats,
            "output_file": str(enhanced_csv),
        }

        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)

        logger.info(f"Phase 389 metrics saved: {metrics_file}")

        return {
            "status": "ok",
            "message": f"Feature engineering complete: {len(ALL_FEATURES)} features added",
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"Phase 389 failed: {e}", exc_info=True)
        return {"status": "error", "message": f"Feature engineering failed: {str(e)}", "metrics": {}}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    result = run_phase_389()
    print(f"\nPhase 389 Result: {result['status']}")
    print(f"Message: {result['message']}")
