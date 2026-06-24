"""Quick check if system is running and generating data"""

import os
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

print("=" * 80)
print("  SYSTEM STATUS CHECK")
print("=" * 80)
print()

# Check files
files_to_check = [
    ("outputs/chain_raw_live.csv", "Data File"),
    ("outputs/pnl_summary.json", "PnL Summary"),
    ("outputs/paper_trades.csv", "Trades File"),
    ("outputs/top_trade_signal.json", "Trade Signal"),
    ("logs/run.log", "Log File"),
]

print("[FILE STATUS]")
print("-" * 80)
all_exist = True
for file_path, name in files_to_check:
    full_path = ROOT_DIR / file_path
    if full_path.exists():
        mod_time = datetime.fromtimestamp(full_path.stat().st_mtime)
        age = (datetime.now() - mod_time).total_seconds()
        status = "[OK]" if age < 60 else "[OLD]"
        print(f"  {status} {name:20s}: EXISTS (updated {int(age)}s ago)")
    else:
        print(f"  [MISS] {name:20s}: NOT FOUND")
        all_exist = False

print()
print("[RECOMMENDATION]")
print("-" * 80)

if all_exist:
    print("  [OK] System is working - files are being created")
    print("  [OK] KEEP BOTH BATCH FILES RUNNING")
    print("  [OK] Monitor will update as data comes in")
else:
    print("  [WAIT] Some files not found yet")
    print("  [WAIT] System may still be initializing")
    print("  [OK] KEEP RUNNING - First cycle may take 30-60 seconds")
    print("  [OK] Check paper trading window for activity")

print()
print("=" * 80)
