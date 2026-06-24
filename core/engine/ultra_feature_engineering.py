"""
System3 Ultra - Feature Expander

Extends features from ~25 to ~100 for Ultra models only (shadow).
Does not modify baseline features.

Inputs:
- storage/training/dhan_index_options_training.csv (synthetic baseline)
- storage/learning_ultra/dhan_ultra_shadow_master.parquet (Phase 10)

Outputs:
- storage/training/dhan_ultra_training.parquet
- storage/training/dhan_ultra_training.csv

Menu Option: 74
"""

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
TRAINING_DIR = PROJECT_ROOT / "storage" / "training"
LEARNING_ULTRA_DIR = PROJECT_ROOT / "storage" / "learning_ultra"

# Inputs
SYNTHETIC_CSV = TRAINING_DIR / "dhan_index_options_training.csv"
SHADOW_PARQUET = LEARNING_ULTRA_DIR / "dhan_ultra_shadow_master.parquet"
SHADOW_CSV = LEARNING_ULTRA_DIR / "dhan_ultra_shadow_master.csv"

# Outputs
ULTRA_TRAINING_PARQUET = TRAINING_DIR / "dhan_ultra_training.parquet"
ULTRA_TRAINING_CSV = TRAINING_DIR / "dhan_ultra_training.csv"

TRAINING_DIR.mkdir(parents=True, exist_ok=True)
LEARNING_ULTRA_DIR.mkdir(parents=True, exist_ok=True)


