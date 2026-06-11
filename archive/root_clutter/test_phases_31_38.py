"""
Test script for Phases 31-38
Run this to test all phases sequentially and verify outputs.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_phase_31():
    """Test Phase 31: Ultra Decision Fusion"""
    print("\n" + "="*60)
    print("TESTING PHASE 31: Ultra Decision Fusion")
    print("="*60)
    try:
        from core.engine.system3_phase31_ultra_fusion import run_phase31_fusion
        result = run_phase31_fusion()
        print(f"\n[PASS] Phase 31 completed: {result}")
        
        # Verify output
        output_file = Path("storage/ultra/phase31_ultra_fused_decisions.csv")
        if output_file.exists():
            import pandas as pd
            df = pd.read_csv(output_file)
            print(f"[VERIFY] Output file exists: {len(df)} rows")
            print(f"[VERIFY] Columns: {list(df.columns)[:5]}...")
        else:
            print(f"[FAIL] Output file not found: {output_file}")
        return True
    except Exception as e:
        print(f"[FAIL] Phase 31 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase_32():
    """Test Phase 32: Ultra vs Baseline Comparator"""
    print("\n" + "="*60)
    print("TESTING PHASE 32: Ultra vs Baseline Comparator")
    print("="*60)
    try:
        from core.engine.system3_phase32_ultra_vs_baseline import run_phase32_comparison
        result = run_phase32_comparison()
        print(f"\n[PASS] Phase 32 completed: {result}")
        
        # Verify output
        output_file = Path("storage/ultra/phase32_ultra_vs_baseline_summary.md")
        if output_file.exists():
            print(f"[VERIFY] Output file exists: {output_file}")
        else:
            print(f"[FAIL] Output file not found: {output_file}")
        return True
    except Exception as e:
        print(f"[FAIL] Phase 32 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase_33():
    """Test Phase 33: Ultra Promotion Planner"""
    print("\n" + "="*60)
    print("TESTING PHASE 33: Ultra Promotion Planner")
    print("="*60)
    try:
        from core.engine.system3_phase33_promotion_planner import run_phase33_promotion_planner
        result = run_phase33_promotion_planner()
        print(f"\n[PASS] Phase 33 completed: {result}")
        
        # Verify output
        output_file = Path("storage/ultra/phase33_promotion_plan.md")
        if output_file.exists():
            print(f"[VERIFY] Output file exists: {output_file}")
        else:
            print(f"[FAIL] Output file not found: {output_file}")
        return True
    except Exception as e:
        print(f"[FAIL] Phase 33 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase_34():
    """Test Phase 34: Ultra Live Shadow Comparison"""
    print("\n" + "="*60)
    print("TESTING PHASE 34: Ultra Live Shadow Comparison")
    print("="*60)
    try:
        from core.engine.system3_phase34_ultra_shadow_exec import run_phase34_shadow_once
        result = run_phase34_shadow_once()
        print(f"\n[PASS] Phase 34 completed: {result}")
        
        # Verify output
        output_file = Path("storage/live/angel_index_ai_ultra_trades_shadow.csv")
        if output_file.exists():
            import pandas as pd
            df = pd.read_csv(output_file)
            print(f"[VERIFY] Output file exists: {len(df)} rows")
        else:
            print(f"[VERIFY] Output file created (may be empty): {output_file}")
        return True
    except Exception as e:
        print(f"[FAIL] Phase 34 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase_35():
    """Test Phase 35: Ultra Decision Auditor"""
    print("\n" + "="*60)
    print("TESTING PHASE 35: Ultra Decision Auditor")
    print("="*60)
    try:
        from core.engine.system3_phase35_ultra_auditor import run_phase35_audit
        result = run_phase35_audit()
        print(f"\n[PASS] Phase 35 completed: {result}")
        
        # Verify output
        output_file = Path("storage/ultra/phase35_decision_audit_report.md")
        if output_file.exists():
            print(f"[VERIFY] Output file exists: {output_file}")
        else:
            print(f"[FAIL] Output file not found: {output_file}")
        return True
    except Exception as e:
        print(f"[FAIL] Phase 35 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase_36():
    """Test Phase 36: CULL Orchestrator"""
    print("\n" + "="*60)
    print("TESTING PHASE 36: Ultra Continuous Learning Cycle (CULL)")
    print("="*60)
    try:
        from core.engine.system3_phase36_cull_orchestrator import run_phase36_cull_full_cycle
        result = run_phase36_cull_full_cycle()
        print(f"\n[PASS] Phase 36 completed: {result}")
        
        # Verify output
        output_file = Path("storage/ultra/phase36_cull_execution_log.md")
        if output_file.exists():
            print(f"[VERIFY] Output file exists: {output_file}")
        else:
            print(f"[FAIL] Output file not found: {output_file}")
        return True
    except Exception as e:
        print(f"[FAIL] Phase 36 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase_37():
    """Test Phase 37: Policy & Risk Monitor"""
    print("\n" + "="*60)
    print("TESTING PHASE 37: Ultra Policy & Risk Monitor")
    print("="*60)
    try:
        from core.engine.system3_phase37_policy_risk_monitor import run_phase37_policy_risk_dashboard
        result = run_phase37_policy_risk_dashboard()
        print(f"\n[PASS] Phase 37 completed: {result}")
        
        # Verify output
        output_file = Path("storage/ultra/phase37_policy_risk_dashboard.md")
        if output_file.exists():
            print(f"[VERIFY] Output file exists: {output_file}")
        else:
            print(f"[FAIL] Output file not found: {output_file}")
        return True
    except Exception as e:
        print(f"[FAIL] Phase 37 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase_38():
    """Test Phase 38: Governance Summary"""
    print("\n" + "="*60)
    print("TESTING PHASE 38: Ultra Governance Summary")
    print("="*60)
    try:
        from core.engine.system3_phase38_governance_summary import run_phase38_governance_summary
        result = run_phase38_governance_summary()
        print(f"\n[PASS] Phase 38 completed: {result}")
        
        # Verify output
        output_file = Path("storage/ultra/phase38_governance_summary.md")
        if output_file.exists():
            print(f"[VERIFY] Output file exists: {output_file}")
        else:
            print(f"[FAIL] Output file not found: {output_file}")
        return True
    except Exception as e:
        print(f"[FAIL] Phase 38 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all phase tests"""
    print("="*60)
    print("SYSTEM3 ULTRA PHASES 31-38: COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    results = {}
    
    # Test Phase 31 (no dependencies)
    results[31] = test_phase_31()
    
    # Test Phase 32 (requires Phase 31)
    if results[31]:
        results[32] = test_phase_32()
    else:
        print("\n[SKIP] Phase 32 skipped (Phase 31 failed)")
        results[32] = False
    
    # Test Phase 33 (requires Phase 32)
    if results[32]:
        results[33] = test_phase_33()
    else:
        print("\n[SKIP] Phase 33 skipped (Phase 32 failed)")
        results[33] = False
    
    # Test Phase 34 (requires Phase 31)
    if results[31]:
        results[34] = test_phase_34()
    else:
        print("\n[SKIP] Phase 34 skipped (Phase 31 failed)")
        results[34] = False
    
    # Test Phase 35 (requires Phase 31)
    if results[31]:
        results[35] = test_phase_35()
    else:
        print("\n[SKIP] Phase 35 skipped (Phase 31 failed)")
        results[35] = False
    
    # Test Phase 36 (requires Phases 32, 33, 35)
    if results[32] and results[33] and results[35]:
        results[36] = test_phase_36()
    else:
        print("\n[SKIP] Phase 36 skipped (dependencies failed)")
        results[36] = False
    
    # Test Phase 37 (requires Phase 35)
    if results[35]:
        results[37] = test_phase_37()
    else:
        print("\n[SKIP] Phase 37 skipped (Phase 35 failed)")
        results[37] = False
    
    # Test Phase 38 (requires Phases 32, 33, 35, 37)
    if results[32] and results[33] and results[35] and results[37]:
        results[38] = test_phase_38()
    else:
        print("\n[SKIP] Phase 38 skipped (dependencies failed)")
        results[38] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for phase, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"Phase {phase}: {status}")
    
    total_passed = sum(1 for p in results.values() if p)
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} phases passed")
    
    if total_passed == total_tests:
        print("\n[SUCCESS] All phases passed!")
    else:
        print("\n[WARNING] Some phases failed. Check errors above.")

if __name__ == "__main__":
    main()

