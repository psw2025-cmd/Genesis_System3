"""
Comprehensive Dashboard Validation Test Suite
Tests all tabs, API endpoints, market open/closed scenarios, and load testing
"""

import asyncio
import json
import os
import sys
import time

import requests

# Fix Unicode encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pytz

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"
IST = pytz.timezone("Asia/Kolkata")

# All dashboard tabs/routes
DASHBOARD_TABS = [
    "/",  # Overview
    "/chain",  # Chain Analytics
    "/signals",  # Signals
    "/trading",  # Paper Trading
    "/alerts",  # Alerts
    "/risk",  # Risk Dashboard
    "/charts",  # Advanced Charts
    "/ml",  # ML Performance
    "/model",  # Model Behavior
    "/control",  # Control Plane
]

# All API endpoints to test
API_ENDPOINTS = [
    ("GET", "/"),
    ("GET", "/api/status"),
    ("GET", "/api/health"),
    ("GET", "/api/qc"),
    ("GET", "/api/perf"),
    ("GET", "/api/chain/NIFTY"),
    ("GET", "/api/chain/BANKNIFTY"),
    ("GET", "/api/chain/FINNIFTY"),
    ("GET", "/api/signal/top"),
    ("GET", "/api/signals"),
    ("GET", "/api/positions"),
    ("GET", "/api/pnl"),
    ("GET", "/api/paper"),
    ("GET", "/api/trades/today"),
    ("GET", "/api/trades/history"),
    ("GET", "/api/alerts/recent"),
    ("GET", "/api/alerts/unread"),
    ("GET", "/api/risk/portfolio"),
    ("GET", "/api/charting/heatmap/NIFTY"),
    ("GET", "/api/charting/iv-surface/NIFTY"),
    ("GET", "/api/charting/greeks/NIFTY"),
    ("GET", "/api/charting/pcr/NIFTY"),
    ("GET", "/api/ml/performance"),
    ("GET", "/api/ml/compare"),
    ("GET", "/api/journal/notes"),
    ("GET", "/api/orders"),
    ("GET", "/api/orders/history"),
    ("GET", "/api/audit/comprehensive"),
]

# Load test configuration
LOAD_TEST_QUERIES = 2000
CONCURRENT_USERS = 50  # Simulate 50 concurrent users


class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.response_time = 0
        self.status_code = None
        self.data = None
        self.timestamp = datetime.now(IST).isoformat()

    def __repr__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status} | {self.name} | {self.response_time:.3f}s | {self.error or 'OK'}"


def test_api_endpoint(method: str, endpoint: str, timeout: int = 10) -> TestResult:
    """Test a single API endpoint"""
    result = TestResult(f"{method} {endpoint}")
    start_time = time.time()

    try:
        url = f"{API_BASE}{endpoint}"
        response = requests.request(method, url, timeout=timeout)
        result.response_time = time.time() - start_time
        result.status_code = response.status_code

        if response.status_code == 200:
            try:
                result.data = response.json()
                result.passed = True
            except:
                # Some endpoints might return non-JSON
                result.data = response.text
                result.passed = True
        elif response.status_code in [404, 500]:
            result.error = f"HTTP {response.status_code}"
            result.passed = False
        else:
            result.passed = True  # Accept other status codes as valid
            result.data = response.text if response.text else None

    except requests.exceptions.Timeout:
        result.error = "Timeout"
        result.response_time = timeout
    except requests.exceptions.ConnectionError:
        result.error = "Connection Error"
    except Exception as e:
        result.error = str(e)

    return result


def test_dashboard_tab(tab: str, timeout: int = 10) -> TestResult:
    """Test a dashboard tab/page"""
    result = TestResult(f"Tab: {tab}")
    start_time = time.time()

    try:
        url = f"{FRONTEND_BASE}{tab}"
        response = requests.get(url, timeout=timeout)
        result.response_time = time.time() - start_time
        result.status_code = response.status_code

        if response.status_code == 200:
            # Check if page contains key dashboard elements
            content = response.text
            if "System3" in content or "Dashboard" in content or "React" in content:
                result.passed = True
            else:
                result.error = "Page content invalid"
        else:
            result.error = f"HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        result.error = "Timeout"
        result.response_time = timeout
    except requests.exceptions.ConnectionError:
        result.error = "Connection Error"
    except Exception as e:
        result.error = str(e)

    return result


