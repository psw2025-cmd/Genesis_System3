"""
Monitor Paper Trading for 10 Minutes
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def read_json_safe(filepath):
    """Safely read JSON file."""
    try:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        pass
    return {}


def clear_screen():
    """Clear terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def main():
    """Main monitoring loop for 10 minutes."""
    outputs_dir = ROOT_DIR / "outputs"
    pnl_file = outputs_dir / "pnl_live.json"
    positions_file = outputs_dir / "positions_live.json"
    trades_file = outputs_dir / "paper_trades_live.csv"
    signal_file = outputs_dir / "top_trade_signal.json"

    print("\n" + "=" * 80)
    print("  PAPER TRADING MONITOR - 10 MINUTES")
    print("=" * 80)
    print("\nMonitoring for 10 minutes...")
    print("Press Ctrl+C to stop early\n")
    time.sleep(2)

    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=10)
    cycle = 0

    try:
        while datetime.now() < end_time:
            cycle += 1
            elapsed = (datetime.now() - start_time).total_seconds()
            remaining = 600 - elapsed

            clear_screen()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("\n" + "=" * 80)
            print(f"  PAPER TRADING MONITOR - {now}")
            print(
                f"  Elapsed: {int(elapsed/60)}m {int(elapsed%60)}s | Remaining: {int(remaining/60)}m {int(remaining%60)}s | Cycle: {cycle}"
            )
            print("=" * 80 + "\n")

            # Read PnL data
            pnl_data = read_json_safe(pnl_file)
            positions_data = read_json_safe(positions_file)
            signal_data = read_json_safe(signal_file)

            # Read trades CSV
            trades_df = pd.DataFrame()
            if trades_file.exists():
                try:
                    trades_df = pd.read_csv(trades_file)
                except:
                    pass

            # Display PnL Summary
            print("PnL SUMMARY:")
            print("-" * 80)
            if pnl_data:
                total_pnl = pnl_data.get("total_pnl", 0.0)
                unrealized = pnl_data.get("total_unrealized_pnl", 0.0)
                realized = pnl_data.get("total_realized_pnl", 0.0)
                total_trades = pnl_data.get("total_trades", 0)
                win_rate = pnl_data.get("win_rate", 0.0)
                open_count = pnl_data.get("open_positions", 0)

                pnl_status = "[PROFIT]" if total_pnl >= 0 else "[LOSS]"
                print(f"  {pnl_status} Total PnL: Rs {total_pnl:.2f}")
                print(f"     Unrealized: Rs {unrealized:.2f} | Realized: Rs {realized:.2f}")
                print(f"  Total Trades: {total_trades} | Win Rate: {win_rate:.1f}%")
                print(f"  Open Positions: {open_count}")
            else:
                print("  Waiting for data...")
            print()

            # Display Open Positions
            open_positions = positions_data.get("open_positions", [])
            if open_positions:
                print(f"OPEN POSITIONS ({len(open_positions)}):")
                print("-" * 80)
                for i, pos in enumerate(open_positions[:10], 1):
                    underlying = pos.get("underlying", "N/A")
                    strike = pos.get("strike", 0)
                    opt_type = pos.get("option_type", "")
                    entry = pos.get("entry_price", 0)
                    current = pos.get("current_price", 0)
                    pnl = pos.get("unrealized_pnl", 0)
                    pnl_pct = pos.get("unrealized_pnl_pct", 0)
                    strategy = pos.get("strategy", "")

                    pnl_status = "[PROFIT]" if pnl >= 0 else "[LOSS]"
                    print(f"  {i}. {underlying} {strike} {opt_type} ({strategy})")
                    print(
                        f"     Entry: Rs {entry:.2f} | Current: Rs {current:.2f} | "
                        f"{pnl_status} PnL: Rs {pnl:.2f} ({pnl_pct:.2f}%)"
                    )
                if len(open_positions) > 10:
                    print(f"     ... and {len(open_positions) - 10} more positions")
                print()

            # Display Recent Trades
            if not trades_df.empty:
                print(f"RECENT TRADES ({len(trades_df)} total):")
                print("-" * 80)
                recent = trades_df.tail(5)
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
                print()

            # Display Latest Signal
            if signal_data:
                print("LATEST TRADE SIGNAL:")
                print("-" * 80)
                action = signal_data.get("action", "N/A")
                underlying = signal_data.get("underlying", "N/A")
                strategy = signal_data.get("strategy", "N/A")
                confidence = signal_data.get("confidence", 0)

                action_status = "[TRADE]" if action == "TRADE" else "[NO TRADE]"
                print(f"  {action_status} Action: {action}")
                print(f"  Underlying: {underlying}")
                print(f"  Strategy: {strategy}")
                print(f"  Confidence: {confidence*100:.1f}%")
                print()

            print("=" * 80)
            print(f"  Next update in 3 seconds... ({int(remaining)}s remaining)")
            print("=" * 80)

            time.sleep(3)

        # Final summary
        clear_screen()
        print("\n" + "=" * 80)
        print("  10 MINUTE MONITOR COMPLETE")
        print("=" * 80 + "\n")

        # Final status
        pnl_data = read_json_safe(pnl_file)
        if pnl_data:
            print("FINAL STATUS:")
            print("-" * 80)
            print(f"  Total PnL: Rs {pnl_data.get('total_pnl', 0):.2f}")
            print(f"  Total Trades: {pnl_data.get('total_trades', 0)}")
            print(f"  Win Rate: {pnl_data.get('win_rate', 0):.1f}%")
            print(f"  Open Positions: {pnl_data.get('open_positions', 0)}")
            print()

        print("=" * 80)
        print("  Monitor completed successfully")
        print("=" * 80 + "\n")

    except KeyboardInterrupt:
        print("\n\nMonitor stopped by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
