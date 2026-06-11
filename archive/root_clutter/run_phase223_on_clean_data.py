"""
Run Phase 223 (Threshold Optimizer) on Clean EV-Ready CSV

This script runs Phase 223 using the cleaned EV-ready CSV instead of the raw CSV.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import Phase 223
from core.engine.system3_phase223_threshold_optimizer import run_phase223

# Override the CSV path to use clean EV-ready CSV
CLEAN_EV_CSV = PROJECT_ROOT / "storage" / "clean" / "angel_index_ai_signals_with_forward_ev_ready.csv"

print("="*80)
print("PHASE 223 - THRESHOLD OPTIMIZER (CLEAN DATA)")
print("="*80)
print(f"Using clean EV-ready CSV: {CLEAN_EV_CSV}")
print(f"File exists: {CLEAN_EV_CSV.exists()}")
print("="*80)
print()

if not CLEAN_EV_CSV.exists():
    print(f"❌ Clean EV-ready CSV not found: {CLEAN_EV_CSV}")
    print("   Please run: run_clean_signals_and_validate.bat")
    sys.exit(1)

# Temporarily override the CSV path in Phase 223
import core.engine.system3_phase223_threshold_optimizer as phase223_module
original_csv = phase223_module.SIGNALS_CSV
phase223_module.SIGNALS_CSV = CLEAN_EV_CSV

try:
    # Run Phase 223
    result = run_phase223()
    
    print("\n" + "="*80)
    print("PHASE 223 RESULTS")
    print("="*80)
    print(f"Status: {result['status']}")
    print(f"Details: {result['details']}")
    
    if 'outputs' in result:
        print(f"\nOutputs:")
        for key, value in result['outputs'].items():
            print(f"  {key}: {value}")
    
    if 'errors' in result and result['errors']:
        print(f"\nErrors/Warnings:")
        for error in result['errors']:
            # Truncate long tracebacks
            if len(error) > 500:
                print(f"  - {error[:500]}...")
            else:
                print(f"  - {error}")
    
    print("\n" + "="*80)
    
    if result['status'] == 'SUCCESS' or result['status'] == 'OK':
        print("✅ Phase 223 completed successfully on clean data")
    else:
        print(f"⚠️ Phase 223 completed with status: {result['status']}")
        
except Exception as e:
    print(f"\n❌ Phase 223 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    # Restore original CSV path
    phase223_module.SIGNALS_CSV = original_csv