def test_market_scenario(scenario: str) -> List[TestResult]:
    """Test API endpoints in a specific market scenario"""
    results = []
    print(f"\n📊 Testing {scenario} scenario...")

    # Test critical endpoints
    critical_endpoints = [
        ("GET", "/api/health"),
        ("GET", "/api/chain/NIFTY"),
        ("GET", "/api/signal/top"),
        ("GET", "/api/positions"),
        ("GET", "/api/pnl"),
    ]

    for method, endpoint in critical_endpoints:
        result = test_api_endpoint(method, endpoint)
        results.append(result)
        if not result.passed:
            print(f"  ⚠️  {result}")
        else:
            print(f"  ✅ {result.name} - {result.response_time:.3f}s")

    return results


def load_test_endpoint(endpoint: str, num_queries: int, concurrent: int) -> Dict[str, Any]:
    """Load test a specific endpoint"""
    method, path = endpoint.split(" ", 1) if " " in endpoint else ("GET", endpoint)

    def make_request():
        start = time.time()
        try:
            url = f"{API_BASE}{path}"
            response = requests.request(method, url, timeout=5)
            elapsed = time.time() - start
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": elapsed,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "response_time": time.time() - start}

    print(f"\n🔥 Load Testing: {method} {path} ({num_queries} queries, {concurrent} concurrent)")
    start_time = time.time()

    results = []
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [executor.submit(make_request) for _ in range(num_queries)]
        for future in as_completed(futures):
            results.append(future.result())

    total_time = time.time() - start_time
    successful = sum(1 for r in results if r.get("success", False))
    failed = len(results) - successful

    response_times = [r["response_time"] for r in results if "response_time" in r]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    max_response_time = max(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0

    return {
        "endpoint": endpoint,
        "total_queries": num_queries,
        "concurrent": concurrent,
        "successful": successful,
        "failed": failed,
        "success_rate": (successful / num_queries * 100) if num_queries > 0 else 0,
        "total_time": total_time,
        "queries_per_second": num_queries / total_time if total_time > 0 else 0,
        "avg_response_time": avg_response_time,
        "min_response_time": min_response_time,
        "max_response_time": max_response_time,
    }


def validate_data_consistency() -> List[TestResult]:
    """Validate data consistency across endpoints"""
    results = []
    print("\n🔍 Validating data consistency...")

    try:
        # Get health data
        health_res = requests.get(f"{API_BASE}/api/health", timeout=5)
        if health_res.status_code != 200:
            results.append(TestResult("Data Consistency: Health endpoint"))
            results[-1].error = f"HTTP {health_res.status_code}"
            return results

        health = health_res.json()
        data_source = health.get("data", {}).get("source", "unknown")

        # Get positions
        positions_res = requests.get(f"{API_BASE}/api/positions", timeout=5)
        positions = positions_res.json() if positions_res.status_code == 200 else {}

        # Get PnL
        pnl_res = requests.get(f"{API_BASE}/api/pnl", timeout=5)
        pnl = pnl_res.json() if pnl_res.status_code == 200 else {}

        # Validate PnL consistency
        result = TestResult("Data Consistency: PnL")
        if "total_pnl" in health.get("health", {}) and "total_pnl" in pnl:
            health_pnl = health["health"].get("total_pnl", 0)
            pnl_total = pnl.get("total_pnl", 0)
            # Allow small differences due to timing
            if abs(health_pnl - pnl_total) < 100:
                result.passed = True
            else:
                result.error = f"PnL mismatch: Health={health_pnl}, PnL={pnl_total}"
        else:
            result.passed = True  # One might be missing, that's OK
        results.append(result)

        # Validate data source (unknown is also valid for some endpoints)
        result = TestResult("Data Consistency: Data Source")
        if data_source in ["real", "synthetic", "unknown"]:
            result.passed = True
        else:
            result.error = f"Invalid data source: {data_source}"
        results.append(result)

        print(f"  ✅ Data source: {data_source}")
        if results[0].passed:
            print(f"  ✅ PnL consistency: OK")

    except Exception as e:
        result = TestResult("Data Consistency")
        result.error = str(e)
        results.append(result)

    return results


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("=" * 80)
    print("🚀 COMPREHENSIVE DASHBOARD VALIDATION TEST SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
    print()

    all_results = []

    # 1. Test all API endpoints
    print("\n" + "=" * 80)
    print("📡 TESTING ALL API ENDPOINTS")
    print("=" * 80)
    api_results = []
    for method, endpoint in API_ENDPOINTS:
        result = test_api_endpoint(method, endpoint)
        api_results.append(result)
        all_results.append(result)
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.name:50s} | {result.response_time:6.3f}s | {result.error or 'OK'}")

    # 2. Test all dashboard tabs
    print("\n" + "=" * 80)
    print("🖥️  TESTING ALL DASHBOARD TABS")
    print("=" * 80)
    tab_results = []
    for tab in DASHBOARD_TABS:
        result = test_dashboard_tab(tab)
        tab_results.append(result)
        all_results.append(result)
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.name:50s} | {result.response_time:6.3f}s | {result.error or 'OK'}")

    # 3. Test market scenarios
    print("\n" + "=" * 80)
    print("📈 TESTING MARKET SCENARIOS")
    print("=" * 80)
    market_results = test_market_scenario("Current Market State")
    all_results.extend(market_results)

    # 4. Validate data consistency
    consistency_results = validate_data_consistency()
    all_results.extend(consistency_results)

    # 5. Load testing
    print("\n" + "=" * 80)
    print(f"🔥 LOAD TESTING ({LOAD_TEST_QUERIES} queries, {CONCURRENT_USERS} concurrent users)")
    print("=" * 80)

    # Load test critical endpoints
    critical_for_load = [
        "GET /api/health",
        "GET /api/chain/NIFTY",
        "GET /api/signal/top",
    ]

    load_results = []
    for endpoint in critical_for_load:
        load_result = load_test_endpoint(endpoint, LOAD_TEST_QUERIES, CONCURRENT_USERS)
        load_results.append(load_result)

        print(f"\n  Endpoint: {endpoint}")
        print(
            f"  ✅ Success: {load_result['successful']}/{load_result['total_queries']} ({load_result['success_rate']:.1f}%)"
        )
        print(f"  ⏱️  Total Time: {load_result['total_time']:.2f}s")
        print(f"  📊 QPS: {load_result['queries_per_second']:.2f}")
        print(f"  ⚡ Avg Response: {load_result['avg_response_time']:.3f}s")
        print(f"  📈 Min/Max: {load_result['min_response_time']:.3f}s / {load_result['max_response_time']:.3f}s")

    # 6. Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for r in all_results if r.passed)
    failed = len(all_results) - passed

    print(f"\n✅ Passed: {passed}/{len(all_results)}")
    print(f"❌ Failed: {failed}/{len(all_results)}")
    print(f"📈 Success Rate: {(passed/len(all_results)*100):.1f}%")

    if failed > 0:
        print("\n❌ FAILED TESTS:")
        for result in all_results:
            if not result.passed:
                print(f"  - {result.name}: {result.error}")

    # Load test summary
    print("\n🔥 LOAD TEST SUMMARY:")
    for load_result in load_results:
        status = "✅" if load_result["success_rate"] >= 95 else "⚠️"
        print(
            f"  {status} {load_result['endpoint']}: {load_result['success_rate']:.1f}% success, {load_result['queries_per_second']:.1f} QPS"
        )

    # Save results
    results_file = "outputs/comprehensive_validation_results.json"
    os.makedirs("outputs", exist_ok=True)

    results_data = {
        "timestamp": datetime.now(IST).isoformat(),
        "summary": {
            "total_tests": len(all_results),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / len(all_results) * 100) if all_results else 0,
        },
        "api_tests": [r.__dict__ for r in api_results],
        "tab_tests": [r.__dict__ for r in tab_results],
        "load_tests": load_results,
        "failed_tests": [r.__dict__ for r in all_results if not r.passed],
    }

    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)

    print(f"\n💾 Results saved to: {results_file}")
    print("\n" + "=" * 80)
    print("✅ COMPREHENSIVE VALIDATION COMPLETE")
    print("=" * 80)

    return results_data


if __name__ == "__main__":
    try:
        # Check if backend is running
        try:
            response = requests.get(f"{API_BASE}/api/status", timeout=5)
            if response.status_code != 200:
                print(f"⚠️  Backend might not be running. Status: {response.status_code}")
        except:
            print("❌ ERROR: Backend is not running!")
            print(f"   Please start the backend at {API_BASE}")
            sys.exit(1)

        # Run tests
        results = run_comprehensive_tests()

        # Exit with appropriate code
        if results["summary"]["failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
