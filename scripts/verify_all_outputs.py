"""
Verify All Outputs - Simple checker without encoding issues
"""

import sys
import json
import os
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

print("\n" + "=" * 80)
print("  COMPREHENSIVE OUTPUT VERIFICATION")
print("=" * 80 + "\n")

issues = []

# Check PnL file
pnl_file = ROOT_DIR / "outputs" / "pnl_live.json"
if pnl_file.exists():
    try:
        pnl = json.load(open(pnl_file))
        total = pnl.get("total_pnl", 0)
        realized = pnl.get("total_realized_pnl", 0)
        unrealized = pnl.get("total_unrealized_pnl", 0)
        expected = realized + unrealized

        if abs(total - expected) > 0.01:
            issues.append(f"PnL mismatch: total={total:.2f}, expected={expected:.2f}")
            print(f"[ISSUE] PnL calculation mismatch")
        else:
            print(f"[OK] PnL calculation: {total:.2f}")
        print(f"  Realized: {realized:.2f}, Unrealized: {unrealized:.2f}")
    except Exception as e:
        issues.append(f"PnL file error: {e}")
        print(f"[ERROR] PnL file: {e}")
else:
    print("[WARNING] PnL file not found")

# Check trades CSV
trades_file = ROOT_DIR / "outputs" / "paper_trades_live.csv"
if trades_file.exists():
    try:
        df = pd.read_csv(trades_file)
        print(f"\n[OK] Trades CSV: {len(df)} rows")

        if "price" in df.columns:
            zero_prices = (df["price"] == 0).sum()
            if zero_prices > 0:
                issues.append(f"{zero_prices} trades with zero price")
                print(f"[ISSUE] {zero_prices} trades with zero price")
            else:
                print(f"[OK] All trades have valid prices")

        if "action" in df.columns:
            actions = df["action"].value_counts()
            print(f"  Actions: {dict(actions)}")
    except Exception as e:
        issues.append(f"Trades CSV error: {e}")
        print(f"[ERROR] Trades CSV: {e}")
else:
    print("[WARNING] Trades CSV not found")

# Check positions
pos_file = ROOT_DIR / "outputs" / "positions_live.json"
if pos_file.exists():
    try:
        pos = json.load(open(pos_file))
        open_pos = pos.get("open_positions", [])
        print(f"\n[OK] Positions: {len(open_pos)} open")

        for p in open_pos:
            if p.get("current_price", 0) == 0:
                issues.append(f"Position {p.get('position_id')} has zero price")
    except Exception as e:
        issues.append(f"Positions error: {e}")
        print(f"[ERROR] Positions: {e}")
else:
    print("[WARNING] Positions file not found")

# Check QC report
qc_file = ROOT_DIR / "outputs" / "qc_report_live.json"
if qc_file.exists():
    try:
        qc = json.load(open(qc_file))
        passed = qc.get("overall_passed", False)
        print(f"\n[OK] QC Report: {'PASS' if passed else 'FAIL'}")
    except Exception as e:
        issues.append(f"QC report error: {e}")
        print(f"[ERROR] QC report: {e}")
else:
    print("[WARNING] QC report not found")

# Summary
print("\n" + "=" * 80)
if issues:
    print(f"[WARNING] Found {len(issues)} issues:")
    for i, issue in enumerate(issues[:10], 1):
        print(f"  {i}. {issue}")
else:
    print("[OK] No issues found - All outputs valid")
print("=" * 80 + "\n")
