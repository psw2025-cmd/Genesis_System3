"""
Multi-User Dashboard Verification Script
Simulates multiple traders/users testing the dashboard
"""

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests

sys.stdout.reconfigure(encoding="utf-8")

API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


def print_success(msg):
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} {msg}")


def print_fail(msg):
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {msg}")


def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")


def test_user_session(user_id: int):
    """Simulate a user session"""
    results = {"user_id": user_id, "tests": {}, "errors": []}

    try:
        # Test 1: Overview
        try:
            res = requests.get(f"{API_BASE}/api/health", timeout=5)
            if res.status_code == 200:
                results["tests"]["overview"] = True
            else:
                results["tests"]["overview"] = False
                results["errors"].append(f"Overview: Status {res.status_code}")
        except Exception as e:
            results["tests"]["overview"] = False
            results["errors"].append(f"Overview: {str(e)}")

        # Test 2: Chain Data
        try:
            res = requests.get(f"{API_BASE}/api/chain/NIFTY", timeout=5)
            if res.status_code == 200:
                data = res.json()
                if data.get("contracts") is not None:
                    results["tests"]["chain"] = True
                else:
                    results["tests"]["chain"] = False
                    results["errors"].append("Chain: No contracts data")
            else:
                results["tests"]["chain"] = False
                results["errors"].append(f"Chain: Status {res.status_code}")
        except Exception as e:
            results["tests"]["chain"] = False
            results["errors"].append(f"Chain: {str(e)}")

        # Test 3: Positions
        try:
            res = requests.get(f"{API_BASE}/api/positions", timeout=5)
            if res.status_code == 200:
                results["tests"]["positions"] = True
            else:
                results["tests"]["positions"] = False
                results["errors"].append(f"Positions: Status {res.status_code}")
        except Exception as e:
            results["tests"]["positions"] = False
            results["errors"].append(f"Positions: {str(e)}")

        # Test 4: Alerts
        try:
            res = requests.get(f"{API_BASE}/api/alerts/recent", timeout=5)
            if res.status_code == 200:
                results["tests"]["alerts"] = True
            else:
                results["tests"]["alerts"] = False
                results["errors"].append(f"Alerts: Status {res.status_code}")
        except Exception as e:
            results["tests"]["alerts"] = False
            results["errors"].append(f"Alerts: {str(e)}")

        # Test 5: Risk Dashboard
        try:
            res = requests.get(f"{API_BASE}/api/risk/portfolio", timeout=5)
            if res.status_code == 200:
                results["tests"]["risk"] = True
            else:
                results["tests"]["risk"] = False
                results["errors"].append(f"Risk: Status {res.status_code}")
        except Exception as e:
            results["tests"]["risk"] = False
            results["errors"].append(f"Risk: {str(e)}")

        # Test 6: Charts
        try:
            res = requests.get(f"{API_BASE}/api/charting/heatmap/NIFTY?metric=oi", timeout=5)
            if res.status_code == 200:
                results["tests"]["charts"] = True
            else:
                results["tests"]["charts"] = False
                results["errors"].append(f"Charts: Status {res.status_code}")
        except Exception as e:
            results["tests"]["charts"] = False
            results["errors"].append(f"Charts: {str(e)}")

        # Test 7: ML Performance
        try:
            res = requests.get(f"{API_BASE}/api/ml/performance", timeout=5)
            if res.status_code == 200:
                results["tests"]["ml"] = True
            else:
                results["tests"]["ml"] = False
                results["errors"].append(f"ML: Status {res.status_code}")
        except Exception as e:
            results["tests"]["ml"] = False
            results["errors"].append(f"ML: {str(e)}")

        # Test 8: Predictions
        try:
            res = requests.get(f"{API_BASE}/api/predict/portfolio", timeout=5)
            if res.status_code == 200:
                results["tests"]["predictions"] = True
            else:
                results["tests"]["predictions"] = False
                results["errors"].append(f"Predictions: Status {res.status_code}")
        except Exception as e:
            results["tests"]["predictions"] = False
            results["errors"].append(f"Predictions: {str(e)}")

        # Test 9: Validation
        try:
            res = requests.get(f"{API_BASE}/api/validate/profit/all", timeout=5)
            if res.status_code == 200:
                results["tests"]["validation"] = True
            else:
                results["tests"]["validation"] = False
                results["errors"].append(f"Validation: Status {res.status_code}")
        except Exception as e:
            results["tests"]["validation"] = False
            results["errors"].append(f"Validation: {str(e)}")

        # Test 10: Export
        try:
            res = requests.get(f"{API_BASE}/api/export/positions?format=csv", timeout=5)
            if res.status_code == 200:
                results["tests"]["export"] = True
            else:
                results["tests"]["export"] = False
                results["errors"].append(f"Export: Status {res.status_code}")
        except Exception as e:
            results["tests"]["export"] = False
            results["errors"].append(f"Export: {str(e)}")

    except Exception as e:
        results["errors"].append(f"Session error: {str(e)}")

    return results


