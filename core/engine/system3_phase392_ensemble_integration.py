"""
Phase 392 - Ultra + ML + Delta Ensemble Integration
====================================================

Implements three-layer ensemble combining:
  1. Ultra Models (Phases 381-388) → Weight 0.50
  2. XGBoost Models (Phase 391) → Weight 0.40
  3. Delta Fallback Logic → Weight 0.10

Produces normalized ensemble score in range [-1.0, +1.0].

Key Functions:
    - run_phase_392(context: dict | None = None) -> dict
    - ensemble_predict(features, underlying) -> float
    - load_ultra_models() -> dict
    - load_xgboost_models() -> dict

Safety:
    - DRY-RUN ONLY (no trading execution)
    - No broker API calls
    - LIVE_TRADING_ENABLED must remain False
    - Graceful degradation if any model layer fails

Author: System3 AI Team
Date: 2025-12-08
"""

import json
import logging
import os
import pickle
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.engine.ultra_models_loader import load_ultra_model
from model_training_v2 import load_balanced_dataset

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================


@dataclass
class EnsembleConfig:
    """Configuration for ensemble integration."""

    ultra_weight: float = 0.50
    xgboost_weight: float = 0.40
    delta_weight: float = 0.10

    ultra_models_dir: str = "core/models/dhan_ultra"
    xgboost_models_dir: str = "models/xgboost_v1"
    dataset_path: str = "storage/datasets/phase_390_balanced_features.csv"

    output_csv: str = "storage/outputs/phase_392_ensemble_scores_sample.csv"
    output_json: str = "storage/metrics/phase_392_ensemble_report.json"

    random_state: int = 42

    def __post_init__(self):
        """Validate weights sum to 1.0"""
        weight_sum = self.ultra_weight + self.xgboost_weight + self.delta_weight
        if not np.isclose(weight_sum, 1.0):
            raise ValueError(
                f"Ensemble weights must sum to 1.0, got {weight_sum}. "
                f"Ultra: {self.ultra_weight}, XGBoost: {self.xgboost_weight}, Delta: {self.delta_weight}"
            )


# Supported underlyings
SUPPORTED_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


# ============================================================================
# SAFETY & VALIDATION
# ============================================================================


def verify_safety_flags() -> bool:
    """
    Verify that system is in DRY-RUN mode.

    Checks:
        - LIVE_TRADING_ENABLED = False
        - USE_LIVE_EXECUTION_ENGINE = False

    Returns:
        True if safe, raises exception otherwise
    """
    live_trading = os.environ.get("LIVE_TRADING_ENABLED", "False").lower() == "true"
    live_execution = os.environ.get("USE_LIVE_EXECUTION_ENGINE", "False").lower() == "true"

    if live_trading or live_execution:
        raise RuntimeError(
            f"Phase 392 SAFETY CHECK FAILED: "
            f"LIVE_TRADING_ENABLED={live_trading}, "
            f"USE_LIVE_EXECUTION_ENGINE={live_execution}. "
            f"Phase 392 is DRY-RUN ONLY."
        )

    logger.info("✓ Safety flags verified (DRY-RUN mode)")
    return True


# ============================================================================
# MODEL LOADING
# ============================================================================


def load_ultra_models() -> Dict[str, Any]:
    """
    Load all available Ultra models (one per underlying).

    Returns:
        {
            "NIFTY": model_object | None,
            "BANKNIFTY": model_object | None,
            ...
        }

    Note:
        Returns None for missing models (enables delta fallback).
    """
    models = {}

    for underlying in SUPPORTED_UNDERLYINGS:
        model = load_ultra_model(underlying)
        models[underlying] = model
        status = "✓ LOADED" if model else "✗ NOT_FOUND (will use delta fallback)"
        logger.info(f"  Ultra Model {underlying}: {status}")

    return models


