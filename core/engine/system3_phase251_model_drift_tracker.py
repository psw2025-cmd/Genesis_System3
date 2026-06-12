"""
System3 Phase 251 - Model Drift Tracker

Detect when LSTM model performance degrades and trigger retraining.
Reads Phase 249 Extended evaluation metrics from Phase 250 output.
Shadow-only monitoring - does not impact live trading decisions.

References:
- SPRINT1_DL_SPEC.md (Phase 251 specification)
- Phase 250: Online Learning Manager (metric source)
- Phase 249 Extended: Model Evaluation (evaluation output)
- Phase 252: Model Retraining Scheduler (next phase)

Status: FULLY FUNCTIONAL (wired to Phase 250 JSON evaluation output)
Date: 2025-12-06
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import LSTM utilities for reading Phase 250 output
from core.engine.system3_lstm_utils import (
    read_latest_evaluation_metrics,
    extract_model_metrics,
    compare_to_baseline,
    write_promotion_decision,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Directories
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan"
LOGS_DIR = PROJECT_ROOT / "logs"
STORAGE_DIR = PROJECT_ROOT / "storage" / "live"

# Drift detection thresholds
ACCURACY_THRESHOLD = 0.55  # Alert if < 55% (baseline for profitable models)
BASELINE_ACCURACY = 0.55  # Expected model accuracy baseline
DEGRADATION_THRESHOLD = 0.10  # Alert if drops >10% from baseline
MIN_TEST_SAMPLES = 10  # Minimum test samples for valid evaluation

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def detect_drift_for_underlying(underlying: str, model_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if model performance has degraded based on Phase 250 evaluation metrics.

    Args:
        underlying: Symbol (NIFTY, BANKNIFTY, etc.)
        model_metrics: Model metrics dict from Phase 249 Extended evaluation
                      Should have keys: accuracy, precision, recall, f1_score, test_samples

    Returns:
        Dict with drift detection results:
        {
            'status': 'OK' | 'DRIFT' | 'ERROR',
            'underlying': str,
            'drift_detected': bool,
            'reasons': list[str],
            'metrics': {...},
            'decision': 'PROMOTE' | 'HOLD' | 'REJECT'
        }
    """

    if model_metrics is None:
        return {
            "status": "ERROR",
            "underlying": underlying,
            "drift_detected": False,
            "reasons": ["No evaluation metrics available"],
            "metrics": {},
            "decision": "HOLD",
        }

    # Extract key metrics
    accuracy = model_metrics.get("accuracy")
    precision = model_metrics.get("precision", 0.0)
    recall = model_metrics.get("recall", 0.0)
    f1_score = model_metrics.get("f1_score", 0.0)
    test_samples = model_metrics.get("test_samples", 0)

    # Validate metrics
    if accuracy is None:
        return {
            "status": "ERROR",
            "underlying": underlying,
            "drift_detected": False,
            "reasons": ["Missing accuracy metric"],
            "metrics": model_metrics,
            "decision": "HOLD",
        }

    # Check for drift conditions
    drift_detected = False
    reasons = []

    # Condition 1: Accuracy below threshold
    if accuracy < ACCURACY_THRESHOLD:
        drift_detected = True
        reasons.append(f"Low accuracy: {accuracy:.1%} < {ACCURACY_THRESHOLD:.0%}")

    # Condition 2: Insufficient test samples
    if test_samples < MIN_TEST_SAMPLES:
        drift_detected = True
        reasons.append(f"Insufficient test samples: {test_samples} < {MIN_TEST_SAMPLES}")

    # Condition 3: Precision/Recall severely unbalanced (indicates mode collapse)
    if precision > 0 and recall > 0:
        recall_precision_ratio = min(recall / precision, precision / recall) if (recall + precision) > 0 else 0
        if recall_precision_ratio < 0.3:  # More than 3x difference
            drift_detected = True
            reasons.append(f"Precision/Recall imbalance: P={precision:.1%}, R={recall:.1%}")

    # Decision logic
    if drift_detected:
        decision = "REJECT"  # Do not promote models with detected drift
        logger.warning(f"[PHASE 251] DRIFT DETECTED for {underlying}: {', '.join(reasons)}")
    else:
        decision = "PROMOTE"  # Models pass all drift checks
        logger.info(f"[PHASE 251] {underlying} passes drift detection - ready for promotion")

    return {
        "status": "OK",
        "underlying": underlying,
        "drift_detected": drift_detected,
        "reasons": reasons,
        "metrics": {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1_score),
            "test_samples": int(test_samples),
        },
        "thresholds": {"accuracy_minimum": ACCURACY_THRESHOLD, "min_test_samples": MIN_TEST_SAMPLES},
        "decision": decision,
    }


