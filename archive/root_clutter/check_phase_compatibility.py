"""
Check compatibility between current signal files and Phase 339/370 requirements
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals.csv"

# From phase370_signal_schema_normalizer.py
PHASE_370_EXPECTED = [
    "underlying", "symbol", "signal", "spot", "expiry", "strike",
    "ltp", "iv", "delta", "gamma", "theta", "vega", "rho",
    "confidence", "score", "pred_label", "pred_proba",
    "fwd_ret_1", "fwd_ret_2", "fwd_ret_3", "fwd_ret_5",
    "time_to_expiry", "timestamp", "data_source"
]

df = pd.read_csv(SIGNALS_CSV)
actual_cols = set(df.columns)
expected_cols = set(PHASE_370_EXPECTED)

print("="*80)
print("PHASE 339/370 COMPATIBILITY CHECK")
print("="*80)

print(f"\n[CURRENT FILE]")
print(f"  File: {SIGNALS_CSV.name}")
print(f"  Rows: {len(df)}")
print(f"  Columns: {len(df.columns)}")

print(f"\n[PHASE 370 REQUIREMENTS]")
print(f"  Expected columns: {len(PHASE_370_EXPECTED)}")

missing = expected_cols - actual_cols
extra = actual_cols - expected_cols

print(f"\n[MISSING COLUMNS] ({len(missing)})")
if missing:
    for col in sorted(missing):
        print(f"  - {col}")
else:
    print("  None")

print(f"\n[EXTRA COLUMNS] ({len(extra)})")
if extra:
    # Show first 20 only
    for col in sorted(list(extra))[:20]:
        print(f"  - {col}")
    if len(extra) > 20:
        print(f"  ... and {len(extra) - 20} more")
else:
    print("  None")

print(f"\n[ANALYSIS]")
if missing:
    print(f"  [WARNING] Missing {len(missing)} required columns")
    print(f"  [ACTION] Add these columns with default values")
else:
    print(f"  [OK] All required columns present")

if extra:
    print(f"  [INFO] {len(extra)} additional feature columns present")
    print(f"  [ACTION] Keep extra columns - they enhance the system")

print("\n[COMPATIBILITY STATUS]")
critical_missing = [c for c in missing if c in ['underlying', 'symbol', 'signal', 'strike', 'ltp']]
if critical_missing:
    print(f"  [FAIL] Missing critical columns: {critical_missing}")
else:
    print(f"  [PASS] All critical columns present")
    if missing:
        print(f"  [MINOR] {len(missing)} optional columns missing but system can function")
    else:
        print(f"  [EXCELLENT] Complete schema match + {len(extra)} bonus features")

print("\n" + "="*80)
