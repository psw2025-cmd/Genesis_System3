"""
Get All Trades from Today (Feb 6, 2026) - Market Hours Only (9:15 AM - 3:30 PM IST)
"""

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

import pytz

sys.stdout.reconfigure(encoding="utf-8")

IST = pytz.timezone("Asia/Kolkata")
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
STORAGE_DIR = Path(__file__).parent.parent / "storage"

TODAY = datetime.now(IST).date()  # 2026-02-06
MARKET_OPEN = datetime.combine(TODAY, datetime.min.time().replace(hour=9, minute=15))
MARKET_CLOSE = datetime.combine(TODAY, datetime.min.time().replace(hour=15, minute=30))


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")


def is_market_hours(timestamp_str):
    """Check if timestamp is within market hours"""
    try:
        if isinstance(timestamp_str, str):
            # Parse timestamp
            if "T" in timestamp_str:
                dt = datetime.fromisoformat(timestamp_str.replace("+05:30", ""))
            else:
                dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

            # Convert to IST
            if dt.tzinfo is None:
                dt = IST.localize(dt)
            else:
                dt = dt.astimezone(IST)

            # Check if same date and within market hours
            if dt.date() == TODAY:
                time_only = dt.time()
                market_open_time = MARKET_OPEN.time()
                market_close_time = MARKET_CLOSE.time()
                return market_open_time <= time_only <= market_close_time
    except:
        pass
    return False


def search_json_files():
    """Search all JSON files for today's trades"""
    trades = []

    # Check positions_live.json
    positions_file = OUTPUTS_DIR / "positions_live.json"
    if positions_file.exists():
        try:
            data = json.loads(positions_file.read_text())
            if isinstance(data, dict) and "positions" in data:
                for pos in data["positions"]:
                    entry_time = pos.get("entry_timestamp") or pos.get("entry_time_ist")
                    if entry_time and is_market_hours(entry_time):
                        trades.append(
                            {
                                "type": "ENTRY",
                                "position_id": pos.get("position_id"),
                                "symbol": pos.get("symbol"),
                                "entry_time": entry_time,
                                "exit_time": pos.get("exit_timestamp") or pos.get("exit_time_ist") or "OPEN",
                                "entry_price": pos.get("entry_price"),
                                "exit_price": pos.get("exit_price"),
                                "qty": pos.get("qty") or pos.get("quantity"),
                                "pnl": pos.get("unrealized_pnl") or pos.get("realized_pnl", 0),
                                "status": pos.get("status", "OPEN"),
                            }
                        )
        except Exception as e:
            print(f"Error reading positions: {e}")

    # Check paper_pnl.csv
    pnl_csv = OUTPUTS_DIR / "paper_pnl.csv"
    if pnl_csv.exists():
        try:
            with open(pnl_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    timestamp = row.get("timestamp", "")
                    if is_market_hours(timestamp):
                        trades.append(
                            {
                                "type": "PNL_UPDATE",
                                "timestamp": timestamp,
                                "total_pnl": row.get("total_pnl"),
                                "realized_pnl": row.get("total_realized_pnl"),
                                "unrealized_pnl": row.get("total_unrealized_pnl"),
                                "total_trades": row.get("total_trades"),
                            }
                        )
        except Exception as e:
            print(f"Error reading PnL CSV: {e}")

    # Check event log
    event_log = OUTPUTS_DIR / "audit" / "event_log.jsonl"
    if event_log.exists():
        try:
            with open(event_log, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            event = json.loads(line)
                            timestamp = event.get("timestamp", "")
                            if is_market_hours(timestamp):
                                if event.get("event_type") in ["TRADE_EXECUTED", "POSITION_OPENED", "POSITION_CLOSED"]:
                                    trades.append(
                                        {"type": event.get("event_type"), "timestamp": timestamp, "data": event}
                                    )
                        except:
                            pass
        except Exception as e:
            print(f"Error reading event log: {e}")

    # Check storage/metrics
    if STORAGE_DIR.exists():
        metrics_dir = STORAGE_DIR / "metrics"
        if metrics_dir.exists():
            for file in metrics_dir.glob("*.json"):
                if file.stat().st_mtime >= MARKET_OPEN.timestamp():
                    try:
                        data = json.loads(file.read_text())
                        timestamp = data.get("timestamp", "")
                        if is_market_hours(timestamp):
                            trades.append({"type": "METRIC", "timestamp": timestamp, "file": file.name, "data": data})
                    except:
                        pass

    return trades


def main():
    """Main function"""
    print_header(f"TODAY'S TRADES - {TODAY.strftime('%B %d, %Y')}")
    print(f"{Colors.BLUE}Market Hours: 9:15 AM - 3:30 PM IST{Colors.RESET}\n")

    trades = search_json_files()

    if not trades:
        print(f"{Colors.YELLOW}No trades found from today's market hours (9:15 AM - 3:30 PM IST){Colors.RESET}")
        print(f"\n{Colors.CYAN}Possible reasons:{Colors.RESET}")
        print("  1. Market was closed today (holiday/weekend)")
        print("  2. No trades were executed during market hours")
        print("  3. Trade data is stored in a different location")
        print("  4. System was not running during market hours")
        return

    # Group by type
    entries = [t for t in trades if t.get("type") == "ENTRY"]
    pnl_updates = [t for t in trades if t.get("type") == "PNL_UPDATE"]
    events = [t for t in trades if t.get("type") in ["TRADE_EXECUTED", "POSITION_OPENED", "POSITION_CLOSED"]]

    print(f"{Colors.BOLD}SUMMARY:{Colors.RESET}")
    print(f"  Total Entries: {len(entries)}")
    print(f"  PnL Updates: {len(pnl_updates)}")
    print(f"  Trade Events: {len(events)}")
    print(f"  Total Records: {len(trades)}\n")

    # Show entries
    if entries:
        print(f"{Colors.BOLD}{Colors.YELLOW}POSITION ENTRIES:{Colors.RESET}")
        print("-" * 70)
        for i, entry in enumerate(entries, 1):
            print(f"\n{Colors.BOLD}Entry #{i}{Colors.RESET}")
            print(f"  Position ID: {entry.get('position_id')}")
            print(f"  Symbol: {entry.get('symbol')}")
            print(f"  Entry Time: {entry.get('entry_time')}")
            print(f"  Exit Time: {entry.get('exit_time')}")
            print(f"  Entry Price: ₹{entry.get('entry_price', 0):.2f}")
            print(f"  Quantity: {entry.get('qty', 0)}")
            print(f"  PnL: ₹{entry.get('pnl', 0):.2f}")
            print(f"  Status: {entry.get('status')}")

    # Show PnL updates
    if pnl_updates:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}PNL UPDATES:{Colors.RESET}")
        print("-" * 70)
        for update in pnl_updates[:10]:  # Show first 10
            print(f"  {update.get('timestamp')}: Total PnL = ₹{update.get('total_pnl', 0)}")

    # Show events
    if events:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}TRADE EVENTS:{Colors.RESET}")
        print("-" * 70)
        for event in events[:10]:  # Show first 10
            print(f"  {event.get('timestamp')}: {event.get('type')}")

    print(f"\n{Colors.GREEN}Analysis complete!{Colors.RESET}\n")


if __name__ == "__main__":
    main()
