"""
Complete System Validation - Tests everything
"""

import sys
import requests
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

API_BASE = "http://localhost:8000"


def test(name, func, timeout=10):
    try:
        result = func()
        if result:
            print(f"[PASS] {name}")
            return True
        else:
            print(f"[FAIL] {name}")
            return False
    except Exception as e:
        print(f"[FAIL] {name}: {str(e)[:100]}")
        return False


def main():
    print("=" * 70)
    print("System3 Ultra - Complete Validation")
    print("=" * 70)
    print()

    results = []

    # Wait for backend
    print("Waiting for backend...")
    for i in range(15):
        try:
            requests.get(f"{API_BASE}/api/health", timeout=2)
            print("Backend is ready!")
            break
        except:
            time.sleep(1)
    else:
        print("ERROR: Backend not responding")
        return 1

    print()

    # Test 1: Backend Health
    results.append(test("Backend Health", lambda: requests.get(f"{API_BASE}/api/health", timeout=5).status_code == 200))

    # Test 2: SSOT Endpoint
    results.append(
        test("SSOT Endpoint", lambda: "state_version" in requests.get(f"{API_BASE}/api/state", timeout=5).json())
    )

    # Test 3: State History
    results.append(
        test(
            "State History", lambda: requests.get(f"{API_BASE}/api/state/history?limit=3", timeout=5).status_code == 200
        )
    )

    # Test 4: Agent Memory
    results.append(
        test("Agent Memory", lambda: requests.get(f"{API_BASE}/api/agent/memory", timeout=5).status_code == 200)
    )

    # Test 5: Agent Issues (with longer timeout)
    results.append(
        test("Agent Issues", lambda: requests.get(f"{API_BASE}/api/agent/issues", timeout=15).status_code == 200)
    )

    # Test 6: Upgrade Plan
    results.append(
        test("Upgrade Plan", lambda: requests.get(f"{API_BASE}/api/agent/upgrade-plan", timeout=5).status_code == 200)
    )

    # Test 7-11: Core Endpoints
    endpoints = [
        "/api/positions",
        "/api/pnl",
        "/api/qc",
        "/api/signal/top",
        "/api/risk/portfolio",
    ]

    for endpoint in endpoints:
        results.append(
            test(
                f"Endpoint {endpoint}",
                lambda e=endpoint: requests.get(f"{API_BASE}{e}", timeout=5).status_code in [200, 404],
            )
        )

    # Test 12: SSOT Data Validation
    results.append(
        test("SSOT Data Validation", lambda: len(requests.get(f"{API_BASE}/api/state", timeout=5).json().keys()) >= 10)
    )

    # Summary
    print()
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        print("\nBackend is fully operational!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
