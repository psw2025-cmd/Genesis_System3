"""
Phase 391 - XGBoost Model Training per Underlying
==================================================

Trains per-underlying XGBoost classifiers on balanced Phase 390 dataset.
Outputs models, metrics, and feature importance rankings.

Uses model_training_v2.py as core trainer. Handles safety verification,
data loading, per-underlying model training, and metrics generation.

Key Functions:
    - run_phase_391(context: dict | None = None) -> dict
    - Integrates with model_training_v2.train_models_per_underlying()
    - Saves models to models/xgboost_v1/
    - Generates metrics JSON: storage/metrics/phase_391_xgb_metrics.json

Author: System3 AI Team
Date: 2025-12-08
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from model_training_v2 import (
    TrainingConfig,
    load_balanced_dataset,
    serialize_metrics,
    train_models_per_underlying,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============================================================================
# SAFETY & VALIDATION
# ============================================================================


def verify_safety_flags() -> bool:
    """Verify DRY-RUN safety before execution."""
    logger.info("\n[SAFETY CHECK]")

    checks = [
        ("LIVE_TRADING_ENABLED", "False"),
        ("USE_LIVE_EXECUTION_ENGINE", "False"),
    ]

    for env_var, expected_val in checks:
        actual_val = os.environ.get(env_var, expected_val)
        if actual_val.lower() != expected_val.lower():
            logger.error(f"  [FAIL] {env_var}={actual_val} (expected {expected_val})")
            return False

    logger.info(f"  [OK] All safety flags verified (DRY-RUN mode)")
    return True


# ============================================================================
# MAIN PHASE 391 EXECUTION
# ============================================================================


def run_phase_391(context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute Phase 391: XGBoost Model Training per Underlying.

    Uses model_training_v2.py as core trainer. Handles:
    - Safety verification
    - Data loading from Phase 390 output
    - Per-underlying model training
    - Metrics aggregation and JSON output

    Args:
        context: Optional context dict (reserved for future use)

    Returns:
        dict: Execution result with keys:
        - phase: int (391)
        - success: bool
        - status: str ('complete', 'error', 'pending')
        - underlyings_trained: list[str]
        - underlyings_skipped: list[str]
        - metrics_path: str
        - model_dir: str
        - message: str
        - duration_ms: int
        - warnings: list[str]
    """

    phase_start = datetime.now()
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 391 - XGBOOST MODEL TRAINING")
    logger.info("=" * 80)

    result = {
        "phase": 391,
        "success": False,
        "status": "pending",
        "underlyings_trained": [],
        "underlyings_skipped": [],
        "metrics_path": None,
        "model_dir": None,
        "message": "",
        "duration_ms": None,
        "warnings": [],
    }

    try:
        # ===== SAFETY CHECK =====
        if not verify_safety_flags():
            result["status"] = "error"
            result["message"] = "Safety check failed: DRY-RUN flags not set correctly"
            logger.error(result["message"])
            return result

        # ===== LOAD BALANCED DATASET =====
        logger.info("\n[STEP 1] Loading Phase 390 balanced dataset...")
        csv_path = "storage/datasets/phase_390_balanced_features.csv"
        df = load_balanced_dataset(csv_path)
        logger.info(f"  [OK] Loaded {len(df)} rows × {len(df.columns)} columns")

        # Verify target column and underlyings
        if "signal" not in df.columns:
            raise ValueError("Target column 'signal' not found in dataset")
        if "underlying" not in df.columns:
            raise ValueError("Underlying identifier column 'underlying' not found")

        logger.info(f"  [OK] Classes: {sorted(df['signal'].unique())}")
        logger.info(f"  [OK] Underlyings: {sorted(df['underlying'].unique())}")

        # ===== CONFIGURE TRAINING =====
        logger.info("\n[STEP 2] Configuring model training...")
        config = TrainingConfig(
            test_size=0.2,
            random_state=42,
            min_samples_per_underlying=100,
            model_dir="models/xgboost_v1",
            xgb_max_depth=6,
            xgb_n_estimators=100,
            xgb_learning_rate=0.1,
        )
        logger.info(f"  [OK] Config: test_size={config.test_size}, random_state={config.random_state}")

        # ===== TRAIN MODELS =====
        logger.info("\n[STEP 3] Training per-underlying models...")
        training_result = train_models_per_underlying(df, config)

        result["success"] = training_result["success"]
        result["underlyings_trained"] = training_result["underlyings_trained"]
        result["underlyings_skipped"] = training_result["underlyings_skipped"]
        result["model_dir"] = config.model_dir
        result["warnings"] = training_result["warnings"]

        # ===== SAVE METRICS JSON =====
        logger.info("\n[STEP 4] Saving metrics JSON...")

        metrics_output_dir = Path("storage/metrics")
        metrics_output_dir.mkdir(parents=True, exist_ok=True)
        metrics_path = metrics_output_dir / "phase_391_xgb_metrics.json"

        # Aggregate metrics
        aggregated_metrics = {
            "phase": 391,
            "status": "complete" if result["success"] else "error",
            "timestamp": phase_start.isoformat(),
            "underlyings_trained": result["underlyings_trained"],
            "underlyings_skipped": result["underlyings_skipped"],
            "config": config.to_dict(),
            "warnings": result["warnings"],
            "per_underlying_metrics": {},
        }

        # Add metrics for each trained underlying
        for underlying, metrics in training_result["metrics"].items():
            aggregated_metrics["per_underlying_metrics"][underlying] = serialize_metrics(metrics)

        # Write JSON
        with open(metrics_path, "w") as f:
            json.dump(aggregated_metrics, f, indent=2)

        logger.info(f"  [OK] Metrics saved: {metrics_path}")
        result["metrics_path"] = str(metrics_path)

        # ===== COMPLETION =====
        phase_end = datetime.now()
        duration_ms = int((phase_end - phase_start).total_seconds() * 1000)

        result["status"] = "complete" if result["success"] else "error"
        result["duration_ms"] = duration_ms

        if result["success"]:
            result["message"] = (
                f"Phase 391 complete: {len(result['underlyings_trained'])} models trained in {duration_ms}ms"
            )
        else:
            result["message"] = f"Phase 391 error: no models trained (skipped: {result['underlyings_skipped']})"

        # ===== SUMMARY LOGGING =====
        logger.info(f"\n{'='*80}")
        logger.info(f"PHASE 391 SUMMARY")
        logger.info(f"  Status: {result['status'].upper()}")
        logger.info(f"  Models trained: {len(result['underlyings_trained'])} - {result['underlyings_trained']}")
        logger.info(f"  Models skipped: {len(result['underlyings_skipped'])} - {result['underlyings_skipped']}")

        if result["underlyings_trained"]:
            logger.info(f"  Per-underlying metrics:")
            for underlying in result["underlyings_trained"]:
                metrics = training_result["metrics"][underlying]
                logger.info(f"    {underlying}: accuracy={metrics['accuracy']:.4f}, macro_f1={metrics['macro_f1']:.4f}")

        if result["warnings"]:
            logger.info(f"  Warnings:")
            for w in result["warnings"]:
                logger.info(f"    - {w}")

        logger.info(f"  Duration: {duration_ms}ms")
        logger.info(f"{'='*80}\n")

        return result

    except Exception as e:
        logger.error(f"[FAIL] Phase 391 failed: {str(e)}", exc_info=True)
        phase_end = datetime.now()
        duration_ms = int((phase_end - phase_start).total_seconds() * 1000)

        result["status"] = "error"
        result["success"] = False
        result["message"] = f"Phase 391 error: {str(e)}"
        result["duration_ms"] = duration_ms
        return result


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    result = run_phase_391()

    # Print summary
    print("\n" + "=" * 80)
    print("PHASE 391 RESULT")
    print("=" * 80)
    print(f"Status: {result['status'].upper()}")
    print(f"Message: {result['message']}")

    if result["success"]:
        print(f"\nModels trained ({len(result['underlyings_trained'])}):")
        for underlying in result["underlyings_trained"]:
            print(f"  - {underlying}")

        if result["underlyings_skipped"]:
            print(f"\nModels skipped ({len(result['underlyings_skipped'])}):")
            for underlying in result["underlyings_skipped"]:
                print(f"  - {underlying}")

    print(f"\nDuration: {result.get('duration_ms', 'N/A')} ms")
    print(f"Metrics: {result['metrics_path']}")
    print(f"Models: {result['model_dir']}")
    print("=" * 80 + "\n")

    sys.exit(0 if result["success"] else 1)
