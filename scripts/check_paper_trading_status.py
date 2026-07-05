"""Quick status check for paper trading"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

pnl_file = ROOT_DIR / "outputs" / "pnl_live.json"
positions_file = ROOT_DIR / "outputs" / "positions_live.json"
trades_file = ROOT_DIR / "outputs" / "paper_trades_live.csv"


def get_file_age(filepath):
    """Get file age in minutes."""
    if not filepath.exists():
        return None
    age = datetime.now() - datetime.fromtimestamp(filepath.stat().st_mtime)
    return age.total_seconds() / 60


def check_simulation_running():
    """Check if simulation process is running."""
    try:
        import subprocess

        result = subprocess.run(
            ["tasklist", "/FI", "WINDOWTITLE eq Paper Trading Sim*", "/NH"], capture_output=True, text=True
        )
        return "cmd.exe" in result.stdout or "python.exe" in result.stdout
    except:
        return None


print("\n" + "=" * 80)
print("  PAPER TRADING STATUS REPORT")
print("=" * 80 + "\n")

# Check simulation status
sim_running = check_simulation_running()
if sim_running is False:
    print("[INFO] Simulation appears to have stopped")
    print()

# Read PnL
if pnl_file.exists():
    pnl = json.load(open(pnl_file))
    pnl_age = get_file_age(pnl_file)

    print("PnL SUMMARY:")
    print("-" * 80)
    print(f"  Total PnL: Rs {pnl.get('total_pnl', 0):.2f}")
    print(f"  Unrealized: Rs {pnl.get('total_unrealized_pnl', 0):.2f}")
    print(f"  Realized: Rs {pnl.get('total_realized_pnl', 0):.2f}")
    print(f"  Open Positions: {pnl.get('open_positions', 0)}")
    print(f"  Total Trades: {pnl.get('total_trades', 0)}")
    print(f"  Winning: {pnl.get('winning_trades', 0)} | Losing: {pnl.get('losing_trades', 0)}")
    print(f"  Win Rate: {pnl.get('win_rate', 0):.1f}%")
    print(f"  Avg PnL per Trade: Rs {pnl.get('avg_pnl_per_trade', 0):.2f}")

    # Show data freshness
    if pnl_age is not None:
        if pnl_age < 1:
            print(f"  [Data updated: {int(pnl_age*60)}s ago - FRESH]")
        elif pnl_age < 5:
            print(f"  [Data updated: {int(pnl_age)}min ago - RECENT]")
        else:
            print(f"  [Data updated: {int(pnl_age)}min ago - STALE]")
    print()
else:
    print("[INFO] Waiting for data...")
    print()

# Read Positions
if positions_file.exists():
    pos = json.load(open(positions_file))
    open_pos = pos.get("open_positions", [])
    if open_pos:
        print(f"OPEN POSITIONS ({len(open_pos)}):")
        print("-" * 80)
        for i, p in enumerate(open_pos[:5], 1):
            print(f"  {i}. {p.get('underlying')} {p.get('strike')} {p.get('option_type')}")
            print(f"     Entry: Rs {p.get('entry_price', 0):.2f} | Current: Rs {p.get('current_price', 0):.2f}")
            pnl_val = p.get("unrealized_pnl", 0)
            pnl_pct = p.get("unrealized_pnl_pct", 0)
            status = "[PROFIT]" if pnl_val >= 0 else "[LOSS]"
            print(f"     {status} PnL: Rs {pnl_val:.2f} ({pnl_pct:.2f}%)")
        print()

# Read Trades
if trades_file.exists():
    try:
        df = pd.read_csv(trades_file, on_bad_lines="skip", engine="python")
        if not df.empty:
            print(f"TRADE HISTORY ({len(df)} trades):")
            print("-" * 80)
            recent = df.tail(5)
            for _, t in recent.iterrows():
                action = t.get("action", "N/A")
                underlying = t.get("underlying", "N/A")
                strike = t.get("strike", 0)
                opt_type = t.get("option_type", "")
                price = t.get("price", 0)
                print(f"  [{action}]: {underlying} {strike} {opt_type} @ Rs {price:.2f}")
            print()
    except Exception as e:
        print(f"[WARN] Could not read trades file: {str(e)[:50]}")
        print()

# System status
print("=" * 80)
if sim_running is True:
    print("  System Status: RUNNING (Simulation active)")
elif sim_running is False:
    print("  System Status: STOPPED (Simulation finished)")
else:
    print("  System Status: UNKNOWN")
print("=" * 80)
