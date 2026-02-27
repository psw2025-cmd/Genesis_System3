"""
System3 Ultra - Risk Regime Classifier

Classifies market regimes (low/medium/high volatility, trending vs ranging).
Adds regime labels to Ultra training data.

Inputs:
- storage/training/angel_ultra_training.parquet

Outputs:
- storage/training/angel_ultra_training_with_regime.parquet
- storage/reports_ultra/ultra_regime_summary.csv

Menu Option: 77
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
TRAINING_DIR = PROJECT_ROOT / "storage" / "training"
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

ULTRA_TRAINING_PARQUET = TRAINING_DIR / "angel_ultra_training.parquet"
ULTRA_TRAINING_CSV = TRAINING_DIR / "angel_ultra_training.csv"
ULTRA_TRAINING_WITH_REGIME_PARQUET = TRAINING_DIR / "angel_ultra_training_with_regime.parquet"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def classify_regime(row: pd.Series) -> str:
    """
    Classify regime for a single row.

    Returns:
        Regime label: LOW_VOL, MEDIUM_VOL, HIGH_VOL, TREND_UP, TREND_DOWN, RANGE
    """
    # Volatility classification
    vol = row.get("spot_roll_std_5", 0.0)
    if pd.isna(vol):
        vol = 0.0

    # Momentum classification
    momentum = row.get("u_spot_momentum_5", 0.0)
    if pd.isna(momentum):
        momentum = 0.0

    # Volatility thresholds (percentile-based if possible)
    vol_low_thresh = 0.33
    vol_high_thresh = 0.67

    # Classify volatility
    if vol < vol_low_thresh:
        vol_regime = "LOW_VOL"
    elif vol > vol_high_thresh:
        vol_regime = "HIGH_VOL"
    else:
        vol_regime = "MEDIUM_VOL"

    # Classify trend
    if momentum > 0.01:
        trend_regime = "TREND_UP"
    elif momentum < -0.01:
        trend_regime = "TREND_DOWN"
    else:
        trend_regime = "RANGE"

    # Combine
    return f"{vol_regime}_{trend_regime}"


def label_regimes() -> Dict[str, Any]:
    """
    Label regimes for Ultra training dataset.

    Returns:
        Dict with labeling results
    """
    print("=== SYSTEM3 ULTRA - RISK REGIME CLASSIFIER ===")
    print("[INFO] Classifying market regimes\n")
    print("[SAFETY] Shadow mode only - no overwrites\n")

    # Load Ultra training dataset
    df_ultra = None
    if ULTRA_TRAINING_PARQUET.exists():
        try:
            df_ultra = pd.read_parquet(ULTRA_TRAINING_PARQUET)
            print(f"[LOAD] Ultra training (Parquet): {len(df_ultra)} rows")
        except Exception:
            if ULTRA_TRAINING_CSV.exists():
                df_ultra = pd.read_csv(ULTRA_TRAINING_CSV)
                print(f"[LOAD] Ultra training (CSV): {len(df_ultra)} rows")
    elif ULTRA_TRAINING_CSV.exists():
        df_ultra = pd.read_csv(ULTRA_TRAINING_CSV)
        print(f"[LOAD] Ultra training (CSV): {len(df_ultra)} rows")

    if df_ultra is None or df_ultra.empty:
        return {
            "status": "NO_DATA",
            "message": "Ultra training dataset not found",
        }

    # Classify regimes
    print("[CLASSIFY] Labeling regimes...")
    df_ultra["regime_label"] = df_ultra.apply(classify_regime, axis=1)

    # Summary per underlying + regime
    summary_rows = []
    for underlying in UNDERLYINGS:
        df_u = df_ultra[df_ultra["underlying"] == underlying] if "underlying" in df_ultra.columns else pd.DataFrame()
        if df_u.empty:
            continue

        regime_counts = df_u["regime_label"].value_counts().to_dict()
        for regime, count in regime_counts.items():
            summary_rows.append(
                {
                    "underlying": underlying,
                    "regime": regime,
                    "count": count,
                    "percentage": float(count / len(df_u) * 100),
                }
            )

    # Save with regime labels
    try:
        # Save Parquet
        try:
            df_ultra.to_parquet(ULTRA_TRAINING_WITH_REGIME_PARQUET, index=False, engine="pyarrow")
            print(f"[SAVE] Ultra training with regime (Parquet): {ULTRA_TRAINING_WITH_REGIME_PARQUET}")
        except ImportError:
            print(f"[WARN] Parquet save skipped: pyarrow not installed")
        except Exception as e:
            print(f"[WARN] Parquet save failed: {e}")

        # Save summary
        if summary_rows:
            df_summary = pd.DataFrame(summary_rows)
            summary_csv = REPORTS_ULTRA_DIR / "ultra_regime_summary.csv"
            df_summary.to_csv(summary_csv, index=False)
            print(f"[SAVE] Regime summary: {summary_csv}")

        return {
            "status": "SUCCESS",
            "total_rows": len(df_ultra),
            "regime_distribution": df_ultra["regime_label"].value_counts().to_dict(),
            "summary_rows": len(summary_rows),
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Failed to save: {e}",
        }


def main() -> None:
    """Main entry point."""
    result = label_regimes()

    if result["status"] == "SUCCESS":
        print("\n=== REGIME CLASSIFICATION SUMMARY ===")
        print(f"Total Rows: {result['total_rows']}")
        print(f"\nRegime Distribution:")
        for regime, count in result["regime_distribution"].items():
            pct = count / result["total_rows"] * 100
            print(f"  {regime}: {count} ({pct:.1f}%)")
        print(f"\n[SAVE] Regime-labeled dataset saved")
        print("[NOTE] No model training performed - labeling only")
    else:
        print(f"\n[INFO] {result.get('message', 'Classification not completed')}")


if __name__ == "__main__":
    main()
