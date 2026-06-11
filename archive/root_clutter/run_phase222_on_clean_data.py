"""
Run Phase 222 (Signal Edge Analysis) on Clean EV-Ready CSV

This script runs Phase 222 using the cleaned EV-ready CSV instead of the raw CSV.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import Phase 222
from core.engine.system3_phase222_signal_edge import run_phase222

# Override the CSV path to use clean EV-ready CSV
CLEAN_EV_CSV = PROJECT_ROOT / "storage" / "clean" / "angel_index_ai_signals_with_forward_ev_ready.csv"

print("="*80)
print("PHASE 222 - SIGNAL EDGE ANALYSIS (CLEAN DATA)")
print("="*80)
print(f"Using clean EV-ready CSV: {CLEAN_EV_CSV}")
print(f"File exists: {CLEAN_EV_CSV.exists()}")
print("="*80)
print()

if not CLEAN_EV_CSV.exists():
    print(f"❌ Clean EV-ready CSV not found: {CLEAN_EV_CSV}")
    print("   Please run: run_clean_signals_and_validate.bat")
    sys.exit(1)

# Temporarily override the CSV path in Phase 222
import core.engine.system3_phase222_signal_edge as phase222_module
original_csv = phase222_module.SIGNALS_CSV
phase222_module.SIGNALS_CSV = CLEAN_EV_CSV

try:
    # Run Phase 222 with clean CSV path override
    result = run_phase222(csv_path=str(CLEAN_EV_CSV))
    
    print("\n" + "="*80)
    print("PHASE 222 RESULTS")
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
            print(f"  - {error}")
    
    print("\n" + "="*80)
    
    if result['status'] == 'SUCCESS' or result['status'] == 'OK':
        print("✅ Phase 222 completed successfully on clean data")
    else:
        print(f"⚠️ Phase 222 completed with status: {result['status']}")
        
except TypeError:
    # Phase 222 doesn't accept csv_path parameter, use module override instead
    try:
        result = run_phase222()
        
        print("\n" + "="*80)
        print("PHASE 222 RESULTS")
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
                print(f"  - {error}")
        
        print("\n" + "="*80)
        
        if result['status'] == 'SUCCESS' or result['status'] == 'OK':
            print("✅ Phase 222 completed successfully on clean data")
        else:
            print(f"⚠️ Phase 222 completed with status: {result['status']}")
    except Exception as e:
        print(f"\n❌ Phase 222 failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
finally:
    # Restore original CSV path
    phase222_module.SIGNALS_CSV = original_csv

