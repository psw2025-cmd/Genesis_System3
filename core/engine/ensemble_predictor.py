"""
Phase 392: Ensemble Predictor - UPGRADED
=========================================

Purpose: Combine multiple ML models (5-7 models) into dynamically weighted ensemble.

UPGRADED FEATURES:
- Support for 5-7 models (Ultra, XGBoost, LightGBM, CatBoost, RandomForest, Neural Net, Delta)
- Dynamic weighting based on recent performance
- Performance tracking and automatic weight adjustment
- Enhanced ensemble strategy with confidence-based routing

Ensemble Strategy:
1. Ultra Model - Pre-trained RandomForest per-underlying
2. XGBoost - Gradient boosting
3. LightGBM - Fast gradient boosting (if available)
4. CatBoost - Categorical boosting (if available)
5. RandomForest - Sklearn ensemble (if available)
6. Neural Net - Deep learning model (if available)
7. Delta Fallback - Always works baseline

Dynamic Weighting:
- Weights adjusted based on recent accuracy (rolling window)
- High-performing models get higher weights
- Underperforming models get lower weights or excluded

Routing Logic:
- If any model has high confidence (>0.7), use that model exclusively
- Otherwise, dynamically weighted average of all available models
- Graceful degradation (fallback to available models)

Author: System3 AI Team
Date: 2025-12-08 (Upgraded: 2026-02-22)
Phase: 392/400
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple, List
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque
import logging
import joblib
import json

logger = logging.getLogger(__name__)

# Base model weights (will be adjusted dynamically)
BASE_WEIGHTS = {
    "ultra": 0.25,
    "xgboost": 0.20,
    "lightgbm": 0.15,
    "catboost": 0.15,
    "randomforest": 0.10,
    "neural_net": 0.10,
    "delta": 0.05,
}

# Confidence threshold for exclusive model use
CONFIDENCE_THRESHOLD = 0.7

# Performance tracking window (last N predictions)
PERFORMANCE_WINDOW = 100


class DynamicWeightTracker:
    """Tracks model performance and adjusts weights dynamically."""

    def __init__(self, window_size: int = PERFORMANCE_WINDOW):
        self.window_size = window_size
        self.performance_history: Dict[str, deque] = {}
        self.accuracy_scores: Dict[str, float] = {}
        self.prediction_counts: Dict[str, int] = {}

    def update_performance(self, model_name: str, correct: bool):
        """Update performance tracking for a model."""
        if model_name not in self.performance_history:
            self.performance_history[model_name] = deque(maxlen=self.window_size)
            self.accuracy_scores[model_name] = 0.5  # Default 50%
            self.prediction_counts[model_name] = 0

        self.performance_history[model_name].append(1 if correct else 0)
        self.prediction_counts[model_name] += 1

        # Update accuracy
        if len(self.performance_history[model_name]) > 0:
            self.accuracy_scores[model_name] = np.mean(list(self.performance_history[model_name]))

    def get_dynamic_weights(self, model_names: List[str]) -> Dict[str, float]:
        """Calculate dynamic weights based on recent performance."""
        if not model_names:
            return {}

        # Get accuracies for available models
        accuracies = {}
        for name in model_names:
            if name in self.accuracy_scores:
                accuracies[name] = self.accuracy_scores[name]
            else:
                accuracies[name] = 0.5  # Default for new models

        # Normalize accuracies to weights
        total_accuracy = sum(accuracies.values())
        if total_accuracy > 0:
            weights = {name: acc / total_accuracy for name, acc in accuracies.items()}
        else:
            # Equal weights if no performance data
            weights = {name: 1.0 / len(model_names) for name in model_names}

        # Blend with base weights (70% dynamic, 30% base)
        final_weights = {}
        for name in model_names:
            base_weight = BASE_WEIGHTS.get(name, 0.1)
            dynamic_weight = weights.get(name, 0.1)
            final_weights[name] = 0.7 * dynamic_weight + 0.3 * base_weight

        # Normalize to sum to 1.0
        total = sum(final_weights.values())
        if total > 0:
            final_weights = {name: w / total for name, w in final_weights.items()}

        return final_weights


# Global weight tracker
_weight_tracker = DynamicWeightTracker()


def load_ultra_model(underlying: str) -> Optional[Any]:
    """Load Ultra Model for given underlying."""
    try:
        model_path = Path(f"core/models/angel_one_ultra/{underlying}_ultra_model.pkl")
        if model_path.exists():
            model = joblib.load(model_path)
            logger.debug(f"Loaded Ultra model: {underlying}")
            return model
    except Exception as e:
        logger.warning(f"Failed to load Ultra model for {underlying}: {e}")
    return None


def load_xgboost_model(underlying: str) -> Optional[Any]:
    """Load XGBoost model for given underlying."""
    try:
        model_path = Path(f"core/models/xgboost/{underlying}_xgboost_model.pkl")
        if model_path.exists():
            model = joblib.load(model_path)
            logger.debug(f"Loaded XGBoost model: {underlying}")
            return model
    except Exception as e:
        logger.warning(f"Failed to load XGBoost model for {underlying}: {e}")
    return None


def load_lightgbm_model(underlying: str) -> Optional[Any]:
    """Load LightGBM model for given underlying."""
    try:
        import lightgbm as lgb

        model_path = Path(f"core/models/lightgbm/{underlying}_lightgbm_model.pkl")
        if model_path.exists():
            model = joblib.load(model_path)
            logger.debug(f"Loaded LightGBM model: {underlying}")
            return model
    except ImportError:
        logger.debug("LightGBM not available")
    except Exception as e:
        logger.warning(f"Failed to load LightGBM model for {underlying}: {e}")
    return None


def load_catboost_model(underlying: str) -> Optional[Any]:
    """Load CatBoost model for given underlying."""
    try:
        import catboost as cb

        model_path = Path(f"core/models/catboost/{underlying}_catboost_model.pkl")
        if model_path.exists():
            model = joblib.load(model_path)
            logger.debug(f"Loaded CatBoost model: {underlying}")
            return model
    except ImportError:
        logger.debug("CatBoost not available")
    except Exception as e:
        logger.warning(f"Failed to load CatBoost model for {underlying}: {e}")
    return None


def load_randomforest_model(underlying: str) -> Optional[Any]:
    """Load RandomForest model for given underlying."""
    try:
        from sklearn.ensemble import RandomForestClassifier

        model_path = Path(f"core/models/randomforest/{underlying}_rf_model.pkl")
        if model_path.exists():
            model = joblib.load(model_path)
            logger.debug(f"Loaded RandomForest model: {underlying}")
            return model
    except ImportError:
        logger.debug("Sklearn RandomForest not available")
    except Exception as e:
        logger.warning(f"Failed to load RandomForest model for {underlying}: {e}")
    return None


def load_neural_net_model(underlying: str) -> Optional[Any]:
    """Load Neural Network model for given underlying."""
    try:
        import torch

        model_path = Path(f"core/models/neural_net/{underlying}_nn_model.pkl")
        if model_path.exists():
            model = joblib.load(model_path)
            logger.debug(f"Loaded Neural Net model: {underlying}")
            return model
    except ImportError:
        logger.debug("PyTorch not available")
    except Exception as e:
        logger.warning(f"Failed to load Neural Net model for {underlying}: {e}")
    return None


def compute_delta_scores(df: pd.DataFrame) -> np.ndarray:
    """
    Compute delta-based fallback scores.

    This is the baseline scoring method used when ML models are unavailable.
    Formula: (delta * 2.0 - 1.0).clip(-1.0, 1.0) * 0.3
    """
    if "delta" in df.columns:
        delta_proxy = df["delta"].fillna(0)
        scores = (delta_proxy * 2.0 - 1.0).clip(-1.0, 1.0) * 0.3
        return scores.values
    else:
        # Fallback if delta not available
        return np.zeros(len(df))


def get_model_predictions(model: Any, X: pd.DataFrame, model_type: str) -> Tuple[np.ndarray, float]:
    """
    Get predictions and confidence from a model.

    Args:
        model: Trained model (Ultra or XGBoost)
        X: Feature matrix
        model_type: 'ultra' or 'xgboost'

    Returns:
        scores (array), confidence (float)
    """
    try:
        # Get probability predictions
        probas = model.predict_proba(X)

        # Calculate confidence (max probability across classes)
        confidence = probas.max(axis=1).mean()

        # Convert to scores: BUY prob - SELL prob
        # Assumes classes are ordered [-1, 0, 1] or [SELL, HOLD, BUY]
        if probas.shape[1] == 3:
            # Multi-class: BUY - SELL
            scores = probas[:, 2] - probas[:, 0]
        elif probas.shape[1] == 2:
            # Binary: positive class prob
            scores = probas[:, 1]
        else:
            scores = np.zeros(len(X))

        logger.info(f"{model_type} model: confidence={confidence:.3f}, avg_score={scores.mean():.3f}")

        return scores, confidence

    except Exception as e:
        logger.error(f"Prediction failed for {model_type}: {e}")
        return np.zeros(len(X)), 0.0


def prepare_features_for_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare feature matrix for model prediction.

    Extracts only feature columns and fills missing values.
    """
    # Exclude non-feature columns
    exclude_cols = ["ts", "expiry", "underlying", "strike", "side", "signal", "symbol", "approved", "ai_score"]
    feature_cols = [col for col in df.columns if col not in exclude_cols and df[col].dtype in [np.float64, np.int64]]

    X = df[feature_cols].fillna(0)
    return X


