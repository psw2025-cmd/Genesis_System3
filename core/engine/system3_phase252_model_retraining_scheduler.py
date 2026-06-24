"""
System3 Phase 252 - Model Retraining Scheduler

Process drift alerts from Phase 251 and schedule full LSTM retraining.
Shadow-only automation - does not impact live trading decisions.

References:
- SPRINT1_DL_SPEC.md (Phase 252 specification)
- Phase 251: Model Drift Tracker (promotion decision source)
- Phase 250: Online Learning Manager (retraining logic)

Status: FULLY FUNCTIONAL (wired to Phase 251 promotion decision JSON)
Date: 2025-12-06
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import LSTM utilities
from core.engine.system3_lstm_utils import read_promotion_decision

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Directories
LOGS_DIR = PROJECT_ROOT / "logs"

# Retraining queue
QUEUE_FILE = LOGS_DIR / "retraining_queue.json"

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def schedule_retraining(underlying: str, trigger: str = "drift_detected") -> Dict[str, Any]:
    """
    Add underlying to retraining queue.

    Args:
        underlying: Symbol to retrain
        trigger: Reason for retraining

    Returns:
        dict with scheduling result
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing queue
    if QUEUE_FILE.exists():
        with QUEUE_FILE.open("r") as f:
            queue = json.load(f)
    else:
        queue = []

    # Check if already queued
    for item in queue:
        if item["underlying"] == underlying and item["status"] == "PENDING":
            return {
                "status": "SKIP",
                "reason": "Already queued for retraining",
            }

    # Add to queue
    queue_item = {
        "underlying": underlying,
        "scheduled_at": datetime.utcnow().isoformat(),
        "trigger": trigger,
        "status": "PENDING",
    }
    queue.append(queue_item)

    # Save queue
    with QUEUE_FILE.open("w") as f:
        json.dump(queue, f, indent=2)

    print(f"[SCHEDULE] {underlying} queued for retraining (trigger: {trigger})")

    return {
        "status": "SUCCESS",
        "underlying": underlying,
        "queue_position": len([q for q in queue if q["status"] == "PENDING"]),
    }


def check_retraining_queue() -> List[Dict[str, Any]]:
    """Get current retraining queue."""
    if not QUEUE_FILE.exists():
        return []

    with QUEUE_FILE.open("r") as f:
        queue = json.load(f)

    return [q for q in queue if q["status"] == "PENDING"]


def run_phase252(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 252: Model Retraining Scheduler (SHADOW MODEL).

    Pipeline:
    1. Read Phase 251 promotion decision JSON
    2. For each drifted model, schedule retraining
    3. Queue retraining jobs (post-market or pre-market execution)
    4. Return phase result

    Returns:
        Dict: Phase execution result with structure:
        {
            'phase': 252,
            'status': 'OK' | 'WARN' | 'ERROR',
            'details': str,
            'outputs': {
                'decision_source': str,
                'drifted_models': [...],
                'scheduled_for_retraining': [...],
                'pending_queue': [...],
                'queue_file': str
            },
            'errors': [...]
        }
    """
    errors = []

    logger.info("=" * 80)
    logger.info("Phase 252: Model Retraining Scheduler")
    logger.info("=" * 80)

    try:
        # Step 1: Read Phase 251 promotion decision
        logger.info("[PHASE 252] Reading Phase 251 promotion decision...")
        decision = read_promotion_decision(decision_dir="logs", filename="phase251_promotion_decision.json")

        if decision is None:
            msg = "No Phase 251 promotion decision available; skipping retraining scheduling"
            logger.warning(f"[PHASE 252] {msg}")
            return {
                "phase": 252,
                "status": "WARN",
                "details": msg,
                "outputs": {
                    "decision_source": None,
                    "drifted_models": [],
                    "scheduled_for_retraining": [],
                    "pending_queue": [],
                    "queue_file": str(QUEUE_FILE),
                },
                "errors": ["No promotion decision"],
            }

        logger.info(f"[PHASE 252] ✓ Loaded promotion decision (timestamp: {decision.get('decision_timestamp')})")

        # Step 2: Process drifted models
        drifted_models = decision.get("drift_alerts", [])
        scheduled = []

        if drifted_models:
            logger.info(f"[PHASE 252] Processing {len(drifted_models)} drifted models...")

            for underlying in drifted_models:
                logger.info(f"[PHASE 252]   - Scheduling {underlying} for retraining...")
                result = schedule_retraining(underlying, trigger="drift_detected")

                if result["status"] == "SUCCESS":
                    scheduled.append(underlying)
                    logger.info(f"[PHASE 252]     ✓ {underlying} queued")
                else:
                    logger.warning(f"[PHASE 252]     ✗ {underlying}: {result.get('reason', 'unknown')}")

        # Step 3: Check current queue status
        pending_queue = check_retraining_queue()
        logger.info(f"[PHASE 252] Retraining queue: {len(pending_queue)} pending jobs")

        # Step 4: Summary
        if scheduled:
            logger.info(f"[PHASE 252] ✓ Scheduled {len(scheduled)} models: {', '.join(scheduled)}")
        else:
            logger.info("[PHASE 252] No drifted models to schedule (all models pass drift checks)")

        # NOTE: Actual retraining would be executed:
        # - Post-market (after 3:30 PM IST)
        # - Or pre-market (before 9:15 AM IST)
        # To avoid interruption of live trading

        status = "OK"
        details = f"Scheduled {len(scheduled)} models for retraining, {len(pending_queue)} total in queue"

        logger.info(f"[PHASE 252] Status: {status}")
        logger.info(f"[PHASE 252] {details}")
        logger.info("[PHASE 252] " + "=" * 80)

        return {
            "phase": 252,
            "status": status,
            "details": details,
            "outputs": {
                "decision_source": decision.get("decision_timestamp"),
                "drifted_models": drifted_models,
                "scheduled_for_retraining": scheduled,
                "pending_queue": pending_queue,
                "queue_file": str(QUEUE_FILE),
            },
            "errors": errors,
        }

    except Exception as e:
        error_msg = f"Phase 252 exception: {e}"
        errors.append(error_msg)
        logger.error(f"[PHASE 252] ✗ {error_msg}")

        return {
            "phase": 252,
            "status": "ERROR",
            "details": f"Retraining scheduling failed: {e}",
            "outputs": {},
            "errors": errors,
        }


def main():
    """CLI entry point."""
    result = run_phase252()

    print(f"\n[PHASE 252] Status: {result['status']}")
    print(f"[PHASE 252] Details: {result['details']}")

    if result["outputs"].get("drifted_models"):
        print(f"[PHASE 252] Drifted models: {result['outputs']['drifted_models']}")

    if result["outputs"].get("scheduled_for_retraining"):
        print(f"[PHASE 252] Scheduled for retraining: {result['outputs']['scheduled_for_retraining']}")

    if result["outputs"].get("pending_queue"):
        print(f"[PHASE 252] Pending queue: {len(result['outputs']['pending_queue'])} jobs")

    if result["errors"]:
        print(f"[PHASE 252] Errors: {result['errors']}")


if __name__ == "__main__":
    main()
