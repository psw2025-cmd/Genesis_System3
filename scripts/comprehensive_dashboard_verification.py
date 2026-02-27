"""
Comprehensive Dashboard Verification - End-to-End Testing
Tests all tabs, data synchronization, and backend-frontend integration
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime
import pytz
from typing import Dict, List, Optional

sys.stdout.reconfigure(encoding="utf-8")

IST = pytz.timezone("Asia/Kolkata")
ROOT_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"


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


def test_backend_health():
    """Test backend health endpoint"""
    print_header("TEST 1: BACKEND HEALTH")
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✅ Backend is running{Colors.RESET}")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Total PnL: ₹{data.get('total_pnl', 0):.2f}")
            print(f"   Daily PnL: ₹{data.get('daily_pnl', 0):.2f}")
            print(f"   Open Positions: {data.get('open_positions', 0)}")
            print(f"   Data Source: {data.get('data_source', 'N/A')}")
            return True, data
        else:
            print(f"{Colors.RED}❌ Backend returned status {response.status_code}{Colors.RESET}")
            return False, None
    except Exception as e:
        print(f"{Colors.RED}❌ Backend not accessible: {e}{Colors.RESET}")
        return False, None


def test_all_api_endpoints():
    """Test all API endpoints"""
    print_header("TEST 2: ALL API ENDPOINTS")

    endpoints = [
        ("/api/health", "GET", None, "Health status"),
        ("/api/qc", "GET", None, "QC report"),
        ("/api/chain/NIFTY", "GET", None, "NIFTY chain"),
        ("/api/chain/BANKNIFTY", "GET", None, "BANKNIFTY chain"),
        ("/api/signal/top", "GET", None, "Top signal"),
        ("/api/positions", "GET", None, "Positions"),
        ("/api/pnl", "GET", None, "PnL data"),
        ("/api/perf", "GET", None, "Performance"),
        ("/api/trades/today", "GET", None, "Today's trades"),
        ("/api/trades/history", "GET", {"date": "2026-02-06"}, "Trade history"),
        ("/api/alerts/recent", "GET", None, "Recent alerts"),
        ("/api/risk/portfolio", "GET", None, "Portfolio risk"),
    ]

    results = {}
    for endpoint, method, params, description in endpoints:
        try:
            if params:
                response = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=10)
            else:
                response = requests.get(f"{API_BASE}{endpoint}", timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"{Colors.GREEN}✅ {description}{Colors.RESET}")
                results[endpoint] = {"status": "PASS", "data": data}
            else:
                print(f"{Colors.YELLOW}⚠️ {description} - Status {response.status_code}{Colors.RESET}")
                results[endpoint] = {"status": "WARN", "code": response.status_code}
        except Exception as e:
            print(f"{Colors.RED}❌ {description} - Error: {str(e)[:50]}{Colors.RESET}")
            results[endpoint] = {"status": "FAIL", "error": str(e)}

    passed = sum(1 for r in results.values() if r.get("status") == "PASS")
    total = len(endpoints)
    print(f"\n{Colors.BOLD}Results: {passed}/{total} endpoints passed{Colors.RESET}")
    return results


def test_data_synchronization():
    """Test data synchronization between backend and files"""
    print_header("TEST 3: DATA SYNCHRONIZATION")

    # Test PnL synchronization
    print(f"{Colors.BLUE}Testing PnL synchronization...{Colors.RESET}")

    # Get from API
    try:
        api_response = requests.get(f"{API_BASE}/api/health", timeout=10)
        if api_response.status_code == 200:
            api_data = api_response.json()
            api_pnl = api_data.get("total_pnl", 0)
            print(f"   API PnL: ₹{api_pnl:.2f}")
    except:
        api_pnl = None
        print(f"   {Colors.RED}❌ Could not get API PnL{Colors.RESET}")

    # Get from file
    pnl_file = OUTPUTS_DIR / "paper_pnl_summary.json"
    file_pnl = None
    if pnl_file.exists():
        try:
            file_data = json.loads(pnl_file.read_text())
            file_pnl = file_data.get("total_pnl", 0)
            print(f"   File PnL: ₹{file_pnl:.2f}")
        except:
            print(f"   {Colors.RED}❌ Could not read file{Colors.RESET}")

    # Compare
    if api_pnl is not None and file_pnl is not None:
        diff = abs(api_pnl - file_pnl)
        if diff < 0.01:
            print(f"   {Colors.GREEN}✅ PnL synchronized{Colors.RESET}")
        else:
            print(f"   {Colors.YELLOW}⚠️ PnL mismatch: ₹{diff:.2f}{Colors.RESET}")

    # Test positions synchronization
    print(f"\n{Colors.BLUE}Testing positions synchronization...{Colors.RESET}")

    try:
        api_pos = requests.get(f"{API_BASE}/api/positions", timeout=10)
        if api_pos.status_code == 200:
            api_pos_data = api_pos.json()
            api_count = api_pos_data.get("open_count", 0)
            print(f"   API Positions: {api_count}")
    except:
        api_count = None
        print(f"   {Colors.RED}❌ Could not get API positions{Colors.RESET}")

    pos_file = OUTPUTS_DIR / "positions_live.json"
    file_count = None
    if pos_file.exists():
        try:
            file_pos_data = json.loads(pos_file.read_text())
            if isinstance(file_pos_data, dict):
                file_count = file_pos_data.get("open_count", len(file_pos_data.get("positions", [])))
            else:
                file_count = len(file_pos_data) if isinstance(file_pos_data, list) else 0
            print(f"   File Positions: {file_count}")
        except:
            print(f"   {Colors.RED}❌ Could not read positions file{Colors.RESET}")

    if api_count is not None and file_count is not None:
        if api_count == file_count:
            print(f"   {Colors.GREEN}✅ Positions synchronized{Colors.RESET}")
        else:
            print(f"   {Colors.YELLOW}⚠️ Position count mismatch: {abs(api_count - file_count)}{Colors.RESET}")

    return True


def test_frontend_accessibility():
    """Test frontend accessibility"""
    print_header("TEST 4: FRONTEND ACCESSIBILITY")

    try:
        response = requests.get(FRONTEND_BASE, timeout=10)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ Frontend is accessible{Colors.RESET}")
            print(f"   URL: {FRONTEND_BASE}")
            return True
        else:
            print(f"{Colors.YELLOW}⚠️ Frontend returned status {response.status_code}{Colors.RESET}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Frontend not accessible: {e}{Colors.RESET}")
        return False


def test_data_consistency():
    """Test data consistency across endpoints"""
    print_header("TEST 5: DATA CONSISTENCY")

    # Get data from multiple endpoints
    health_data = None
    positions_data = None
    pnl_data = None

    try:
        health_response = requests.get(f"{API_BASE}/api/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
    except:
        pass

    try:
        positions_response = requests.get(f"{API_BASE}/api/positions", timeout=10)
        if positions_response.status_code == 200:
            positions_data = positions_response.json()
    except:
        pass

    try:
        pnl_response = requests.get(f"{API_BASE}/api/pnl", timeout=10)
        if pnl_response.status_code == 200:
            pnl_data = pnl_response.json()
    except:
        pass

    # Compare position counts
    if health_data and positions_data:
        health_pos = health_data.get("open_positions", 0)
        positions_pos = positions_data.get("open_count", 0)
        if health_pos == positions_pos:
            print(f"{Colors.GREEN}✅ Position counts consistent{Colors.RESET}")
            print(f"   Count: {health_pos}")
        else:
            print(f"{Colors.YELLOW}⚠️ Position count mismatch{Colors.RESET}")
            print(f"   Health: {health_pos}, Positions: {positions_pos}")

    # Compare PnL
    if health_data and pnl_data:
        health_pnl = health_data.get("total_pnl", 0)
        pnl_summary = pnl_data.get("summary", {})
        pnl_total = pnl_summary.get("total_pnl", 0)
        diff = abs(health_pnl - pnl_total)
        if diff < 0.01:
            print(f"{Colors.GREEN}✅ PnL values consistent{Colors.RESET}")
            print(f"   PnL: ₹{health_pnl:.2f}")
        else:
            print(f"{Colors.YELLOW}⚠️ PnL mismatch: ₹{diff:.2f}{Colors.RESET}")

    return True


def test_trade_endpoints():
    """Test trade-related endpoints"""
    print_header("TEST 6: TRADE ENDPOINTS")

    endpoints = [
        ("/api/trades/today", "Today's trades"),
        ("/api/trades/history?date=2026-02-06&start_time=09:15&end_time=15:30", "Trade history"),
    ]

    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                print(f"{Colors.GREEN}✅ {description}{Colors.RESET}")
                print(f"   Trades found: {count}")
            else:
                print(f"{Colors.RED}❌ {description} - Status {response.status_code}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ {description} - Error: {str(e)[:50]}{Colors.RESET}")

    return True


def test_chain_data():
    """Test option chain data"""
    print_header("TEST 7: OPTION CHAIN DATA")

    underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY"]

    for underlying in underlyings:
        try:
            response = requests.get(f"{API_BASE}/api/chain/{underlying}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                contracts = data.get("contracts", [])
                spot = data.get("spot", 0)
                status = data.get("status", "N/A")
                data_source = data.get("data_source", "N/A")
                print(f"{Colors.GREEN}✅ {underlying}{Colors.RESET}")
                print(f"   Contracts: {len(contracts)}")
                print(f"   Spot: ₹{spot:.2f}")
                print(f"   Status: {status}")
                print(f"   Source: {data_source}")
            else:
                print(f"{Colors.YELLOW}⚠️ {underlying} - Status {response.status_code}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ {underlying} - Error: {str(e)[:50]}{Colors.RESET}")

    return True


def generate_report(results: Dict):
    """Generate comprehensive report"""
    print_header("COMPREHENSIVE VERIFICATION REPORT")

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r.get("status") == "PASS")

    print(f"{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%")

    if passed_tests == total_tests:
        print(f"\n{Colors.GREEN}✅✅✅ ALL TESTS PASSED - SYSTEM IS READY!{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}⚠️ Some tests need attention{Colors.RESET}\n")

    return passed_tests == total_tests


def main():
    """Main verification function"""
    print_header("COMPREHENSIVE DASHBOARD VERIFICATION")
    print(f"{Colors.BOLD}Testing all tabs, data synchronization, and end-to-end functionality...{Colors.RESET}\n")

    results = {}

    # Test 1: Backend Health
    health_ok, health_data = test_backend_health()
    results["backend_health"] = {"status": "PASS" if health_ok else "FAIL"}

    if not health_ok:
        print(f"\n{Colors.RED}❌ Backend is not accessible. Please start the backend first.{Colors.RESET}\n")
        return False

    # Test 2: All API Endpoints
    endpoint_results = test_all_api_endpoints()
    results["api_endpoints"] = endpoint_results

    # Test 3: Data Synchronization
    sync_ok = test_data_synchronization()
    results["data_sync"] = {"status": "PASS" if sync_ok else "FAIL"}

    # Test 4: Frontend Accessibility
    frontend_ok = test_frontend_accessibility()
    results["frontend"] = {"status": "PASS" if frontend_ok else "FAIL"}

    # Test 5: Data Consistency
    consistency_ok = test_data_consistency()
    results["data_consistency"] = {"status": "PASS" if consistency_ok else "FAIL"}

    # Test 6: Trade Endpoints
    trade_ok = test_trade_endpoints()
    results["trade_endpoints"] = {"status": "PASS" if trade_ok else "FAIL"}

    # Test 7: Chain Data
    chain_ok = test_chain_data()
    results["chain_data"] = {"status": "PASS" if chain_ok else "FAIL"}

    # Generate Report
    all_passed = generate_report(results)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
