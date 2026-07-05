"""
Show Practical Results - Complete System Output
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

print("\n" + "=" * 80)
print("  PRACTICAL TEST RESULTS - COMPLETE SYSTEM OUTPUT")
print("=" * 80 + "\n")

# Check PnL
pnl_file = ROOT_DIR / "outputs" / "pnl_live.json"
if pnl_file.exists():
    pnl = json.load(open(pnl_file))
    print("PnL SUMMARY:")
    print("-" * 80)
    print(f"  Total PnL: Rs {pnl.get('total_pnl', 0):.2f}")
    print(f"  Realized: Rs {pnl.get('total_realized_pnl', 0):.2f}")
    print(f"  Unrealized: Rs {pnl.get('total_unrealized_pnl', 0):.2f}")
    print(f"  Total Trades: {pnl.get('total_trades', 0)}")
    print(f"  Winning: {pnl.get('winning_trades', 0)}")
    print(f"  Losing: {pnl.get('losing_trades', 0)}")
    print(f"  Win Rate: {pnl.get('win_rate', 0):.1f}%")
    print(f"  Avg PnL/Trade: Rs {pnl.get('avg_pnl_per_trade', 0):.2f}")
    print(f"  Max Profit: Rs {pnl.get('max_profit', 0):.2f}")
    print(f"  Max Drawdown: Rs {pnl.get('max_drawdown', 0):.2f}")
    print(f"  Open Positions: {pnl.get('open_positions', 0)}")
    print()
else:
    print("[WARNING] PnL file not found\n")

# Check Positions
pos_file = ROOT_DIR / "outputs" / "positions_live.json"
if pos_file.exists():
    pos = json.load(open(pos_file))
    open_pos = pos.get("open_positions", [])
    print(f"OPEN POSITIONS: {len(open_pos)}")
    print("-" * 80)
    if open_pos:
        for i, p in enumerate(open_pos[:10], 1):
            underlying = p.get("underlying", "N/A")
            strike = p.get("strike", 0)
            opt = p.get("option_type", "N/A")
            entry = p.get("entry_price", 0)
            current = p.get("current_price", 0)
            pnl_val = p.get("unrealized_pnl", 0)
            print(f"  {i}. {underlying} {strike} {opt}")
            print(f"     Entry: Rs {entry:.2f} | Current: Rs {current:.2f} | PnL: Rs {pnl_val:.2f}")
    else:
        print("  No open positions")
    print()
else:
    print("[WARNING] Positions file not found\n")

# Check Trades CSV
trades_file = ROOT_DIR / "outputs" / "paper_trades_live.csv"
if trades_file.exists():
    try:
        df = pd.read_csv(trades_file, on_bad_lines="skip", engine="python")
    except:
        # Try reading with error handling
        try:
            df = pd.read_csv(trades_file, error_bad_lines=False, warn_bad_lines=False)
        except:
            df = pd.DataFrame()
    print(f"TRADE HISTORY: {len(df)} total positions")
    print("-" * 80)

    if "status" in df.columns:
        closed = df[df["status"] == "CLOSED"]
        open_pos = df[df["status"] == "OPEN"]
        print(f"  Closed: {len(closed)}")
        print(f"  Open: {len(open_pos)}")
        print()

        if len(closed) > 0:
            print("RECENT CLOSED TRADES:")
            print("-" * 80)
            for i, row in closed.tail(10).iterrows():
                underlying = row.get("underlying", "N/A")
                strike = row.get("strike", 0)
                opt = row.get("option_type", "N/A")
                entry = row.get("entry_price", 0)
                exit_price = row.get("exit_price", 0)
                pnl_val = row.get("realized_pnl", 0)
                pnl_pct = row.get("realized_pnl_pct", 0)
                reason = row.get("exit_reason", "N/A")
                timestamp = row.get("exit_time_ist", "N/A")

                print(f"  {underlying} {strike} {opt}")
                print(
                    f"    Entry: Rs {entry:.2f} | Exit: Rs {exit_price:.2f} | PnL: Rs {pnl_val:.2f} ({pnl_pct:.2f}%) | {reason}"
                )
                print(f"    Closed: {timestamp}")
                print()
    else:
        print("  [INFO] CSV format detected - showing sample rows")
        print("  Last 5 rows:")
        for i, row in df.tail(5).iterrows():
            print(f"    Row {i+1}: {dict(row)}")
else:
    print("[WARNING] Trades CSV not found\n")

# Check QC Report
qc_file = ROOT_DIR / "outputs" / "qc_report_live.json"
if qc_file.exists():
    qc = json.load(open(qc_file))
    print("QC STATUS:")
    print("-" * 80)
    print(f"  Overall: {'PASS' if qc.get('overall_passed') else 'FAIL'}")
    print()
    if "underlying_results" in qc:
        for underlying, result in qc["underlying_results"].items():
            status = "PASS" if result.get("passed") else "FAIL"
            print(f"  {underlying}: {status}")
            if result.get("reasons"):
                for reason in result["reasons"]:
                    print(f"    - {reason}")
    print()

# Check Trade Signal
signal_file = ROOT_DIR / "outputs" / "top_trade_signal.json"
if signal_file.exists():
    signal = json.load(open(signal_file))
    print("LATEST TRADE SIGNAL:")
    print("-" * 80)
    print(f"  Action: {signal.get('action', 'N/A')}")
    print(f"  Underlying: {signal.get('underlying', 'N/A')}")
    print(f"  Strategy: {signal.get('strategy', 'N/A')}")
    print(f"  Confidence: {signal.get('confidence', 0)*100:.1f}%")
    print()

print("=" * 80)
print("  END OF RESULTS")
print("=" * 80 + "\n")
