"""
Quick check of monitor output format
"""

import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

print("\n" + "=" * 80)
print("  MONITOR OUTPUT VERIFICATION")
print("=" * 80 + "\n")

# Read CSV
trades_file = ROOT_DIR / "outputs" / "paper_trades_live.csv"
if trades_file.exists():
    df = pd.read_csv(trades_file)
    print(f"Total positions: {len(df)}")
    print(f"\nSample of how monitor will display:\n")
    print("-" * 80)

    # Show last 3 positions
    recent = df.tail(3)
    for _, trade in recent.iterrows():
        underlying = trade.get("underlying", "N/A")
        strike = trade.get("strike", 0)
        opt_type = trade.get("option_type", "")

        # Detect format: position-level (has 'status') or trade-level (has 'action')
        if "action" in trade and pd.notna(trade.get("action")):
            # Trade-level format (OPEN/CLOSE events)
            action = str(trade.get("action", "N/A"))
            price = float(trade.get("price", 0))
            qty = trade.get("qty", 0)
            if pd.isna(qty):
                qty = 0
            timestamp = trade.get("time_ist", "N/A")
            if pd.isna(timestamp) or timestamp == "N/A":
                timestamp = trade.get("timestamp", "N/A")

            # Get PnL if available
            pnl = trade.get("realized_pnl", trade.get("unrealized_pnl", 0))
            pnl_pct = trade.get("realized_pnl_pct", trade.get("unrealized_pnl_pct", 0))
            reason = trade.get("exit_reason", "")

            status_display = "[OPEN]" if action == "OPEN" else "[CLOSE]"
        else:
            # Position-level format (has 'status')
            status = trade.get("status", "N/A")

            # Get price - use exit_price if closed, entry_price if open
            if status == "CLOSED":
                if pd.notna(trade.get("exit_price")):
                    price = float(trade.get("exit_price", 0))
                    timestamp = trade.get("exit_time_ist", "N/A")
                    if pd.isna(timestamp) or timestamp == "N/A":
                        timestamp = trade.get("exit_timestamp", "N/A")
                    pnl = trade.get("realized_pnl", 0)
                    pnl_pct = trade.get("realized_pnl_pct", 0)
                    reason = trade.get("exit_reason", "")
                else:
                    price = float(trade.get("entry_price", 0))
                    timestamp = trade.get("entry_time_ist", "N/A")
                    pnl = trade.get("realized_pnl", 0)
                    pnl_pct = trade.get("realized_pnl_pct", 0)
                    reason = trade.get("exit_reason", "")
            else:
                # Open position
                price = float(trade.get("entry_price", 0))
                timestamp = trade.get("entry_time_ist", "N/A")
                if pd.isna(timestamp) or timestamp == "N/A":
                    timestamp = trade.get("entry_timestamp", "N/A")
                pnl = trade.get("unrealized_pnl", 0)
                pnl_pct = trade.get("unrealized_pnl_pct", 0)
                reason = ""

            qty = trade.get("qty", 0)
            if pd.isna(qty):
                qty = 0

            status_display = "[CLOSED]" if status == "CLOSED" else "[OPEN]"

        # Format PnL display - handle NaN
        if pd.notna(pnl) and pnl != 0:
            if pd.notna(pnl_pct):
                pnl_display = f" | PnL: Rs {pnl:.2f} ({pnl_pct:.2f}%)"
            else:
                pnl_display = f" | PnL: Rs {pnl:.2f}"
        else:
            pnl_display = ""

        reason_display = f" | {reason}" if reason else ""

        print(
            f"  {status_display} {underlying} {strike} {opt_type} | "
            f"Price: Rs {price:.2f} | Qty: {int(qty)}{pnl_display}{reason_display} | {timestamp}"
        )

    print("-" * 80)
    print("\n[OK] Monitor output format verified")
else:
    print("[WARNING] Trades CSV not found")

print("\n" + "=" * 80 + "\n")
