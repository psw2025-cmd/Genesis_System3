"""
Test Phases 331-340 Implementation

Validates all new phases are working correctly.
"""

import sys
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

def test_phase_import(phase_num: int, module_name: str, func_name: str):
    """Test importing and calling a phase."""
    try:
        logger.info(f"\n{'='*70}")
        logger.info(f"Testing Phase {phase_num}: {module_name}")
        logger.info(f"{'='*70}")
        
        # Import module
        module = __import__(f"core.engine.{module_name}", fromlist=[func_name])
        phase_func = getattr(module, func_name)
        
        # Call phase
        result = phase_func(root_path=str(PROJECT_ROOT))
        
        logger.info(f"Phase {phase_num} Status: {result}")
        logger.info(f"✓ Phase {phase_num} completed successfully")
        
        return True
    except Exception as e:
        logger.error(f"❌ Phase {phase_num} failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all phase tests."""
    logger.info("="*70)
    logger.info("TESTING PHASES 331-340 IMPLEMENTATION")
    logger.info("="*70)
    
    phases = [
        (331, "system3_phase331_signal_integrity", "run_phase_331"),
        (332, "system3_phase332_signal_volume_coverage", "run_phase_332"),
        (333, "system3_phase333_signal_consistency", "run_phase_333"),
        (334, "system3_phase334_model_drift_snapshot", "run_phase_334"),
        (335, "system3_phase335_model_drift_analyzer", "run_phase_335"),
        (336, "system3_phase336_safe_mode_suggestor", "run_phase_336"),
        (337, "system3_phase337_forward_return_quality_tracker", "run_phase_337"),
        (338, "system3_phase338_signal_outcome_correlation", "run_phase_338"),
        (339, "system3_phase339_daily_signal_pipeline_summary", "run_phase_339"),
        (340, "system3_phase340_signal_pipeline_regression_guard", "run_phase_340"),
    ]
    
    results = {}
    
    for phase_num, module_name, func_name in phases:
        success = test_phase_import(phase_num, module_name, func_name)
        results[phase_num] = success
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)
    
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed
    
    for phase_num, success in results.items():
        status = "✓ PASS" if success else "❌ FAIL"
        logger.info(f"Phase {phase_num}: {status}")
    
    logger.info("="*70)
    logger.info(f"Total: {len(results)} phases")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info("="*70)
    
    if failed == 0:
        logger.info("✓ ALL TESTS PASSED")
    else:
        logger.error(f"❌ {failed} TESTS FAILED")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
