"""
System3 Ultra - Hyperparameter Space Explorer

Offline hyperparameter exploration for Ultra models.
Reports only - no model overwrites.

Inputs:
- storage/training/dhan_ultra_training.parquet

Outputs:
- storage/reports_ultra/ultra_hparam_results_{underlying}.csv

Menu Option: 76
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score

PROJECT_ROOT = Path(__file__).parent.parent.parent
TRAINING_DIR = PROJECT_ROOT / "storage" / "training"
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

ULTRA_TRAINING_PARQUET = TRAINING_DIR / "dhan_ultra_training.parquet"
ULTRA_TRAINING_CSV = TRAINING_DIR / "dhan_ultra_training.csv"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def prepare_features_labels(
    df: pd.DataFrame,
) -> tuple[Optional[pd.DataFrame], Optional[pd.Series], Optional[List[str]]]:
    """Prepare features and labels."""
    if df.empty:
        return None, None, None

    exclude_cols = [
        "ts",
        "timestamp",
        "underlying",
        "expiry",
        "side",
        "strike",
        "label",
        "pred_label",
        "true_label",
        "signal_label",
        "pred_confidence",
        "confidence",
        "score",
        "pnl_pct",
        "exit_reason",
    ]

    feature_cols = [c for c in df.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df[c])]

    X = df[feature_cols].copy().dropna()
    if X.empty:
        return None, None, None

    label_col = "label" if "label" in df.columns else None
    if label_col is None:
        return None, None, None

    y = df.loc[X.index, label_col]
    mask = ~y.isna()
    X = X[mask]
    y = y[mask]

    if X.empty or y.empty:
        return None, None, None

    return X, y, feature_cols


def explore_hyperparameters() -> Dict[str, Any]:
    """
    Explore hyperparameter space for Ultra models.

    Returns:
        Dict with exploration results
    """
    print("=== SYSTEM3 ULTRA - HYPERPARAMETER EXPLORER ===")
    print("[INFO] Offline hyperparameter exploration (report only)\n")
    print("[SAFETY] No model files written - reports only\n")

    # Load Ultra training dataset
    df_ultra = None
    if ULTRA_TRAINING_PARQUET.exists():
        try:
            df_ultra = pd.read_parquet(ULTRA_TRAINING_PARQUET)
        except Exception:
            if ULTRA_TRAINING_CSV.exists():
                df_ultra = pd.read_csv(ULTRA_TRAINING_CSV)
    elif ULTRA_TRAINING_CSV.exists():
        df_ultra = pd.read_csv(ULTRA_TRAINING_CSV)

    if df_ultra is None or df_ultra.empty:
        return {
            "status": "NO_DATA",
            "message": "Ultra training dataset not found",
        }

    print(f"[LOAD] Ultra training: {len(df_ultra)} rows")

    # Hyperparameter grids
    rf_params = [
        {"n_estimators": 100, "max_depth": 5},
        {"n_estimators": 200, "max_depth": 10},
        {"n_estimators": 300, "max_depth": 15},
    ]

    gb_params = [
        {"n_estimators": 100, "max_depth": 5, "learning_rate": 0.1},
        {"n_estimators": 200, "max_depth": 7, "learning_rate": 0.05},
        {"n_estimators": 300, "max_depth": 10, "learning_rate": 0.1},
    ]

    all_results = {}

    for underlying in UNDERLYINGS:
        df_u = df_ultra[df_ultra["underlying"] == underlying] if "underlying" in df_ultra.columns else pd.DataFrame()
        if df_u.empty:
            continue

        print(f"\n[EXPLORE] {underlying}...")

        X, y, feature_cols = prepare_features_labels(df_u)
        if X is None or y is None:
            continue

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if len(y.unique()) > 1 else None
        )

        results = []

        # Test RandomForest
        for params in rf_params:
            model = RandomForestClassifier(**params, random_state=42, n_jobs=-1)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average="weighted")

            results.append(
                {
                    "underlying": underlying,
                    "model_type": "RandomForest",
                    "params_json": json.dumps(params),
                    "accuracy": float(accuracy),
                    "f1": float(f1),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        # Test GradientBoosting
        for params in gb_params:
            model = GradientBoostingClassifier(**params, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average="weighted")

            results.append(
                {
                    "underlying": underlying,
                    "model_type": "GradientBoosting",
                    "params_json": json.dumps(params),
                    "accuracy": float(accuracy),
                    "f1": float(f1),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        all_results[underlying] = results

        # Save per underlying
        if results:
            df_results = pd.DataFrame(results)
            csv_path = REPORTS_ULTRA_DIR / f"ultra_hparam_results_{underlying}.csv"
            df_results.to_csv(csv_path, index=False)
            print(f"[SAVE] {underlying} results: {csv_path}")

    return {
        "status": "SUCCESS",
        "results": all_results,
    }


def main() -> None:
    """Main entry point."""
    result = explore_hyperparameters()

    if result["status"] == "SUCCESS":
        print("\n=== HYPERPARAMETER EXPLORATION SUMMARY ===")
        for underlying, results in result["results"].items():
            if results:
                best = max(results, key=lambda x: x["accuracy"])
                print(f"{underlying}:")
                print(f"  Best: {best['model_type']} - Accuracy: {best['accuracy']:.4f}, F1: {best['f1']:.4f}")
                print(f"  Params: {best['params_json']}")
        print(f"\n[SAVE] All results saved to: {REPORTS_ULTRA_DIR}")
        print("[NOTE] No model files written - reports only")
    else:
        print(f"\n[INFO] {result.get('message', 'Exploration not completed')}")


if __name__ == "__main__":
    main()
