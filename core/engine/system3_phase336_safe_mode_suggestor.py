"""
System3 Phase 336 - Safe-Mode Suggestor (Based on Drift)

Suggests safer mode for next trading day if drift is severe (smaller positions, no new positions).
Does NOT enforce automatically - only provides recommendations.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Severity thresholds
CRITICAL_DRIFT_THRESHOLD = 2  # Number of drift signals to trigger critical mode


def run_phase336_safe_mode_suggestor(root_path: str = None, **kwargs) -> Dict[str, Any]:
    """
    Phase 336: Safe-Mode Suggestor (Based on Drift)

    Returns:
        Dict with phase status and results
    """
    logger.info("=" * 70)
    logger.info("PHASE 336: Safe-Mode Suggestor")
    logger.info("=" * 70)

    root = Path(root_path) if root_path else PROJECT_ROOT

    # Load drift status from Phase 335
    drift_status_file = root / "storage" / "live" / "diagnostics" / "model_drift_status.json"

    if not drift_status_file.exists():
        logger.warning(f"Drift status file not found: {drift_status_file}")
        return {"phase": 336, "status": "WARN", "outputs": {"error": "Drift status not found - run Phase 335 first"}}

    try:
        with open(drift_status_file, "r", encoding="utf-8") as f:
            drift_data = json.load(f)

        drift_detected = drift_data.get("drift_detected", False)
        drift_signals = drift_data.get("drift_signals", [])

        recommendation = "NORMAL"
        reason = "No drift detected"
        severity = "LOW"

        if drift_detected:
            num_signals = len(drift_signals)

            if num_signals >= CRITICAL_DRIFT_THRESHOLD:
                recommendation = "REDUCE_POSITION_SIZES"
                reason = f"Severe model drift detected: {num_signals} drift signals"
                severity = "HIGH"
                logger.warning(f"⚠️  CRITICAL DRIFT: {num_signals} signals detected")
            else:
                recommendation = "MONITOR_CLOSELY"
                reason = f"Mild model drift detected: {num_signals} drift signal(s)"
                severity = "MEDIUM"
                logger.warning(f"⚠️  Mild drift: {num_signals} signal(s) detected")
        else:
            logger.info("✓ No drift detected - normal operation recommended")

        # Write recommendation
        diagnostics_dir = root / "storage" / "live" / "diagnostics"
        diagnostics_dir.mkdir(parents=True, exist_ok=True)

        recommendation_data = {
            "timestamp": datetime.now().isoformat(),
            "phase": 336,
            "recommendation": recommendation,
            "reason": reason,
            "severity": severity,
            "drift_signals_count": len(drift_signals),
            "drift_signals": drift_signals,
            "actions": {
                "NORMAL": "No action required",
                "MONITOR_CLOSELY": "Monitor performance closely; consider manual review",
                "REDUCE_POSITION_SIZES": "Reduce position sizes by 50%; avoid new high-risk positions",
            }.get(recommendation, "No action specified"),
        }

        recommendation_file = diagnostics_dir / "next_day_safety_recommendation.json"
        with open(recommendation_file, "w", encoding="utf-8") as f:
            json.dump(recommendation_data, f, indent=2)

        logger.info(f"Recommendation written to: {recommendation_file}")
        logger.info(f"Recommendation: {recommendation}")
        logger.info(f"Reason: {reason}")

        # Determine phase status
        status = "WARN" if recommendation != "NORMAL" else "OK"

        logger.info("=" * 70)
        logger.info(f"Phase 336 Complete: {status}")
        logger.info(f"Recommendation: {recommendation}")
        logger.info("=" * 70)

        return {
            "phase": 336,
            "status": status,
            "outputs": recommendation_data,
        }

    except Exception as e:
        logger.error(f"Error in Phase 336: {e}")
        return {"phase": 336, "status": "ERROR", "outputs": {"error": str(e)}}


def run_phase_336(**kwargs) -> str:
    """Wrapper for autorun integration - returns status string."""
    result = run_phase336_safe_mode_suggestor(**kwargs)
    return result.get("status", "ERROR")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    result = run_phase336_safe_mode_suggestor()
    print(f"\nPhase 336 Status: {result['status']}")
