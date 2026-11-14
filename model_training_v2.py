"""
Model Training v2 - Core XGBoost Trainer
=========================================

Reusable training utility for Phase 391 (XGBoost Model Training).
Loads balanced dataset, trains per-underlying classifiers, computes metrics.

Features:
- Load balanced dataset from Phase 390
- Validate schema (signal target, underlying identifier)
- Per-underlying stratified train/test split
- XGBoost with sklearn fallback
- Comprehensive metrics (accuracy, F1, per-class precision/recall, confusion matrix)
- Model serialization with metadata

Author: System3 AI Team
Date: 2025-12-08
"""

import json
import hashlib
import logging
import os
import pickle
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.preprocessing import LabelEncoder

# Try XGBoost; fall back to sklearn ensemble
try:
    import xgboost as xgb

    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    from sklearn.ensemble import GradientBoostingClassifier

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """Configuration for model training."""

    test_size: float = 0.2
    random_state: int = 42
    min_samples_per_underlying: int = 100
    model_dir: str = "models/xgboost_v1"
    xgb_max_depth: int = 6
    xgb_n_estimators: int = 100
    xgb_learning_rate: float = 0.1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict with JSON-serializable values."""
        return {
            "test_size": float(self.test_size),
            "random_state": int(self.random_state),
            "min_samples_per_underlying": int(self.min_samples_per_underlying),
            "model_dir": str(self.model_dir),
            "xgb_max_depth": int(self.xgb_max_depth),
            "xgb_n_estimators": int(self.xgb_n_estimators),
            "xgb_learning_rate": float(self.xgb_learning_rate),
        }


def load_balanced_dataset(path: str) -> pd.DataFrame:
    """
    Load balanced dataset from Phase 390.

    Args:
        path: Path to CSV file (e.g., 'storage/datasets/phase_390_balanced_features.csv')

    Returns:
        pd.DataFrame with columns including 'signal' and 'underlying'

    Raises:
        FileNotFoundError: If CSV not found
        ValueError: If required columns missing
    """
    logger.info(f"Loading balanced dataset from: {path}")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} rows × {len(df.columns)} columns")

    # Validate required columns
    required_cols = ["signal", "underlying"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    logger.info(f"✓ Dataset validation passed")
    return df


def point_in_time_split(df: pd.DataFrame, test_size: float) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Separate matured, real sessions before any fitting or resampling.

    A random row split or a pre-balanced/SMOTE frame can leak the same market
    event into both sets. Only explicitly named, numeric pre-decision features
    are admitted; forward returns and labels are never candidate features.
    """
    required = {"underlying", "signal", "ts", "label_available_at", "data_origin"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"POINT_IN_TIME_PROOF_MISSING:{sorted(missing)}")
    if not 0 < test_size < 0.5:
        raise ValueError("INVALID_TEST_SIZE")
    frame = df.copy()
    feature_time = pd.to_datetime(frame["ts"], utc=True, errors="coerce")
    label_time = pd.to_datetime(frame["label_available_at"], utc=True, errors="coerce")
    if (feature_time.isna().any() or label_time.isna().any()
            or (label_time <= feature_time).any()
            or (label_time > pd.Timestamp.now(tz="UTC")).any()):
        raise ValueError("INVALID_OR_UNMATURED_LABEL_TIME")
    origins = frame["data_origin"].astype(str).str.lower()
    if not origins.isin({"dhan_timestamped", "nse_archive_timestamped"}).all():
        raise ValueError("UNVERIFIED_OR_RESAMPLED_TRAINING_DATA")
    features = [col for col in frame.columns if col.startswith("feature_")]
    if not features or any(any(token in col.lower() for token in
                               ("future", "forward", "label", "target", "outcome", "pnl"))
                           for col in features):
        raise ValueError("SAFE_FEATURE_SCHEMA_MISSING")
    if any(not pd.api.types.is_numeric_dtype(frame[col]) or not frame[col].notna().all()
           for col in features):
        raise ValueError("INVALID_POINT_IN_TIME_FEATURE")
    frame["_feature_time"] = feature_time
    frame["_label_time"] = label_time
    sessions = sorted(feature_time.dt.date.unique())
    if len(sessions) < 30:
        raise ValueError("NEED_AT_LEAST_30_SOURCE_SESSIONS")
    split = max(1, int(len(sessions) * (1 - test_size)))
    first_test_day = sessions[split]
    test_start = pd.Timestamp(first_test_day, tz="UTC")
    train = frame[(frame["_feature_time"] < test_start) & (frame["_label_time"] < test_start)]
    test = frame[frame["_feature_time"] >= test_start]
    if (train.empty or test.empty or len(set(train["signal"])) < 2
            or len(set(test["signal"]) - set(train["signal"]))):
        raise ValueError("CHRONOLOGICAL_SPLIT_UNUSABLE")
    return train, test, features


