"""
System3 CSV Cleaning Module

Automated cleaning pipeline for dhan_index_ai_signals_with_forward.csv
Produces clean and EV-ready versions of the CSV file.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================================
# CONSTANTS
# ============================================================================

# Input/Output paths
CSV_INPUT = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals_with_forward.csv"
CLEAN_DIR = PROJECT_ROOT / "storage" / "clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

CSV_CLEAN = CLEAN_DIR / "dhan_index_ai_signals_with_forward_clean.csv"
CSV_EV_READY = CLEAN_DIR / "dhan_index_ai_signals_with_forward_ev_ready.csv"
CSV_SELL_ANOMALIES = CLEAN_DIR / "dhan_index_ai_signals_sell_anomalies.csv"

# Outlier threshold for forward returns
OUTLIER_THRESHOLD = 1.0

# Numeric columns to convert
NUMERIC_COLUMNS = [
    # Prices / levels
    "spot",
    "ltp",
    "strike",
    "entry_price",
    "stop_loss",
    "target_price",
    "risk_amount",
    # Greeks / IV
    "iv",
    "iv_estimate",
    "delta",
    "gamma",
    "theta",
    "vega",
    # Indicators
    "rsi",
    "macd",
    "macd_signal",
    "macd_histogram",
    "vwap",
    "price_vs_vwap",
    "trend_score",
    "multi_tf_trend_score",
    "trend_strength",
    "trend_1m",
    "trend_3m",
    "trend_5m",
    "trend_15m",
    "iv_percentile",
    "iv_rank",
    "volatility_score",
    "iv_change_rate",
    "breakout_score",
    "momentum_score",
    "roc_1",
    "roc_3",
    "roc_5",
    "roc_10",
    "acceleration",
    "momentum_strength",
    # Probabilities / ML
    "ml_prediction",
    "ml_probability",
    "prob_BUY_CE",
    "prob_BUY_PE",
    "prob_HOLD",
    "ai_score",
    "greeks_score",
    "final_score",
    "expected_move_score",
    "pred_confidence",
    # Option structure
    "moneyness",
    "ce_pe_ratio",
    "atm_dist_pct",
    "atm_dist_abs",
    "ce_pe_diff",
    # Vol / change fields
    "spot_chg_1_pct",
    "ltp_chg_1_pct",
    "spot_roll_std_5",
    "ltp_roll_std_5",
    # Forward returns
    "fwd_ret_1",
    "fwd_ret_3",
    "fwd_ret_5",
]


# ============================================================================
# CLEANING FUNCTIONS
# ============================================================================


def load_raw_csv() -> pd.DataFrame:
    """Load the raw CSV file."""
    print(f"Loading CSV from: {CSV_INPUT}")
    try:
        df = pd.read_csv(CSV_INPUT, engine="python", on_bad_lines="skip")
        print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
        return df
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        raise


def remove_bad_rows(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Remove duplicate header rows and invalid rows.

    Returns:
        Tuple of (cleaned DataFrame, removal statistics)
    """
    stats = {"duplicate_headers": 0, "invalid_rows": 0, "total_removed": 0}

    initial_count = len(df)

    # Remove duplicate header rows
    mask_duplicate = pd.Series([False] * len(df))

    if "signal" in df.columns:
        mask_duplicate |= df["signal"] == "signal"

    if "pred_label" in df.columns:
        mask_duplicate |= df["pred_label"] == "pred_label"

    stats["duplicate_headers"] = mask_duplicate.sum()
    df = df[~mask_duplicate].copy()

    # Remove completely empty rows (all NaN except identifiers)
    identifier_cols = ["underlying", "index_exch", "opt_exch"]
    if all(col in df.columns for col in identifier_cols):
        non_id_cols = [col for col in df.columns if col not in identifier_cols]
        mask_empty = df[non_id_cols].isna().all(axis=1)
        stats["invalid_rows"] = mask_empty.sum()
        df = df[~mask_empty].copy()

    stats["total_removed"] = initial_count - len(df)

    print(f"\n📋 Bad Row Removal:")
    print(f"  Duplicate headers removed: {stats['duplicate_headers']}")
    print(f"  Invalid rows removed: {stats['invalid_rows']}")
    print(f"  Total removed: {stats['total_removed']}")
    print(f"  Rows remaining: {len(df):,}")

    return df, stats


