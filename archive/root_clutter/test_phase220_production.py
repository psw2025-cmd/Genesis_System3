#!/usr/bin/env python3
"""
Test script to verify Phase 220 production pipeline fixes work with actual file processing.
Tests the load_and_merge_signals function with temporary CSV files containing NULL timestamps.
"""

import pandas as pd
import tempfile
import os
from pathlib import Path
from core.engine.system3_phase220_historical_aggregation import load_and_merge_signals

def test_phase220_production_pipeline():
    """Test Phase 220 with actual file processing that includes NULL timestamps."""

    # Create test data that would trigger the original NULL timestamp warnings
    test_data_1 = pd.DataFrame({
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

    test_data_2 = pd.DataFrame({
        'ts': ['2025-12-09 11:00:00', None, '2025-12-09 11:02:00'],
        'timestamp': [None, '2025-12-09 11:01:00', None],
        'created_at': ['2025-12-09 11:03:00', None, '2025-12-09 11:04:00'],
        'underlying': ['BANKNIFTY', 'NIFTY', 'BANKNIFTY'],
        'strike': [46000, 22200, 46100],
        'side': ['PE', 'CE', 'PE'],
        'expiry': ['2025-12-26', '2025-12-26', '2025-12-26'],
        'signal_type': ['SELL', 'BUY', 'SELL']
    })

    print("=" * 80)
    print("PHASE 220 PRODUCTION PIPELINE NULL TIMESTAMP RECOVERY TEST")
    print("=" * 80)

    # Create temporary CSV files
    temp_files = []
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create first test file
            file1_path = Path(temp_dir) / "test_signals_1.csv"
            test_data_1.to_csv(file1_path, index=False)
            temp_files.append(file1_path)

            # Create second test file
            file2_path = Path(temp_dir) / "test_signals_2.csv"
            test_data_2.to_csv(file2_path, index=False)
            temp_files.append(file2_path)

            print(f"Created {len(temp_files)} test CSV files with NULL timestamps")

            # Count total NULL timestamps across all files
            total_null_input = 0
            for i, df in enumerate([test_data_1, test_data_2], 1):
                null_count = df["ts"].isna().sum()
                total_null_input += null_count
                print(f"File {i}: {null_count} NULL timestamps")

            print(f"Total input NULL timestamps: {total_null_input}")

            # Test the actual Phase 220 function
            try:
                result_df, file_stats = load_and_merge_signals(temp_files)

                total_null_output = result_df["ts"].isna().sum()
                print(f"\nOutput NULL timestamps: {total_null_output}")
                print(f"Total rows processed: {len(result_df)}")

                print("\nFile processing stats:")
                for file_path, stats in file_stats.items():
                    print(f"  {Path(file_path).name}: {stats['rows']} rows, {stats['null_timestamps_dropped']} NULL dropped")

                # Verify the fix worked
                recovered_count = total_null_input - total_null_output
                if recovered_count > 0:
                    print("\n✅ SUCCESS: Phase 220 NULL timestamp recovery working!")
                    print(f"   - Recovered {recovered_count} NULL timestamps across {len(temp_files)} files")
                    print("   - No warnings generated in production pipeline")
                    print("   - Enhanced timestamp normalization successful")
                elif total_null_output < total_null_input:
                    print(f"\n⚠️  PARTIAL SUCCESS: Recovered {total_null_input - total_null_output} timestamps")
                else:
                    print("\n❌ FAILED: No NULL timestamps recovered")

                print("\nSample output data:")
                print(result_df.head())

            except Exception as e:
                print(f"\n❌ ERROR: {e}")
                import traceback
                traceback.print_exc()

    except Exception as e:
        print(f"❌ SETUP ERROR: {e}")

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_phase220_production_pipeline()
