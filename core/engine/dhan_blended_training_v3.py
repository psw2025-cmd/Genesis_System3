"""
Dhan Index Options - Blended Training V3

Trains models using synthetic + real data.
Saves to dedicated directory (core/models/dhan_real_blended/) without overwriting baseline.

Inputs:
- storage/training/dhan_index_options_training.csv (baseline synthetic)
- storage/learning/dhan_index_real_master_dataset.parquet (or CSV fallback)

Outputs:
- core/models/dhan_real_blended/*_model_blended_v3.pkl
- core/models/dhan_real_blended/*_model_blended_v3_meta.json

Config: storage/config/dhan_blended_training_v3_config.json (optional)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report

PROJECT_ROOT = Path(__file__).parent.parent.parent
TRAINING_DIR = PROJECT_ROOT / "storage" / "training"
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan"
BLENDED_MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan_real_blended"

# Input files
SYNTHETIC_CSV = TRAINING_DIR / "dhan_index_options_training.csv"
REAL_MASTER_PARQUET = LEARNING_DIR / "dhan_index_real_master_dataset.parquet"
REAL_MASTER_CSV = LEARNING_DIR / "dhan_index_real_master_dataset.csv"
CONFIG_JSON = CONFIG_DIR / "dhan_blended_training_v3_config.json"

BLENDED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Load training config or use defaults."""
    defaults = {
        "max_synthetic_rows_per_underlying": 600,
        "max_real_rows_per_underlying": 200,
        "validation_split": 0.2,
    }

    if CONFIG_JSON.exists():
        try:
            with CONFIG_JSON.open("r", encoding="utf-8") as f:
                user_config = json.load(f)
                defaults.update(user_config)
        except Exception as e:
            print(f"[WARN] Failed to load config, using defaults: {e}")

    return defaults


