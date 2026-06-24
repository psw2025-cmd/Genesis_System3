"""
Profit-Focused Monitor - Shows only what user cares about: PnL, Trades, Profit
All background processes run automatically - user only sees results.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytz

# Fix Unicode encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def clear_screen():
    """Clear console screen."""
    os.system("cls" if os.name == "nt" else "clear")


def get_latest_trades():
    """Get latest trades from history."""
    trades_file = ROOT_DIR / "outputs" / "paper_trades_live.csv"
    if trades_file.exists():
        try:
            df = pd.read_csv(trades_file)
            if len(df) > 0:
                # Get last 5 trades
                return df.tail(5).to_dict("records")
        except:
            pass
    return []


def get_pnl_summary():
    """Get PnL summary from file."""
    pnl_file = ROOT_DIR / "outputs" / "pnl_live.json"
    if pnl_file.exists():
        try:
            with open(pnl_file, "r") as f:
                data = json.load(f)
                # Get trades for calculations
                trades = get_latest_trades()

                # Calculate additional metrics
                winning = data.get("winning_trades", 0)
                losing = data.get("losing_trades", 0)
                realized = data.get("total_realized_pnl", 0.0)

                # Calculate average win/loss from trades
                if trades:
                    wins = [t.get("realized_pnl", 0) for t in trades if t.get("realized_pnl", 0) > 0]
                    losses = [abs(t.get("realized_pnl", 0)) for t in trades if t.get("realized_pnl", 0) < 0]
                    avg_win = (sum(wins) / len(wins)) if wins else 0.0
                    avg_loss = (sum(losses) / len(losses)) if losses else 0.0
                    total_wins = sum(wins)
                    total_losses = sum(losses)
                    profit_factor = (
                        (total_wins / total_losses) if total_losses > 0 else (total_wins if total_wins > 0 else 0.0)
                    )
                else:
                    # Fallback to simple calculation
                    avg_win = (realized / winning) if winning > 0 else 0.0
                    avg_loss = (realized / losing) if losing > 0 else 0.0
                    profit_factor = 0.0

                data["avg_win"] = avg_win
                data["avg_loss"] = avg_loss
                data["profit_factor"] = profit_factor
                return data
        except Exception as e:
            pass
    return {
        "total_pnl": 0.0,
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "win_rate": 0.0,
        "open_positions": 0,
        "realized_pnl": 0.0,
        "unrealized_pnl": 0.0,
        "avg_win": 0.0,
        "avg_loss": 0.0,
        "profit_factor": 0.0,
    }


def get_latest_trades():
    """Get latest trades from history."""
    trades_file = ROOT_DIR / "outputs" / "paper_trades_live.csv"
    if trades_file.exists():
        try:
            df = pd.read_csv(trades_file)
            if len(df) > 0:
                # Get last 5 trades
                return df.tail(5).to_dict("records")
        except:
            pass
    return []


def get_open_positions():
    """Get open positions from paper executor or history."""
    # Try to get from positions file if it exists (primary source)
    positions_file = ROOT_DIR / "outputs" / "positions_live.json"
    if positions_file.exists():
        try:
            with open(positions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    positions = data.get("open_positions", [])
                    if positions:
                        return positions
                elif isinstance(data, list):
                    return data
        except Exception as e:
            pass

    # Fallback: try alternate filename
    alt_positions_file = ROOT_DIR / "outputs" / "paper_positions_live.json"
    if alt_positions_file.exists():
        try:
            with open(alt_positions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    positions = data.get("open_positions", [])
                    if positions:
                        return positions
                elif isinstance(data, list):
                    return data
        except:
            pass

    # Fallback: try to get from trade history
    trades_file = ROOT_DIR / "outputs" / "paper_trades_live.csv"
    if trades_file.exists():
        try:
            df = pd.read_csv(trades_file, on_bad_lines="skip", engine="python")
            if not df.empty:
                # Get positions that are OPEN but not yet CLOSED
                open_trades = df[df["action"] == "OPEN"]
                closed_trades = set(
                    df[df["action"] == "CLOSE"]["position_id"].unique() if "position_id" in df.columns else []
                )

                if len(open_trades) > 0:
                    # Get latest open trade for each position_id that hasn't been closed
                    positions = []
                    seen_ids = set()
                    for _, row in open_trades.iterrows():
                        pos_id = row.get("position_id", "")
                        if pos_id and pos_id not in closed_trades and pos_id not in seen_ids:
                            seen_ids.add(pos_id)
                            positions.append(
                                {
                                    "position_id": pos_id,
                                    "underlying": row.get("underlying", "N/A"),
                                    "strike": row.get("strike", "N/A"),
                                    "option_type": row.get("option_type", "N/A"),
                                    "entry_price": float(row.get("price", 0)),
                                    "current_price": float(row.get("price", 0)),  # Will be updated
                                    "unrealized_pnl": 0.0,
                                }
                            )
                    return positions
        except Exception as e:
            pass

    return []


def get_system_status():
    """Check if system is running."""
    # Check if data file is recent (updated in last 30 seconds)
    data_file = ROOT_DIR / "outputs" / "chain_raw_live.csv"
    if data_file.exists():
        age = time.time() - data_file.stat().st_mtime
        if age < 30:
            return "LIVE", "System running - Data updating"
        elif age < 300:
            return "SLOW", f"Data stale ({int(age/60)} min old)"
        else:
            return "STALE", f"Data very old ({int(age/60)} min old)"
    return "WAITING", "Waiting for first data fetch..."


def format_currency(amount):
    """Format currency with proper sign."""
    if amount >= 0:
        return f"Rs {amount:,.2f}"
    else:
        return f"-Rs {abs(amount):,.2f}"


def main():
    """Main monitor loop."""
    print("=" * 80)
    print("  FULLY AUTOMATED PAPER TRADING - PROFIT MONITOR")
    print("=" * 80)
    print()
    print("  [AUTOMATED] All background processes running")
    print("  [FOCUS] Showing only: PnL, Trades, Profit")
    print()
    print("  Press Ctrl+C to stop")
    print()
    print("=" * 80)
    print()

    cycle = 0

    try:
        while True:
            cycle += 1
            ist = pytz.timezone("Asia/Kolkata")
            now = datetime.now(ist)

            # Get data
            pnl = get_pnl_summary()
            trades = get_latest_trades()
            positions = get_open_positions()
            status, status_msg = get_system_status()

            # Clear and redraw
            clear_screen()

            print("=" * 80)
            print(f"  AUTOMATED PAPER TRADING - PROFIT MONITOR")
            print(f"  Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')} | Cycle: {cycle}")
            print("=" * 80)
            print()

            # System Status
            status_icon = "🟢" if status == "LIVE" else "🟡" if status == "SLOW" else "🔴"
            print(f"[SYSTEM STATUS] {status_icon} {status}: {status_msg}")
            print()

            # PnL Summary (Main Focus)
            print("=" * 80)
            print("  💰 PROFIT & LOSS SUMMARY")
            print("=" * 80)
            print()

            total_pnl = pnl.get("total_pnl", 0)
            pnl_icon = "🟢" if total_pnl >= 0 else "🔴"

            print(f"  Total PnL:        {pnl_icon} {format_currency(total_pnl)}")
            print(f"  Realized PnL:    {format_currency(pnl.get('realized_pnl', 0))}")
            print(f"  Unrealized PnL:  {format_currency(pnl.get('unrealized_pnl', 0))}")
            print()

            # Trading Statistics
            print("=" * 80)
            print("  📊 TRADING STATISTICS")
            print("=" * 80)
            print()

            total_trades = pnl.get("total_trades", 0)
            winning = pnl.get("winning_trades", 0)
            losing = pnl.get("losing_trades", 0)
            win_rate = pnl.get("win_rate", 0.0)

            print(f"  Total Trades:     {total_trades}")
            print(f"  Winning Trades:   🟢 {winning}")
            print(f"  Losing Trades:    🔴 {losing}")
            print(f"  Win Rate:         {win_rate:.1f}%")
            print(f"  Open Positions:   {pnl.get('open_positions', 0)}")
            print()

            # Open Positions
            if positions:
                print("=" * 80)
                print("  📈 OPEN POSITIONS")
                print("=" * 80)
                print()
                for i, pos in enumerate(positions[:5], 1):
                    underlying = pos.get("underlying", "N/A")
                    strike = pos.get("strike", "N/A")
                    option_type = pos.get("option_type", "N/A")
                    entry_price = pos.get("entry_price", 0)
                    current_price = pos.get("current_price", 0)
                    unrealized_pnl = pos.get("unrealized_pnl", 0)
                    pnl_icon = "🟢" if unrealized_pnl >= 0 else "🔴"

                    print(f"  [{i}] {underlying} {strike} {option_type}")
                    print(f"      Entry: {format_currency(entry_price)} | Current: {format_currency(current_price)}")
                    print(f"      Unrealized PnL: {pnl_icon} {format_currency(unrealized_pnl)}")
                    print()

            # Latest Trades
            if trades:
                print("=" * 80)
                print("  📋 LATEST TRADES (Last 5)")
                print("=" * 80)
                print()
                for i, trade in enumerate(reversed(trades[-5:]), 1):
                    action = trade.get("action", "N/A")
                    underlying = trade.get("underlying", "N/A")
                    strike = trade.get("strike", "N/A")
                    option_type = trade.get("option_type", "N/A")
                    price = trade.get("price", 0)
                    pnl_val = trade.get("realized_pnl", 0)
                    pnl_icon = "🟢" if pnl_val >= 0 else "🔴"

                    print(f"  [{i}] {action}: {underlying} {strike} {option_type} @ {format_currency(price)}")
                    if pnl_val != 0:
                        print(f"      PnL: {pnl_icon} {format_currency(pnl_val)}")
                    print()

            # Performance Metrics
            if total_trades > 0:
                print("=" * 80)
                print("  📈 PERFORMANCE METRICS")
                print("=" * 80)
                print()

                # Calculate from trades if available
                if trades:
                    wins = [t.get("realized_pnl", 0) for t in trades if t.get("realized_pnl", 0) > 0]
                    losses = [abs(t.get("realized_pnl", 0)) for t in trades if t.get("realized_pnl", 0) < 0]

                    avg_win = (sum(wins) / len(wins)) if wins else 0
                    avg_loss = (sum(losses) / len(losses)) if losses else 0
                    total_wins = sum(wins)
                    total_losses = sum(losses)
                    profit_factor = (
                        (total_wins / total_losses) if total_losses > 0 else (total_wins if total_wins > 0 else 0.0)
                    )
                else:
                    avg_win = pnl.get("avg_win", 0)
                    avg_loss = pnl.get("avg_loss", 0)
                    profit_factor = pnl.get("profit_factor", 0)

                if avg_win > 0:
                    print(f"  Average Win:      {format_currency(avg_win)}")
                if avg_loss > 0:
                    print(f"  Average Loss:     {format_currency(-avg_loss)}")
                if profit_factor > 0:
                    print(f"  Profit Factor:    {profit_factor:.2f}")
                if pnl.get("max_profit", 0) > 0:
                    print(f"  Max Profit:       {format_currency(pnl.get('max_profit', 0))}")
                if pnl.get("max_drawdown", 0) > 0:
                    print(f"  Max Drawdown:     {format_currency(-pnl.get('max_drawdown', 0))}")
                print()

            # Footer
            print("=" * 80)
            print(f"  Auto-refresh: Every 5 seconds | Press Ctrl+C to stop")
            print("=" * 80)

            # Wait for next update
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n[INFO] Stopping monitor...")
        print("[INFO] Background trading engine will continue running")
        print("[INFO] To stop everything, close the background window or restart system")


if __name__ == "__main__":
    main()
