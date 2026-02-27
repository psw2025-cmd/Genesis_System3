#!/usr/bin/env python3
"""
Test script for patch_symbol_on_enriched function logic.
Tests various scenarios including safe merge keys and edge cases.
"""

import pandas as pd
import tempfile
import os
from pathlib import Path
import sys

# Add current directory to path to import the function
sys.path.insert(0, '.')

from system3_multivalidate_autofix import patch_symbol_on_enriched

def test_no_safe_keys():
    """Test case where only 'side' overlaps - should not merge."""
    print("=== Test 1: No Safe Keys (only 'side' overlaps) ===")

    # Create test dataframes
    enriched_data = {
        'ts': ['2025-01-01 10:00:00', '2025-01-01 10:01:00'],
        'underlying': ['NIFTY', 'NIFTY'],
        'strike': [26000, 26100],
        'side': ['BUY', 'SELL'],
        'symbol': [pd.NA, pd.NA]
    }
    df_enriched = pd.DataFrame(enriched_data)

    raw_data = {
        'timestamp': ['2025-01-01 10:00:00', '2025-01-01 10:01:00'],
        'symbol': ['NIFTY25JAN26000CE', 'NIFTY25JAN26100PE'],
        'side': ['BUY', 'SELL']
    }
    df_raw = pd.DataFrame(raw_data)

    # Create temp files
    with tempfile.TemporaryDirectory() as tmpdir:
        enriched_path = Path(tmpdir) / "enriched.csv"
        raw_path = Path(tmpdir) / "raw.csv"

        df_enriched.to_csv(enriched_path, index=False)
        df_raw.to_csv(raw_path, index=False)

        # Mock the function call
        result = patch_symbol_on_enriched.__wrapped__(enriched_path, raw_path)

        print(f"Action: {result['action']}")
        print(f"Merge keys used: {result['merge_keys_used']}")
        print(f"Symbol filled count: {result['symbol_filled_count']}")
        print(f"Error: {result.get('error', 'None')}")

        assert result['action'] == 'symbol_not_filled_no_safe_keys'
        assert result['merge_keys_used'] == []
        assert result['symbol_filled_count'] == 0
        print("✓ Test passed\n")

def test_with_safe_keys():
    """Test case where safe merge keys exist."""
    print("=== Test 2: Safe Keys Available ===")

    # Create test dataframes with common safe keys
    enriched_data = {
        'ts': ['2025-01-01 10:00:00', '2025-01-01 10:01:00'],
        'underlying': ['NIFTY', 'NIFTY'],
        'strike': [26000, 26100],
        'side': ['BUY', 'SELL'],
        'symbol': [pd.NA, pd.NA]
    }
    df_enriched = pd.DataFrame(enriched_data)

    raw_data = {
        'ts': ['2025-01-01 10:00:00', '2025-01-01 10:01:00'],
        'underlying': ['NIFTY', 'NIFTY'],
        'strike': [26000, 26100],
        'symbol': ['NIFTY25JAN26000CE', 'NIFTY25JAN26100PE'],
        'side': ['BUY', 'SELL']
    }
    df_raw = pd.DataFrame(raw_data)

    # Create temp files
    with tempfile.TemporaryDirectory() as tmpdir:
        enriched_path = Path(tmpdir) / "enriched.csv"
        raw_path = Path(tmpdir) / "raw.csv"

        df_enriched.to_csv(enriched_path, index=False)
        df_raw.to_csv(raw_path, index=False)

        # Mock the function call
        result = patch_symbol_on_enriched.__wrapped__(enriched_path, raw_path)

        print(f"Action: {result['action']}")
        print(f"Merge keys used: {result['merge_keys_used']}")
        print(f"Symbol filled count: {result['symbol_filled_count']}")
        print(f"Error: {result.get('error', 'None')}")

        assert result['action'] == 'patched_symbol'
        assert len(result['merge_keys_used']) > 0
        assert result['symbol_filled_count'] == 2  # Both symbols filled
        print("✓ Test passed\n")

def test_missing_raw_file():
    """Test case where raw orders file is missing."""
    print("=== Test 3: Missing Raw Orders File ===")

    enriched_data = {
        'ts': ['2025-01-01 10:00:00'],
        'symbol': [pd.NA]
    }
    df_enriched = pd.DataFrame(enriched_data)

    with tempfile.TemporaryDirectory() as tmpdir:
        enriched_path = Path(tmpdir) / "enriched.csv"
        raw_path = Path(tmpdir) / "raw.csv"  # Doesn't exist

        df_enriched.to_csv(enriched_path, index=False)

        result = patch_symbol_on_enriched.__wrapped__(enriched_path, raw_path)

        print(f"Action: {result['action']}")
        print(f"Error: {result.get('error', 'None')}")

        assert result['action'] == 'symbol_source_missing'
        print("✓ Test passed\n")

def test_missing_enriched_file():
    """Test case where enriched file is missing."""
    print("=== Test 4: Missing Enriched File ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        enriched_path = Path(tmpdir) / "enriched.csv"  # Doesn't exist
        raw_path = Path(tmpdir) / "raw.csv"

        # Create empty raw file
        pd.DataFrame({'symbol': ['test']}).to_csv(raw_path, index=False)

        result = patch_symbol_on_enriched.__wrapped__(enriched_path, raw_path)

        print(f"Action: {result['action']}")
        print(f"Error: {result.get('error', 'None')}")

        assert result['action'] == 'enriched_missing'
        print("✓ Test passed\n")

if __name__ == "__main__":
    print("Running patch_symbol_on_enriched logic tests...\n")

    test_no_safe_keys()
    test_with_safe_keys()
    test_missing_raw_file()
    test_missing_enriched_file()

    print("All tests passed! ✓")