def predict_with_ensemble(
    df: pd.DataFrame,
    underlying: str,
    ultra_model: Optional[Any] = None,
    xgboost_model: Optional[Any] = None,
    use_dynamic_weights: bool = True,
) -> pd.DataFrame:
    """
    Generate ensemble predictions combining 5-7 models with dynamic weighting.

    Args:
        df: Input dataframe with features
        underlying: Underlying symbol
        ultra_model: Pre-loaded Ultra model (optional)
        xgboost_model: Pre-loaded XGBoost model (optional)
        use_dynamic_weights: Whether to use dynamic weight adjustment

    Returns:
        DataFrame with ai_score and ensemble_method columns added
    """
    # Load all available models
    if ultra_model is None:
        ultra_model = load_ultra_model(underlying)
    if xgboost_model is None:
        xgboost_model = load_xgboost_model(underlying)

    lightgbm_model = load_lightgbm_model(underlying)
    catboost_model = load_catboost_model(underlying)
    rf_model = load_randomforest_model(underlying)
    nn_model = load_neural_net_model(underlying)

    # Prepare features
    X = prepare_features_for_prediction(df)

    # Collect model scores and confidences
    model_scores = []
    available_models = []

    # Model 1: Ultra Model
    if ultra_model is not None:
        try:
            ultra_scores, ultra_conf = get_model_predictions(ultra_model, X, "ultra")
            model_scores.append(("ultra", ultra_scores, ultra_conf))
            available_models.append("ultra")
        except Exception as e:
            logger.warning(f"Ultra model prediction failed: {e}")

    # Model 2: XGBoost
    if xgboost_model is not None:
        try:
            xgb_scores, xgb_conf = get_model_predictions(xgboost_model, X, "xgboost")
            model_scores.append(("xgboost", xgb_scores, xgb_conf))
            available_models.append("xgboost")
        except Exception as e:
            logger.warning(f"XGBoost prediction failed: {e}")

    # Model 3: LightGBM
    if lightgbm_model is not None:
        try:
            lgb_scores, lgb_conf = get_model_predictions(lightgbm_model, X, "lightgbm")
            model_scores.append(("lightgbm", lgb_scores, lgb_conf))
            available_models.append("lightgbm")
        except Exception as e:
            logger.warning(f"LightGBM prediction failed: {e}")

    # Model 4: CatBoost
    if catboost_model is not None:
        try:
            cb_scores, cb_conf = get_model_predictions(catboost_model, X, "catboost")
            model_scores.append(("catboost", cb_scores, cb_conf))
            available_models.append("catboost")
        except Exception as e:
            logger.warning(f"CatBoost prediction failed: {e}")

    # Model 5: RandomForest
    if rf_model is not None:
        try:
            rf_scores, rf_conf = get_model_predictions(rf_model, X, "randomforest")
            model_scores.append(("randomforest", rf_scores, rf_conf))
            available_models.append("randomforest")
        except Exception as e:
            logger.warning(f"RandomForest prediction failed: {e}")

    # Model 6: Neural Net
    if nn_model is not None:
        try:
            nn_scores, nn_conf = get_model_predictions(nn_model, X, "neural_net")
            model_scores.append(("neural_net", nn_scores, nn_conf))
            available_models.append("neural_net")
        except Exception as e:
            logger.warning(f"Neural Net prediction failed: {e}")

    # Model 7: Delta Fallback (always available)
    delta_scores = compute_delta_scores(df)
    model_scores.append(("delta", delta_scores, 1.0))
    available_models.append("delta")

    # Get dynamic weights if enabled
    if use_dynamic_weights:
        weights = _weight_tracker.get_dynamic_weights(available_models)
    else:
        # Use base weights
        weights = {name: BASE_WEIGHTS.get(name, 0.1) for name in available_models}
        # Normalize
        total = sum(weights.values())
        if total > 0:
            weights = {name: w / total for name, w in weights.items()}

    # Routing logic: Check for high-confidence model
    ensemble_method = "weighted_average"
    final_scores = np.zeros(len(df))

    # Check if any model (except delta) has high confidence
    for model_name, scores, confidence in model_scores:
        if model_name != "delta" and confidence > CONFIDENCE_THRESHOLD:
            logger.info(f"Using {model_name} exclusively (confidence={confidence:.3f} > {CONFIDENCE_THRESHOLD})")
            final_scores = scores
            ensemble_method = f"{model_name}_confident"
            break

    # If no high-confidence model, use dynamically weighted average
    if ensemble_method == "weighted_average":
        total_weight = sum(weights.get(name, 0.0) for name, _, _ in model_scores)
        for model_name, scores, confidence in model_scores:
            weight = weights.get(model_name, 0.0)
            if total_weight > 0:
                final_scores += (scores * weight) / total_weight

        model_list = ", ".join(available_models)
        logger.info(f"Using dynamically weighted ensemble ({len(model_scores)} models: {model_list})")

    # Clip scores to valid range
    final_scores = np.clip(final_scores, -1.0, 1.0)

    # Add to dataframe
    df = df.copy()
    df["ai_score"] = final_scores
    df["ensemble_method"] = ensemble_method
    df["ensemble_model_count"] = len(model_scores)
    df["ensemble_models_used"] = ",".join(available_models)

    return df


