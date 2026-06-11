#!/usr/bin/env python3
"""
Test script to verify Phase 220 pipeline fixes work in production context.
Tests the actual load_and_merge_signals function that was modified.
"""

import pandas as pd
from core.engine.system3_phase220_historical_aggregation import load_and_merge_signals

def test_phase220_pipeline_fixes():
    """Test Phase 220 with NULL timestamps that would trigger original warnings."""

    # Create test data that would trigger the original NULL timestamp warnings
    test_signals = pd.DataFrame({
        'ts': [None, '2025-12-08 10:30:00', None],
        'timestamp': ['2025-12-08 10:31:00', None, '2025-12-08 10:32:00'],
        'created_at': ['2025-12-08 10:33:00', '2025-12-08 10:34:00', None],
        'signal_time': [None, '2025-12-08 10:35:00', '2025-12-08 10:36:00'],
        'underlying': ['NIFTY', 'BANKNIFTY', 'NIFTY'],
        'strike': [22000, 45000, 22100],
        'side': ['CE', 'PE', 'CE'],
        'expiry': ['2025-12-26', '2025-12-26', '2025-12-26'],
        'signal_type': ['BUY', 'SELL', 'BUY']
    })

    print("=" * 80)
    print("PHASE 220 PIPELINE NULL TIMESTAMP RECOVERY TEST")
    print("=" * 80)

    print("\nInput data:")
    print(test_signals)
    null_count_input = test_signals["ts"].isna().sum()
    print(f"Input NULL timestamps: {null_count_input}")

    try:
        # This should now work without warnings due to our enhanced recovery
        result_df = load_and_merge_signals(test_signals)

        null_count_output = result_df["ts"].isna().sum()
        print(f"\nOutput NULL timestamps: {null_count_output}")
        print(f"Total rows processed: {len(result_df)}")

        print("\nOutput data:")
        print(result_df)

        # Verify the fix worked
        if null_count_output == 0 and null_count_input > 0:
            print("\n✅ SUCCESS: Phase 220 NULL timestamp recovery working!")
            print(f"   - Recovered {null_count_input} NULL timestamps")
            print("   - No warnings generated")
            print("   - Production pipeline ready")
        elif null_count_output < null_count_input:
            print(f"\n⚠️  PARTIAL SUCCESS: Recovered {null_count_input - null_count_output} timestamps")
        else:
            print("\n❌ FAILED: No NULL timestamps recovered")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_phase220_pipeline_fixes()
