"""
Investigate PnL Discrepancy - Why API shows different PnL than files
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import pytz

sys.stdout.reconfigure(encoding="utf-8")

IST = pytz.timezone("Asia/Kolkata")
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"


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


def investigate_pnl_sources():
    """Investigate all PnL data sources"""
    print_header("PNL DATA SOURCE INVESTIGATION")

    sources = {}

    # 1. paper_pnl_summary.json
    pnl_summary_file = OUTPUTS_DIR / "paper_pnl_summary.json"
    if pnl_summary_file.exists():
        try:
            data = json.loads(pnl_summary_file.read_text())
            sources["paper_pnl_summary.json"] = {
                "total_pnl": data.get("total_pnl", 0),
                "realized_pnl": data.get("total_realized_pnl", 0),
                "unrealized_pnl": data.get("total_unrealized_pnl", 0),
                "timestamp": data.get("timestamp", "N/A"),
                "total_trades": data.get("total_trades", 0),
            }
        except Exception as e:
            sources["paper_pnl_summary.json"] = {"error": str(e)}

    # 2. health.json
    health_file = OUTPUTS_DIR / "health.json"
    if health_file.exists():
        try:
            data = json.loads(health_file.read_text())
            sources["health.json"] = {
                "total_pnl": data.get("total_pnl", 0),
                "daily_pnl": data.get("daily_pnl", 0),
                "trades_executed": data.get("trades_executed", 0),
                "current_positions": data.get("current_positions", 0),
                "timestamp": data.get("last_data_fetch", "N/A"),
            }
        except Exception as e:
            sources["health.json"] = {"error": str(e)}

    # 3. positions_live.json
    positions_file = OUTPUTS_DIR / "positions_live.json"
    if positions_file.exists():
        try:
            data = json.loads(positions_file.read_text())
            if isinstance(data, dict) and "positions" in data:
                positions = data["positions"]
                total_unrealized = sum(p.get("unrealized_pnl", 0) for p in positions)
                sources["positions_live.json"] = {
                    "open_positions": len(positions),
                    "total_unrealized_pnl": total_unrealized,
                    "timestamp": data.get("timestamp", "N/A"),
                }
        except Exception as e:
            sources["positions_live.json"] = {"error": str(e)}

    # Print results
    print(f"{Colors.BOLD}PNL VALUES FROM DIFFERENT SOURCES:{Colors.RESET}\n")
    for source, data in sources.items():
        print(f"{Colors.YELLOW}{source}:{Colors.RESET}")
        if "error" in data:
            print(f"  {Colors.RED}ERROR: {data['error']}{Colors.RESET}")
        else:
            for key, value in data.items():
                if "pnl" in key.lower():
                    color = Colors.GREEN if value >= 0 else Colors.RED
                    print(f"  {key}: {color}₹{value:.2f}{Colors.RESET}")
                else:
                    print(f"  {key}: {value}")
        print()

    # Identify discrepancies
    print(f"{Colors.BOLD}DISCREPANCY ANALYSIS:{Colors.RESET}\n")
    pnl_values = {}
    for source, data in sources.items():
        if "error" not in data:
            if "total_pnl" in data:
                pnl_values[source] = data["total_pnl"]

    if len(set(pnl_values.values())) > 1:
        print(f"{Colors.RED}⚠️ DISCREPANCY FOUND:{Colors.RESET}")
        for source, value in pnl_values.items():
            print(f"  {source}: ₹{value:.2f}")
        print(f"\n{Colors.YELLOW}Root Cause: Different data sources showing different values{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}✅ All sources show same PnL value{Colors.RESET}")

    return sources


def check_trade_logging():
    """Check if trades are being logged properly"""
    print_header("TRADE LOGGING INVESTIGATION")

    issues = []

    # Check if trade execution logs exist
    trade_logs = list(OUTPUTS_DIR.glob("*trade*.json"))
    trade_logs.extend(list(OUTPUTS_DIR.glob("*executed*.json")))

    print(f"{Colors.BOLD}Trade Log Files Found: {len(trade_logs)}{Colors.RESET}\n")
    if trade_logs:
        for log in trade_logs[:5]:
            print(f"  {log.name} - Modified: {datetime.fromtimestamp(log.stat().st_mtime, IST)}")
    else:
        print(f"{Colors.RED}❌ No trade log files found{Colors.RESET}")
        issues.append("No trade execution logs")

    # Check event log
    event_log = OUTPUTS_DIR / "audit" / "event_log.jsonl"
    if event_log.exists():
        trade_events = []
        with open(event_log, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        if "TRADE" in event.get("event_type", "") or "POSITION" in event.get("event_type", ""):
                            trade_events.append(event)
                    except:
                        pass

        print(f"\n{Colors.BOLD}Trade Events in Event Log: {len(trade_events)}{Colors.RESET}")
        if trade_events:
            print(f"{Colors.GREEN}✅ Trade events are being logged{Colors.RESET}")
            for event in trade_events[-5:]:
                print(f"  {event.get('timestamp')}: {event.get('event_type')}")
        else:
            print(f"{Colors.RED}❌ No trade events found in log{Colors.RESET}")
            issues.append("No trade events in event log")
    else:
        print(f"{Colors.RED}❌ Event log file not found{Colors.RESET}")
        issues.append("Event log file missing")

    return issues


def main():
    """Main investigation"""
    print_header("COMPREHENSIVE PNL & TRADE INVESTIGATION")

    # Investigate PnL sources
    sources = investigate_pnl_sources()

    # Check trade logging
    issues = check_trade_logging()

    # Summary
    print_header("INVESTIGATION SUMMARY")

    print(f"{Colors.BOLD}Issues Found:{Colors.RESET}")
    if issues:
        for issue in issues:
            print(f"  {Colors.RED}❌ {issue}{Colors.RESET}")
    else:
        print(f"  {Colors.GREEN}✅ No major issues found{Colors.RESET}")

    print(f"\n{Colors.BOLD}Recommendations:{Colors.RESET}")
    print(f"  1. Standardize PnL calculation to use single source")
    print(f"  2. Add comprehensive trade logging")
    print(f"  3. Add trade execution timestamps")
    print(f"  4. Add trade history tracking")
    print(f"  5. Validate PnL calculations")

    print()


if __name__ == "__main__":
    main()
