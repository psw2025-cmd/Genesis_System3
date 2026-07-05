"""
Comprehensive Issue Checker - Checks all logs and output files
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def check_logs():
    """Check log files for errors."""
    print("\n" + "=" * 80)
    print("  CHECKING LOG FILES")
    print("=" * 80 + "\n")

    log_file = ROOT_DIR / "logs" / "2026-01-31.log"
    issues = []

    if not log_file.exists():
        print("[WARNING] Log file not found")
        return issues

    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # Check for errors
    errors = [l for l in lines if "ERROR" in l.upper() or "Traceback" in l or "Exception" in l]
    warnings = [l for l in lines if "WARNING" in l and ("FAIL" in l or "QC FAIL" in l)]

    print(f"Total log lines: {len(lines)}")
    print(f"Errors found: {len(errors)}")
    print(f"QC Failures: {len(warnings)}")

    if errors:
        print("\n[ERRORS]:")
        for e in errors[:5]:
            try:
                print(f"  {e.rstrip()[:120]}")
            except:
                print(f"  [Error line with encoding issue]")
        issues.append(f"Found {len(errors)} errors in logs")

    if warnings:
        print("\n[QC FAILURES]:")
        unique_failures = {}
        for w in warnings:
            if "QC FAIL" in w:
                parts = w.split("QC FAIL")
                if len(parts) > 1:
                    key = parts[1].strip()[:50]
                    unique_failures[key] = unique_failures.get(key, 0) + 1

        for key, count in list(unique_failures.items())[:5]:
            print(f"  {key} (x{count})")

    return issues


def check_output_files():
    """Check output files for issues."""
    print("\n" + "=" * 80)
    print("  CHECKING OUTPUT FILES")
    print("=" * 80 + "\n")

    issues = []
    outputs_dir = ROOT_DIR / "outputs"

    # Check PnL file
    pnl_file = outputs_dir / "pnl_live.json"
    if pnl_file.exists():
        try:
            pnl = json.load(open(pnl_file))
            total = pnl.get("total_pnl", 0)
            realized = pnl.get("total_realized_pnl", 0)
            unrealized = pnl.get("total_unrealized_pnl", 0)

            # Verify calculation
            expected = realized + unrealized
            if abs(total - expected) > 0.01:
                issues.append(f"PnL mismatch: total={total}, expected={expected}")
                print(f"[ISSUE] PnL calculation mismatch")
            else:
                print(f"[OK] PnL calculation correct: {total:.2f}")
        except Exception as e:
            issues.append(f"PnL file error: {e}")
            print(f"[ERROR] PnL file: {e}")
    else:
        print("[WARNING] PnL file not found")

    # Check trades CSV
    trades_file = outputs_dir / "paper_trades_live.csv"
    if trades_file.exists():
        try:
            df = pd.read_csv(trades_file)
            print(f"[OK] Trades CSV: {len(df)} rows")

            # Check for zero prices
            if "price" in df.columns:
                zero_prices = (df["price"] == 0).sum()
                if zero_prices > 0:
                    issues.append(f"Found {zero_prices} trades with zero price")
                    print(f"[ISSUE] {zero_prices} trades with zero price")
                else:
                    print(f"[OK] All trades have valid prices")

            # Check for missing data
            if "action" in df.columns:
                missing_action = df["action"].isna().sum()
                if missing_action > 0:
                    issues.append(f"Found {missing_action} trades with missing action")
                    print(f"[ISSUE] {missing_action} trades with missing action")
        except Exception as e:
            issues.append(f"Trades CSV error: {e}")
            print(f"[ERROR] Trades CSV: {e}")
    else:
        print("[WARNING] Trades CSV not found")

    # Check positions file
    pos_file = outputs_dir / "positions_live.json"
    if pos_file.exists():
        try:
            pos = json.load(open(pos_file))
            open_pos = pos.get("open_positions", [])
            print(f"[OK] Positions file: {len(open_pos)} open positions")

            # Check position data
            for p in open_pos:
                if p.get("current_price", 0) == 0:
                    issues.append(f"Position {p.get('position_id')} has zero current price")
        except Exception as e:
            issues.append(f"Positions file error: {e}")
            print(f"[ERROR] Positions file: {e}")
    else:
        print("[WARNING] Positions file not found")

    return issues


def check_data_quality():
    """Check data quality issues."""
    print("\n" + "=" * 80)
    print("  CHECKING DATA QUALITY")
    print("=" * 80 + "\n")

    issues = []

    # Check chain_raw CSV
    chain_file = ROOT_DIR / "outputs" / "chain_raw_live.csv"
    if chain_file.exists():
        try:
            df = pd.read_csv(chain_file, nrows=1000)  # Sample first 1000 rows
            print(f"[OK] Chain CSV: {len(df)} rows (sampled)")

            # Check for duplicate columns
            if len(df.columns) != len(set(df.columns)):
                issues.append("Duplicate columns in chain CSV")
                print("[ISSUE] Duplicate columns found")

            # Check for critical missing data
            critical_cols = ["ltp", "strike", "option_type", "underlying"]
            for col in critical_cols:
                if col in df.columns:
                    missing = df[col].isna().sum()
                    pct = (missing / len(df)) * 100 if len(df) > 0 else 0
                    if pct > 10:
                        issues.append(f"{col}: {pct:.1f}% missing")
                        print(f"[ISSUE] {col}: {pct:.1f}% missing")
                    else:
                        print(f"[OK] {col}: {pct:.1f}% missing")
        except Exception as e:
            issues.append(f"Chain CSV error: {e}")
            print(f"[ERROR] Chain CSV: {e}")

    return issues


def main():
    """Main checker."""
    print("\n" + "=" * 80)
    print("  COMPREHENSIVE ISSUE CHECKER")
    print("=" * 80)

    all_issues = []

    # Check logs
    all_issues.extend(check_logs())

    # Check output files
    all_issues.extend(check_output_files())

    # Check data quality
    all_issues.extend(check_data_quality())

    # Summary
    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80 + "\n")

    if all_issues:
        print(f"[WARNING] Found {len(all_issues)} issues:")
        for i, issue in enumerate(all_issues[:10], 1):
            print(f"  {i}. {issue}")
    else:
        print("[OK] No issues found - All systems operational")

    print("\n" + "=" * 80 + "\n")

    return len(all_issues) == 0


if __name__ == "__main__":
    main()