def load_xgboost_models(config: EnsembleConfig) -> Dict[str, Any]:
    """
    Load all XGBoost models trained in Phase 391.

    Args:
        config: EnsembleConfig with xgboost_models_dir

    Returns:
        {
            "NIFTY": {"model": model_object, "metadata": dict},
            "BANKNIFTY": ...,
            ...
        }

    Raises:
        FileNotFoundError if any XGBoost model is missing
    """
    models_dir = Path(project_root) / config.xgboost_models_dir
    models = {}

    for underlying in SUPPORTED_UNDERLYINGS:
        model_path = models_dir / f"{underlying}_xgb_model.pkl"
        meta_path = models_dir / f"{underlying}_xgb_meta.json"

        if not model_path.exists():
            raise FileNotFoundError(f"XGBoost model missing for {underlying}: {model_path}")

        # Load model
        try:
            with open(model_path, "rb") as f:
                # Loads only locally-trained artifacts from models_dir, never
                # externally-supplied or user-uploaded data.
                model = pickle.load(f)  # nosec B301
            logger.info(f"  XGBoost Model {underlying}: ✓ LOADED")
        except Exception as e:
            raise RuntimeError(f"Failed to load XGBoost model for {underlying}: {e}")

        # Load metadata
        metadata = {}
        if meta_path.exists():
            try:
                with open(meta_path, "r") as f:
                    metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load metadata for {underlying}: {e}")

        models[underlying] = {"model": model, "metadata": metadata}

    return models


# ============================================================================
# ENSEMBLE SCORING
# ============================================================================


def delta_fallback_score(features: np.ndarray) -> float:
    """
    Delta-based fallback scoring logic.

    Simple heuristic when Ultra/XGBoost models unavailable:
    - Sums numerical features and normalizes to [-1, 1]
    - Always returns a valid score

    Args:
        features: numpy array of feature values

    Returns:
        float in range [-1.0, +1.0]
    """
    try:
        # Remove NaNs and Infs
        clean = features[~np.isnan(features) & ~np.isinf(features)]

        if len(clean) == 0:
            return 0.0

        # Sum and normalize
        score = np.sum(clean) / (len(clean) + 1.0)

        # Clip to [-1, 1]
        score = np.clip(score, -1.0, 1.0)

        return float(score)
    except Exception as e:
        logger.warning(f"Delta fallback computation failed: {e}, returning 0.0")
        return 0.0


def get_model_score(model: Any, features: np.ndarray) -> Optional[float]:
    """
    Get prediction score from a single model.

    Tries predict_proba for classification, falls back to predict.

    Args:
        model: sklearn/xgboost model object
        features: 1D numpy array of feature values (reshaped to 2D)

    Returns:
        float score or None if prediction fails
    """
    try:
        features_2d = features.reshape(1, -1)

        # Try predict_proba (for classifiers)
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(features_2d)
            # Return probability of positive class (usually index 1 or 2)
            if proba.shape[1] > 1:
                return float(proba[0, 1])  # BUY or SELL probability
            else:
                return float(proba[0, 0])

        # Try predict (for regressors)
        elif hasattr(model, "predict"):
            pred = model.predict(features_2d)
            return float(pred[0]) if len(pred) > 0 else None

        else:
            logger.warning(f"Model has no predict_proba or predict method")
            return None

    except Exception as e:
        logger.warning(f"Model scoring failed: {e}")
        return None


def normalize_score(score: float) -> float:
    """
    Normalize score to [-1.0, +1.0] range.

    Assumes input is in [0, 1] (probability) and maps to [-1, 1].
    Formula: 2 * score - 1

    Args:
        score: float in [0, 1] or unbounded

    Returns:
        float in [-1.0, +1.0]
    """
    if np.isnan(score) or np.isinf(score):
        return 0.0

    # Clip to [0, 1] if needed
    score = np.clip(score, 0.0, 1.0)

    # Map [0, 1] -> [-1, 1]
    normalized = 2.0 * score - 1.0

    return float(normalized)


def ensemble_predict(
    features: np.ndarray,
    underlying: str,
    ultra_models: Dict[str, Any],
    xgboost_models: Dict[str, Any],
    config: EnsembleConfig,
) -> float:
    """
    Compute ensemble score using three-layer weighting.

    Weighting:
        - Ultra Model: 0.50
        - XGBoost Model: 0.40
        - Delta Fallback: 0.10

    Normalization:
        - Final score bounded to [-1.0, +1.0]
        - Handles NaN/Inf gracefully

    Args:
        features: numpy array of feature values
        underlying: "NIFTY", "BANKNIFTY", etc.
        ultra_models: loaded Ultra models dict
        xgboost_models: loaded XGBoost models dict
        config: EnsembleConfig

    Returns:
        float ensemble score in [-1.0, +1.0]
    """
    scores = []
    weights = []

    # ---- LAYER 1: Ultra Model (50% weight) ----
    ultra_model = ultra_models.get(underlying)
    if ultra_model:
        ultra_score = get_model_score(ultra_model, features)
        if ultra_score is not None:
            scores.append(normalize_score(ultra_score))
            weights.append(config.ultra_weight)
            logger.debug(f"  Ultra {underlying}: {ultra_score:.4f}")

    # ---- LAYER 2: XGBoost Model (40% weight) ----
    xgb_entry = xgboost_models.get(underlying)
    if xgb_entry:
        xgb_model = xgb_entry["model"]
        xgb_score = get_model_score(xgb_model, features)
        if xgb_score is not None:
            scores.append(normalize_score(xgb_score))
            weights.append(config.xgboost_weight)
            logger.debug(f"  XGBoost {underlying}: {xgb_score:.4f}")

    # ---- LAYER 3: Delta Fallback (10% weight) ----
    delta_score = delta_fallback_score(features)
    scores.append(normalize_score(delta_score))
    weights.append(config.delta_weight)
    logger.debug(f"  Delta {underlying}: {delta_score:.4f}")

    # ---- WEIGHTED ENSEMBLE ----
    if len(scores) == 0:
        logger.warning(f"No scores available for {underlying}, returning 0.0")
        return 0.0

    # Normalize weights to sum to 1.0 (in case some layers missing)
    weights = np.array(weights)
    weights = weights / weights.sum()

    # Compute weighted average
    ensemble_score = np.average(scores, weights=weights)

    # Ensure bounded
    ensemble_score = np.clip(ensemble_score, -1.0, 1.0)

    return float(ensemble_score)


