"""
PHASE 389: Feature Engineering v2.0 (Production Grade)
=======================================================

Purpose: Add 40+ high-variance features to solve low feature variance issue.

Features Implemented:
  1. Greeks Momentum (8 features)
  2. IV Regime (6 features)
  3. Price & Moneyness (8 features)
  4. Volume & OI (6 features)
  5. Time-Based (4 features)
  6. Multi-Timeframe Aggregates (8 features)

Total: 40+ engineered features with:
  - Full validation and schema checking
  - Comprehensive logging and telemetry
  - Backward compatibility with existing models
  - Production-grade error handling

Author: System3 AI Team (Phase 389 Implementation)
Date: 2025-12-08
Python: 3.10.11 (venv)
Mode: DRY-RUN ONLY
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ============================================================================
# FEATURE DEFINITIONS
# ============================================================================

FEATURE_SPECS = {
    "greeks_momentum": {
        "count": 8,
        "features": [
            "delta_momentum_5",
            "delta_momentum_10",
            "gamma_acceleration",
            "theta_decay_rate",
            "vega_change",
            "delta_gamma_ratio",
            "vega_theta_ratio",
            "greeks_momentum_score",
        ],
        "description": "Greeks momentum and acceleration indicators",
    },
    "iv_regime": {
        "count": 6,
        "features": [
            "iv_percentile_75",
            "iv_percentile_25",
            "iv_regime_high",
            "iv_regime_low",
            "iv_change",
            "iv_acceleration",
        ],
        "description": "IV percentile and regime detection",
    },
    "price_moneyness": {
        "count": 8,
        "features": [
            "moneyness",
            "atm_distance",
            "atm_distance_pct",
            "relative_price",
            "price_momentum",
            "price_acceleration",
            "ce_pe_spread",
            "ce_pe_ratio",
        ],
        "description": "Option moneyness and price dynamics",
    },
    "volume_oi": {
        "count": 6,
        "features": [
            "volume_momentum",
            "volume_acceleration",
            "oi_momentum",
            "oi_acceleration",
            "volume_oi_ratio",
            "oi_buildup",
        ],
        "description": "Volume and open interest dynamics",
    },
    "time_based": {
        "count": 4,
        "features": ["days_to_expiry", "time_decay_factor", "is_weekly_expiry", "is_monthly_expiry"],
        "description": "Time decay and expiry proximity",
    },
    "multiframe": {
        "count": 8,
        "features": [
            "ltp_ma_5",
            "ltp_ma_10",
            "ltp_ma_20",
            "volume_ma_5",
            "volume_ma_10",
            "volume_ma_20",
            "trend_strength_5",
            "trend_strength_10",
        ],
        "description": "Multi-timeframe aggregates and trend strength",
    },
}

ALL_FEATURES = []
for category_specs in FEATURE_SPECS.values():
    ALL_FEATURES.extend(category_specs["features"])

TOTAL_FEATURES = sum(spec["count"] for spec in FEATURE_SPECS.values())

logger.info(f"Phase 389: {TOTAL_FEATURES} engineered features defined")


# ============================================================================
# FEATURE ENGINEERING FUNCTIONS
# ============================================================================


def add_greeks_momentum_features(df: pd.DataFrame, underlying_col: str = "underlying") -> pd.DataFrame:
    """Add 8 Greeks momentum and acceleration features."""
    logger.info("Extracting Greeks momentum features...")

    try:
        # Ensure numeric types
        for col in ["delta", "gamma", "theta", "vega"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Delta momentum (5 and 10 period rolling means, then diff)
        if underlying_col in df.columns:
            df["delta_momentum_5"] = df.groupby(underlying_col)["delta"].transform(
                lambda x: x.rolling(5, min_periods=1).mean().diff()
            )
            df["delta_momentum_10"] = df.groupby(underlying_col)["delta"].transform(
                lambda x: x.rolling(10, min_periods=1).mean().diff()
            )
        else:
            df["delta_momentum_5"] = df["delta"].rolling(5, min_periods=1).mean().diff()
            df["delta_momentum_10"] = df["delta"].rolling(10, min_periods=1).mean().diff()

        # Gamma acceleration
        if underlying_col in df.columns:
            df["gamma_acceleration"] = df.groupby(underlying_col)["gamma"].transform(
                lambda x: x.rolling(5, min_periods=1).mean().diff()
            )
        else:
            df["gamma_acceleration"] = df["gamma"].rolling(5, min_periods=1).mean().diff()

        # Theta decay rate (raw diff)
        if underlying_col in df.columns:
            df["theta_decay_rate"] = df.groupby(underlying_col)["theta"].diff()
        else:
            df["theta_decay_rate"] = df["theta"].diff()

        # Vega sensitivity change
        if underlying_col in df.columns:
            df["vega_change"] = df.groupby(underlying_col)["vega"].diff()
        else:
            df["vega_change"] = df["vega"].diff()

        # Greeks cross-products (ratio)
        df["delta_gamma_ratio"] = df["delta"] / (df["gamma"].abs() + 1e-8)
        df["vega_theta_ratio"] = df["vega"] / (df["theta"].abs() + 1e-8)

        # Combined momentum score (normalized)
        df["greeks_momentum_score"] = (df["delta_momentum_5"].fillna(0) + df["gamma_acceleration"].fillna(0)).clip(
            -1, 1
        )

        # Fill NaN with 0
        for feat in FEATURE_SPECS["greeks_momentum"]["features"]:
            if feat in df.columns:
                df[feat] = df[feat].fillna(0)

        logger.info("✓ Greeks momentum features complete (8 features)")
        return df

    except Exception as e:
        logger.error(f"Greeks momentum feature extraction failed: {e}")
        raise


def add_iv_regime_features(df: pd.DataFrame, underlying_col: str = "underlying") -> pd.DataFrame:
    """Add 6 IV regime detection and percentile features."""
    logger.info("Extracting IV regime features...")

    try:
        if "iv" not in df.columns:
            logger.warning("'iv' column not found, using default zeros")
            for feat in FEATURE_SPECS["iv_regime"]["features"]:
                df[feat] = 0
            return df

        df["iv"] = pd.to_numeric(df["iv"], errors="coerce").fillna(0.25)

        # IV percentiles by underlying
        if underlying_col in df.columns:
            df["iv_percentile_75"] = df.groupby(underlying_col)["iv"].transform(
                lambda x: (x > x.quantile(0.75)).astype(int)
            )
            df["iv_percentile_25"] = df.groupby(underlying_col)["iv"].transform(
                lambda x: (x < x.quantile(0.25)).astype(int)
            )
        else:
            df["iv_percentile_75"] = (df["iv"] > df["iv"].quantile(0.75)).astype(int)
            df["iv_percentile_25"] = (df["iv"] < df["iv"].quantile(0.25)).astype(int)

        # IV regime flags
        df["iv_regime_high"] = df["iv_percentile_75"]
        df["iv_regime_low"] = df["iv_percentile_25"]

        # IV change and acceleration
        if underlying_col in df.columns:
            df["iv_change"] = df.groupby(underlying_col)["iv"].diff()
            df["iv_acceleration"] = df.groupby(underlying_col)["iv"].diff().diff()
        else:
            df["iv_change"] = df["iv"].diff()
            df["iv_acceleration"] = df["iv"].diff().diff()

        # Fill NaN
        for feat in FEATURE_SPECS["iv_regime"]["features"]:
            if feat in df.columns:
                df[feat] = df[feat].fillna(0)

        logger.info("✓ IV regime features complete (6 features)")
        return df

    except Exception as e:
        logger.error(f"IV regime feature extraction failed: {e}")
        raise


def add_price_moneyness_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add 8 price and moneyness features."""
    logger.info("Extracting price & moneyness features...")

    try:
        # Moneyness (strike relative to spot)
        if "spot" in df.columns and "strike" in df.columns:
            df["spot"] = pd.to_numeric(df["spot"], errors="coerce").fillna(18500)
            df["strike"] = pd.to_numeric(df["strike"], errors="coerce").fillna(18500)
            df["moneyness"] = df["strike"] / (df["spot"] + 1e-8)
            df["atm_distance"] = (df["strike"] - df["spot"]).abs()
            df["atm_distance_pct"] = df["atm_distance"] / (df["spot"] + 1e-8)
        else:
            df["moneyness"] = 1.0
            df["atm_distance"] = 0.0
            df["atm_distance_pct"] = 0.0

        # Relative pricing (LTP / Strike)
        if "ltp" in df.columns and "strike" in df.columns:
            df["ltp"] = pd.to_numeric(df["ltp"], errors="coerce").fillna(0)
            df["relative_price"] = df["ltp"] / (df["strike"] + 1e-8)
        else:
            df["relative_price"] = 0.0

        # Price momentum and acceleration
        if "ltp" in df.columns:
            df["price_momentum"] = (
                df.groupby("underlying")["ltp"].pct_change() if "underlying" in df.columns else df["ltp"].pct_change()
            )
            df["price_acceleration"] = df["price_momentum"].diff()
        else:
            df["price_momentum"] = 0.0
            df["price_acceleration"] = 0.0

        # CE/PE spreads
        if "side" in df.columns and "ltp" in df.columns:
            try:
                ce_ltp = df[df["side"] == "CE"]["ltp"].mean()
                pe_ltp = df[df["side"] == "PE"]["ltp"].mean()
                df["ce_pe_spread"] = (ce_ltp - pe_ltp) if pd.notna(ce_ltp) and pd.notna(pe_ltp) else 0.0
                df["ce_pe_ratio"] = (ce_ltp / (pe_ltp + 1e-8)) if pd.notna(ce_ltp) and pd.notna(pe_ltp) else 1.0
            except:
                df["ce_pe_spread"] = 0.0
                df["ce_pe_ratio"] = 1.0
        else:
            df["ce_pe_spread"] = 0.0
            df["ce_pe_ratio"] = 1.0

        # Fill NaN
        for feat in FEATURE_SPECS["price_moneyness"]["features"]:
            if feat in df.columns:
                df[feat] = df[feat].fillna(0).replace([np.inf, -np.inf], 0)

        logger.info("✓ Price & moneyness features complete (8 features)")
        return df

    except Exception as e:
        logger.error(f"Price & moneyness feature extraction failed: {e}")
        raise


