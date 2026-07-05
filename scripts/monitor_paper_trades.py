"""
Monitor Paper Trades - Real-time paper trading status
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

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
    """Main monitoring loop."""
    outputs_dir = ROOT_DIR / "outputs"
    pnl_file = outputs_dir / "pnl_live.json"
    positions_file = outputs_dir / "positions_live.json"
    trades_file = outputs_dir / "paper_trades_live.csv"
    signal_file = outputs_dir / "top_trade_signal.json"

    print("\n" + "=" * 80)
    print("  PAPER TRADING MONITOR - Real-Time Status")
    print("=" * 80)
    print("\nPress Ctrl+C to stop monitoring\n")
    time.sleep(2)

    try:
        while True:
            clear_screen()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("\n" + "=" * 80)
            print(f"  PAPER TRADING MONITOR - {now}")
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
            print("💰 PnL SUMMARY:")
            print("-" * 80)
            if pnl_data:
                total_pnl = pnl_data.get("total_pnl", 0.0)
                unrealized = pnl_data.get("total_unrealized_pnl", 0.0)
                realized = pnl_data.get("total_realized_pnl", 0.0)
                total_trades = pnl_data.get("total_trades", 0)
                win_rate = pnl_data.get("win_rate", 0.0)
                open_count = pnl_data.get("open_positions", 0)

                pnl_icon = "🟢" if total_pnl >= 0 else "🔴"
                print(f"  {pnl_icon} Total PnL: ₹{total_pnl:.2f}")
                print(f"     Unrealized: ₹{unrealized:.2f} | Realized: ₹{realized:.2f}")
                print(f"  📊 Total Trades: {total_trades} | Win Rate: {win_rate:.1f}%")
                print(f"  📈 Open Positions: {open_count}")
            else:
                print("  ⏳ Waiting for data...")
            print()

            # Display Open Positions
            open_positions = positions_data.get("open_positions", [])
            if open_positions:
                print(f"📋 OPEN POSITIONS ({len(open_positions)}):")
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

                    pnl_icon = "🟢" if pnl >= 0 else "🔴"
                    print(f"  {i}. {underlying} {strike} {opt_type} ({strategy})")
                    print(
                        f"     Entry: ₹{entry:.2f} | Current: ₹{current:.2f} | "
                        f"{pnl_icon} PnL: ₹{pnl:.2f} ({pnl_pct:.2f}%)"
                    )
                if len(open_positions) > 10:
                    print(f"     ... and {len(open_positions) - 10} more positions")
                print()

            # Display Recent Trades
            if not trades_df.empty:
                print(f"📝 RECENT TRADES ({len(trades_df)} total):")
                print("-" * 80)
                recent = trades_df.tail(5)
                for _, trade in recent.iterrows():
                    action = trade.get("action", "N/A")
                    underlying = trade.get("underlying", "N/A")
                    strike = trade.get("strike", 0)
                    opt_type = trade.get("option_type", "")
                    price = trade.get("price", 0)
                    qty = trade.get("qty", 0)
                    timestamp = trade.get("time_ist", trade.get("timestamp", "N/A"))

                    action_icon = "✅ OPEN" if action == "OPEN" else "❌ CLOSE"
                    print(
                        f"  {action_icon} {underlying} {strike} {opt_type} | "
                        f"Price: ₹{price:.2f} | Qty: {qty} | {timestamp}"
                    )
                print()

            # Display Latest Signal
            if signal_data:
                print("🎯 LATEST TRADE SIGNAL:")
                print("-" * 80)
                action = signal_data.get("action", "N/A")
                underlying = signal_data.get("underlying", "N/A")
                strategy = signal_data.get("strategy", "N/A")
                confidence = signal_data.get("confidence", 0)

                action_icon = "✅" if action == "TRADE" else "⏸️"
                print(f"  {action_icon} Action: {action}")
                print(f"  📈 Underlying: {underlying}")
                print(f"  🎲 Strategy: {strategy}")
                print(f"  💡 Confidence: {confidence*100:.1f}%")
                print()

            print("=" * 80)
            print("  Refreshing every 3 seconds... (Press Ctrl+C to stop)")
            print("=" * 80)

            time.sleep(3)

    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
