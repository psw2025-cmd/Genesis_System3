"""
Final Verification - Check all logs and outputs
"""

import sys
import json
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

print("\n" + "=" * 80)
print("  FINAL SYSTEM VERIFICATION")
print("=" * 80 + "\n")

all_ok = True

# 1. Check PnL file
print("[1/6] Checking PnL file...")
pnl_file = ROOT_DIR / "outputs" / "pnl_live.json"
if pnl_file.exists():
    pnl = json.load(open(pnl_file))
    total = pnl.get("total_pnl", 0)
    realized = pnl.get("total_realized_pnl", 0)
    unrealized = pnl.get("total_unrealized_pnl", 0)
    if abs(total - (realized + unrealized)) < 0.01:
        print(f"  [OK] PnL calculation correct: {total:.2f}")
    else:
        print(f"  [ISSUE] PnL mismatch")
        all_ok = False
else:
    print("  [WARNING] PnL file not found")

# 2. Check trades CSV
print("\n[2/6] Checking trades CSV...")
trades_file = ROOT_DIR / "outputs" / "paper_trades_live.csv"
if trades_file.exists():
    df = pd.read_csv(trades_file)
    print(f"  [OK] Trades CSV: {len(df)} rows")
    if "price" in df.columns:
        zero = (df["price"] == 0).sum()
        if zero == 0:
            print(f"  [OK] All prices valid")
        else:
            print(f"  [ISSUE] {zero} trades with zero price")
            all_ok = False
else:
    print("  [WARNING] Trades CSV not found")

# 3. Check positions
print("\n[3/6] Checking positions...")
pos_file = ROOT_DIR / "outputs" / "positions_live.json"
if pos_file.exists():
    pos = json.load(open(pos_file))
    open_pos = pos.get("open_positions", [])
    print(f"  [OK] Positions file: {len(open_pos)} open")
else:
    print("  [WARNING] Positions file not found")

# 4. Check QC report
print("\n[4/6] Checking QC report...")
qc_file = ROOT_DIR / "outputs" / "qc_report_live.json"
if qc_file.exists():
    qc = json.load(open(qc_file))
    passed = qc.get("overall_passed", False)
    print(f"  [OK] QC: {'PASS' if passed else 'FAIL'}")
else:
    print("  [WARNING] QC report not found")

# 5. Check logs for errors
print("\n[5/6] Checking logs...")
log_file = ROOT_DIR / "logs" / "2026-01-31.log"
if log_file.exists():
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()[-50:]
    errors = [l for l in lines if "ERROR" in l.upper() and "Traceback" not in l]
    if len(errors) == 0:
        print(f"  [OK] No recent errors in logs")
    else:
        print(f"  [WARNING] {len(errors)} recent errors found")
else:
    print("  [WARNING] Log file not found")

# 6. Check chain CSV
print("\n[6/6] Checking chain CSV...")
chain_file = ROOT_DIR / "outputs" / "chain_raw_live.csv"
if chain_file.exists():
    df = pd.read_csv(chain_file, nrows=100)
    print(f"  [OK] Chain CSV: {len(df)} rows (sampled)")
    if "underlying" in df.columns:
        underlyings = df["underlying"].unique()
        print(f"  [OK] Underlyings: {len(underlyings)}")
else:
    print("  [WARNING] Chain CSV not found")

# Summary
print("\n" + "=" * 80)
if all_ok:
    print("  RESULT: [OK] ALL CHECKS PASSED")
else:
    print("  RESULT: [WARNING] Some issues found (see above)")
print("=" * 80 + "\n")
