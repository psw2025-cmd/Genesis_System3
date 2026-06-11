"""
Run Threshold Proposer on Clean EV Tables from Phase 222

This script runs the threshold proposer which uses EV tables to propose optimal thresholds.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import threshold proposer
from core.engine.system3_threshold_proposer import main

print("="*80)
print("SYSTEM3 THRESHOLD PROPOSER (CLEAN EV TABLES)")
print("="*80)
print("Using EV tables from Phase 222 (clean data)")
print("="*80)
print()

try:
    # Run threshold proposer
    exit_code = main()
    
    if exit_code == 0:
        print("\n✅ Threshold proposer completed successfully")
    else:
        print(f"\n⚠️ Threshold proposer completed with exit code: {exit_code}")
        
except Exception as e:
    print(f"\n❌ Threshold proposer failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

