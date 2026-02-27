"""
Live Simulation Monitor - Real-time dashboard for option chain simulation
Shows: Cycles, QC status, Top underlying, Trade signals, Performance metrics
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime
import sys

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def clear_screen():
    """Clear terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def read_json_safe(filepath):
    """Safely read JSON file."""
    try:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None


def read_last_lines(filepath, n=10):
    """Read last N lines from file."""
    try:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                return lines[-n:] if len(lines) > n else lines
    except Exception:
        pass
    return []


def format_timestamp(ts_str):
    """Format timestamp string."""
    try:
        if "IST" in ts_str:
            return ts_str.split("IST")[0].strip()
        return ts_str
    except:
        return ts_str


def get_file_size(filepath):
    """Get file size in KB."""
    try:
        if filepath.exists():
            size = filepath.stat().st_size
            return f"{size / 1024:.1f} KB"
    except:
        pass
    return "N/A"


def main():
    """Main monitoring loop."""
    outputs_dir = ROOT_DIR / "outputs"
    logs_dir = ROOT_DIR / "logs"

    chain_csv = outputs_dir / "chain_raw_live.csv"
    rank_csv = outputs_dir / "underlying_rank_live.csv"
    trade_signal_json = outputs_dir / "top_trade_signal.json"
    qc_report_json = outputs_dir / "qc_report_live.json"
    positions_json = outputs_dir / "positions_live.json"
    pnl_json = outputs_dir / "pnl_live.json"
    trades_csv = outputs_dir / "paper_trades_live.csv"
    metrics_log = logs_dir / "metrics.log"

    print("\n" + "=" * 80)
    print("  LIVE SIMULATION MONITOR - Real-Time Option Chain Dashboard")
    print("=" * 80)
    print("\nPress Ctrl+C to stop monitoring\n")
    time.sleep(2)

    last_cycle = 0
    last_update_time = None

    try:
        while True:
            clear_screen()

            # Header
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("\n" + "=" * 80)
            print(f"  LIVE SIMULATION MONITOR - {now}")
            print("=" * 80 + "\n")

            # Read latest metrics
            metrics_lines = read_last_lines(metrics_log, 5)
            if metrics_lines:
                latest_metric = metrics_lines[-1].strip()
                print("📊 LATEST CYCLE METRICS:")
                print("-" * 80)
                print(f"  {latest_metric}")

                # Extract cycle number
                if "CYCLE=" in latest_metric:
                    try:
                        cycle_part = latest_metric.split("CYCLE=")[1].split("|")[0].strip()
                        current_cycle = int(cycle_part)
                        if current_cycle > last_cycle:
                            last_cycle = current_cycle
                            last_update_time = now
                    except:
                        pass
                print()

            # Read trade signal
            trade_signal = read_json_safe(trade_signal_json)
            if trade_signal:
                print("🎯 TOP TRADE SIGNAL:")
                print("-" * 80)
                action = trade_signal.get("action", "N/A")
                underlying = trade_signal.get("underlying", "N/A")
                strategy = trade_signal.get("strategy", "N/A")
                reason = trade_signal.get("reason", "N/A")
                confidence = trade_signal.get("confidence", 0)

                action_icon = "✅" if action == "TRADE" else "⏸️"
                print(f"  {action_icon} Action: {action}")
                print(f"  📈 Underlying: {underlying}")
                print(f"  🎲 Strategy: {strategy}")
                print(f"  💡 Reason: {reason}")
                if confidence > 0:
                    print(f"  📊 Confidence: {confidence*100:.1f}%")

                if trade_signal.get("strikes"):
                    print(f"  🎯 Strikes: {trade_signal.get('strikes')}")
                if trade_signal.get("entry_mid"):
                    print(f"  💰 Entry Mid: ₹{trade_signal.get('entry_mid'):.2f}")
                print()

            # Read QC report
            qc_report = read_json_safe(qc_report_json)
            if qc_report:
                print("🔍 QUALITY CONTROL:")
                print("-" * 80)
                overall_passed = qc_report.get("overall_passed", False)
                qc_icon = "✅" if overall_passed else "❌"
                print(f"  {qc_icon} Overall: {'PASS' if overall_passed else 'FAIL'}")

                underlying_results = qc_report.get("underlying_results", {})
                if underlying_results:
                    print(f"  📋 Underlyings Checked: {len(underlying_results)}")
                    total_contracts = sum(r.get("contract_count", 0) for r in underlying_results.values())
                    print(f"  📊 Total Contracts: {total_contracts}")

                    # Show per-underlying status
                    for name, result in underlying_results.items():
                        status = "✅" if result.get("passed", False) else "❌"
                        count = result.get("contract_count", 0)
                        print(f"    {status} {name}: {count} contracts")
                print()

            # Read rankings
            rank_lines = read_last_lines(rank_csv, 6)
            if rank_lines and len(rank_lines) > 1:
                print("🏆 UNDERLYING RANKINGS:")
                print("-" * 80)
                # Show header and top 3
                for i, line in enumerate(rank_lines):
                    if i == 0:
                        # Header
                        cols = line.strip().split(",")
                        if "underlying" in cols and "score" in cols:
                            print(f"  {'Rank':<6} {'Underlying':<15} {'Score':<8} {'PCR':<8} {'Signal':<8}")
                            print("  " + "-" * 50)
                    elif i <= 3:  # Top 3
                        parts = line.strip().split(",")
                        if len(parts) >= 3:
                            try:
                                underlying = parts[0] if parts[0] else "N/A"
                                score = float(parts[1]) if parts[1] else 0
                                pcr = parts[2] if len(parts) > 2 else "N/A"
                                signal = parts[3] if len(parts) > 3 else "N/A"
                                print(f"  {i:<6} {underlying:<15} {score:<8.2f} {pcr:<8} {signal:<8}")
                            except:
                                pass
                print()

            # File status
            print("📁 OUTPUT FILES:")
            print("-" * 80)
            files_status = [
                ("chain_raw_live.csv", chain_csv),
                ("underlying_rank_live.csv", rank_csv),
                ("top_trade_signal.json", trade_signal_json),
                ("qc_report_live.json", qc_report_json),
                ("positions_live.json", positions_json),
                ("pnl_live.json", pnl_json),
                ("paper_trades_live.csv", trades_csv),
                ("metrics.log", metrics_log),
            ]

            for name, filepath in files_status:
                exists = "✅" if filepath.exists() else "❌"
                size = get_file_size(filepath) if filepath.exists() else "N/A"
                mtime = ""
                if filepath.exists():
                    try:
                        mtime = datetime.fromtimestamp(filepath.stat().st_mtime).strftime("%H:%M:%S")
                    except:
                        mtime = "N/A"
                print(f"  {exists} {name:<30} {size:>10}  (Updated: {mtime})")
            print()

            # Read paper trading data
            positions_json = outputs_dir / "positions_live.json"
            pnl_json = outputs_dir / "pnl_live.json"

            positions_data = read_json_safe(positions_json)
            pnl_data = read_json_safe(pnl_json)

            if positions_data or pnl_data:
                print("💰 PAPER TRADING:")
                print("-" * 80)

                if pnl_data:
                    total_pnl = pnl_data.get("total_pnl", 0.0)
                    unrealized_pnl = pnl_data.get("total_unrealized_pnl", 0.0)
                    realized_pnl = pnl_data.get("total_realized_pnl", 0.0)
                    total_trades = pnl_data.get("total_trades", 0)
                    win_rate = pnl_data.get("win_rate", 0.0)
                    open_positions = pnl_data.get("open_positions", 0)

                    pnl_color = "🟢" if total_pnl >= 0 else "🔴"
                    print(
                        f"  {pnl_color} Total PnL: ₹{total_pnl:.2f} (Unrealized: ₹{unrealized_pnl:.2f}, Realized: ₹{realized_pnl:.2f})"
                    )
                    print(f"  📊 Total Trades: {total_trades} | Win Rate: {win_rate:.1f}%")
                    print(f"  📈 Open Positions: {open_positions}")

                if positions_data:
                    open_positions_list = positions_data.get("open_positions", [])
                    if open_positions_list:
                        print(f"\n  📋 OPEN POSITIONS ({len(open_positions_list)}):")
                        for i, pos in enumerate(open_positions_list[:5], 1):  # Show max 5
                            pnl = pos.get("unrealized_pnl", 0.0)
                            pnl_pct = pos.get("unrealized_pnl_pct", 0.0)
                            pnl_icon = "🟢" if pnl >= 0 else "🔴"
                            print(
                                f"    {i}. {pos.get('underlying', 'N/A')} {pos.get('strike', 0)} {pos.get('option_type', '')} | "
                                f"Entry: ₹{pos.get('entry_price', 0):.2f} | Current: ₹{pos.get('current_price', 0):.2f} | "
                                f"{pnl_icon} PnL: ₹{pnl:.2f} ({pnl_pct:.2f}%)"
                            )
                        if len(open_positions_list) > 5:
                            print(f"    ... and {len(open_positions_list) - 5} more positions")
                print()

            # Status summary
            print("📈 STATUS SUMMARY:")
            print("-" * 80)
            if last_update_time:
                print(f"  ✅ Last Update: {last_update_time}")
                print(f"  🔄 Current Cycle: {last_cycle}")
            else:
                print(f"  ⏳ Waiting for simulation to start...")

            if trade_signal and trade_signal.get("action") == "TRADE":
                print(f"  🎯 Active Signal: YES")
            else:
                print(f"  🎯 Active Signal: NO")

            if qc_report:
                qc_status = "PASS" if qc_report.get("overall_passed") else "FAIL"
                print(f"  🔍 QC Status: {qc_status}")

            print("\n" + "=" * 80)
            print("  Refreshing every 2 seconds... (Press Ctrl+C to stop)")
            print("=" * 80)

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