def _encode_labels(signal_values: np.ndarray) -> Tuple[np.ndarray, Dict[int, str]]:
    """
    Encode signal labels to integers.

    Args:
        signal_values: Array of signal values (BUY, SELL, HOLD)

    Returns:
        (encoded_values, reverse_mapping)
    """
    le = LabelEncoder()
    encoded = le.fit_transform(signal_values)
    reverse_map = {i: label for i, label in enumerate(le.classes_)}
    logger.debug(f"Label encoding: {reverse_map}")
    return encoded, reverse_map


def _serialize_numpy(obj: Any) -> Any:
    """Convert numpy types to JSON-serializable Python types."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: _serialize_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_serialize_numpy(item) for item in obj]
    return obj


def serialize_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert all numpy types in metrics dict to JSON-serializable values.

    Args:
        metrics: Metrics dict (may contain numpy types)

    Returns:
        Sanitized dict safe for JSON serialization
    """
    return _serialize_numpy(metrics)


def train_models_per_underlying(df: pd.DataFrame, config: TrainingConfig) -> Dict[str, Any]:
    """
    Train per-underlying XGBoost models.

    Args:
        df: Balanced dataset (from Phase 390)
        config: Training configuration

    Returns:
        Dict with keys:
        - 'success': bool
        - 'underlyings_trained': list[str]
        - 'underlyings_skipped': list[str]
        - 'models': {underlying: model_path}
        - 'metrics': {underlying: metrics_dict}
        - 'warnings': list[str]
        - 'config': config dict
    """
    logger.info("=" * 80)
    logger.info("TRAINING PER-UNDERLYING XGBOOST MODELS")
    logger.info("=" * 80)

    result = {
        "success": False,
        "underlyings_trained": [],
        "underlyings_skipped": [],
        "models": {},
        "metrics": {},
        "warnings": [],
        "config": config.to_dict(),
    }

    # Create model directory
    model_dir = Path(config.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"✓ Model directory: {model_dir}")

    # Get unique underlyings
    underlyings = df["underlying"].unique()
    logger.info(f"Found {len(underlyings)} underlyings: {list(underlyings)}")

    # Train per underlying
    for underlying in underlyings:
        try:
            logger.info(f"\n[{underlying}] Starting training...")

            # Filter data for this underlying
            df_underlying = df[df["underlying"] == underlying].copy()
            n_samples = len(df_underlying)

            logger.info(f"  Samples: {n_samples}")

            # Check minimum samples
            if n_samples < config.min_samples_per_underlying:
                msg = f"{underlying} has only {n_samples} samples (min: {config.min_samples_per_underlying})"
                logger.warning(f"  ✗ {msg}")
                result["underlyings_skipped"].append(underlying)
                result["warnings"].append(msg)
                continue

            train_rows, test_rows, feature_cols = point_in_time_split(df_underlying, config.test_size)
            _, label_map = _encode_labels(df_underlying["signal"].values)
            label_to_id = {label: index for index, label in label_map.items()}
            X_train = train_rows[feature_cols].to_numpy()
            X_test = test_rows[feature_cols].to_numpy()
            y_train = train_rows["signal"].map(label_to_id).to_numpy()
            y_test = test_rows["signal"].map(label_to_id).to_numpy()

            logger.info(f"  Features: {len(feature_cols)}")
            logger.info(f"  Target classes: {sorted(label_map.values())}")

            logger.info(f"  Feature matrix shape: {(len(df_underlying), len(feature_cols))}")

            logger.info(f"  Train/Test split: {len(X_train)}/{len(X_test)}")

            # Train model
            if HAS_XGBOOST:
                logger.info(f"  Training XGBClassifier...")
                model = xgb.XGBClassifier(
                    max_depth=config.xgb_max_depth,
                    n_estimators=config.xgb_n_estimators,
                    learning_rate=config.xgb_learning_rate,
                    random_state=config.random_state,
                    verbosity=0,
                    eval_metric="mlogloss",
                )
            else:
                logger.info(f"  XGBoost not available, using GradientBoostingClassifier...")
                model = GradientBoostingClassifier(
                    max_depth=config.xgb_max_depth,
                    n_estimators=config.xgb_n_estimators,
                    learning_rate=config.xgb_learning_rate,
                    random_state=config.random_state,
                    verbose=0,
                )

            model.fit(X_train, y_train)
            logger.info(f"  ✓ Model trained")

            # Evaluate
            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

            logger.info(f"  Accuracy: {accuracy:.4f}")
            logger.info(f"  Macro F1: {macro_f1:.4f}")

            # Per-class metrics
            per_class_report = classification_report(
                y_test,
                y_pred,
                labels=sorted(label_map.keys()),
                target_names=sorted(label_map.values()),
                output_dict=True,
                zero_division=0,
            )

            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)

            # Build metrics dict
            metrics = {
                "underlying": underlying,
                "n_samples": int(n_samples),
                "n_train": int(len(X_train)),
                "n_test": int(len(X_test)),
                "n_train_sessions": int(train_rows["_feature_time"].dt.date.nunique()),
                "n_test_sessions": int(test_rows["_feature_time"].dt.date.nunique()),
                "n_features": int(len(feature_cols)),
                "feature_columns": feature_cols,
                "validation_method": "chronological_purged_holdout",
                "train_end_utc": train_rows["_feature_time"].max().isoformat(),
                "test_start_utc": test_rows["_feature_time"].min().isoformat(),
                "training_rows_sha256": hashlib.sha256(
                    train_rows[["ts", "label_available_at", "signal", *feature_cols]]
                    .to_csv(index=False).encode("utf-8")
                ).hexdigest(),
                "holdout_rows_sha256": hashlib.sha256(
                    test_rows[["ts", "label_available_at", "signal", *feature_cols]]
                    .to_csv(index=False).encode("utf-8")
                ).hexdigest(),
                "accuracy": float(accuracy),
                "macro_f1": float(macro_f1),
                "model_proof_ready": False,
                "ready_for_live": False,
                "accuracy_status": "CHRONOLOGICAL_HOLDOUT_ONLY_NOT_MARKET_PROOF",
                "per_class_metrics": {
                    label: {
                        "precision": float(per_class_report[label]["precision"]),
                        "recall": float(per_class_report[label]["recall"]),
                        "f1_score": float(per_class_report[label]["f1-score"]),
                        "support": int(per_class_report[label]["support"]),
                    }
                    for label in sorted(label_map.values())
                },
                "confusion_matrix": cm.tolist(),
                "label_mapping": label_map,
            }

            # Save model
            model_path = model_dir / f"{underlying}_xgb_model.pkl"
            with open(model_path, "wb") as f:
                pickle.dump(model, f)
            logger.info(f"  ✓ Model saved: {model_path}")

            # Save metadata
            meta_path = model_dir / f"{underlying}_xgb_meta.json"
            with open(meta_path, "w") as f:
                json.dump(serialize_metrics(metrics), f, indent=2)
            logger.info(f"  ✓ Metadata saved: {meta_path}")

            result["underlyings_trained"].append(underlying)
            result["models"][underlying] = str(model_path)
            result["metrics"][underlying] = metrics

        except Exception as e:
            logger.error(f"  ✗ Failed to train {underlying}: {str(e)}")
            result["warnings"].append(f"{underlying} training failed: {str(e)}")

    # Summary
    logger.info(f"\n" + "=" * 80)
    logger.info(f"TRAINING SUMMARY")
    logger.info(f"=" * 80)
    logger.info(f"Trained: {len(result['underlyings_trained'])} underlyings")
    logger.info(f"  {result['underlyings_trained']}")
    logger.info(f"Skipped: {len(result['underlyings_skipped'])} underlyings")
    if result["underlyings_skipped"]:
        logger.info(f"  {result['underlyings_skipped']}")

    if len(result["underlyings_trained"]) > 0:
        result["success"] = True
        logger.info(f"✓ Training COMPLETE - {len(result['underlyings_trained'])} models ready")
    else:
        logger.error(f"✗ Training FAILED - no models trained")

    return result


def main():
    """Example usage."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Load dataset
    df = load_balanced_dataset("storage/datasets/phase_390_balanced_features.csv")

    # Configure training
    config = TrainingConfig(
        test_size=0.2, random_state=42, min_samples_per_underlying=100, model_dir="models/xgboost_v1"
    )

    # Train models
    result = train_models_per_underlying(df, config)

    # Print summary
    print("\n" + "=" * 80)
    print("TRAINING RESULT")
    print("=" * 80)
    print(f"Success: {result['success']}")
    print(f"Trained: {len(result['underlyings_trained'])} underlyings")
    for underlying in result["underlyings_trained"]:
        metrics = result["metrics"][underlying]
        print(f"\n  {underlying}:")
        print(f"    Accuracy: {metrics['accuracy']:.4f}")
        print(f"    Macro F1: {metrics['macro_f1']:.4f}")

    if result["warnings"]:
        print(f"\nWarnings:")
        for w in result["warnings"]:
            print(f"  - {w}")

    print("=" * 80)


if __name__ == "__main__":
    main()