# ============================================================================
# PHASE 392 MAIN EXECUTION
# ============================================================================


def run_phase_392(context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute Phase 392: Ensemble Integration.

    Workflow:
        1. Verify safety flags (DRY-RUN mode)
        2. Load Ultra and XGBoost models
        3. Load Phase 390 balanced dataset
        4. Compute ensemble scores for all rows
        5. Generate output CSV and metrics JSON
        6. Return summary with validation results

    Args:
        context: Optional execution context (unused, for API compatibility)

    Returns:
        {
            "status": "SUCCESS" | "FAILED",
            "phase": 392,
            "name": "Ensemble Integration",
            "timestamp": "2025-12-08 14:23:45",
            "safety_verified": True,
            "models_loaded": {
                "ultra": 5,
                "xgboost": 5
            },
            "scores_computed": {
                "total_rows": 3582,
                "valid_scores": 3582,
                "failed_scores": 0
            },
            "score_stats": {
                "mean": 0.125,
                "std": 0.234,
                "min": -1.0,
                "max": 0.998,
                "nan_count": 0,
                "inf_count": 0
            },
            "output_files": {
                "csv": "storage/outputs/phase_392_ensemble_scores_sample.csv",
                "json": "storage/metrics/phase_392_ensemble_report.json"
            },
            "per_underlying": {
                "NIFTY": {"score_mean": 0.14, "score_std": 0.23},
                ...
            },
            "duration_ms": 1234
        }
    """
    start_time = datetime.now()

    try:
        # ---- STEP 1: Safety Verification ----
        logger.info("=" * 80)
        logger.info("PHASE 392: ENSEMBLE INTEGRATION")
        logger.info("=" * 80)
        logger.info("\nSTEP 1: Verifying safety flags...")

        verify_safety_flags()

        # ---- STEP 2: Load Models ----
        logger.info("\nSTEP 2: Loading Ultra models...")
        config = EnsembleConfig()
        ultra_models = load_ultra_models()

        logger.info("\nSTEP 2b: Loading XGBoost models...")
        xgboost_models = load_xgboost_models(config)

        # ---- STEP 3: Load Dataset ----
        logger.info("\nSTEP 3: Loading Phase 390 balanced dataset...")
        dataset_path = Path(project_root) / config.dataset_path

        if not dataset_path.exists():
            raise FileNotFoundError(f"Phase 390 dataset not found: {dataset_path}")

        df = pd.read_csv(dataset_path)
        logger.info(f"  ✓ Loaded {len(df)} rows × {len(df.columns)} columns")

        # ---- STEP 4: Compute Ensemble Scores ----
        logger.info("\nSTEP 4: Computing ensemble scores...")

        ensemble_results = []
        failed_count = 0
        per_underlying_stats = {u: {"scores": []} for u in SUPPORTED_UNDERLYINGS}

        for idx, row in df.iterrows():
            try:
                underlying = row.get("underlying", "UNKNOWN")

                # Extract features (skip non-numeric columns and known string columns)
                skip_cols = ["underlying", "signal", "side", "strike", "side_long", "expiry", "symbol"]
                feature_cols = [c for c in df.columns if c not in skip_cols]

                # Build feature array with error handling
                features = []
                for col in feature_cols:
                    try:
                        val = float(row[col])
                        features.append(val)
                    except (ValueError, TypeError):
                        # Skip non-numeric columns
                        pass

                if len(features) == 0:
                    failed_count += 1
                    continue

                features = np.array(features)

                # Handle NaNs
                features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)

                # Compute ensemble score
                score = ensemble_predict(features, underlying, ultra_models, xgboost_models, config)

                ensemble_results.append(
                    {
                        "index": idx,
                        "underlying": underlying,
                        "ensemble_score": score,
                        "signal": row.get("signal", "UNKNOWN"),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                if underlying in per_underlying_stats:
                    per_underlying_stats[underlying]["scores"].append(score)

            except Exception as e:
                logger.warning(f"Row {idx}: {e}")
                failed_count += 1

        valid_count = len(ensemble_results)
        logger.info(f"  ✓ Computed {valid_count} scores ({failed_count} failed)")

        # ---- STEP 5: Generate Outputs ----
        logger.info("\nSTEP 5: Generating output files...")

        # Create output directories
        output_dir = Path(project_root) / "storage" / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        metrics_dir = Path(project_root) / "storage" / "metrics"
        metrics_dir.mkdir(parents=True, exist_ok=True)

        # Write ensemble scores CSV
        results_df = pd.DataFrame(ensemble_results)
        csv_path = output_dir / "phase_392_ensemble_scores_sample.csv"
        results_df.to_csv(csv_path, index=False)
        logger.info(f"  ✓ Ensemble scores CSV: {csv_path}")

        # Compute score statistics
        scores = [r["ensemble_score"] for r in ensemble_results]
        score_stats = {
            "mean": float(np.mean(scores)),
            "std": float(np.std(scores)),
            "min": float(np.min(scores)),
            "max": float(np.max(scores)),
            "median": float(np.median(scores)),
            "q25": float(np.percentile(scores, 25)),
            "q75": float(np.percentile(scores, 75)),
            "nan_count": int(np.isnan(scores).sum()),
            "inf_count": int(np.isinf(scores).sum()),
        }

        # Compute per-underlying stats
        per_underlying = {}
        for underlying, stats_dict in per_underlying_stats.items():
            if stats_dict["scores"]:
                scores_array = np.array(stats_dict["scores"])
                per_underlying[underlying] = {
                    "score_count": len(scores_array),
                    "score_mean": float(np.mean(scores_array)),
                    "score_std": float(np.std(scores_array)),
                    "score_min": float(np.min(scores_array)),
                    "score_max": float(np.max(scores_array)),
                }

        # Write metrics JSON
        metrics = {
            "status": "SUCCESS",
            "phase": 392,
            "name": "Ensemble Integration",
            "timestamp": datetime.now().isoformat(),
            "safety_verified": True,
            "models_loaded": {
                "ultra": sum(1 for m in ultra_models.values() if m),
                "xgboost": len(xgboost_models),
                "total": 2,  # 2 model types
            },
            "scores_computed": {"total_rows": len(df), "valid_scores": valid_count, "failed_scores": failed_count},
            "score_stats": score_stats,
            "per_underlying": per_underlying,
            "ensemble_config": {
                "ultra_weight": config.ultra_weight,
                "xgboost_weight": config.xgboost_weight,
                "delta_weight": config.delta_weight,
                "score_range": [-1.0, 1.0],
            },
        }

        json_path = metrics_dir / "phase_392_ensemble_report.json"
        with open(json_path, "w") as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"  ✓ Ensemble metrics JSON: {json_path}")

        # ---- STEP 6: Summary ----
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        logger.info("\n" + "=" * 80)
        logger.info("PHASE 392 EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Status: SUCCESS")
        logger.info(f"Scores computed: {valid_count}/{len(df)}")
        logger.info(f"Score range: [{score_stats['min']:.4f}, {score_stats['max']:.4f}]")
        logger.info(f"Score mean: {score_stats['mean']:.4f}")
        logger.info(f"Duration: {duration_ms} ms")
        logger.info("=" * 80)

        metrics["output_files"] = {"csv": str(csv_path), "json": str(json_path)}
        metrics["duration_ms"] = duration_ms

        return metrics

    except Exception as e:
        logger.error(f"Phase 392 FAILED: {e}", exc_info=True)

        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        return {
            "status": "FAILED",
            "phase": 392,
            "name": "Ensemble Integration",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "duration_ms": duration_ms,
        }


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    result = run_phase_392()

    print("\n" + "=" * 80)
    print("PHASE 392 RESULT")
    print("=" * 80)
    print(json.dumps(result, indent=2))
