"""
Get Today's Complete Paper Trading Report
Shows all trading details, performance, predictions, and P&L from real market data
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pytz
import requests

sys.stdout.reconfigure(encoding="utf-8")

IST = pytz.timezone("Asia/Kolkata")
API_BASE = "http://localhost:8000"
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


def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{text}{Colors.RESET}")
    print("-" * 70)


def get_api_data(endpoint, timeout=5):
    """Get data from API endpoint"""
    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=timeout)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_file_data(filepath):
    """Get data from JSON file"""
    try:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return None


def format_currency(amount):
    """Format amount as currency"""
    if amount is None:
        return "₹0.00"
    return f"₹{amount:,.2f}"


def format_percentage(value):
    """Format as percentage"""
    if value is None:
        return "0.00%"
    return f"{value:.2f}%"


def main():
    """Generate complete trading report"""
    print_header("TODAY'S PAPER TRADING REPORT - REAL MARKET DATA")

    today = datetime.now(IST).strftime("%Y-%m-%d")
    print(f"{Colors.BLUE}Report Date: {today}{Colors.RESET}")
    print(f"{Colors.BLUE}Report Time: {datetime.now(IST).strftime('%H:%M:%S IST')}{Colors.RESET}\n")

    # 1. HEALTH & SYSTEM STATUS
    print_section("1. SYSTEM STATUS & HEALTH")
    health = get_api_data("/api/health")
    if health:
        print(
            f"  Status: {Colors.GREEN if health.get('status') == 'ok' else Colors.RED}{health.get('status', 'unknown')}{Colors.RESET}"
        )
        print(f"  Mode: {health.get('mode', 'N/A')}")
        print(f"  Market Status: {health.get('market_status', 'N/A')}")
        print(
            f"  Data Source: {Colors.GREEN if health.get('data_source') == 'real' else Colors.YELLOW}{health.get('data_source', 'N/A')}{Colors.RESET}"
        )
        print(f"  Broker Status: {health.get('broker_status', 'N/A')}")
        print(f"  Total Cycles: {health.get('cycle_count', 0)}")
        print(f"  Trades Executed: {health.get('trades_executed', 0)}")
        print(f"  Open Positions: {health.get('open_positions', 0)}")
    else:
        print(f"  {Colors.RED}[ERROR] Could not fetch health data{Colors.RESET}")

    # 2. POSITIONS
    print_section("2. OPEN POSITIONS")
    positions_data = get_api_data("/api/positions")
    if positions_data and positions_data.get("positions"):
        positions = positions_data["positions"]
        print(f"  Total Open Positions: {len(positions)}\n")

        total_unrealized = 0
        for i, pos in enumerate(positions, 1):
            print(f"  {Colors.BOLD}Position #{i}{Colors.RESET}")
            print(f"    ID: {pos.get('position_id', 'N/A')}")
            print(f"    Symbol: {pos.get('symbol', pos.get('underlying', 'N/A'))}")
            print(f"    Type: {pos.get('option_type', 'N/A')}")
            print(f"    Strike: {pos.get('strike', 'N/A')}")
            print(f"    Expiry: {pos.get('expiry', 'N/A')}")
            print(f"    Quantity: {pos.get('qty', pos.get('quantity', 0))}")
            print(f"    Entry Price: {format_currency(pos.get('entry_price', 0))}")
            print(f"    Current Price: {format_currency(pos.get('current_price', pos.get('entry_price', 0)))}")

            unrealized = pos.get("unrealized_pnl", 0)
            total_unrealized += unrealized
            color = Colors.GREEN if unrealized >= 0 else Colors.RED
            print(f"    Unrealized PnL: {color}{format_currency(unrealized)}{Colors.RESET}")
            print(f"    Status: {pos.get('status', 'OPEN')}")
            print()

        print(
            f"  {Colors.BOLD}Total Unrealized PnL: {Colors.GREEN if total_unrealized >= 0 else Colors.RED}{format_currency(total_unrealized)}{Colors.RESET}"
        )
    else:
        print(f"  {Colors.YELLOW}No open positions{Colors.RESET}")

    # 3. PROFIT & LOSS SUMMARY
    print_section("3. PROFIT & LOSS SUMMARY")
    pnl_data = get_api_data("/api/pnl")
    if pnl_data:
        summary = pnl_data.get("summary", {})
        history = pnl_data.get("history", [])

        print(f"  Total Trades: {summary.get('total_trades', 0)}")
        print(f"  Winning Trades: {Colors.GREEN}{summary.get('winning_trades', 0)}{Colors.RESET}")
        print(f"  Losing Trades: {Colors.RED}{summary.get('losing_trades', 0)}{Colors.RESET}")
        print(
            f"  Win Rate: {Colors.GREEN if summary.get('win_rate', 0) >= 50 else Colors.YELLOW}{format_percentage(summary.get('win_rate', 0))}{Colors.RESET}"
        )
        print(
            f"  Total Realized PnL: {Colors.GREEN if summary.get('total_realized_pnl', 0) >= 0 else Colors.RED}{format_currency(summary.get('total_realized_pnl', 0))}{Colors.RESET}"
        )
        print(
            f"  Total Unrealized PnL: {Colors.GREEN if summary.get('total_unrealized_pnl', 0) >= 0 else Colors.RED}{format_currency(summary.get('total_unrealized_pnl', 0))}{Colors.RESET}"
        )

        total_pnl = summary.get("total_pnl", 0)
        color = Colors.GREEN if total_pnl >= 0 else Colors.RED
        print(f"\n  {Colors.BOLD}Total PnL: {color}{format_currency(total_pnl)}{Colors.RESET}")

        if history:
            print(f"\n  Recent PnL History (Last 10):")
            for entry in history[-10:]:
                timestamp = entry.get("timestamp", "N/A")
                pnl = entry.get("total_pnl", 0)
                color = Colors.GREEN if pnl >= 0 else Colors.RED
                print(f"    {timestamp}: {color}{format_currency(pnl)}{Colors.RESET}")
    else:
        print(f"  {Colors.RED}[ERROR] Could not fetch PnL data{Colors.RESET}")

    # 4. PERFORMANCE METRICS
    print_section("4. PERFORMANCE METRICS")
    perf_data = get_api_data("/api/perf")
    if perf_data and perf_data.get("current"):
        current = perf_data["current"]
        print(f"  Cycle: {current.get('cycle', 'N/A')}")
        print(f"  Fetch Duration: {current.get('fetch_duration_sec', 0):.3f}s")
        print(f"  Strategy Duration: {current.get('strategy_duration_sec', 0):.3f}s")
        print(f"  Cycle Duration: {current.get('cycle_duration_sec', 0):.3f}s")
        print(f"  Signals Generated: {current.get('signals_generated', 0)}")
        print(f"  Trades Executed: {current.get('trades_executed', 0)}")
        print(
            f"  QC Passed: {Colors.GREEN if current.get('qc_passed', False) else Colors.RED}{current.get('qc_passed', False)}{Colors.RESET}"
        )

        if perf_data.get("history"):
            print(f"\n  Performance History (Last 5 cycles):")
            for entry in perf_data["history"][-5:]:
                print(
                    f"    Cycle {entry.get('cycle', 'N/A')}: Duration {entry.get('cycle_duration_sec', 0):.3f}s, Signals: {entry.get('signals_generated', 0)}"
                )
    else:
        print(f"  {Colors.YELLOW}No performance data available{Colors.RESET}")

    # 5. PREDICTIONS
    print_section("5. PREDICTIONS & FORECASTS")
    predictions = get_api_data("/api/predict/portfolio", timeout=10)
    if predictions and predictions.get("status") == "ok":
        pred = predictions.get("prediction", {})
        portfolio_pred = pred.get("portfolio_prediction", {})

        if portfolio_pred:
            print(
                f"  Predicted Portfolio PnL: {Colors.CYAN}{format_currency(portfolio_pred.get('predicted_pnl', 0))}{Colors.RESET}"
            )
            print(f"  Confidence: {format_percentage(portfolio_pred.get('average_confidence', 0) * 100)}")
            print(f"  Risk Level: {portfolio_pred.get('risk_level', 'N/A')}")
            print(f"  Expected Return: {format_percentage(portfolio_pred.get('expected_return', 0) * 100)}")

            methods = portfolio_pred.get("methods", {})
            if methods:
                print(f"\n  Prediction Methods:")
                for method, data in methods.items():
                    print(
                        f"    {method}: {format_currency(data.get('predicted_pnl', 0))} (Confidence: {format_percentage(data.get('confidence', 0) * 100)})"
                    )
    else:
        print(f"  {Colors.YELLOW}Predictions not available{Colors.RESET}")

    # 6. PROFIT VALIDATION
    print_section("6. PROFIT VALIDATION")
    validation = get_api_data("/api/validate/profit/all", timeout=10)
    if validation and validation.get("status") == "ok":
        summary = validation.get("summary", {})
        print(f"  Total Validations: {summary.get('total_count', 0)}")
        print(f"  Passed: {Colors.GREEN}{summary.get('pass_count', 0)}{Colors.RESET}")
        print(f"  Warnings: {Colors.YELLOW}{summary.get('warn_count', 0)}{Colors.RESET}")
        print(f"  Failed: {Colors.RED}{summary.get('fail_count', 0)}{Colors.RESET}")

        validations = validation.get("validations", [])
        if validations:
            print(f"\n  Position Validations:")
            for val in validations[:5]:  # Show first 5
                pos_id = val.get("position_id", "N/A")
                status = val.get("status", "N/A")
                color = Colors.GREEN if status == "PASS" else Colors.YELLOW if status == "WARN" else Colors.RED
                print(f"    {pos_id}: {color}{status}{Colors.RESET} - {format_currency(val.get('reported_pnl', 0))}")
    else:
        print(f"  {Colors.YELLOW}Validation not available{Colors.RESET}")

    # 7. TRADING STATISTICS
    print_section("7. TRADING STATISTICS")
    if health:
        print(f"  Total Trades Today: {health.get('trades_executed', 0)}")
        print(f"  Open Positions: {health.get('open_positions', 0)}")
        print(
            f"  Total PnL: {Colors.GREEN if health.get('total_pnl', 0) >= 0 else Colors.RED}{format_currency(health.get('total_pnl', 0))}{Colors.RESET}"
        )
        print(
            f"  Daily PnL: {Colors.GREEN if health.get('daily_pnl', 0) >= 0 else Colors.RED}{format_currency(health.get('daily_pnl', 0))}{Colors.RESET}"
        )

    # 8. FILE DATA (if available)
    print_section("8. ADDITIONAL DATA FROM FILES")

    pnl_file = OUTPUTS_DIR / "paper_pnl_summary.json"
    pnl_file_data = get_file_data(pnl_file)
    if pnl_file_data:
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} PnL Summary file found")
        print(f"    Total PnL: {format_currency(pnl_file_data.get('total_pnl', 0))}")
        print(f"    Realized: {format_currency(pnl_file_data.get('total_realized_pnl', 0))}")
        print(f"    Unrealized: {format_currency(pnl_file_data.get('total_unrealized_pnl', 0))}")

    positions_file = OUTPUTS_DIR / "positions_live.json"
    positions_file_data = get_file_data(positions_file)
    if positions_file_data:
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Positions file found")
        if isinstance(positions_file_data, list):
            print(f"    Positions count: {len(positions_file_data)}")
        elif isinstance(positions_file_data, dict):
            print(f"    Positions data available")

    perf_file = OUTPUTS_DIR / "perf_metrics.json"
    perf_file_data = get_file_data(perf_file)
    if perf_file_data:
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Performance metrics file found")

    # Summary
    print_header("REPORT SUMMARY")
    print(f"{Colors.BOLD}Date: {today}{Colors.RESET}")
    print(f"{Colors.BOLD}Time: {datetime.now(IST).strftime('%H:%M:%S IST')}{Colors.RESET}\n")

    if health:
        total_pnl = health.get("total_pnl", 0)
        color = Colors.GREEN if total_pnl >= 0 else Colors.RED
        print(f"{Colors.BOLD}Total PnL: {color}{format_currency(total_pnl)}{Colors.RESET}")
        print(f"{Colors.BOLD}Trades Executed: {health.get('trades_executed', 0)}{Colors.RESET}")
        print(f"{Colors.BOLD}Open Positions: {health.get('open_positions', 0)}{Colors.RESET}")

    print(f"\n{Colors.CYAN}Report generated successfully!{Colors.RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Report generation interrupted{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error generating report: {e}{Colors.RESET}")
        import traceback

        traceback.print_exc()
