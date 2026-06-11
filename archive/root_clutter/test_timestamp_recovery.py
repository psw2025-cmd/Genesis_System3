#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced timestamp recovery functionality.
"""

import pandas as pd
from core.utils.timestamp_parser import normalize_timestamp_column_strict_enhanced

def test_timestamp_recovery():
    """Test the enhanced timestamp recovery with NULL values."""

    # Create test data with NULL timestamps
    test_df = pd.DataFrame({
        'ts': [None, '2025-12-08 10:30:00', None],
        'timestamp': ['2025-12-08 10:31:00', None, '2025-12-08 10:32:00'],
        'created_at': ['2025-12-08 10:33:00', '2025-12-08 10:34:00', None],
        'signal_time': [None, '2025-12-08 10:35:00', '2025-12-08 10:36:00']
    })

    print("=" * 80)
    print("ENHANCED TIMESTAMP RECOVERY TEST")
    print("=" * 80)

    print("\nBEFORE normalization:")
    print(test_df)
    null_count_before = test_df["ts"].isna().sum()
    print(f"NULL timestamps: {null_count_before}")

    # Apply enhanced normalization
    normalized_df, metrics = normalize_timestamp_column_strict_enhanced(test_df, col_name='ts')

    print("\nAFTER enhanced normalization:")
    print(normalized_df)
    null_count_after = normalized_df["ts"].isna().sum()
    print(f"NULL timestamps after recovery: {null_count_after}")

    print(f"\nRecovery successful: {null_count_before > null_count_after}")
    print(f"Timestamps recovered: {null_count_before - null_count_after}")

    print("\nDetailed metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    test_timestamp_recovery()