def add_ultra_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add extended Ultra features to DataFrame.

    Extends baseline ~25 features to ~100 features.

    Args:
        df: Input DataFrame with baseline features

    Returns:
        DataFrame with Ultra features added (prefix: u_ or ultra_)
    """
    df = df.copy()

    # Multi-timeframe momentum (1, 3, 5, 10 steps)
    if "ltp" in df.columns:
        df["u_momentum_1"] = df.groupby(["underlying", "strike", "side"])["ltp"].pct_change(1, fill_method=None)
        df["u_momentum_3"] = df.groupby(["underlying", "strike", "side"])["ltp"].pct_change(3, fill_method=None)
        df["u_momentum_5"] = df.groupby(["underlying", "strike", "side"])["ltp"].pct_change(5, fill_method=None)
        df["u_momentum_10"] = df.groupby(["underlying", "strike", "side"])["ltp"].pct_change(10, fill_method=None)

    if "spot" in df.columns:
        df["u_spot_momentum_1"] = df.groupby("underlying")["spot"].pct_change(1, fill_method=None)
        df["u_spot_momentum_3"] = df.groupby("underlying")["spot"].pct_change(3, fill_method=None)
        df["u_spot_momentum_5"] = df.groupby("underlying")["spot"].pct_change(5, fill_method=None)
        df["u_spot_momentum_10"] = df.groupby("underlying")["spot"].pct_change(10, fill_method=None)

    # Volatility windows (short/long)
    if "ltp" in df.columns:
        df["u_vol_short"] = (
            df.groupby(["underlying", "strike", "side"])["ltp"]
            .rolling(3, min_periods=1)
            .std()
            .reset_index(level=[0, 1, 2], drop=True)
        )
        df["u_vol_long"] = (
            df.groupby(["underlying", "strike", "side"])["ltp"]
            .rolling(10, min_periods=1)
            .std()
            .reset_index(level=[0, 1, 2], drop=True)
        )
        df["u_vol_ratio"] = df["u_vol_short"] / (df["u_vol_long"] + 1e-10)

    if "spot" in df.columns:
        df["u_spot_vol_short"] = (
            df.groupby("underlying")["spot"].rolling(3, min_periods=1).std().reset_index(level=0, drop=True)
        )
        df["u_spot_vol_long"] = (
            df.groupby("underlying")["spot"].rolling(10, min_periods=1).std().reset_index(level=0, drop=True)
        )
        df["u_spot_vol_ratio"] = df["u_spot_vol_short"] / (df["u_spot_vol_long"] + 1e-10)

    # Moneyness powers (squared, cube)
    if "moneyness" in df.columns:
        df["u_moneyness_sq"] = df["moneyness"] ** 2
        df["u_moneyness_cube"] = df["moneyness"] ** 3
        df["u_moneyness_sqrt"] = np.sqrt(np.abs(df["moneyness"]))

    # Interaction features
    if "moneyness" in df.columns and "score" in df.columns:
        df["u_moneyness_x_score"] = df["moneyness"] * df["score"]
    if "moneyness" in df.columns and "confidence" in df.columns:
        df["u_moneyness_x_conf"] = df["moneyness"] * df["confidence"]
    if "score" in df.columns and "confidence" in df.columns:
        df["u_score_x_conf"] = df["score"] * df["confidence"]

    # Regime tags (high/low volatility flags)
    if "spot_roll_std_5" in df.columns:
        vol_median = df["spot_roll_std_5"].median()
        df["u_regime_high_vol"] = (df["spot_roll_std_5"] > vol_median).astype(int)
        df["u_regime_low_vol"] = (df["spot_roll_std_5"] <= vol_median).astype(int)

    # Time-of-day features (if timestamp available)
    if "ts" in df.columns:
        try:
            df["ts_parsed"] = pd.to_datetime(df["ts"], errors="coerce")
            df["u_hour"] = df["ts_parsed"].dt.hour
            df["u_minute"] = df["ts_parsed"].dt.minute
            df["u_time_slot"] = (df["u_hour"] // 2).astype(int)  # 12 slots per day
            df = df.drop(columns=["ts_parsed"], errors="ignore")
        except Exception:
            pass

    # Rolling hit rates (if pnl_pct available)
    if "pnl_pct" in df.columns and "underlying" in df.columns:
        df["u_is_win"] = (df["pnl_pct"] > 0).astype(int)
        df["u_rolling_win_rate_5"] = (
            df.groupby("underlying")["u_is_win"].rolling(5, min_periods=1).mean().reset_index(level=0, drop=True)
        )
        df["u_rolling_win_rate_10"] = (
            df.groupby("underlying")["u_is_win"].rolling(10, min_periods=1).mean().reset_index(level=0, drop=True)
        )

    # Additional momentum ratios
    if "u_momentum_1" in df.columns and "u_momentum_5" in df.columns:
        df["u_momentum_ratio_1_5"] = df["u_momentum_1"] / (df["u_momentum_5"].abs() + 1e-10)

    # Price position features
    if "ltp" in df.columns and "underlying" in df.columns:
        df["u_ltp_percentile"] = df.groupby("underlying")["ltp"].transform(
            lambda x: pd.qcut(x, q=10, labels=False, duplicates="drop")
        )

    # Fill NaN values with 0 for new features
    ultra_cols = [c for c in df.columns if c.startswith("u_")]
    df[ultra_cols] = df[ultra_cols].fillna(0.0)

    return df


def build_ultra_training_dataset() -> Dict[str, Any]:
    """
    Build Ultra training dataset with extended features.

    Returns:
        Dict with build results
    """
    print("=== SYSTEM3 ULTRA - FEATURE EXPANDER ===")
    print("[INFO] Building Ultra training dataset with extended features\n")
    print("[SAFETY] Shadow mode only - baseline features untouched\n")

    # Load synthetic training
    df_synthetic = None
    if SYNTHETIC_CSV.exists():
        try:
            df_synthetic = pd.read_csv(SYNTHETIC_CSV)
            print(f"[LOAD] Synthetic training: {len(df_synthetic)} rows")
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Failed to load synthetic training: {e}",
            }
    else:
        return {
            "status": "NO_SYNTHETIC",
            "message": "Synthetic training CSV not found",
        }

    # Load shadow master
    df_shadow = None
    if SHADOW_PARQUET.exists():
        try:
            df_shadow = pd.read_parquet(SHADOW_PARQUET)
            print(f"[LOAD] Shadow master (Parquet): {len(df_shadow)} rows")
        except Exception:
            if SHADOW_CSV.exists():
                try:
                    df_shadow = pd.read_csv(SHADOW_CSV)
                    print(f"[LOAD] Shadow master (CSV): {len(df_shadow)} rows")
                except Exception as e:
                    print(f"[WARN] Failed to load shadow master: {e}")
    elif SHADOW_CSV.exists():
        try:
            df_shadow = pd.read_csv(SHADOW_CSV)
            print(f"[LOAD] Shadow master (CSV): {len(df_shadow)} rows")
        except Exception as e:
            print(f"[WARN] Failed to load shadow master: {e}")

    # Combine datasets
    combined_rows = []

    # Add synthetic rows
    if df_synthetic is not None and not df_synthetic.empty:
        combined_rows.append(df_synthetic)

    # Add shadow rows (convert to training format)
    if df_shadow is not None and not df_shadow.empty:
        # Map shadow columns to training format
        df_shadow_training = df_shadow.copy()
        # Ensure required columns exist
        if "label" not in df_shadow_training.columns:
            # Try to infer label from signal or pred_label
            if "pred_label" in df_shadow_training.columns:
                df_shadow_training["label"] = df_shadow_training["pred_label"]
            elif "signal" in df_shadow_training.columns:
                df_shadow_training["label"] = df_shadow_training["signal"]
            else:
                df_shadow_training["label"] = "HOLD"

        combined_rows.append(df_shadow_training)

    if not combined_rows:
        return {
            "status": "EMPTY",
            "message": "No data to combine",
        }

    # Combine
    df_combined = pd.concat(combined_rows, ignore_index=True)

    # Add Ultra features
    print("[FEATURE] Adding Ultra extended features...")
    df_ultra = add_ultra_features(df_combined)

    # Count features
    base_feature_cols = [
        c
        for c in df_combined.columns
        if c not in ["ts", "timestamp", "underlying", "expiry", "side", "strike", "label", "pred_label"]
    ]
    ultra_feature_cols = [c for c in df_ultra.columns if c.startswith("u_")]
    total_features = len(
        [
            c
            for c in df_ultra.columns
            if c not in ["ts", "timestamp", "underlying", "expiry", "side", "strike", "label", "pred_label"]
        ]
    )

    print(f"[FEATURE] Base features: {len(base_feature_cols)}")
    print(f"[FEATURE] Ultra extra features: {len(ultra_feature_cols)}")
    print(f"[FEATURE] Total features: {total_features}")

    # Save
    try:
        # Save CSV
        df_ultra.to_csv(ULTRA_TRAINING_CSV, index=False)
        print(f"[SAVE] Ultra training CSV: {ULTRA_TRAINING_CSV} ({len(df_ultra)} rows)")

        # Save Parquet
        try:
            df_ultra.to_parquet(ULTRA_TRAINING_PARQUET, index=False, engine="pyarrow")
            print(f"[SAVE] Ultra training Parquet: {ULTRA_TRAINING_PARQUET} ({len(df_ultra)} rows)")
        except ImportError:
            print(f"[WARN] Parquet save skipped: pyarrow not installed. CSV saved successfully.")
        except Exception as e:
            print(f"[WARN] Parquet save failed: {e}. CSV saved successfully.")

        return {
            "status": "SUCCESS",
            "synthetic_rows": len(df_synthetic) if df_synthetic is not None else 0,
            "shadow_rows": len(df_shadow) if df_shadow is not None else 0,
            "total_rows": len(df_ultra),
            "base_features": len(base_feature_cols),
            "ultra_features": len(ultra_feature_cols),
            "total_features": total_features,
            "csv_path": str(ULTRA_TRAINING_CSV),
            "parquet_path": str(ULTRA_TRAINING_PARQUET) if ULTRA_TRAINING_PARQUET.exists() else None,
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Failed to save Ultra training dataset: {e}",
        }


def main() -> None:
    """Main entry point."""
    result = build_ultra_training_dataset()

    if result["status"] == "SUCCESS":
        print(f"\n=== BUILD SUMMARY ===")
        print(f"Synthetic Rows: {result['synthetic_rows']}")
        print(f"Shadow Rows: {result['shadow_rows']}")
        print(f"Total Rows: {result['total_rows']}")
        print(f"Base Features: {result['base_features']}")
        print(f"Ultra Extra Features: {result['ultra_features']}")
        print(f"Total Features: {result['total_features']}")
        print(f"CSV: {result['csv_path']}")
        if result.get("parquet_path"):
            print(f"Parquet: {result['parquet_path']}")
        print("\n✅ Ultra training dataset built successfully")
    else:
        print(f"\n[INFO] {result.get('message', 'Build not completed')}")


if __name__ == "__main__":
    main()