def load_training_data(config: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """
    Load and combine synthetic + real data per underlying.

    Returns:
        Dict mapping underlying -> combined DataFrame
    """
    print("[LOAD] Loading training data...")

    # Load synthetic
    df_synthetic = None
    if SYNTHETIC_CSV.exists():
        try:
            df_synthetic = pd.read_csv(SYNTHETIC_CSV)
            print(f"[LOAD] Synthetic: {len(df_synthetic)} rows")
        except Exception as e:
            print(f"[WARN] Failed to load synthetic: {e}")
    else:
        print("[WARN] Synthetic CSV not found")

    # Load real master dataset
    df_real = None
    if REAL_MASTER_PARQUET.exists():
        try:
            df_real = pd.read_parquet(REAL_MASTER_PARQUET)
            print(f"[LOAD] Real (Parquet): {len(df_real)} rows")
        except Exception:
            if REAL_MASTER_CSV.exists():
                try:
                    df_real = pd.read_csv(REAL_MASTER_CSV)
                    print(f"[LOAD] Real (CSV): {len(df_real)} rows")
                except Exception as e:
                    print(f"[WARN] Failed to load real dataset: {e}")
    elif REAL_MASTER_CSV.exists():
        try:
            df_real = pd.read_csv(REAL_MASTER_CSV)
            print(f"[LOAD] Real (CSV): {len(df_real)} rows")
        except Exception as e:
            print(f"[WARN] Failed to load real dataset: {e}")

    if df_synthetic is None and df_real is None:
        raise ValueError("No training data available (synthetic or real)")

    # Combine per underlying
    underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
    combined_data = {}

    for underlying in underlyings:
        combined_rows = []

        # Add synthetic subset
        if df_synthetic is not None and "underlying" in df_synthetic.columns:
            df_syn_u = df_synthetic[df_synthetic["underlying"] == underlying]
            max_syn = config["max_synthetic_rows_per_underlying"]
            if len(df_syn_u) > max_syn:
                df_syn_u = df_syn_u.sample(max_syn, random_state=42)
            combined_rows.append(df_syn_u)
            print(f"[COMBINE] {underlying}: {len(df_syn_u)} synthetic rows")

        # Add real subset
        if df_real is not None and "underlying" in df_real.columns:
            df_real_u = df_real[df_real["underlying"] == underlying]
            max_real = config["max_real_rows_per_underlying"]
            if len(df_real_u) > max_real:
                df_real_u = df_real_u.sample(max_real, random_state=42)
            combined_rows.append(df_real_u)
            print(f"[COMBINE] {underlying}: {len(df_real_u)} real rows")

        if combined_rows:
            df_combined = pd.concat(combined_rows, ignore_index=True)
            combined_data[underlying] = df_combined
            print(f"[COMBINE] {underlying}: Total {len(df_combined)} rows")

    return combined_data


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
        # Try to infer from other columns
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


def train_model_for_underlying(
    underlying: str,
    df: pd.DataFrame,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Train blended model for one underlying."""
    print(f"\n[TRAIN] {underlying}...")

    # Prepare features and labels
    X, y, feature_cols = prepare_features_labels(df)

    if X is None or y is None or X.empty:
        return {
            "status": "SKIP",
            "message": "No valid features/labels",
        }

    print(f"[TRAIN] {underlying}: {len(X)} samples, {len(feature_cols)} features")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config["validation_split"],
        random_state=42,
        stratify=y if len(y.unique()) > 1 else None,
    )

    # Train
    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"[RESULT] {underlying} accuracy: {accuracy:.4f}")

    # Save model
    model_file = BLENDED_MODELS_DIR / f"{underlying}_model_blended_v3.pkl"
    joblib.dump(model, model_file)
    print(f"[SAVE] Model: {model_file}")

    # Save metadata
    meta = {
        "underlying": underlying,
        "training_date": datetime.utcnow().isoformat(),
        "model_version": "blended_v3",
        "training_data_sources": {
            "synthetic": "storage/training/dhan_index_options_training.csv",
            "real": "storage/learning/dhan_index_real_master_dataset.parquet",
        },
        "num_synthetic_rows": len(df[df.get("source", "") == "synthetic"]) if "source" in df.columns else 0,
        "num_real_rows": len(df[df.get("source", "") == "real"]) if "source" in df.columns else 0,
        "total_rows": len(df),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "feature_count": len(feature_cols),
        "features": feature_cols,
        "accuracy": float(accuracy),
        "validation_split": config["validation_split"],
    }

    meta_file = BLENDED_MODELS_DIR / f"{underlying}_model_blended_v3_meta.json"
    with meta_file.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"[SAVE] Meta: {meta_file}")

    return {
        "status": "SUCCESS",
        "accuracy": accuracy,
        "model_file": str(model_file),
        "meta_file": str(meta_file),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
    }


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - BLENDED TRAINING V3 ===")
    print("[INFO] Training models with synthetic + real data\n")
    print("[SAFETY] Models saved to dedicated directory (not overwriting baseline)\n")

    # Load config
    config = load_config()
    print(f"[CONFIG] Max synthetic rows per underlying: {config['max_synthetic_rows_per_underlying']}")
    print(f"[CONFIG] Max real rows per underlying: {config['max_real_rows_per_underlying']}")
    print(f"[CONFIG] Validation split: {config['validation_split']}\n")

    # Load data
    try:
        combined_data = load_training_data(config)
    except Exception as e:
        print(f"[ERROR] Failed to load training data: {e}")
        return

    if not combined_data:
        print("[ERROR] No combined data available")
        return

    # Train per underlying
    results = {}
    for underlying, df in combined_data.items():
        result = train_model_for_underlying(underlying, df, config)
        results[underlying] = result

    # Summary
    print("\n=== TRAINING SUMMARY ===")
    for underlying, result in results.items():
        if result["status"] == "SUCCESS":
            print(f"{underlying}:")
            print(f"  Accuracy: {result['accuracy']:.4f}")
            print(f"  Train Rows: {result['train_rows']}")
            print(f"  Test Rows: {result['test_rows']}")
            print(f"  Model: {result['model_file']}")
        else:
            print(f"{underlying}: {result.get('message', 'Skipped')}")

    print(f"\n[SAVE] All models saved to: {BLENDED_MODELS_DIR}")
    print("[SAFETY] Baseline models untouched in: core/models/dhan/")


if __name__ == "__main__":
    main()
