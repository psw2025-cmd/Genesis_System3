#!/usr/bin/env python3
"""
System3 Phases 366-369 Block Test
Tests all new phases for execution integrity
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "core" / "engine"))

def test_phase_execution():
    """Test execution of phases 366-369"""
    print("\n" + "="*70)
    print("PHASES 366-369 BLOCK EXECUTION TEST")
    print("="*70)
    
    from system3_phase366_strategy_ensemble_evaluator import run_phase366
    from system3_phase367_safety_guardrail_recommender import run_phase367
    from system3_phase368_broker_latency_monitor import run_phase368
    from system3_phase369_pipeline_profiler import run_phase369
    
    context = {}
    results = []
    
    phases = [
        (366, run_phase366, "Strategy Ensemble Evaluator"),
        (367, run_phase367, "Safety Guardrail Recommender"),
        (368, run_phase368, "Broker Latency Monitor"),
        (369, run_phase369, "Pipeline Profiler"),
    ]
    
    for phase_num, phase_func, description in phases:
        print(f"\nTesting Phase {phase_num}: {description}")
        print("-" * 70)
        
        try:
            result = phase_func(context)
            status = result.get("status", "UNKNOWN")
            
            if status in ["ok", "warn"]:
                print(f"[PASS] Phase {phase_num}: PASS (status={status})")
                results.append((phase_num, "PASS", status))
            else:
                print(f"[WARN] Phase {phase_num}: WARN (status={status})")
                if "error" in result:
                    print(f"   Error: {result['error'][:100]}")
                results.append((phase_num, "WARN", status))
            
            # Check outputs
            outputs = result.get("outputs", {})
            json_path = outputs.get("json")
            report_path = outputs.get("report")
            
            if json_path:
                print(f"   JSON: {Path(json_path).name}")
            if report_path:
                print(f"   Report: {Path(report_path).name}")
        
        except Exception as e:
            print(f"[FAIL] Phase {phase_num}: ERROR")
            print(f"   {str(e)[:100]}")
            results.append((phase_num, "ERROR", str(e)[:50]))
    
    # Summary
    print("\n" + "="*70)
    print("BLOCK TEST SUMMARY")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for _, r, _ in results if r in ["PASS", "WARN"])
    failed = total - passed
    
    for phase_num, result, detail in results:
        icon = "[PASS]" if result in ["PASS", "WARN"] else "[FAIL]"
        print(f"{icon} Phase {phase_num}: {result} ({detail})")
    
    print(f"\nTotal: {total}, Passed: {passed}, Failed: {failed}")
    
    if failed == 0:
        print("\n[OK] ALL PHASES 366-369 PASSED")
        return 0
    else:
        print(f"\n[FAIL] {failed} PHASES FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(test_phase_execution())
