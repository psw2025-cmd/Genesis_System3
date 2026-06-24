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
from sklearn.model_selection import train_test_split
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

            # Encode signal target
            y = df_underlying["signal"].values
            y_encoded, label_map = _encode_labels(y)

            # Prepare features (all columns except metadata)
            exclude_cols = {"underlying", "strike", "side", "symbol", "ts", "signal"}
            feature_cols = [c for c in df_underlying.columns if c not in exclude_cols]
            X = df_underlying[feature_cols].copy()

            logger.info(f"  Features: {len(feature_cols)}")
            logger.info(f"  Target classes: {sorted(label_map.values())}")

            # Convert all object columns to numeric
            object_cols = X.select_dtypes(include="object").columns
            if len(object_cols) > 0:
                logger.info(f"  Converting {len(object_cols)} object columns to numeric...")
                for col in object_cols:
                    try:
                        X[col] = pd.to_numeric(X[col], errors="coerce")
                    except Exception as e:
                        logger.warning(f"    Could not convert {col}: {str(e)}, dropping column")
                        X.drop(columns=[col], inplace=True)

            # Fill any remaining NaNs with 0
            X = X.fillna(0)
            X = X.values  # Convert to numpy array

            logger.info(f"  Feature matrix shape: {X.shape}")

            # Train/test split (stratified)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=config.test_size, random_state=config.random_state, stratify=y_encoded
            )

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
                "n_features": int(X.shape[1]),
                "accuracy": float(accuracy),
                "macro_f1": float(macro_f1),
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
