"""
Test script for Phases 46-55
Runs dry-run tests for all new Ultra phases.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

def test_phase(phase_num: int, module_name: str, function_name: str) -> bool:
    """Test a single phase."""
    print(f"\n{'='*70}")
    print(f"Testing Phase {phase_num}: {module_name}")
    print('='*70)
    
    try:
        module = __import__(module_name, fromlist=[function_name])
        func = getattr(module, function_name)
        func()
        print(f"[OK] Phase {phase_num} completed successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Phase {phase_num} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all phase tests."""
    print("="*70)
    print("SYSTEM3 ULTRA - PHASES 46-55 DRY-RUN TEST")
    print("="*70)
    print("Date:", __import__("datetime").datetime.now().isoformat())
    print("\n[SAFETY] All tests are dry-run, read-only, shadow-only")
    
    phases = [
        (46, "core.ultra.phase46_meta_fusion", "run_phase46_meta_fusion"),
        (47, "core.ultra.phase47_confidence_vector", "run_phase47_confidence_vector"),
        (48, "core.ultra.phase48_error_scanner", "run_phase48_error_scanner"),
        (49, "core.ultra.phase49_risk_regulator", "run_phase49_risk_regulator"),
        (50, "core.ultra.phase50_prediction_explainer", "run_phase50_prediction_explainer"),
        (51, "core.ultra.phase51_probability_engine", "run_phase51_probability_engine"),
        (52, "core.ultra.phase52_multi_broker", "run_phase52_multi_broker"),
        (53, "core.ultra.phase53_monitoring_agent", "run_phase53_monitoring_agent"),
        (54, "core.ultra.phase54_back_reconstruction", "run_phase54_back_reconstruction"),
        (55, "core.ultra.phase55_intelligence_dashboard", "run_phase55_intelligence_dashboard"),
    ]
    
    results = []
    for phase_num, module_name, function_name in phases:
        success = test_phase(phase_num, module_name, function_name)
        results.append((phase_num, success))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"Total phases tested: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    print("\nDetailed results:")
    for phase_num, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  Phase {phase_num}: {status}")
    
    if passed == total:
        print("\n[OK] All phases passed!")
        return 0
    else:
        print(f"\n[WARN] {total - passed} phase(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

