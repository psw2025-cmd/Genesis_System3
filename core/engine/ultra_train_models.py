"""
System3 Ultra - Shadow Model Trainer V3

Trains Ultra shadow models separate from baseline.
Uses Ultra training dataset with extended features.

Inputs:
- storage/training/angel_ultra_training.parquet

Outputs:
- core/models/angel_one_ultra/*_ultra_model.pkl
- core/models/angel_one_ultra/*_ultra_model_meta.json

Menu Option: 75
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report

PROJECT_ROOT = Path(__file__).parent.parent.parent
TRAINING_DIR = PROJECT_ROOT / "storage" / "training"
ULTRA_MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one_ultra"

# Input
ULTRA_TRAINING_PARQUET = TRAINING_DIR / "angel_ultra_training.parquet"
ULTRA_TRAINING_CSV = TRAINING_DIR / "angel_ultra_training.csv"

ULTRA_MODELS_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def prepare_features_labels(
    df: pd.DataFrame,
    selected_features: Optional[List[str]] = None,
) -> tuple[Optional[pd.DataFrame], Optional[pd.Series], Optional[List[str]]]:
    """Prepare features and labels from DataFrame."""
    if df.empty:
        return None, None, None

    # Exclude non-feature columns
    exclude_cols = [
        "ts",
        "timestamp",
        "ts_entry",
        "ts_exit",
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
        "expected_move_score",
        "entry_ltp",
        "exit_ltp",
        "entry_price",
        "exit_price",
        "pnl_pct",
        "exit_reason",
        "market_regime",
        "vol_regime",
        "signal",
        "sl_price",
        "tp_price",
        "is_win",
        "is_loss",
        "is_misfire",
        "profile_source",
    ]

    # Get numeric feature columns
    base_feature_cols = [c for c in df.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df[c])]

    if selected_features:
        feature_cols = [c for c in selected_features if c in base_feature_cols]
        if not feature_cols:
            feature_cols = base_feature_cols
    else:
        feature_cols = base_feature_cols

    # Build feature matrix
    X = df[feature_cols].copy()
    X = X.dropna()

    if X.empty:
        return None, None, None

    # Get labels
    label_col = "label" if "label" in df.columns else None
    if label_col is None:
        for col in ["true_label", "pred_label", "signal_label"]:
            if col in df.columns:
                label_col = col
                break

    if label_col is None:
        return None, None, None

    # Align labels with feature rows
    y = df.loc[X.index, label_col]

    # Drop rows with missing labels
    mask = ~y.isna()
    X = X[mask]
    y = y[mask]

    if X.empty or y.empty:
        return None, None, None

    return X, y, feature_cols


def train_ultra_models() -> Dict[str, Any]:
    """
    Train Ultra shadow models for all underlyings.

    Returns:
        Dict with training results
    """
    print("=== SYSTEM3 ULTRA - SHADOW MODEL TRAINER V3 ===")
    print("[INFO] Training Ultra shadow models with extended features\n")
    print("[SAFETY] Models saved to separate directory (not overwriting baseline)\n")

    # Load Ultra training dataset
    df_ultra = None
    if ULTRA_TRAINING_PARQUET.exists():
        try:
            df_ultra = pd.read_parquet(ULTRA_TRAINING_PARQUET)
            print(f"[LOAD] Ultra training (Parquet): {len(df_ultra)} rows")
        except Exception:
            if ULTRA_TRAINING_CSV.exists():
                try:
                    df_ultra = pd.read_csv(ULTRA_TRAINING_CSV)
                    print(f"[LOAD] Ultra training (CSV): {len(df_ultra)} rows")
                except Exception as e:
                    return {
                        "status": "ERROR",
                        "message": f"Failed to load Ultra training: {e}",
                    }
    elif ULTRA_TRAINING_CSV.exists():
        try:
            df_ultra = pd.read_csv(ULTRA_TRAINING_CSV)
            print(f"[LOAD] Ultra training (CSV): {len(df_ultra)} rows")
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Failed to load Ultra training: {e}",
            }
    else:
        return {
            "status": "NO_DATA",
            "message": "Ultra training dataset not found. Run Phase 11 first.",
        }

    if df_ultra.empty:
        return {
            "status": "EMPTY",
            "message": "Ultra training dataset is empty",
        }

    # Train per underlying
    results = {}
    for underlying in UNDERLYINGS:
        df_u = df_ultra[df_ultra["underlying"] == underlying] if "underlying" in df_ultra.columns else pd.DataFrame()

        if df_u.empty:
            results[underlying] = {
                "status": "SKIP",
                "message": f"No data for {underlying}",
            }
            continue

        print(f"\n[ULTRA TRAIN] {underlying}...")

        # Prepare features and labels
        X, y, feature_cols = prepare_features_labels(df_u)

        if X is None or y is None or X.empty:
            results[underlying] = {
                "status": "SKIP",
                "message": "No valid features/labels",
            }
            continue

        print(f"[ULTRA TRAIN] {underlying}: {len(X)} samples, {len(feature_cols)} features")

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y if len(y.unique()) > 1 else None,
        )

        # Train RandomForest (stronger model for Ultra)
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"[ULTRA RESULT] {underlying} accuracy: {accuracy:.4f}")

        # Save model
        model_file = ULTRA_MODELS_DIR / f"{underlying}_ultra_model.pkl"
        joblib.dump(model, model_file)
        print(f"[SAVE] Model: {model_file}")

        # Save metadata
        meta = {
            "underlying": underlying,
            "training_date": datetime.utcnow().isoformat(),
            "model_version": "ultra_v3",
            "model_type": "RandomForest",
            "training_data_source": "ultra_training",
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "feature_count": len(feature_cols),
            "features": feature_cols,
            "accuracy": float(accuracy),
            "validation_split": 0.2,
        }

        meta_file = ULTRA_MODELS_DIR / f"{underlying}_ultra_model_meta.json"
        with meta_file.open("w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        print(f"[SAVE] Meta: {meta_file}")

        results[underlying] = {
            "status": "SUCCESS",
            "accuracy": accuracy,
            "model_file": str(model_file),
            "meta_file": str(meta_file),
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "feature_count": len(feature_cols),
        }

    return {
        "status": "SUCCESS",
        "results": results,
    }


def main() -> None:
    """Main entry point."""
    result = train_ultra_models()

    if result["status"] == "SUCCESS":
        print("\n=== ULTRA TRAINING SUMMARY ===")
        for underlying, res in result["results"].items():
            if res["status"] == "SUCCESS":
                print(f"{underlying}:")
                print(f"  Accuracy: {res['accuracy']:.4f}")
                print(f"  Train Rows: {res['train_rows']}")
                print(f"  Test Rows: {res['test_rows']}")
                print(f"  Features: {res['feature_count']}")
                print(f"  Model: {res['model_file']}")
            else:
                print(f"{underlying}: {res.get('message', 'Skipped')}")

        print(f"\n[SAVE] All Ultra models saved to: {ULTRA_MODELS_DIR}")
        print("[SAFETY] Baseline models untouched in: core/models/angel_one/")
    else:
        print(f"\n[INFO] {result.get('message', 'Training not completed')}")


if __name__ == "__main__":
    main()
