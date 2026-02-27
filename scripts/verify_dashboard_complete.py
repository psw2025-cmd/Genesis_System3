"""
Comprehensive Dashboard Verification Script
Tests all pages, endpoints, and features to ensure everything works
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime
import pytz

# Fix encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

IST = pytz.timezone("Asia/Kolkata")
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"


def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(test_name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   {details}")


def test_backend_running():
    """Test if backend is running"""
    print_header("Backend Status Check")
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            print_result("Backend is running", True, f"Status: {response.status_code}")
            return True
        else:
            print_result("Backend is running", False, f"Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_result("Backend is running", False, "Connection refused - backend not running")
        return False
    except Exception as e:
        print_result("Backend is running", False, str(e))
        return False


def test_ssot_endpoint():
    """Test SSOT endpoint"""
    print_header("SSOT Endpoint Test")
    try:
        response = requests.get(f"{API_BASE}/api/state", timeout=5)
        if response.status_code == 200:
            state = response.json()
            required_fields = [
                "state_version",
                "data_source",
                "market",
                "broker",
                "qc",
                "signals",
                "positions",
                "pnl",
                "risk",
            ]
            missing = [f for f in required_fields if f not in state]
            if not missing:
                print_result("SSOT endpoint returns valid state", True, f"Version: {state.get('state_version', 'N/A')}")
                return True
            else:
                print_result("SSOT endpoint returns valid state", False, f"Missing: {missing}")
                return False
        else:
            print_result("SSOT endpoint returns valid state", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("SSOT endpoint returns valid state", False, str(e))
        return False


def test_synthetic_data():
    """Test synthetic data realism"""
    print_header("Synthetic Data Realism Test")
    try:
        response = requests.get(f"{API_BASE}/api/chain/NIFTY", timeout=5)
        if response.status_code == 200:
            chain = response.json()
            if chain.get("data_source") == "synthetic":
                contracts = chain.get("contracts", [])
                if contracts:
                    iv_values = [c.get("iv", 0) for c in contracts[:10] if c.get("iv")]
                    if iv_values:
                        max_iv = max(iv_values)
                        # IV should be 8-40% (or 0.08-0.40 if decimal)
                        if max_iv > 50 or (max_iv > 0.5 and max_iv < 1):
                            print_result("Synthetic IV is realistic", False, f"Max IV: {max_iv}% (should be 8-40%)")
                            return False
                        else:
                            print_result(
                                "Synthetic IV is realistic", True, f"IV range: {min(iv_values):.2f}% - {max_iv:.2f}%"
                            )
                            return True
            print_result("Synthetic IV is realistic", True, "Using real data (not synthetic)")
            return True
    except Exception as e:
        print_result("Synthetic IV is realistic", False, str(e))
        return False


def test_risk_limits():
    """Test risk limit logic"""
    print_header("Risk Limit Logic Test")
    try:
        # Get positions
        pos_res = requests.get(f"{API_BASE}/api/positions", timeout=5)
        if pos_res.status_code == 200:
            positions = pos_res.json().get("positions", [])
            count = len(positions)

            # Test with limit equal to count
            limit_res = requests.post(f"{API_BASE}/api/risk/check-limits", json={"max_positions": count}, timeout=5)
            if limit_res.status_code == 200:
                check = limit_res.json().get("limit_check", {})
                breaches = check.get("breaches", [])
                max_pos_breach = any(b.get("limit") == "max_positions" for b in breaches)

                if max_pos_breach and count > 0:
                    print_result("Risk limit logic correct", False, f"Breaches when equal (count: {count})")
                    return False
                else:
                    print_result(
                        "Risk limit logic correct",
                        True,
                        f"Positions: {count}, Limit: {count}, Breaches: {len(breaches)}",
                    )
                    return True
    except Exception as e:
        print_result("Risk limit logic correct", False, str(e))
        return False


def test_endpoints():
    """Test all critical endpoints"""
    print_header("API Endpoints Test")
    endpoints = [
        ("/api/health", "Health"),
        ("/api/positions", "Positions"),
        ("/api/pnl", "PnL"),
        ("/api/qc", "QC"),
        ("/api/signal/top", "Signals"),
        ("/api/risk/portfolio", "Risk"),
        ("/api/perf", "Performance"),
    ]

    results = []
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
            passed = response.status_code == 200
            results.append((name, passed))
            print_result(f"{name} endpoint", passed, f"Status: {response.status_code}")
        except Exception as e:
            results.append((name, False))
            print_result(f"{name} endpoint", False, str(e))

    return all(r[1] for r in results)


def test_frontend_pages():
    """Test frontend pages accessibility"""
    print_header("Frontend Pages Test")
    pages = [
        ("/", "Home"),
        ("/overview", "Overview"),
        ("/trading", "Trading"),
        ("/signals", "Signals"),
        ("/risk", "Risk"),
        ("/ml", "ML"),
        ("/alerts", "Alerts"),
    ]

    results = []
    for page, name in pages:
        try:
            response = requests.get(f"{FRONTEND_BASE}{page}", timeout=5)
            passed = response.status_code == 200
            results.append((name, passed))
            print_result(f"{name} page", passed, f"Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            results.append((name, False))
            print_result(f"{name} page", False, "Frontend not running")
        except Exception as e:
            results.append((name, False))
            print_result(f"{name} page", False, str(e))

    return all(r[1] for r in results)


def test_consistency():
    """Test data consistency across endpoints"""
    print_header("Data Consistency Test")
    try:
        # Get SSOT state
        state_res = requests.get(f"{API_BASE}/api/state", timeout=5)
        if state_res.status_code != 200:
            print_result("Data consistency", False, "SSOT endpoint failed")
            return False

        state = state_res.json()

        # Get individual endpoints
        health_res = requests.get(f"{API_BASE}/api/health", timeout=5)
        positions_res = requests.get(f"{API_BASE}/api/positions", timeout=5)
        pnl_res = requests.get(f"{API_BASE}/api/pnl", timeout=5)

        if all(r.status_code == 200 for r in [health_res, positions_res, pnl_res]):
            health = health_res.json()
            positions_data = positions_res.json()
            pnl_data = pnl_res.json()

            # Compare positions
            ssot_pos = len(state.get("positions", []))
            api_pos = len(positions_data.get("positions", []))

            # Compare PnL (allow small difference)
            ssot_pnl = state.get("pnl", {}).get("total", 0)
            health_pnl = health.get("total_pnl", 0)
            pnl_diff = abs(ssot_pnl - health_pnl)

            if ssot_pos == api_pos and pnl_diff < 10.0:
                print_result("Data consistency", True, f"Positions: {ssot_pos}={api_pos}, PnL diff: ₹{pnl_diff:.2f}")
                return True
            else:
                print_result(
                    "Data consistency", False, f"Positions: {ssot_pos} vs {api_pos}, PnL diff: ₹{pnl_diff:.2f}"
                )
                return False
        else:
            print_result("Data consistency", False, "Some endpoints failed")
            return False
    except Exception as e:
        print_result("Data consistency", False, str(e))
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  COMPREHENSIVE DASHBOARD VERIFICATION")
    print("=" * 70)
    print(f"Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"Backend: {API_BASE}")
    print(f"Frontend: {FRONTEND_BASE}")

    results = []

    # Run tests
    results.append(("Backend Running", test_backend_running()))
    if not results[-1][1]:
        print("\n⚠️  Backend is not running. Please start it first.")
        return 1

    results.append(("SSOT Endpoint", test_ssot_endpoint()))
    results.append(("Synthetic Data", test_synthetic_data()))
    results.append(("Risk Limits", test_risk_limits()))
    results.append(("API Endpoints", test_endpoints()))
    results.append(("Frontend Pages", test_frontend_pages()))
    results.append(("Data Consistency", test_consistency()))

    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Dashboard is fully operational.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
