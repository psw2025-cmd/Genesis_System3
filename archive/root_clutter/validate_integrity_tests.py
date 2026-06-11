#!/usr/bin/env python3
"""
System3 Integrity Validation Test Suite
Tests phases 361-365 and 370-375 for runtime integrity
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "core" / "engine"))

def test_phases_363_365():
    """Test health monitoring block"""
    print("\n" + "="*70)
    print("TESTING PHASES 363-365 (Health & Accuracy Monitoring)")
    print("="*70)
    
    from system3_phase363_model_drift_checker import run_phase363
    from system3_phase364_health_dashboard_feed import run_phase364
    from system3_phase365_accuracy_tracker import run_phase365
    
    context = {}
    results = []
    
    for phase_num, phase_func in [(363, run_phase363), (364, run_phase364), (365, run_phase365)]:
        try:
            result = phase_func(context)
            status = result.get("status", "UNKNOWN")
            results.append((phase_num, status, "PASS"))
            print(f"✅ Phase {phase_num}: {status}")
        except Exception as e:
            results.append((phase_num, "ERROR", f"FAIL: {str(e)[:50]}"))
            print(f"❌ Phase {phase_num}: ERROR - {str(e)[:50]}")
    
    return results

def test_phases_370_375():
    """Test data quality pipeline block"""
    print("\n" + "="*70)
    print("TESTING PHASES 370-375 (Data Quality Pipeline)")
    print("="*70)
    
    from system3_phase370_signal_schema_normalizer import run_phase370
    from system3_phase371_signal_duplicate_scanner import run_phase371
    from system3_phase372_signal_conflict_resolver import run_phase372
    from system3_phase373_signal_clean_curated_builder import run_phase373
    from system3_phase374_signal_history_freshness_checker import run_phase374
    from system3_phase375_signal_data_quality_summary import run_phase375
    
    context = {}
    results = []
    
    phases = [
        (370, run_phase370), (371, run_phase371), (372, run_phase372),
        (373, run_phase373), (374, run_phase374), (375, run_phase375)
    ]
    
    for phase_num, phase_func in phases:
        try:
            result = phase_func(context)
            status = result.get("status", "UNKNOWN")
            results.append((phase_num, status, "PASS"))
            print(f"✅ Phase {phase_num}: {status}")
        except Exception as e:
            results.append((phase_num, "ERROR", f"FAIL: {str(e)[:50]}"))
            print(f"❌ Phase {phase_num}: ERROR - {str(e)[:50]}")
    
    return results

def test_legacy_phase_imports():
    """Test that legacy phases still import correctly"""
    print("\n" + "="*70)
    print("TESTING LEGACY PHASE IMPORTS")
    print("="*70)
    
    results = []
    
    # Test Phase 103 (from prior work)
    try:
        from system3_phase103_order_ledger_support import run_phase103
        print("✅ Phase 103: Import OK")
        results.append((103, "OK", "PASS"))
    except Exception as e:
        print(f"❌ Phase 103: Import failed - {str(e)[:50]}")
        results.append((103, "ERROR", f"FAIL: {str(e)[:50]}"))
    
    # Test Phase 331 (has different function name pattern)
    try:
        from system3_phase331_signal_integrity import run_phase331_signal_integrity
        print("✅ Phase 331: Import OK (uses run_phase331_signal_integrity)")
        results.append((331, "OK", "PASS"))
    except Exception as e:
        print(f"❌ Phase 331: Import failed - {str(e)[:50]}")
        results.append((331, "ERROR", f"FAIL: {str(e)[:50]}"))
    
    # Test Phase 339 (target for schema fix validation)
    try:
        from system3_phase339_daily_signal_pipeline_summary import run_phase339_daily_signal_pipeline_summary
        print("✅ Phase 339: Import OK (uses run_phase339_daily_signal_pipeline_summary)")
        results.append((339, "OK", "PASS"))
    except Exception as e:
        print(f"❌ Phase 339: Import failed - {str(e)[:50]}")
        results.append((339, "ERROR", f"FAIL: {str(e)[:50]}"))
    
    # Test Phase 340 (target for dedup fix validation)
    try:
        from system3_phase340_signal_pipeline_regression_guard import run_phase340_signal_pipeline_regression_guard
        print("✅ Phase 340: Import OK (uses run_phase340_signal_pipeline_regression_guard)")
        results.append((340, "OK", "PASS"))
    except Exception as e:
        print(f"❌ Phase 340: Import failed - {str(e)[:50]}")
        results.append((340, "ERROR", f"FAIL: {str(e)[:50]}"))
    
    return results

def main():
    """Run all integrity tests"""
    print("\n" + "="*70)
    print("SYSTEM3 INTEGRITY VALIDATION TEST SUITE")
    print("="*70)
    
    all_results = []
    
    # Test new phases
    all_results.extend(test_phases_363_365())
    all_results.extend(test_phases_370_375())
    
    # Test legacy imports
    all_results.extend(test_legacy_phase_imports())
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total = len(all_results)
    passed = sum(1 for _, _, result in all_results if result == "PASS")
    failed = total - passed
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {failed} TESTS FAILED")
        for phase_num, status, result in all_results:
            if result != "PASS":
                print(f"  Phase {phase_num}: {result}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