def convert_numeric_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Convert numeric-like columns to proper numeric types.

    Returns:
        Tuple of (converted DataFrame, conversion statistics)
    """
    conversion_stats = {}

    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue

        if df[col].dtype == "object" or df[col].dtype.name == "object":
            before_nulls = df[col].isna().sum()
            df[col] = pd.to_numeric(df[col], errors="coerce")
            after_nulls = df[col].isna().sum()
            new_nulls = after_nulls - before_nulls
            conversion_stats[col] = new_nulls

    print(f"\n🔢 Type Conversion:")
    print(f"  Columns converted: {len(conversion_stats)}")
    total_new_nulls = sum(conversion_stats.values())
    print(f"  Total new nulls created: {total_new_nulls}")

    if conversion_stats:
        print(f"\n  Top columns with new nulls:")
        sorted_stats = sorted(conversion_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        for col, new_nulls in sorted_stats:
            if new_nulls > 0:
                print(f"    {col}: {new_nulls} new nulls")

    return df, conversion_stats


def fix_moneyness(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix moneyness calculation (CRITICAL).
    Recompute as spot / strike for all rows.
    """
    if "moneyness" not in df.columns or "spot" not in df.columns or "strike" not in df.columns:
        print("\n⚠️ Cannot fix moneyness: missing required columns")
        return df

    # Convert to numeric if needed
    spot = pd.to_numeric(df["spot"], errors="coerce")
    strike = pd.to_numeric(df["strike"], errors="coerce")

    # Recalculate moneyness
    valid_mask = spot.notna() & strike.notna() & (strike > 0)
    df.loc[valid_mask, "moneyness"] = spot[valid_mask] / strike[valid_mask]

    fixed_count = valid_mask.sum()
    print(f"\n💰 Moneyness Fix:")
    print(f"  Rows recalculated: {fixed_count:,}")

    return df