def run_phase251(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 251: Model Drift Tracker (SHADOW MODEL).

    Pipeline:
    1. Read latest Phase 249 Extended evaluation JSON (from Phase 250 output)
    2. For each underlying, check for accuracy/metric drift
    3. Produce promotion decision JSON for Phase 252
    4. Return phase result

    Returns:
        Dict: Phase execution result with structure:
        {
            'phase': 251,
            'status': 'OK' | 'WARN' | 'ERROR',
            'details': str,
            'outputs': {
                'evaluation_file': str,
                'decision_file': str,
                'results': {...},
                'drift_alerts': [...],
                'promotion_candidates': [...]
            },
            'errors': [...]
        }
    """
    errors = []
    results = {}
    drift_alerts = []
    promotion_candidates = []

    logger.info("=" * 80)
    logger.info("Phase 251: Model Drift Tracker")
    logger.info("=" * 80)

    try:
        # Step 1: Read Phase 249 Extended evaluation metrics
        logger.info("[PHASE 251] Reading Phase 250 evaluation metrics...")
        evaluation_data = read_latest_evaluation_metrics(eval_dir="logs", pattern="phase249_model_evaluation_*.json")

        if evaluation_data is None:
            msg = "No Phase 250 evaluation metrics available; skipping drift detection"
            logger.warning(f"[PHASE 251] {msg}")
            return {
                "phase": 251,
                "status": "WARN",
                "details": msg,
                "outputs": {
                    "evaluation_file": None,
                    "decision_file": None,
                    "results": {},
                    "drift_alerts": [],
                    "promotion_candidates": [],
                },
                "errors": ["No evaluation metrics"],
            }

        logger.info(f"[PHASE 251] ✓ Loaded evaluation data (timestamp: {evaluation_data.get('evaluation_timestamp')})")

        # Step 2: Run drift detection for each underlying
        logger.info("[PHASE 251] Running drift detection for all underlyings...")

        for underlying in UNDERLYINGS:
            logger.info(f"[PHASE 251]   - Checking {underlying}...")

            # Extract metrics for this underlying
            model_metrics = extract_model_metrics(evaluation_data, underlying)

            # Run drift detection
            drift_result = detect_drift_for_underlying(underlying, model_metrics)
            results[underlying] = drift_result

            # Track alerts and candidates
            if drift_result.get("drift_detected"):
                drift_alerts.append(underlying)
                logger.warning(f"[PHASE 251]     ✗ {underlying}: DRIFT DETECTED")
            else:
                if drift_result.get("decision") == "PROMOTE":
                    promotion_candidates.append(underlying)
                    logger.info(f"[PHASE 251]     ✓ {underlying}: Ready for promotion")

        # Step 3: Build promotion decision
        logger.info("[PHASE 251] Building promotion decision...")

        decision = {
            "phase": 251,
            "decision_timestamp": datetime.now().isoformat(),
            "evaluation_source": evaluation_data.get("evaluation_timestamp"),
            "underlyings_checked": len(UNDERLYINGS),
            "drift_alerts": drift_alerts,
            "promotion_candidates": promotion_candidates,
            "results": results,
            "summary": {
                "total_models": len(UNDERLYINGS),
                "drift_detected_count": len(drift_alerts),
                "ready_for_promotion_count": len(promotion_candidates),
                "drift_detected": len(drift_alerts) > 0,
            },
        }

        # Step 4: Write promotion decision JSON (for Phase 252 to read)
        logger.info("[PHASE 251] Writing promotion decision JSON...")
        decision_file = write_promotion_decision(
            decision, decision_dir="logs", filename="phase251_promotion_decision.json"
        )

        if decision_file is None:
            errors.append("Failed to write promotion decision JSON")
            logger.error("[PHASE 251] ✗ Failed to write decision file")
        else:
            logger.info(f"[PHASE 251] ✓ Decision file: {decision_file}")

        # Step 5: Return phase result
        status = "WARN" if drift_alerts else "OK"
        details = f"Evaluated {len(UNDERLYINGS)} models - {len(drift_alerts)} drift alerts, {len(promotion_candidates)} promotion candidates"

        logger.info(f"[PHASE 251] Status: {status}")
        logger.info(f"[PHASE 251] {details}")
        logger.info("[PHASE 251] " + "=" * 80)

        return {
            "phase": 251,
            "status": status,
            "details": details,
            "outputs": {
                "evaluation_file": evaluation_data.get("evaluation_timestamp"),
                "decision_file": str(decision_file) if decision_file else None,
                "results": results,
                "drift_alerts": drift_alerts,
                "promotion_candidates": promotion_candidates,
            },
            "errors": errors,
        }

    except Exception as e:
        error_msg = f"Phase 251 exception: {e}"
        errors.append(error_msg)
        logger.error(f"[PHASE 251] ✗ {error_msg}")

        return {
            "phase": 251,
            "status": "ERROR",
            "details": f"Drift detection failed: {e}",
            "outputs": {},
            "errors": errors,
        }


def main():
    """CLI entry point."""
    result = run_phase251()

    print(f"\n[PHASE 251] Status: {result['status']}")
    print(f"[PHASE 251] Details: {result['details']}")

    if result["outputs"].get("drift_alerts"):
        print(f"[PHASE 251] Drift alerts: {result['outputs']['drift_alerts']}")

    if result["outputs"].get("promotion_candidates"):
        print(f"[PHASE 251] Promotion candidates: {result['outputs']['promotion_candidates']}")

    if result["errors"]:
        print(f"[PHASE 251] Errors: {result['errors']}")


if __name__ == "__main__":
    main()
