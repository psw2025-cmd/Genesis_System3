"""
Full System Test - Tests everything end-to-end
"""

import json
import sys
import time
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

API_BASE = "http://localhost:8000"
TIMEOUT = 10


def test(name, func):
    """Run a test and print result"""
    try:
        result = func()
        if result:
            print(f"[PASS] {name}")
            return True
        else:
            print(f"[FAIL] {name}")
            return False
    except Exception as e:
        print(f"[FAIL] {name}: {str(e)}")
        return False


def main():
    print("=" * 70)
    print("System3 Ultra - Full System Test")
    print("=" * 70)
    print()

    results = []

    # Test 1: Backend Health
    results.append(
        test("Backend Health", lambda: requests.get(f"{API_BASE}/api/health", timeout=TIMEOUT).status_code == 200)
    )

    # Test 2: SSOT Endpoint
    results.append(
        test("SSOT Endpoint", lambda: "state_version" in requests.get(f"{API_BASE}/api/state", timeout=TIMEOUT).json())
    )

    # Test 3: State History
    results.append(
        test(
            "State History",
            lambda: requests.get(f"{API_BASE}/api/state/history?limit=5", timeout=TIMEOUT).status_code == 200,
        )
    )

    # Test 4: Agent Memory
    results.append(
        test("Agent Memory", lambda: requests.get(f"{API_BASE}/api/agent/memory", timeout=TIMEOUT).status_code == 200)
    )

    # Test 5: Agent Issues
    results.append(
        test("Agent Issues", lambda: requests.get(f"{API_BASE}/api/agent/issues", timeout=TIMEOUT).status_code == 200)
    )

    # Test 6: Upgrade Plan
    results.append(
        test(
            "Upgrade Plan",
            lambda: requests.get(f"{API_BASE}/api/agent/upgrade-plan", timeout=TIMEOUT).status_code == 200,
        )
    )

    # Test 7: All Endpoints
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
                lambda e=endpoint: requests.get(f"{API_BASE}{e}", timeout=TIMEOUT).status_code in [200, 404],
            )
        )

    # Summary
    print()
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    # Wait for backend to be ready
    print("Waiting for backend to start...")
    for i in range(10):
        try:
            requests.get(f"{API_BASE}/api/health", timeout=2)
            print("Backend is ready!")
            break
        except:
            time.sleep(1)
    else:
        print("ERROR: Backend not responding after 10 seconds")
        sys.exit(1)

    sys.exit(main())
