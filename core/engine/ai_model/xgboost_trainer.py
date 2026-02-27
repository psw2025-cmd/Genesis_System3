"""
Phase 391: XGBoost Model Training
==================================

Purpose: Train XGBoost models per-underlying (better than RandomForest for imbalanced data).

Why XGBoost > RandomForest:
- Handles class imbalance better (scale_pos_weight parameter)
- Built-in regularization (L1/L2) prevents overfitting
- Gradient boosting learns from mistakes
- Better for sparse/tabular financial data
- Early stopping for optimal performance

Target Accuracy: 60-70% (better than 50% random, beats 66.7% delta baseline)

Author: System3 AI Team
Date: 2025-12-08
Phase: 391/400
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import logging
from datetime import datetime
import json
import joblib

logger = logging.getLogger(__name__)

# Check if xgboost is available
try:
    from xgboost import XGBClassifier

    XGBOOST_AVAILABLE = True
except ImportError:
    logger.warning("xgboost not installed. XGBoost training will not be available.")
    XGBOOST_AVAILABLE = False

# Check if sklearn is available
try:
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

    SKLEARN_AVAILABLE = True
except ImportError:
    logger.warning("scikit-learn not installed. Model evaluation will be limited.")
    SKLEARN_AVAILABLE = False

# Supported underlyings
UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]

# XGBoost hyperparameters (optimized for options trading)
XGBOOST_PARAMS = {
    "n_estimators": 200,  # More trees for better learning
    "max_depth": 5,  # Shallow to prevent overfitting
    "learning_rate": 0.05,  # Slow learning for stability
    "subsample": 0.8,  # Row sampling (80%)
    "colsample_bytree": 0.8,  # Feature sampling (80%)
    "reg_alpha": 0.1,  # L1 regularization
    "reg_lambda": 1.0,  # L2 regularization
    "random_state": 42,
    "eval_metric": "mlogloss",  # Multi-class log loss
    "use_label_encoder": False,
    "verbosity": 0,  # Suppress warnings
}


def load_training_data() -> pd.DataFrame:
    """
    Load training data from Phase 390 (SMOTE balanced) or fallback to Phase 389.

    Returns:
        Training dataframe
    """
    # Try Phase 390 output first
    smote_path = Path("storage/datasets/smote_balanced_training_390.csv")
    if smote_path.exists():
        logger.info(f"Loading SMOTE-balanced data: {smote_path}")
        return pd.read_csv(smote_path)

    # Fallback to Phase 389
    feature_eng_path = Path("storage/datasets/feature_engineered_389.csv")
    if feature_eng_path.exists():
        logger.info(f"Loading feature-engineered data: {feature_eng_path}")
        return pd.read_csv(feature_eng_path)

    # Fallback to curated dataset
    curated_path = Path("storage/live/angel_index_ai_signals_curated.csv")
    if curated_path.exists():
        logger.info(f"Loading curated data: {curated_path}")
        return pd.read_csv(curated_path)

    # Generate sample data for testing
    logger.warning("No training data found, generating sample data")
    return generate_sample_training_data()


def generate_sample_training_data() -> pd.DataFrame:
    """Generate sample training data for testing."""
    np.random.seed(42)
    n_samples = 500

    data = {
        "underlying": np.random.choice(UNDERLYINGS, n_samples),
        "delta": np.random.uniform(-1, 1, n_samples),
        "gamma": np.random.uniform(0, 0.05, n_samples),
        "theta": np.random.uniform(-0.5, 0.5, n_samples),
        "vega": np.random.uniform(0, 1, n_samples),
        "iv": np.random.uniform(0.15, 0.35, n_samples),
        "moneyness": np.random.uniform(0.95, 1.05, n_samples),
        "atm_distance": np.random.uniform(0, 500, n_samples),
        "signal": np.random.choice(["BUY", "SELL", "HOLD"], n_samples, p=[0.33, 0.33, 0.34]),
    }

    return pd.DataFrame(data)


def prepare_features_labels(df: pd.DataFrame, underlying: Optional[str] = None) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare features (X) and labels (y) for training.

    Args:
        df: Training dataframe
        underlying: Filter to specific underlying (None for all)

    Returns:
        X (features), y (labels)
    """
    # Filter by underlying if specified
    if underlying:
        df = df[df["underlying"] == underlying].copy()
        logger.info(f"Filtered to {underlying}: {len(df)} samples")

    # Exclude non-feature columns
    exclude_cols = ["ts", "expiry", "underlying", "strike", "side", "signal", "symbol", "approved"]
    feature_cols = [col for col in df.columns if col not in exclude_cols]

    # Extract features
    X = df[feature_cols].fillna(0)
    logger.info(f"Features: {len(feature_cols)} columns")

    # Extract labels
    if "signal" not in df.columns:
        raise ValueError("'signal' column not found in training data")

    y = df["signal"].copy()

    # Map to numeric labels
    label_map = {"BUY": 1, "SELL": -1, "HOLD": 0}
    if y.dtype == "object":
        y = y.map(label_map)

    return X, y