def run_phase_392() -> Dict[str, Any]:
    """
    Phase 392 entry point: Ensemble Predictor.

    Tests ensemble prediction on sample data.

    Returns phase execution result with status and metrics.
    """
    try:
        logger.info("=" * 60)
        logger.info("PHASE 392: ENSEMBLE PREDICTOR")
        logger.info("=" * 60)

        # Generate test data
        test_data = pd.DataFrame(
            {
                "underlying": ["NIFTY"] * 10,
                "delta": np.random.uniform(-1, 1, 10),
                "gamma": np.random.uniform(0, 0.05, 10),
                "theta": np.random.uniform(-0.5, 0.5, 10),
                "vega": np.random.uniform(0, 1, 10),
                "iv": np.random.uniform(0.2, 0.3, 10),
            }
        )

        logger.info("Testing ensemble prediction on sample data...")

        # Test ensemble prediction
        result_df = predict_with_ensemble(test_data, "NIFTY")

        # Collect metrics
        ensemble_methods = result_df["ensemble_method"].value_counts().to_dict()
        avg_score = result_df["ai_score"].mean()
        score_std = result_df["ai_score"].std()

        metrics = {
            "status": "ok",
            "phase": 392,
            "timestamp": pd.Timestamp.now().isoformat(),
            "test_samples": len(result_df),
            "ensemble_methods": ensemble_methods,
            "avg_score": float(avg_score),
            "score_std": float(score_std),
            "score_range": [float(result_df["ai_score"].min()), float(result_df["ai_score"].max())],
        }

        # Check model availability (all 7 model types)
        model_counts = {
            "ultra": 0,
            "xgboost": 0,
            "lightgbm": 0,
            "catboost": 0,
            "randomforest": 0,
            "neural_net": 0,
            "delta": 5,  # Always available for all underlyings
        }

        for underlying in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]:
            if load_ultra_model(underlying) is not None:
                model_counts["ultra"] += 1
            if load_xgboost_model(underlying) is not None:
                model_counts["xgboost"] += 1
            if load_lightgbm_model(underlying) is not None:
                model_counts["lightgbm"] += 1
            if load_catboost_model(underlying) is not None:
                model_counts["catboost"] += 1
            if load_randomforest_model(underlying) is not None:
                model_counts["randomforest"] += 1
            if load_neural_net_model(underlying) is not None:
                model_counts["neural_net"] += 1

        metrics["models_available"] = model_counts
        metrics["total_models"] = sum(1 for v in model_counts.values() if v > 0)

        # Save metrics
        metrics_path = Path("storage/metrics")
        metrics_path.mkdir(parents=True, exist_ok=True)
        metrics_file = metrics_path / "ensemble_performance_392.json"

        import json

        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)

        logger.info(f"Ensemble test complete: {ensemble_methods}")
        logger.info(f"Average score: {avg_score:.3f} ± {score_std:.3f}")
        ultra_available = model_counts.get("ultra", 0) > 0
        xgb_available = model_counts.get("xgboost", 0) > 0
        logger.info(f"Models available - Ultra: {ultra_available}, XGBoost: {xgb_available}")
        logger.info("=" * 60)

        return {
            "status": "ok",
            "message": f"Ensemble predictor functional (Ultra:{ultra_available}, XGB:{xgb_available}, Delta:always)",
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"Phase 392 failed: {e}", exc_info=True)
        return {"status": "error", "message": f"Ensemble predictor failed: {str(e)}", "metrics": {}}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    result = run_phase_392()
    print(f"\nPhase 392 Result: {result['status']}")
    print(f"Message: {result['message']}")