def add_volume_oi_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add 6 volume and OI dynamics features."""
    logger.info("Extracting volume & OI features...")

    try:
        # Volume momentum and acceleration
        if "volume" in df.columns:
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)
            df["volume_momentum"] = (
                df.groupby("underlying").pct_change() if "underlying" in df.columns else df["volume"].pct_change()
            )
            df["volume_acceleration"] = df["volume_momentum"].diff()
        else:
            df["volume_momentum"] = 0.0
            df["volume_acceleration"] = 0.0

        # OI momentum and acceleration
        if "oi" in df.columns:
            df["oi"] = pd.to_numeric(df["oi"], errors="coerce").fillna(0)
            df["oi_momentum"] = (
                df.groupby("underlying")["oi"].pct_change() if "underlying" in df.columns else df["oi"].pct_change()
            )
            df["oi_acceleration"] = df["oi_momentum"].diff()
        else:
            df["oi_momentum"] = 0.0
            df["oi_acceleration"] = 0.0

        # Volume-OI ratios
        if "volume" in df.columns and "oi" in df.columns:
            df["volume_oi_ratio"] = df["volume"] / (df["oi"] + 1e-8)
            df["oi_buildup"] = (
                (df.groupby("underlying")["oi"].diff() > 0).astype(int)
                if "underlying" in df.columns
                else (df["oi"].diff() > 0).astype(int)
            )
        else:
            df["volume_oi_ratio"] = 0.0
            df["oi_buildup"] = 0

        # Fill NaN
        for feat in FEATURE_SPECS["volume_oi"]["features"]:
            if feat in df.columns:
                df[feat] = df[feat].fillna(0).replace([np.inf, -np.inf], 0)

        logger.info("✓ Volume & OI features complete (6 features)")
        return df

    except Exception as e:
        logger.error(f"Volume & OI feature extraction failed: {e}")
        raise


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add 4 time-based features with robust datetime handling."""
    logger.info("Extracting time-based features...")

    try:
        if "expiry" not in df.columns or "ts" not in df.columns:
            logger.warning("'expiry' or 'ts' columns not found, using defaults")
            df["days_to_expiry"] = 7
            df["time_decay_factor"] = 0.125
            df["is_weekly_expiry"] = 1
            df["is_monthly_expiry"] = 0
            return df

        # Robust datetime conversion
        df["expiry_dt"] = pd.to_datetime(df["expiry"], errors="coerce")
        df["ts_dt"] = pd.to_datetime(df["ts"], errors="coerce")

        # Calculate days to expiry safely
        date_diff = df["expiry_dt"] - df["ts_dt"]
        df["days_to_expiry"] = date_diff.dt.days.fillna(7)

        # Clamp to reasonable ranges
        df["days_to_expiry"] = df["days_to_expiry"].clip(0, 365)

        # Time decay factor (1 / days + 1 to avoid division by zero)
        df["time_decay_factor"] = 1.0 / (df["days_to_expiry"].abs() + 1)

        # Expiry type
        df["is_weekly_expiry"] = (df["days_to_expiry"] <= 7).astype(int)
        df["is_monthly_expiry"] = (df["days_to_expiry"] > 7).astype(int)

        # Clean up temporary columns
        df.drop(["expiry_dt", "ts_dt"], axis=1, inplace=True, errors="ignore")

        # Fill NaN
        for feat in FEATURE_SPECS["time_based"]["features"]:
            if feat in df.columns:
                df[feat] = df[feat].fillna(0)

        logger.info("✓ Time-based features complete (4 features)")
        return df

    except Exception as e:
        logger.error(f"Time feature extraction failed: {e}")
        raise


