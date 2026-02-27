"""
Comprehensive CSV Files Check - All Files and Data
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def check_paper_trades():
    """Check paper_trades_live.csv"""
    print("\n" + "=" * 80)
    print("  PAPER TRADES CSV - COMPREHENSIVE CHECK")
    print("=" * 80)

    filepath = ROOT_DIR / "outputs" / "paper_trades_live.csv"

    if not filepath.exists():
        print("\n  Status: FILE NOT FOUND")
        print(f"  Path: {filepath}")
        return False

    try:
        df = pd.read_csv(filepath, on_bad_lines="skip", engine="python")

        print(f"\n  File: {filepath.name}")
        print(f"  Size: {filepath.stat().st_size:,} bytes")
        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")

        print(f"\n  Column Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"    {i:2d}. {col}")

        print(f"\n  Data Types:")
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isna().sum()
            print(f"    {col:20s}: {str(dtype):15s} (Nulls: {null_count})")

        print(f"\n  Data Quality:")
        print(f"    Total nulls: {df.isna().sum().sum()}")
        print(f"    Duplicate rows: {df.duplicated().sum()}")

        if "action" in df.columns:
            print(f"\n  Action Distribution:")
            print(df["action"].value_counts().to_string())

        if "underlying" in df.columns:
            print(f"\n  Underlying Distribution:")
            print(df["underlying"].value_counts().to_string())

        # Check for structure issues
        issues = []

        # Check if OPEN and CLOSE rows have different columns
        if "action" in df.columns:
            open_cols = set(df[df["action"] == "OPEN"].columns) if len(df[df["action"] == "OPEN"]) > 0 else set()
            close_cols = set(df[df["action"] == "CLOSE"].columns) if len(df[df["action"] == "CLOSE"]) > 0 else set()

            if open_cols != close_cols:
                extra_in_close = close_cols - open_cols
                extra_in_open = open_cols - close_cols
                if extra_in_close:
                    issues.append(f"CLOSE rows have extra columns: {list(extra_in_close)}")
                if extra_in_open:
                    issues.append(f"OPEN rows have extra columns: {list(extra_in_open)}")

        # Check numeric columns
        numeric_cols = ["strike", "price", "qty", "realized_pnl", "realized_pnl_pct"]
        for col in numeric_cols:
            if col in df.columns:
                if df[col].dtype == "object":
                    issues.append(f"{col} is object type, should be numeric")

        if issues:
            print(f"\n  Issues Found: {len(issues)}")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"\n  Status: VALID - No issues found")

        print(f"\n  Sample Data (first 3 rows):")
        print(df.head(3).to_string())

        return len(issues) == 0

    except Exception as e:
        print(f"\n  Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def check_chain_raw():
    """Check chain_raw_live.csv"""
    print("\n" + "=" * 80)
    print("  CHAIN RAW CSV - COMPREHENSIVE CHECK")
    print("=" * 80)

    filepath = ROOT_DIR / "outputs" / "chain_raw_live.csv"

    if not filepath.exists():
        print("\n  Status: FILE NOT FOUND")
        return False

    try:
        df = pd.read_csv(filepath, nrows=1000)  # Sample

        print(f"\n  File: {filepath.name}")
        print(f"  Size: {filepath.stat().st_size:,} bytes")
        print(f"  Sampled Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")

        print(f"\n  Column Names (first 20):")
        for i, col in enumerate(df.columns[:20], 1):
            print(f"    {i:2d}. {col}")
        if len(df.columns) > 20:
            print(f"    ... and {len(df.columns) - 20} more")

        print(f"\n  Data Quality:")
        print(f"    Total nulls: {df.isna().sum().sum()}")
        print(f"    Nulls in key columns:")
        key_cols = ["underlying", "strike", "option_type", "ltp", "oi"]
        for col in key_cols:
            if col in df.columns:
                nulls = df[col].isna().sum()
                pct = (nulls / len(df)) * 100
                print(f"      {col:15s}: {nulls:5d} ({pct:5.1f}%)")

        # Check numeric columns
        numeric_cols = ["strike", "ltp", "oi", "volume", "spot_price"]
        issues = []
        for col in numeric_cols:
            if col in df.columns:
                if df[col].dtype == "object":
                    issues.append(f"{col} is object type, should be numeric")

        if issues:
            print(f"\n  Issues Found: {len(issues)}")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"\n  Status: VALID - No critical issues")
            print(f"  Note: Some NaN values are expected in option chain data")

        return len(issues) == 0

    except Exception as e:
        print(f"\n  Error: {str(e)}")
        return False


def check_underlying_rank():
    """Check underlying_rank_live.csv"""
    print("\n" + "=" * 80)
    print("  UNDERLYING RANK CSV - COMPREHENSIVE CHECK")
    print("=" * 80)

    filepath = ROOT_DIR / "outputs" / "underlying_rank_live.csv"

    if not filepath.exists():
        print("\n  Status: FILE NOT FOUND")
        return False

    try:
        df = pd.read_csv(filepath)

        print(f"\n  File: {filepath.name}")
        print(f"  Size: {filepath.stat().st_size:,} bytes")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")

        print(f"\n  Column Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"    {i:2d}. {col}")

        print(f"\n  Data Quality:")
        print(f"    Total nulls: {df.isna().sum().sum()}")

        print(f"\n  Data:")
        print(df.to_string())

        # Check numeric columns
        numeric_cols = ["underlying_score", "signal_strength", "execution_quality", "pcr", "expected_move"]
        issues = []
        for col in numeric_cols:
            if col in df.columns:
                if df[col].dtype == "object":
                    issues.append(f"{col} is object type, should be numeric")

        if issues:
            print(f"\n  Issues Found: {len(issues)}")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"\n  Status: VALID - No issues found")

        return len(issues) == 0

    except Exception as e:
        print(f"\n  Error: {str(e)}")
        return False


def main():
    """Check all CSV files."""
    print("\n" + "=" * 80)
    print("  COMPREHENSIVE CSV FILES CHECK")
    print("=" * 80)

    results = {}
    results["paper_trades"] = check_paper_trades()
    results["chain_raw"] = check_chain_raw()
    results["underlying_rank"] = check_underlying_rank()

    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80)

    total = len(results)
    valid = sum(1 for v in results.values() if v)

    print(f"\nTotal Files: {total}")
    print(f"  Valid: {valid}")
    print(f"  Issues: {total - valid}")

    print("\nFile Status:")
    for name, status in results.items():
        status_icon = "[OK]" if status else "[ISSUES]"
        print(f"  {status_icon} {name}")

    print("\n" + "=" * 80)
    print("  CHECK COMPLETE")
    print("=" * 80 + "\n")

    return valid == total


if __name__ == "__main__":
    main()
