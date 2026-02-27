"""
Check All Output Files - Comprehensive Verification
"""

import sys
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
import os

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def get_file_info(filepath):
    """Get file information."""
    if not filepath.exists():
        return None

    stat = filepath.stat()
    age = datetime.now() - datetime.fromtimestamp(stat.st_mtime)

    return {
        "exists": True,
        "size": stat.st_size,
        "size_kb": stat.st_size / 1024,
        "age_minutes": age.total_seconds() / 60,
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
    }


def check_json_file(filepath, name):
    """Check JSON file."""
    print(f"\n[{name}]")
    print("-" * 80)

    info = get_file_info(filepath)
    if not info:
        print(f"  Status: MISSING")
        return False

    print(f"  Status: EXISTS")
    print(f"  Size: {info['size']:,} bytes ({info['size_kb']:.2f} KB)")
    print(f"  Modified: {info['modified']}")
    print(f"  Age: {info['age_minutes']:.1f} minutes ago")

    try:
        data = json.load(open(filepath))
        print(f"  Format: Valid JSON")
        print(f"  Keys: {list(data.keys())[:10]}")

        # Check if empty
        if not data or (isinstance(data, dict) and len(data) == 0):
            print(f"  Content: EMPTY")
        else:
            print(f"  Content: Has data")

        return True
    except Exception as e:
        print(f"  Format: INVALID JSON - {str(e)[:50]}")
        return False


def check_csv_file(filepath, name):
    """Check CSV file."""
    print(f"\n[{name}]")
    print("-" * 80)

    info = get_file_info(filepath)
    if not info:
        print(f"  Status: MISSING")
        return False

    print(f"  Status: EXISTS")
    print(f"  Size: {info['size']:,} bytes ({info['size_kb']:.2f} KB)")
    print(f"  Modified: {info['modified']}")
    print(f"  Age: {info['age_minutes']:.1f} minutes ago")

    try:
        df = pd.read_csv(filepath, on_bad_lines="skip", engine="python")
        print(f"  Format: Valid CSV")
        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Column names: {list(df.columns)[:10]}")

        # Check for empty
        if len(df) == 0:
            print(f"  Content: EMPTY (no rows)")
        else:
            print(f"  Content: Has {len(df):,} rows")
            # Check for NaN
            nan_count = df.isna().sum().sum()
            if nan_count > 0:
                print(f"  Data Quality: {nan_count:,} NaN values found")
            else:
                print(f"  Data Quality: No NaN values")

        return True
    except Exception as e:
        print(f"  Format: INVALID CSV - {str(e)[:50]}")
        return False


def main():
    """Check all output files."""
    print("\n" + "=" * 80)
    print("  COMPREHENSIVE OUTPUT FILES CHECK")
    print("=" * 80)

    outputs_dir = ROOT_DIR / "outputs"

    # List of files to check
    files_to_check = [
        # JSON files
        (outputs_dir / "pnl_live.json", "PnL Live (JSON)", "json"),
        (outputs_dir / "positions_live.json", "Positions Live (JSON)", "json"),
        (outputs_dir / "top_trade_signal.json", "Top Trade Signal (JSON)", "json"),
        (outputs_dir / "qc_report_live.json", "QC Report Live (JSON)", "json"),
        # CSV files
        (outputs_dir / "paper_trades_live.csv", "Paper Trades Live (CSV)", "csv"),
        (outputs_dir / "chain_raw_live.csv", "Chain Raw Live (CSV)", "csv"),
        (outputs_dir / "underlying_rank_live.csv", "Underlying Rank Live (CSV)", "csv"),
    ]

    results = {}

    for filepath, name, file_type in files_to_check:
        if file_type == "json":
            results[name] = check_json_file(filepath, name)
        else:
            results[name] = check_csv_file(filepath, name)

    # Summary
    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80)

    total = len(results)
    existing = sum(1 for v in results.values() if v)
    missing = total - existing

    print(f"\nTotal Files Checked: {total}")
    print(f"  [OK] Existing & Valid: {existing}")
    print(f"  [FAIL] Missing or Invalid: {missing}")

    print("\nFile Status:")
    for name, status in results.items():
        status_icon = "[OK]" if status else "[FAIL]"
        print(f"  {status_icon} {name}")

    # Check data freshness
    print("\n" + "=" * 80)
    print("  DATA FRESHNESS")
    print("=" * 80)

    fresh_files = []
    stale_files = []

    for filepath, name, file_type in files_to_check:
        info = get_file_info(filepath)
        if info:
            if info["age_minutes"] < 5:
                fresh_files.append((name, info["age_minutes"]))
            else:
                stale_files.append((name, info["age_minutes"]))

    if fresh_files:
        print("\n[FRESH] Files (< 5 minutes):")
        for name, age in fresh_files:
            print(f"  [OK] {name}: {age:.1f} min ago")

    if stale_files:
        print("\n[STALE] Files (> 5 minutes):")
        for name, age in stale_files:
            print(f"  [WARN] {name}: {age:.1f} min ago")

    print("\n" + "=" * 80)
    print("  CHECK COMPLETE")
    print("=" * 80 + "\n")

    return existing == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
