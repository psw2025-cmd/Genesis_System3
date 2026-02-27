"""
Comprehensive Validation and Test - All Fixes
Tests PnL calculation, trade logging, API endpoints, and system integrity
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime
import pytz

sys.stdout.reconfigure(encoding="utf-8")

IST = pytz.timezone("Asia/Kolkata")
ROOT_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
API_BASE = "http://localhost:8000"


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


def test_pnl_calculation():
    """Test PnL calculation accuracy"""
    print_header("TEST 1: PNL CALCULATION ACCURACY")

    # Read paper_pnl_summary.json (source of truth)
    pnl_summary_file = OUTPUTS_DIR / "paper_pnl_summary.json"
    expected_pnl = 0.0
    if pnl_summary_file.exists():
        try:
            pnl_summary = json.loads(pnl_summary_file.read_text())
            expected_pnl = float(pnl_summary.get("total_pnl", 0.0))
            print(f"{Colors.GREEN}✅ paper_pnl_summary.json found{Colors.RESET}")
            print(f"   Expected Total PnL: ₹{expected_pnl:.2f}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error reading paper_pnl_summary.json: {e}{Colors.RESET}")
            return False
    else:
        print(f"{Colors.YELLOW}⚠️ paper_pnl_summary.json not found{Colors.RESET}")
        return False

    # Test API endpoint
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            api_pnl = float(data.get("total_pnl", 0.0))
            print(f"\n{Colors.BLUE}API Response:{Colors.RESET}")
            print(f"   Total PnL: ₹{api_pnl:.2f}")

            # Check if values match (allow small floating point differences)
            if abs(api_pnl - expected_pnl) < 0.01:
                print(f"\n{Colors.GREEN}✅ PASS: API PnL matches paper_pnl_summary.json{Colors.RESET}")
                return True
            else:
                print(f"\n{Colors.RED}❌ FAIL: PnL mismatch!{Colors.RESET}")
                print(f"   Expected: ₹{expected_pnl:.2f}")
                print(f"   Got: ₹{api_pnl:.2f}")
                print(f"   Difference: ₹{abs(api_pnl - expected_pnl):.2f}")
                return False
        else:
            print(f"{Colors.RED}❌ API returned status {response.status_code}{Colors.RESET}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Colors.YELLOW}⚠️ Backend not running - cannot test API{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error testing API: {e}{Colors.RESET}")
        return False


def test_trade_logging():
    """Test trade logging functionality"""
    print_header("TEST 2: TRADE LOGGING FUNCTIONALITY")

    # Check if trade logger module exists
    trade_logger_file = ROOT_DIR / "dashboard" / "backend" / "trade_logger.py"
    if trade_logger_file.exists():
        print(f"{Colors.GREEN}✅ trade_logger.py module exists{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ trade_logger.py module not found{Colors.RESET}")
        return False

    # Check if trade execution log file exists (or will be created)
    trade_log_file = OUTPUTS_DIR / "trade_execution_log.jsonl"
    if trade_log_file.exists():
        print(f"{Colors.GREEN}✅ Trade execution log file exists{Colors.RESET}")
        # Count trades
        try:
            count = 0
            with open(trade_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        count += 1
            print(f"   Trades logged: {count}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ Error reading log: {e}{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠️ Trade execution log not created yet (will be created on first trade){Colors.RESET}")

    # Check if paper_executor has logging integration
    paper_executor_file = ROOT_DIR / "src" / "trading" / "paper_executor.py"
    if paper_executor_file.exists():
        try:
            content = paper_executor_file.read_text(encoding="utf-8")
            if "log_trade_event" in content and "from dashboard.backend.trade_logger import" in content:
                print(f"{Colors.GREEN}✅ paper_executor.py has trade logging integration{Colors.RESET}")
                return True
            else:
                print(f"{Colors.RED}❌ paper_executor.py missing trade logging integration{Colors.RESET}")
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ Error reading paper_executor.py: {e}{Colors.RESET}")
            return False
    else:
        print(f"{Colors.RED}❌ paper_executor.py not found{Colors.RESET}")
        return False


def test_api_endpoints():
    """Test new API endpoints"""
    print_header("TEST 3: API ENDPOINTS")

    endpoints = [
        ("/api/trades/today", "GET", None),
        ("/api/trades/history", "GET", {"date": "2026-02-06", "start_time": "09:15", "end_time": "15:30"}),
        ("/api/trades/history", "GET", None),
    ]

    results = []
    for endpoint, method, params in endpoints:
        try:
            if params:
                response = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=5)
            else:
                response = requests.get(f"{API_BASE}{endpoint}", timeout=5)

            if response.status_code == 200:
                data = response.json()
                print(f"{Colors.GREEN}✅ {endpoint}{Colors.RESET}")
                if endpoint == "/api/trades/today":
                    print(f"   Trades found: {data.get('count', 0)}")
                    print(f"   Date: {data.get('date', 'N/A')}")
                elif endpoint == "/api/trades/history":
                    print(f"   Trades found: {data.get('count', 0)}")
                results.append(True)
            elif response.status_code == 404:
                print(f"{Colors.RED}❌ {endpoint} - 404 Not Found (backend may need restart){Colors.RESET}")
                results.append(False)
            else:
                print(f"{Colors.YELLOW}⚠️ {endpoint} - Status {response.status_code}{Colors.RESET}")
                results.append(False)
        except requests.exceptions.ConnectionError:
            print(f"{Colors.YELLOW}⚠️ {endpoint} - Backend not running{Colors.RESET}")
            results.append(False)
        except Exception as e:
            print(f"{Colors.RED}❌ {endpoint} - Error: {e}{Colors.RESET}")
            results.append(False)

    return all(results)


def test_data_sources():
    """Test data source consistency"""
    print_header("TEST 4: DATA SOURCE CONSISTENCY")

    # Check all PnL sources
    sources = {}

    # paper_pnl_summary.json
    pnl_summary_file = OUTPUTS_DIR / "paper_pnl_summary.json"
    if pnl_summary_file.exists():
        try:
            data = json.loads(pnl_summary_file.read_text())
            sources["paper_pnl_summary.json"] = float(data.get("total_pnl", 0.0))
        except:
            sources["paper_pnl_summary.json"] = None

    # positions_live.json
    positions_file = OUTPUTS_DIR / "positions_live.json"
    if positions_file.exists():
        try:
            data = json.loads(positions_file.read_text())
            if isinstance(data, dict) and "positions" in data:
                positions = data["positions"]
                total_unrealized = sum(p.get("unrealized_pnl", 0) for p in positions)
                sources["positions_live.json"] = total_unrealized
        except:
            sources["positions_live.json"] = None

    # health.json
    health_file = OUTPUTS_DIR / "health.json"
    if health_file.exists():
        try:
            data = json.loads(health_file.read_text())
            sources["health.json"] = float(data.get("total_pnl", 0.0))
        except:
            sources["health.json"] = None

    print(f"{Colors.BOLD}Data Sources:{Colors.RESET}")
    for source, value in sources.items():
        if value is not None:
            print(f"   {source}: ₹{value:.2f}")
        else:
            print(f"   {source}: {Colors.RED}Error reading{Colors.RESET}")

    # Check consistency
    pnl_values = [v for v in sources.values() if v is not None]
    if len(set(pnl_values)) > 1:
        print(f"\n{Colors.YELLOW}⚠️ Data sources show different values{Colors.RESET}")
        print(f"   Note: API should use paper_pnl_summary.json as primary source")
        return False
    else:
        print(f"\n{Colors.GREEN}✅ Data sources are consistent{Colors.RESET}")
        return True


def test_trade_visibility():
    """Test trade visibility in dashboard"""
    print_header("TEST 5: TRADE VISIBILITY")

    # Check if trade logger functions exist
    try:
        sys.path.insert(0, str(ROOT_DIR))
        from dashboard.backend.trade_logger import get_trades_by_date, get_all_trades, log_trade_event

        print(f"{Colors.GREEN}✅ Trade logger functions available{Colors.RESET}")

        # Test get_trades_by_date
        today = datetime.now(IST).strftime("%Y-%m-%d")
        trades = get_trades_by_date(today, start_time="09:15", end_time="15:30")
        print(f"   Trades found for today (9:15 AM - 3:30 PM): {len(trades)}")

        # Test get_all_trades
        all_trades = get_all_trades()
        print(f"   Total trades in log: {len(all_trades)}")

        return True
    except ImportError as e:
        print(f"{Colors.RED}❌ Trade logger functions not available: {e}{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error testing trade visibility: {e}{Colors.RESET}")
        return False


def main():
    """Main validation function"""
    print_header("COMPREHENSIVE VALIDATION AND TEST")

    print(f"{Colors.BOLD}Testing all fixes and validations...{Colors.RESET}\n")

    results = {
        "PnL Calculation": test_pnl_calculation(),
        "Trade Logging": test_trade_logging(),
        "API Endpoints": test_api_endpoints(),
        "Data Sources": test_data_sources(),
        "Trade Visibility": test_trade_visibility(),
    }

    print_header("VALIDATION SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"   {test_name}: {status}")

    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}\n")

    if passed == total:
        print(f"{Colors.GREEN}✅ ALL TESTS PASSED - System is ready!{Colors.RESET}\n")
    else:
        print(f"{Colors.YELLOW}⚠️ Some tests failed - Review above for details{Colors.RESET}\n")
        print(f"{Colors.BOLD}Recommendations:{Colors.RESET}")
        if not results["API Endpoints"]:
            print("   1. Restart backend to activate new endpoints")
        if not results["PnL Calculation"]:
            print("   2. Restart backend to apply PnL calculation fix")
        print()


if __name__ == "__main__":
    main()