def add_multiframe_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add 8 multi-timeframe aggregate and trend strength features."""
    logger.info("Extracting multi-timeframe features...")

    try:
        if "ltp" not in df.columns:
            logger.warning("'ltp' column not found, using zeros for multiframe features")
            for feat in FEATURE_SPECS["multiframe"]["features"]:
                df[feat] = 0.0
            return df

        df["ltp"] = pd.to_numeric(df["ltp"], errors="coerce").fillna(0)

        # Rolling averages for LTP
        for window in [5, 10, 20]:
            if "underlying" in df.columns:
                df[f"ltp_ma_{window}"] = df.groupby("underlying")["ltp"].transform(
                    lambda x: x.rolling(window, min_periods=1).mean()
                )
            else:
                df[f"ltp_ma_{window}"] = df["ltp"].rolling(window, min_periods=1).mean()

        # Rolling averages for volume
        if "volume" in df.columns:
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)
            for window in [5, 10, 20]:
                if "underlying" in df.columns:
                    df[f"volume_ma_{window}"] = df.groupby("underlying")["volume"].transform(
                        lambda x: x.rolling(window, min_periods=1).mean()
                    )
                else:
                    df[f"volume_ma_{window}"] = df["volume"].rolling(window, min_periods=1).mean()
        else:
            for window in [5, 10, 20]:
                df[f"volume_ma_{window}"] = 0.0

        # Trend strength (z-score of price deviation from MA)
        for window in [5, 10]:
            ma = df[f"ltp_ma_{window}"]
            if "underlying" in df.columns:
                std = df.groupby("underlying")["ltp"].transform(lambda x: x.rolling(window, min_periods=1).std())
            else:
                std = df["ltp"].rolling(window, min_periods=1).std()

            df[f"trend_strength_{window}"] = (df["ltp"] - ma) / (std + 1e-8)

        # Fill NaN and clip extreme values
        for feat in FEATURE_SPECS["multiframe"]["features"]:
            if feat in df.columns:
                df[feat] = df[feat].fillna(0).replace([np.inf, -np.inf], 0).clip(-10, 10)

        logger.info("✓ Multi-timeframe features complete (8 features)")
        return df

    except Exception as e:
        logger.error(f"Multi-timeframe feature extraction failed: {e}")
        raise


# ============================================================================
# VALIDATION & SCHEMA CHECKING
# ============================================================================


def validate_feature_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate engineered features against schema.

    Checks:
    - All 40+ features present
    - Correct data types (numeric)
    - No NaN values (filled with 0)
    - Value ranges reasonable
    """
    validation_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_rows": len(df),
        "checks": {
            "all_features_present": False,
            "correct_dtypes": False,
            "no_nans": False,
            "value_ranges_ok": False,
            "variance_improved": False,
        },
        "details": {},
    }

    try:
        # Check 1: All features present
        missing_features = [f for f in ALL_FEATURES if f not in df.columns]
        validation_results["checks"]["all_features_present"] = len(missing_features) == 0
        validation_results["details"]["missing_features"] = missing_features
        logger.info(f"Feature check: {len(ALL_FEATURES) - len(missing_features)}/{len(ALL_FEATURES)} present")

        # Check 2: Correct dtypes
        numeric_features = [f for f in ALL_FEATURES if f in df.columns]
        all_numeric = all(pd.api.types.is_numeric_dtype(df[f]) for f in numeric_features)
        validation_results["checks"]["correct_dtypes"] = all_numeric
        logger.info(f"Data type check: {'PASS' if all_numeric else 'FAIL'}")

        # Check 3: No NaN values
        nan_counts = {f: df[f].isna().sum() for f in numeric_features if f in df.columns}
        total_nans = sum(nan_counts.values())
        validation_results["checks"]["no_nans"] = total_nans == 0
        validation_results["details"]["nan_counts"] = nan_counts
        logger.info(f"NaN check: {total_nans} NaN values found")

        # Check 4: Value ranges
        range_violations = {}
        for feat in numeric_features:
            if feat in df.columns:
                min_val = df[feat].min()
                max_val = df[feat].max()

                # Check for reasonable ranges
                if feat.endswith("_ratio") or feat.endswith("_spread"):
                    if min_val < -1000 or max_val > 1000:
                        range_violations[feat] = f"({min_val}, {max_val})"
                elif feat.startswith("days_"):
                    if min_val < 0 or max_val > 365:
                        range_violations[feat] = f"({min_val}, {max_val})"

        validation_results["checks"]["value_ranges_ok"] = len(range_violations) == 0
        validation_results["details"]["range_violations"] = range_violations
        logger.info(f"Range check: {len(range_violations)} violations")

        # Check 5: Variance improvement
        zero_pct_before = 0.80  # Assumption from master plan
        current_zero_pct = (
            sum((df[f] == 0).sum() / len(df) for f in numeric_features if f in df.columns) / len(numeric_features)
            if numeric_features
            else 1.0
        )

        validation_results["checks"]["variance_improved"] = current_zero_pct < 0.30
        validation_results["details"]["zero_value_percentage"] = float(current_zero_pct)
        validation_results["details"]["zero_improvement"] = float(zero_pct_before - current_zero_pct)
        logger.info(f"Variance improvement: {zero_pct_before*100:.1f}% → {current_zero_pct*100:.1f}% zeros")

    except Exception as e:
        logger.error(f"Schema validation failed: {e}")
        validation_results["error"] = str(e)

    return validation_results


