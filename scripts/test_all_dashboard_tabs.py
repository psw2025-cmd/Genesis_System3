"""
Test All Dashboard Tabs - Frontend Component Verification
"""

import sys
import requests
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def test_tab(tab_name, api_endpoint, description):
    """Test a dashboard tab"""
    print(f"\n{Colors.CYAN}Testing {tab_name}...{Colors.RESET}")
    try:
        response = requests.get(f"{API_BASE}{api_endpoint}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✅ {tab_name} - {description}{Colors.RESET}")
            return True, data
        else:
            print(f"{Colors.YELLOW}⚠️ {tab_name} - Status {response.status_code}{Colors.RESET}")
            return False, None
    except Exception as e:
        print(f"{Colors.RED}❌ {tab_name} - Error: {str(e)[:50]}{Colors.RESET}")
        return False, None


def main():
    """Test all dashboard tabs"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}DASHBOARD TABS VERIFICATION{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

    tabs = [
        ("Overview", "/api/health", "System overview and health"),
        ("Chain Analytics", "/api/chain/NIFTY", "Option chain data"),
        ("Signals", "/api/signal/top", "Trade signals"),
        ("Positions", "/api/positions", "Open positions"),
        ("Paper Trading", "/api/pnl", "PnL and trading data"),
        ("Performance", "/api/perf", "Performance metrics"),
        ("QC Report", "/api/qc", "Quality control report"),
        ("Trades", "/api/trades/today", "Today's trades"),
        ("Alerts", "/api/alerts/recent", "Recent alerts"),
        ("Risk", "/api/risk/portfolio", "Portfolio risk"),
    ]

    results = {}
    for tab_name, endpoint, description in tabs:
        success, data = test_tab(tab_name, endpoint, description)
        results[tab_name] = {"success": success, "data": data}

    # Summary
    passed = sum(1 for r in results.values() if r["success"])
    total = len(tabs)

    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}SUMMARY: {passed}/{total} tabs working{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

    if passed == total:
        print(f"{Colors.GREEN}✅✅✅ ALL TABS WORKING!{Colors.RESET}\n")
    else:
        print(f"{Colors.YELLOW}⚠️ Some tabs need attention{Colors.RESET}\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
