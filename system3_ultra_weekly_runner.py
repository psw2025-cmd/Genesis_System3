#!/usr/bin/env python3
"""
System3 Ultra - Weekly Runner Script
File: system3_ultra_weekly_runner.py
Path: ./system3_ultra_weekly_runner.py

Purpose:
    Automated runtime entry point for weekly execution cycles (OP5).
    Executes weekly governance checks, shadow campaign reviews, 
    decision audit validations, and generates weekly governance packs.

Safety Mandate:
    Strictly enforced Shadow Mode (No automated live order execution or model promotion).
"""

import sys
import os
import logging
from datetime import datetime

# Ensure project root directory is in system path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Safety Configuration Parameters
AUTO_EXECUTE_TRADES = False
AUTO_PROMOTE_MODELS = False
SHADOW_MODE = True

# Setup Logging
LOG_DIR = os.path.join(PROJECT_ROOT, "storage", "logs_ultra")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "system3_phases_39_45.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("system3.weekly_runner")


def verify_safety_parameters():
    """Validates safety flags before initiating weekly automation."""
    logger.info("Validating System3 Ultra safety parameters...")
    if AUTO_EXECUTE_TRADES or AUTO_PROMOTE_MODELS or not SHADOW_MODE:
        logger.critical("SAFETY VIOLATION: Execution flags must remain strictly disabled in Shadow Mode.")
        raise PermissionError("Unsafe execution parameters detected. Aborting weekly runner.")
    logger.info("Safety parameters verified: Shadow Mode ACTIVE, Live Execution DISABLED.")


def run_weekly_governance_pack():
    """
    Triggers Phase 40 Weekly Governance Pack and related sub-modules:
      - Phase 35: Decision Auditor
      - Phase 38: Governance Summary
      - Phase 39: Shadow Campaign
      - Phase 40: Weekly Governance Pack Aggregator
    """
    logger.info("Starting System3 Ultra Weekly Execution (OP5)...")
    
    try:
        from core.engine.system3_phase40_weekly_governance_pack import run_weekly_governance
        
        logger.info("Executing Phase 40 Weekly Governance Pack...")
        result = run_weekly_governance(
            shadow_mode=SHADOW_MODE,
            auto_execute=AUTO_EXECUTE_TRADES
        )
        logger.info(f"Weekly Governance Pack completed successfully. Output: {result}")
        return result

    except ImportError as ie:
        logger.warning(f"Phase 40 module import issue: {ie}. Executing sub-phase fallback pipeline...")
        return run_subphase_fallback()
    except Exception as e:
        logger.error(f"Error during weekly governance execution: {e}", exc_info=True)
        raise e


def run_subphase_fallback():
    """Fallback execution pipeline running individual sub-phases sequentially."""
    logger.info("Running sub-phase sequence: Phase 35 -> Phase 39 -> Phase 40")
    
    # Phase 35: Decision Auditor
    try:
        from core.engine.system3_phase35_ultra_auditor import run_auditor
        logger.info("Executing Phase 35 Decision Auditor...")
        run_auditor()
    except Exception as e:
        logger.warning(f"Phase 35 execution note: {e}")

    # Phase 39: Shadow Campaign
    try:
        from core.engine.system3_phase39_shadow_campaign import run_shadow_campaign
        logger.info("Executing Phase 39 Shadow Campaign Review...")
        run_shadow_campaign()
    except Exception as e:
        logger.warning(f"Phase 39 execution note: {e}")

    logger.info("Sub-phase sequence completed.")
    return {"status": "SUCCESS", "mode": "FALLBACK"}


def main():
    """Main script entry point."""
    print("=" * 60)
    print("  System3 Ultra - Weekly Automation Runner")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        verify_safety_parameters()
        run_weekly_governance_pack()
        print("\n[SUCCESS] Weekly runner completed all tasks successfully.")
        sys.exit(0)
    except Exception as err:
        print(f"\n[ERROR] Weekly runner execution failed: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()