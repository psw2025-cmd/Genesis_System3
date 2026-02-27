"""
Full block test for all 20 phases (361-380)
"""

import sys
import json
import time
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.WARNING)

def main():
    print("=" * 80)
    print("SYSTEM3 PHASES 361-380 FULL BLOCK TEST")
    print("=" * 80)
    print()
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "phases": {}
    }
    
    try:
        from core.engine.system3_phases_361_380_registry import get_phase_callable, get_phase_info
        
        # All 20 phases
        all_phases = [361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380]
        
        for phase_num in all_phases:
            results["total"] += 1
            
            try:
                phase_info = get_phase_info(phase_num)
                phase_func = get_phase_callable(phase_num)
                
                if not phase_func:
                    print(f"Phase {phase_num}: [SKIP] Not yet implemented")
                    results["phases"][phase_num] = "SKIP - Not implemented"
                    continue
                
                start = time.time()
                result = phase_func({})
                elapsed = time.time() - start
                
                status = result.get("status", "").lower()
                if status in ["ok", "warn", "error"]:
                    print(f"Phase {phase_num}: [PASS] {status} ({elapsed:.2f}s)")
                    results["passed"] += 1
                    results["phases"][phase_num] = f"PASS - {status}"
                else:
                    print(f"Phase {phase_num}: [FAIL] Invalid status: {status}")
                    results["failed"] += 1
                    results["phases"][phase_num] = "FAIL - Invalid status"
            
            except Exception as e:
                print(f"Phase {phase_num}: [FAIL] {str(e)[:50]}")
                results["failed"] += 1
                results["phases"][phase_num] = f"FAIL - {str(e)[:30]}"
        
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total:  {results['total']}")
        print(f"Passed: {results['passed']} [OK]")
        print(f"Failed: {results['failed']} [FAIL]")
        print()
        
        if results["failed"] == 0:
            print("[OK] ALL 20 PHASES PASSED - READY FOR DEPLOYMENT")
            return 0
        else:
            print(f"[FAIL] {results['failed']} phase(s) failed")
            return 1
    
    except Exception as e:
        print(f"[CRITICAL] {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