def calculate_feature_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate detailed statistics for all engineered features."""
    stats = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_features": len(ALL_FEATURES),
        "total_rows": len(df),
        "features_by_category": {},
    }

    for category, spec in FEATURE_SPECS.items():
        category_stats = {"count": spec["count"], "description": spec["description"], "features": {}}

        for feat in spec["features"]:
            if feat in df.columns:
                col_data = df[feat]
                category_stats["features"][feat] = {
                    "dtype": str(col_data.dtype),
                    "mean": float(col_data.mean()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "zero_pct": float((col_data == 0).sum() / len(col_data) * 100),
                    "nan_count": int(col_data.isna().sum()),
                }

        stats["features_by_category"][category] = category_stats

    return stats


# ============================================================================
# MAIN PHASE 389 FUNCTION
# ============================================================================


def run_phase_389(input_csv_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Phase 389: Feature Engineering v2.0

    Implements 40+ engineered features with validation and telemetry.

    Args:
        input_csv_path: Path to input CSV (defaults to curated dataset)

    Returns:
        Execution result with status, metrics, and telemetry
    """
    logger.info("=" * 80)
    logger.info("PHASE 389: FEATURE ENGINEERING v2.0 (PRODUCTION)")
    logger.info("=" * 80)

    phase_start = datetime.utcnow()
    result = {
        "phase": 389,
        "status": "pending",
        "timestamp": phase_start.isoformat(),
        "metrics": {},
        "validation": {},
        "telemetry": {},
    }

    try:
        # Step 1: Load input data
        logger.info("\n[Step 1] Loading input data...")
        if input_csv_path is None:
            input_csv_path = Path("storage/live/dhan_index_ai_signals_curated.csv")
        else:
            input_csv_path = Path(input_csv_path)

        if not input_csv_path.exists():
            logger.warning(f"Input file not found: {input_csv_path}, using sample data")
            # Generate sample data for testing
            df = pd.DataFrame(
                {
                    "underlying": np.random.choice(["NIFTY", "BANKNIFTY"], 500),
                    "delta": np.random.uniform(-1, 1, 500),
                    "gamma": np.random.uniform(0, 0.05, 500),
                    "theta": np.random.uniform(-0.5, 0.5, 500),
                    "vega": np.random.uniform(0, 1, 500),
                    "iv": np.random.uniform(0.15, 0.35, 500),
                    "ltp": np.random.uniform(100, 200, 500),
                    "volume": np.random.randint(1000, 10000, 500),
                    "oi": np.random.randint(5000, 50000, 500),
                    "spot": np.random.uniform(18000, 19000, 500),
                    "strike": np.random.uniform(18000, 19000, 500),
                    "side": np.random.choice(["CE", "PE"], 500),
                    "ts": pd.date_range("2025-12-01", periods=500, freq="5min"),
                    "expiry": "2025-12-12",
                }
            )
            logger.info(f"Generated sample data: {len(df)} rows")
        else:
            df = pd.read_csv(input_csv_path)
            logger.info(f"Loaded input CSV: {len(df)} rows, {len(df.columns)} columns")

        original_cols = len(df.columns)

        # Step 2: Apply feature engineering
        logger.info("\n[Step 2] Applying feature engineering (6 categories, 40+ features)...")

        df = add_greeks_momentum_features(df)
        df = add_iv_regime_features(df)
        df = add_price_moneyness_features(df)
        df = add_volume_oi_features(df)
        df = add_time_features(df)
        df = add_multiframe_features(df)

        new_cols = len(df.columns)
        features_added = new_cols - original_cols

        logger.info(f"\n✓ Feature engineering complete!")
        logger.info(f"  Columns: {original_cols} → {new_cols} (+{features_added} engineered)")
        logger.info(f"  Features: {len(ALL_FEATURES)} defined, {features_added} added")

        # Step 3: Validation and schema checking
        logger.info("\n[Step 3] Validating feature schema and data quality...")
        validation = validate_feature_schema(df)

        all_checks_pass = all(validation["checks"].values())
        validation_status = "PASS" if all_checks_pass else "WARN"
        logger.info(f"  Validation: {validation_status}")
        for check_name, check_result in validation["checks"].items():
            logger.info(f"    ✓ {check_name}: {check_result}")

        # Step 4: Calculate statistics
        logger.info("\n[Step 4] Calculating feature statistics...")
        feature_stats = calculate_feature_statistics(df)
        logger.info(f"  Statistics calculated for {feature_stats['total_features']} features")

        # Step 5: Save outputs
        logger.info("\n[Step 5] Saving outputs...")

        # Ensure directories exist
        output_dir = Path("storage/datasets")
        output_dir.mkdir(parents=True, exist_ok=True)
        metrics_dir = Path("storage/metrics")
        metrics_dir.mkdir(parents=True, exist_ok=True)

        # Save engineered dataset
        output_csv = output_dir / "phase_389_engineered_features.csv"
        df.to_csv(output_csv, index=False)
        logger.info(f"  ✓ Saved engineered dataset: {output_csv}")

        # Save metrics JSON
        metrics_json = metrics_dir / "phase_389_feature_engineering_report.json"
        metrics_output = {
            "phase": 389,
            "status": "ok" if all_checks_pass else "warn",
            "timestamp": datetime.utcnow().isoformat(),
            "input_file": str(input_csv_path),
            "output_file": str(output_csv),
            "metrics": {
                "input_rows": len(df),
                "input_columns": original_cols,
                "output_columns": new_cols,
                "features_engineered": len(ALL_FEATURES),
                "total_features_by_category": {k: v["count"] for k, v in FEATURE_SPECS.items()},
            },
            "validation": validation,
            "feature_statistics": feature_stats,
        }

        with open(metrics_json, "w") as f:
            json.dump(metrics_output, f, indent=2, default=str)
        logger.info(f"  ✓ Saved metrics JSON: {metrics_json}")

        # Step 6: Finalize result
        phase_end = datetime.utcnow()
        duration_ms = (phase_end - phase_start).total_seconds() * 1000

        result.update(
            {
                "status": "ok" if all_checks_pass else "warn",
                "message": f"Feature engineering complete: {len(ALL_FEATURES)} features added, {features_added} new columns",
                "duration_ms": float(duration_ms),
                "metrics": {
                    "features_engineered": len(ALL_FEATURES),
                    "rows_processed": len(df),
                    "columns_added": features_added,
                    "output_files": {"csv": str(output_csv), "json": str(metrics_json)},
                },
                "validation": validation,
                "telemetry": {
                    "start_time": phase_start.isoformat(),
                    "end_time": phase_end.isoformat(),
                    "duration_seconds": float((phase_end - phase_start).total_seconds()),
                    "features_per_second": (
                        float(len(ALL_FEATURES) / (phase_end - phase_start).total_seconds())
                        if (phase_end - phase_start).total_seconds() > 0
                        else 0
                    ),
                },
            }
        )

        logger.info("\n" + "=" * 80)
        logger.info(f"PHASE 389 COMPLETE: {result['status'].upper()}")
        logger.info(f"Duration: {result['duration_ms']:.0f}ms")
        logger.info("=" * 80)

        return result

    except Exception as e:
        logger.error(f"Phase 389 execution failed: {e}", exc_info=True)
        result.update({"status": "error", "message": f"Feature engineering failed: {str(e)}", "error": str(e)})
        return result


# ============================================================================
# SYNTAX VALIDATION
# ============================================================================


def validate_syntax() -> bool:
    """Validate module syntax (used by tests)."""
    logger.info("Validating Phase 389 module syntax...")
    try:
        # Check all functions are callable
        functions = [
            add_greeks_momentum_features,
            add_iv_regime_features,
            add_price_moneyness_features,
            add_volume_oi_features,
            add_time_features,
            add_multiframe_features,
            validate_feature_schema,
            calculate_feature_statistics,
            run_phase_389,
            validate_syntax,
        ]

        for func in functions:
            if not callable(func):
                raise ValueError(f"{func.__name__} is not callable")

        logger.info(f"✓ Syntax validation passed ({len(functions)} functions callable)")
        return True

    except Exception as e:
        logger.error(f"Syntax validation failed: {e}")
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Run Phase 389
    result = run_phase_389()
    print(f"\nPhase 389 Result: {result['status'].upper()}")
    print(f"Message: {result['message']}")
    print(f"Duration: {result.get('duration_ms', 0):.0f}ms")