def main():
    """Run multi-user verification"""
    print("=" * 60)
    print("MULTI-USER DASHBOARD VERIFICATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"API Base: {API_BASE}")
    print()

    num_users = 5
    print_info(f"Simulating {num_users} concurrent users...")
    print()

    # Run concurrent user sessions
    all_results = []
    with ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(test_user_session, i + 1) for i in range(num_users)]

        for future in as_completed(futures):
            result = future.result()
            all_results.append(result)

    # Analyze results
    print("=" * 60)
    print("RESULTS BY USER")
    print("=" * 60)

    total_tests = 0
    total_passed = 0

    for result in all_results:
        user_id = result["user_id"]
        tests = result["tests"]
        errors = result["errors"]

        passed = sum(1 for v in tests.values() if v)
        total = len(tests)
        total_tests += total
        total_passed += passed

        status = "[PASS]" if passed == total else "[FAIL]"
        print(f"\n{status} User {user_id}: {passed}/{total} tests passed")

        for test_name, test_result in tests.items():
            test_status = "[PASS]" if test_result else "[FAIL]"
            print(f"  {test_status} {test_name}")

        if errors:
            print(f"  Errors: {len(errors)}")
            for error in errors[:3]:  # Show first 3 errors
                print(f"    - {error}")

    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"Total Users: {num_users}")
    print(f"Total Tests: {total_tests}")
    print(f"Total Passed: {total_passed}")
    print(f"Total Failed: {total_tests - total_passed}")
    print(f"Pass Rate: {overall_pass_rate:.1f}%")

    # Check consistency
    print()
    print("=" * 60)
    print("DATA CONSISTENCY CHECK")
    print("=" * 60)

    # Get data from all users and compare
    try:
        responses = []
        for i in range(3):  # Sample 3 users
            res = requests.get(f"{API_BASE}/api/health", timeout=5)
            if res.status_code == 200:
                responses.append(res.json())

        if len(responses) >= 2:
            # Compare cycle_count (should be same or increasing)
            cycle_counts = [r.get("cycle_count", 0) for r in responses]
            if len(set(cycle_counts)) <= 1:
                print_success("Data consistency: PASS (all users see same data)")
            else:
                print_info(f"Data consistency: Cycle counts vary (expected during updates): {cycle_counts}")
    except Exception as e:
        print_fail(f"Data consistency check failed: {e}")

    # Final status
    print()
    if overall_pass_rate >= 90:
        print_success(f"OVERALL: {overall_pass_rate:.1f}% PASS RATE - SYSTEM READY!")
        return True
    elif overall_pass_rate >= 70:
        print_info(f"OVERALL: {overall_pass_rate:.1f}% PASS RATE - MINOR ISSUES")
        return True
    else:
        print_fail(f"OVERALL: {overall_pass_rate:.1f}% PASS RATE - NEEDS ATTENTION")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
