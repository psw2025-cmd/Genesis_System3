"""
Dhan Index Options - Feature Drift Analyzer

Detects feature drift between training and live data.
No model update - detection only.
SAFE MODE ONLY - Read-only analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
TRAINING_DIR = PROJECT_ROOT / "storage" / "training"
TRAINING_CSV = TRAINING_DIR / "dhan_index_options_training.csv"
LIVE_SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
FEATURE_DRIFT_DIR = REPORTS_DIR / "feature_drift"

FEATURE_DRIFT_DIR.mkdir(parents=True, exist_ok=True)


def analyze_feature_drift() -> Dict[str, Any]:
    """
    Analyze feature drift between training and live data.

    No model update - detection only.

    Returns:
        Dict with drift analysis results
    """
    print("=== ANGEL ONE INDEX OPTIONS - FEATURE DRIFT ANALYZER ===")
    print("[INFO] SAFE MODE - Detection only, NO model update\n")

    if not TRAINING_CSV.exists():
        return {
            "status": "NO_TRAINING_DATA",
            "message": "Training CSV not found",
        }

    if not LIVE_SIGNALS_CSV.exists():
        return {
            "status": "NO_LIVE_DATA",
            "message": "Live signals CSV not found",
        }

    try:
        df_training = pd.read_csv(TRAINING_CSV)
        df_live = pd.read_csv(LIVE_SIGNALS_CSV)

        if df_training.empty or df_live.empty:
            return {
                "status": "EMPTY",
                "message": "Training or live data is empty",
            }

        # Get numeric feature columns (exclude metadata)
        exclude_cols = [
            "ts",
            "timestamp",
            "underlying",
            "expiry",
            "side",
            "strike",
            "label",
            "pred_label",
            "pred_confidence",
            "expected_move_score",
        ]
        training_features = [
            c for c in df_training.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df_training[c])
        ]
        live_features = [
            c for c in df_live.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df_live[c])
        ]

        # Common features
        common_features = [f for f in training_features if f in live_features]

        if not common_features:
            return {
                "status": "NO_COMMON_FEATURES",
                "message": "No common numeric features found",
            }

        # Analyze drift
        drift_results = {}

        for feature in common_features:
            train_values = df_training[feature].dropna()
            live_values = df_live[feature].dropna()

            if len(train_values) == 0 or len(live_values) == 0:
                continue

            train_mean = train_values.mean()
            train_std = train_values.std()
            live_mean = live_values.mean()
            live_std = live_values.std()

            # Drift metrics
            mean_drift = abs(live_mean - train_mean) / (train_std + 1e-10) if train_std > 0 else 0.0
            std_drift = abs(live_std - train_std) / (train_std + 1e-10) if train_std > 0 else 0.0

            drift_results[feature] = {
                "train_mean": float(train_mean),
                "train_std": float(train_std),
                "live_mean": float(live_mean),
                "live_std": float(live_std),
                "mean_drift": float(mean_drift),
                "std_drift": float(std_drift),
                "drift_severity": _classify_drift_severity(mean_drift, std_drift),
            }

        # Overall drift summary
        high_drift_features = [f for f, data in drift_results.items() if data["drift_severity"] in ["HIGH", "CRITICAL"]]

        return {
            "status": "SUCCESS",
            "total_features_analyzed": len(common_features),
            "drift_results": drift_results,
            "high_drift_features": high_drift_features,
            "drift_summary": {
                "features_with_drift": len(high_drift_features),
                "total_features": len(common_features),
            },
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
        }


def _classify_drift_severity(mean_drift: float, std_drift: float) -> str:
    """Classify drift severity."""
    max_drift = max(mean_drift, std_drift)

    if max_drift > 3.0:
        return "CRITICAL"
    elif max_drift > 2.0:
        return "HIGH"
    elif max_drift > 1.0:
        return "MEDIUM"
    else:
        return "LOW"


def save_drift_analysis(analysis: Dict[str, Any]) -> Path:
    """
    Save drift analysis to CSV.

    Returns:
        Path to saved CSV
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    csv_path = FEATURE_DRIFT_DIR / f"feature_drift_analysis_{today}.csv"

    if analysis["status"] == "SUCCESS":
        rows = []
        for feature, data in analysis["drift_results"].items():
            rows.append(
                {
                    "feature": feature,
                    "train_mean": data["train_mean"],
                    "live_mean": data["live_mean"],
                    "mean_drift": data["mean_drift"],
                    "std_drift": data["std_drift"],
                    "drift_severity": data["drift_severity"],
                }
            )

        if rows:
            df = pd.DataFrame(rows)
            df = df.sort_values("mean_drift", ascending=False)
            df.to_csv(csv_path, index=False)

    return csv_path


def main() -> None:
    """Main entry point."""
    analysis = analyze_feature_drift()

    if analysis["status"] == "SUCCESS":
        print(f"=== FEATURE DRIFT ANALYSIS ===\n")
        print(f"Total Features Analyzed: {analysis['total_features_analyzed']}")
        print(f"Features with High/Critical Drift: {len(analysis['high_drift_features'])}")

        if analysis["high_drift_features"]:
            print("\n=== HIGH DRIFT FEATURES ===")
            for feature in analysis["high_drift_features"]:
                data = analysis["drift_results"][feature]
                print(f"{feature}:")
                print(f"  Train Mean: {data['train_mean']:.3f}, Live Mean: {data['live_mean']:.3f}")
                print(f"  Mean Drift: {data['mean_drift']:.3f} ({data['drift_severity']})")

        # Top 5 features by drift
        sorted_features = sorted(analysis["drift_results"].items(), key=lambda x: x[1]["mean_drift"], reverse=True)[:5]

        print("\n=== TOP 5 FEATURES BY DRIFT ===")
        for feature, data in sorted_features:
            print(f"{feature}: drift={data['mean_drift']:.3f}, severity={data['drift_severity']}")

        # Save
        save_path = save_drift_analysis(analysis)
        print(f"\n[SAVE] Drift analysis saved to: {save_path}")
        print("\n[NOTE] This is detection only. No model update performed.")
    else:
        print(f"[INFO] {analysis.get('message', 'Drift analysis not available')}")


if __name__ == "__main__":
    main()