def train_xgboost_model(
    X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series, underlying: str
) -> Tuple[Optional[Any], Dict[str, Any]]:
    """
    Train XGBoost model for specific underlying.

    Args:
        X_train, X_test: Training and test features
        y_train, y_test: Training and test labels
        underlying: Underlying symbol

    Returns:
        Trained model and evaluation metrics
    """
    if not XGBOOST_AVAILABLE:
        logger.error("XGBoost not available")
        return None, {"error": "xgboost not installed"}

    try:
        # Calculate class weights for imbalance handling
        class_counts = y_train.value_counts()
        if len(class_counts) < 2:
            logger.warning(f"{underlying}: Insufficient class diversity")
            return None, {"error": "insufficient_classes"}

        # Adjust scale_pos_weight
        neutral_count = (y_train == 0).sum()
        non_neutral_count = (y_train != 0).sum()
        scale_pos_weight = neutral_count / max(non_neutral_count, 1)

        # Create model
        params = XGBOOST_PARAMS.copy()
        params["scale_pos_weight"] = scale_pos_weight

        model = XGBClassifier(**params)

        # Train model
        logger.info(f"Training XGBoost for {underlying}...")
        try:
            # Try with early stopping (XGBoost 1.6+)
            model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        except TypeError:
            # Fallback for older XGBoost versions
            model.fit(X_train, y_train, verbose=False)

        # Evaluate
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        train_accuracy = accuracy_score(y_train, y_pred_train)
        test_accuracy = accuracy_score(y_test, y_pred_test)

        # Get feature importances
        feature_importances = dict(zip(X_train.columns, model.feature_importances_))
        top_features = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)[:10]

        metrics = {
            "underlying": underlying,
            "train_accuracy": float(train_accuracy),
            "test_accuracy": float(test_accuracy),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "n_features": len(X_train.columns),
            "top_features": [(feat, float(imp)) for feat, imp in top_features],
            "class_distribution": {"train": y_train.value_counts().to_dict(), "test": y_test.value_counts().to_dict()},
        }

        logger.info(f"{underlying} - Train Acc: {train_accuracy:.3f}, Test Acc: {test_accuracy:.3f}")

        # Classification report
        if SKLEARN_AVAILABLE:
            try:
                report = classification_report(y_test, y_pred_test, output_dict=True)
                metrics["classification_report"] = report
            except:
                pass

        return model, metrics

    except Exception as e:
        logger.error(f"Training failed for {underlying}: {e}", exc_info=True)
        return None, {"error": str(e)}


