"""
Comprehensive CSV Files Verification and Correction
Checks all CSV files for issues and fixes them for future-proofing
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def verify_paper_trades_csv(filepath):
    """Verify and fix paper_trades_live.csv"""
    print("\n[1/3] PAPER TRADES CSV")
    print("-" * 80)

    if not filepath.exists():
        print("  Status: MISSING")
        return False

    issues = []
    fixes_applied = []

    try:
        # Try reading with error handling
        df = pd.read_csv(filepath, on_bad_lines="skip", engine="python")

        print(f"  Status: EXISTS")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")

        # Check required columns
        required_cols = ["position_id", "action", "timestamp", "underlying", "strike", "option_type", "price", "qty"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")
        else:
            print(f"  Required columns: All present")

        # Check data types
        if "price" in df.columns:
            if df["price"].dtype == "object":
                issues.append("Price column is object type, should be numeric")
                try:
                    df["price"] = pd.to_numeric(df["price"], errors="coerce")
                    fixes_applied.append("Converted price to numeric")
                except:
                    pass

        if "strike" in df.columns:
            if df["strike"].dtype == "object":
                issues.append("Strike column is object type, should be numeric")
                try:
                    df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
                    fixes_applied.append("Converted strike to numeric")
                except:
                    pass

        if "qty" in df.columns:
            if df["qty"].dtype == "object":
                issues.append("Qty column is object type, should be numeric")
                try:
                    df["qty"] = pd.to_numeric(df["qty"], errors="coerce")
                    fixes_applied.append("Converted qty to numeric")
                except:
                    pass

        # Check for duplicate position_ids
        if "position_id" in df.columns:
            duplicates = df["position_id"].duplicated().sum()
            if duplicates > 0:
                issues.append(f"Found {duplicates} duplicate position_ids")

        # Check for invalid actions
        if "action" in df.columns:
            valid_actions = ["OPEN", "CLOSE"]
            invalid = df[~df["action"].isin(valid_actions)]
            if len(invalid) > 0:
                issues.append(f"Found {len(invalid)} rows with invalid action values")

        # Check for missing timestamps
        if "timestamp" in df.columns:
            missing_ts = df["timestamp"].isna().sum()
            if missing_ts > 0:
                issues.append(f"Found {missing_ts} rows with missing timestamps")

        # Apply fixes if any
        if fixes_applied:
            print(f"  Fixes applied: {len(fixes_applied)}")
            for fix in fixes_applied:
                print(f"    - {fix}")
            # Save corrected file
            backup_path = filepath.with_suffix(".csv.backup")
            if not backup_path.exists():
                df.to_csv(backup_path, index=False)
            df.to_csv(filepath, index=False)
            print(f"  File corrected and saved")

        # Report issues
        if issues:
            print(f"  Issues found: {len(issues)}")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"  Status: VALID - No issues found")

        return len(issues) == 0

    except Exception as e:
        print(f"  Status: ERROR - {str(e)[:100]}")
        return False


def verify_chain_raw_csv(filepath):
    """Verify and fix chain_raw_live.csv"""
    print("\n[2/3] CHAIN RAW CSV")
    print("-" * 80)

    if not filepath.exists():
        print("  Status: MISSING")
        return False

    issues = []
    fixes_applied = []

    try:
        df = pd.read_csv(filepath, nrows=1000)  # Sample first 1000 rows

        print(f"  Status: EXISTS")
        print(f"  Rows (sampled): {len(df)}")
        print(f"  Columns: {len(df.columns)}")

        # Check required columns
        required_cols = ["underlying", "strike", "option_type", "expiry"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")
        else:
            print(f"  Required columns: All present")

        # Check numeric columns
        numeric_cols = ["strike", "ltp", "oi", "volume", "spot_price"]
        for col in numeric_cols:
            if col in df.columns:
                if df[col].dtype == "object":
                    try:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                        fixes_applied.append(f"Converted {col} to numeric")
                    except:
                        pass

        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate rows")

        # Check underlying values
        if "underlying" in df.columns:
            valid_underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
            invalid = df[~df["underlying"].isin(valid_underlyings)]
            if len(invalid) > 0:
                issues.append(f"Found {len(invalid)} rows with invalid underlying values")

        # Check option types
        if "option_type" in df.columns:
            valid_types = ["CE", "PE"]
            invalid = df[~df["option_type"].isin(valid_types)]
            if len(invalid) > 0:
                issues.append(f"Found {len(invalid)} rows with invalid option_type values")

        # Report issues
        if issues:
            print(f"  Issues found: {len(issues)}")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"  Status: VALID - No critical issues found")
            print(f"  Note: Some NaN values are expected in option chain data")

        return len(issues) == 0

    except Exception as e:
        print(f"  Status: ERROR - {str(e)[:100]}")
        return False


def verify_underlying_rank_csv(filepath):
    """Verify and fix underlying_rank_live.csv"""
    print("\n[3/3] UNDERLYING RANK CSV")
    print("-" * 80)

    if not filepath.exists():
        print("  Status: MISSING")
        return False

    issues = []
    fixes_applied = []

    try:
        df = pd.read_csv(filepath)

        print(f"  Status: EXISTS")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")

        # Check required columns
        required_cols = ["underlying", "underlying_score"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")
        else:
            print(f"  Required columns: All present")

        # Check numeric columns
        numeric_cols = ["underlying_score", "signal_strength", "execution_quality", "pcr", "expected_move"]
        for col in numeric_cols:
            if col in df.columns:
                if df[col].dtype == "object":
                    try:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                        fixes_applied.append(f"Converted {col} to numeric")
                    except:
                        pass

        # Check underlying values
        if "underlying" in df.columns:
            valid_underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
            invalid = df[~df["underlying"].isin(valid_underlyings)]
            if len(invalid) > 0:
                issues.append(f"Found {len(invalid)} rows with invalid underlying values")

        # Check score range (should be 0-100)
        if "underlying_score" in df.columns:
            invalid_scores = df[(df["underlying_score"] < 0) | (df["underlying_score"] > 100)]
            if len(invalid_scores) > 0:
                issues.append(f"Found {len(invalid_scores)} rows with scores outside 0-100 range")

        # Apply fixes if any
        if fixes_applied:
            print(f"  Fixes applied: {len(fixes_applied)}")
            for fix in fixes_applied:
                print(f"    - {fix}")
            # Save corrected file
            backup_path = filepath.with_suffix(".csv.backup")
            if not backup_path.exists():
                df.to_csv(backup_path, index=False)
            df.to_csv(filepath, index=False)
            print(f"  File corrected and saved")

        # Report issues
        if issues:
            print(f"  Issues found: {len(issues)}")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"  Status: VALID - No issues found")

        return len(issues) == 0

    except Exception as e:
        print(f"  Status: ERROR - {str(e)[:100]}")
        return False


def main():
    """Main verification function."""
    print("\n" + "=" * 80)
    print("  COMPREHENSIVE CSV FILES VERIFICATION AND CORRECTION")
    print("=" * 80)

    outputs_dir = ROOT_DIR / "outputs"

    # Verify all CSV files
    results = {}

    paper_trades_path = outputs_dir / "paper_trades_live.csv"
    if not paper_trades_path.exists():
        print(f"\n[1/3] PAPER TRADES CSV")
        print("-" * 80)
        print(f"  Status: MISSING (path: {paper_trades_path})")
        results["paper_trades"] = False
    else:
        results["paper_trades"] = verify_paper_trades_csv(paper_trades_path)
    results["chain_raw"] = verify_chain_raw_csv(outputs_dir / "chain_raw_live.csv")
    results["underlying_rank"] = verify_underlying_rank_csv(outputs_dir / "underlying_rank_live.csv")

    # Summary
    print("\n" + "=" * 80)
    print("  VERIFICATION SUMMARY")
    print("=" * 80)

    total = len(results)
    valid = sum(1 for v in results.values() if v)
    invalid = total - valid

    print(f"\nTotal CSV Files Checked: {total}")
    print(f"  [OK] Valid: {valid}")
    print(f"  [FAIL] Invalid: {invalid}")

    print("\nFile Status:")
    for name, status in results.items():
        status_icon = "[OK]" if status else "[FAIL]"
        print(f"  {status_icon} {name}")

    print("\n" + "=" * 80)
    print("  VERIFICATION COMPLETE")
    print("=" * 80 + "\n")

    return invalid == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