def remove_outliers(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Remove extreme forward return outliers.

    Returns:
        Tuple of (cleaned DataFrame, outlier DataFrame)
    """
    # Create outlier mask aligned with DataFrame index
    mask_outliers = pd.Series(False, index=df.index)

    for col in ["fwd_ret_1", "fwd_ret_3", "fwd_ret_5"]:
        if col in df.columns:
            mask_outliers |= df[col].abs() > OUTLIER_THRESHOLD

    outliers_df = df[mask_outliers].copy()
    df_clean = df[~mask_outliers].copy()

    print(f"\n🚨 Outlier Removal:")
    print(f"  Outliers removed: {len(outliers_df)}")
    print(f"  Rows remaining: {len(df_clean):,}")

    if len(outliers_df) > 0:
        print(f"\n  Outlier statistics:")
        for col in ["fwd_ret_1", "fwd_ret_3", "fwd_ret_5"]:
            if col in outliers_df.columns:
                outliers_col = outliers_df[col].dropna()
                if len(outliers_col) > 0:
                    print(f"    {col}: min={outliers_col.min():.4f}, max={outliers_col.max():.4f}")

    return df_clean, outliers_df


def detect_sell_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect SELL signal anomalies (SELL signals with extreme positive forward returns).

    Returns:
        DataFrame with anomaly rows
    """
    anomalies = []

    # Check signal column
    if "signal" in df.columns:
        sell_mask = df["signal"] == "SELL"
        if sell_mask.any():
            for col in ["fwd_ret_1", "fwd_ret_3", "fwd_ret_5"]:
                if col in df.columns:
                    extreme_mask = df[col] > OUTLIER_THRESHOLD
                    anomalies.extend(df[sell_mask & extreme_mask].index.tolist())

    # Check pred_label column
    if "pred_label" in df.columns:
        sell_ce_mask = df["pred_label"] == "SELL_CE"
        sell_pe_mask = df["pred_label"] == "SELL_PE"
        sell_mask = sell_ce_mask | sell_pe_mask

        if sell_mask.any():
            for col in ["fwd_ret_1", "fwd_ret_3", "fwd_ret_5"]:
                if col in df.columns:
                    extreme_mask = df[col] > OUTLIER_THRESHOLD
                    anomalies.extend(df[sell_mask & extreme_mask].index.tolist())

    # Remove duplicates
    anomaly_indices = list(set(anomalies))

    if anomaly_indices:
        anomalies_df = df.loc[anomaly_indices].copy()
        print(f"\n⚠️ SELL Signal Anomalies Detected:")
        print(f"  Anomaly rows: {len(anomalies_df)}")
        print(f"  Saving to: {CSV_SELL_ANOMALIES}")
        CSV_SELL_ANOMALIES.parent.mkdir(parents=True, exist_ok=True)
        anomalies_df.to_csv(CSV_SELL_ANOMALIES, index=False)
    else:
        anomalies_df = pd.DataFrame()
        print(f"\n✅ No SELL signal anomalies detected")

    return anomalies_df


def create_ev_ready_subset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create EV-ready subset with strict filtering criteria.

    Returns:
        Filtered DataFrame ready for EV analysis
    """
    print(f"\n📊 Creating EV-Ready Subset:")

    initial_count = len(df)

    # Filter: All three forward returns must be non-null
    mask_fwd = df["fwd_ret_1"].notna() & df["fwd_ret_3"].notna() & df["fwd_ret_5"].notna()
    print(f"  Rows with all forward returns: {mask_fwd.sum():,}")

    # Filter: Signal is not null and not bogus
    if "signal" in df.columns:
        mask_signal = df["signal"].notna() & (df["signal"] != "signal")
    else:
        mask_signal = pd.Series([True] * len(df))
    print(f"  Rows with valid signal: {mask_signal.sum():,}")

    # Filter: Forward returns within [-1.0, 1.0] (already done by outlier removal, but double-check)
    mask_range = (
        (df["fwd_ret_1"].abs() <= OUTLIER_THRESHOLD)
        & (df["fwd_ret_3"].abs() <= OUTLIER_THRESHOLD)
        & (df["fwd_ret_5"].abs() <= OUTLIER_THRESHOLD)
    )
    print(f"  Rows with forward returns in range: {mask_range.sum():,}")

    # Filter: Required numeric columns present
    required_cols = ["spot", "ltp", "strike"]
    mask_required = pd.Series(True, index=df.index)
    for col in required_cols:
        if col in df.columns:
            mask_required &= df[col].notna()
    print(f"  Rows with required columns: {mask_required.sum():,}")

    # Combine all filters
    mask_combined = mask_fwd & mask_signal & mask_range & mask_required
    df_ev = df[mask_combined].copy()

    print(f"\n  EV-Ready Subset:")
    print(f"    Initial rows: {initial_count:,}")
    print(f"    Final rows: {len(df_ev):,}")
    print(f"    Rows removed: {initial_count - len(df_ev):,}")

    return df_ev


def save_clean_files(df_clean: pd.DataFrame, df_ev: pd.DataFrame) -> None:
    """Save cleaned and EV-ready CSV files."""
    print(f"\n💾 Saving Clean Files:")

    # Save clean CSV
    print(f"  Clean CSV: {CSV_CLEAN}")
    df_clean.to_csv(CSV_CLEAN, index=False)
    print(f"    Rows: {len(df_clean):,}")

    # Save EV-ready CSV
    print(f"  EV-Ready CSV: {CSV_EV_READY}")
    df_ev.to_csv(CSV_EV_READY, index=False)
    print(f"    Rows: {len(df_ev):,}")

    print(f"\n✅ All clean files saved successfully")


def run_cleaning_pipeline() -> Dict:
    """
    Run the complete cleaning pipeline.

    Returns:
        Dictionary with cleaning statistics
    """
    print("=" * 80)
    print("SYSTEM3 CSV CLEANING PIPELINE")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    stats = {
        "initial_rows": 0,
        "after_bad_rows": 0,
        "after_type_conversion": 0,
        "after_outliers": 0,
        "final_clean_rows": 0,
        "ev_ready_rows": 0,
        "removal_stats": {},
        "conversion_stats": {},
        "outliers_removed": 0,
        "sell_anomalies": 0,
    }

    # Step 1: Load raw CSV
    df = load_raw_csv()
    stats["initial_rows"] = len(df)

    # Step 2: Remove bad rows
    df, removal_stats = remove_bad_rows(df)
    stats["after_bad_rows"] = len(df)
    stats["removal_stats"] = removal_stats

    # Step 3: Convert numeric columns
    df, conversion_stats = convert_numeric_columns(df)
    stats["after_type_conversion"] = len(df)
    stats["conversion_stats"] = conversion_stats

    # Step 4: Fix moneyness (CRITICAL)
    df = fix_moneyness(df)

    # Step 5: Detect SELL anomalies (before removing outliers)
    anomalies_df = detect_sell_anomalies(df)
    stats["sell_anomalies"] = len(anomalies_df)

    # Step 6: Remove outliers
    df, outliers_df = remove_outliers(df)
    stats["after_outliers"] = len(df)
    stats["outliers_removed"] = len(outliers_df)

    # Step 7: Create EV-ready subset
    df_ev = create_ev_ready_subset(df)
    stats["final_clean_rows"] = len(df)
    stats["ev_ready_rows"] = len(df_ev)

    # Step 8: Save clean files
    save_clean_files(df, df_ev)

    print("\n" + "=" * 80)
    print("CLEANING PIPELINE COMPLETE")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"  Initial rows: {stats['initial_rows']:,}")
    print(f"  After bad row removal: {stats['after_bad_rows']:,}")
    print(f"  After outlier removal: {stats['after_outliers']:,}")
    print(f"  Final clean rows: {stats['final_clean_rows']:,}")
    print(f"  EV-ready rows: {stats['ev_ready_rows']:,}")
    print(f"\n  Bad rows removed: {stats['removal_stats'].get('total_removed', 0)}")
    print(f"  Outliers removed: {stats['outliers_removed']}")
    print(f"  SELL anomalies detected: {stats['sell_anomalies']}")

    return stats


if __name__ == "__main__":
    try:
        stats = run_cleaning_pipeline()
        print("\n✅ Cleaning pipeline completed successfully")
    except Exception as e:
        print(f"\n❌ Cleaning pipeline failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