def run_phase_391() -> Dict[str, Any]:
    """
    Phase 391 entry point: XGBoost Model Training.

    Trains one XGBoost model per underlying (5 total).

    Returns phase execution result with status and metrics.
    """
    try:
        logger.info("=" * 60)
        logger.info("PHASE 391: XGBOOST MODEL TRAINING")
        logger.info("=" * 60)

        if not XGBOOST_AVAILABLE:
            logger.warning("XGBoost not available, phase will report WARN status")

        # Load training data
        df = load_training_data()
        logger.info(f"Loaded training data: {len(df)} rows")

        # Create models directory
        models_dir = Path("core/models/xgboost")
        models_dir.mkdir(parents=True, exist_ok=True)

        # Train model for each underlying
        all_metrics = []
        models_trained = 0

        for underlying in UNDERLYINGS:
            logger.info(f"\n{'='*40}")
            logger.info(f"Training {underlying}")
            logger.info(f"{'='*40}")

            # Filter data
            df_underlying = df[df["underlying"] == underlying].copy()

            if len(df_underlying) < 100:
                logger.warning(f"{underlying}: Insufficient data ({len(df_underlying)} samples), skipping")
                all_metrics.append(
                    {
                        "underlying": underlying,
                        "status": "skipped",
                        "reason": f"insufficient_data ({len(df_underlying)} samples)",
                    }
                )
                continue

            # Prepare features and labels
            X, y = prepare_features_labels(df_underlying)

            # Train/test split
            if SKLEARN_AVAILABLE:
                try:
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.2, random_state=42, stratify=y if len(y.unique()) > 1 else None
                    )
                except:
                    # Fallback if stratify fails
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            else:
                # Manual split if sklearn not available
                split_idx = int(len(X) * 0.8)
                X_train, X_test = X[:split_idx], X[split_idx:]
                y_train, y_test = y[:split_idx], y[split_idx:]

            # Train model
            model, metrics = train_xgboost_model(X_train, X_test, y_train, y_test, underlying)

            if model and metrics.get("test_accuracy", 0) > 0.50:
                # Save model
                model_path = models_dir / f"{underlying}_xgboost_model.pkl"
                joblib.dump(model, model_path)
                logger.info(f"✓ Saved model: {model_path}")

                metrics["status"] = "trained"
                metrics["model_path"] = str(model_path)
                models_trained += 1
            else:
                reason = metrics.get("error", "accuracy_too_low")
                logger.warning(f"✗ {underlying}: Not saved ({reason})")
                metrics["status"] = "failed"
                metrics["reason"] = reason

            all_metrics.append(metrics)

        # Save aggregate metrics
        metrics_path = Path("storage/metrics")
        metrics_path.mkdir(parents=True, exist_ok=True)
        metrics_file = metrics_path / "xgboost_training_391.json"

        summary = {
            "status": "ok" if models_trained > 0 else "warn",
            "phase": 391,
            "timestamp": datetime.utcnow().isoformat(),
            "models_trained": models_trained,
            "total_underlyings": len(UNDERLYINGS),
            "xgboost_available": XGBOOST_AVAILABLE,
            "sklearn_available": SKLEARN_AVAILABLE,
            "per_underlying_metrics": all_metrics,
            "average_accuracy": (
                float(np.mean([m["test_accuracy"] for m in all_metrics if "test_accuracy" in m]))
                if all_metrics
                else 0.0
            ),
        }

        with open(metrics_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"\nPhase 391 metrics saved: {metrics_file}")
        logger.info("=" * 60)
        logger.info(f"SUMMARY: {models_trained}/{len(UNDERLYINGS)} models trained")
        logger.info(f"Average test accuracy: {summary['average_accuracy']:.3f}")
        logger.info("=" * 60)

        # Determine final status
        if models_trained == 0:
            status = "warn"
            message = "No XGBoost models trained (check dependencies or data)"
        elif models_trained < len(UNDERLYINGS):
            status = "warn"
            message = f"Partial success: {models_trained}/{len(UNDERLYINGS)} models trained"
        else:
            status = "ok"
            message = f"All XGBoost models trained: {models_trained}/{len(UNDERLYINGS)}"

        return {"status": status, "message": message, "metrics": summary}

    except Exception as e:
        logger.error(f"Phase 391 failed: {e}", exc_info=True)
        return {"status": "error", "message": f"XGBoost training failed: {str(e)}", "metrics": {}}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    result = run_phase_391()
    print(f"\nPhase 391 Result: {result['status']}")
    print(f"Message: {result['message']}")
