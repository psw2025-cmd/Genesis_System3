"""
Comprehensive System Test - Tests all components
"""

import sys
import json
import requests
import subprocess
import time
from pathlib import Path

# Fix encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).parent.parent
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"


def print_test(name, passed, details=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {name}")
    if details:
        print(f"      {details}")
    return passed


def test_backend_imports():
    """Test backend imports"""
    print("\n=== Testing Backend Imports ===")
    results = []

    try:
        sys.path.insert(0, str(ROOT_DIR / "dashboard" / "backend"))
        from runtime_state_store import RuntimeStateStore

        results.append(print_test("SSOT Import", True))
    except Exception as e:
        results.append(print_test("SSOT Import", False, str(e)))

    try:
        from upgrade_agent import get_upgrade_agent

        results.append(print_test("Upgrade Agent Import", True))
    except Exception as e:
        results.append(print_test("Upgrade Agent Import", False, str(e)))

    return all(results)


def test_backend_running():
    """Test if backend is running"""
    print("\n=== Testing Backend Service ===")
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            return print_test("Backend Running", True, f"Status: {response.status_code}")
        else:
            return print_test("Backend Running", False, f"Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        return print_test("Backend Running", False, "Connection refused - backend not running")
    except Exception as e:
        return print_test("Backend Running", False, str(e))


def test_ssot_endpoint():
    """Test SSOT endpoint"""
    print("\n=== Testing SSOT Endpoint ===")
    try:
        response = requests.get(f"{API_BASE}/api/state", timeout=5)
        if response.status_code == 200:
            state = response.json()
            required = ["state_version", "data_source", "market", "broker", "qc", "signals", "positions", "pnl", "risk"]
            missing = [f for f in required if f not in state]
            if not missing:
                return print_test("SSOT Endpoint", True, f"Version: {state.get('state_version')}")
            else:
                return print_test("SSOT Endpoint", False, f"Missing: {missing}")
        else:
            return print_test("SSOT Endpoint", False, f"Status: {response.status_code}")
    except Exception as e:
        return print_test("SSOT Endpoint", False, str(e))


def test_upgrade_agent_endpoints():
    """Test upgrade agent endpoints"""
    print("\n=== Testing Upgrade Agent Endpoints ===")
    results = []

    endpoints = [
        ("/api/agent/memory", "GET"),
        ("/api/agent/issues", "GET"),
        ("/api/agent/upgrade-plan", "GET"),
    ]

    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{API_BASE}{endpoint}", timeout=5)

            passed = response.status_code in [200, 404]  # 404 is OK if no data yet
            results.append(print_test(f"Agent {endpoint}", passed, f"Status: {response.status_code}"))
        except Exception as e:
            results.append(print_test(f"Agent {endpoint}", False, str(e)))

    return all(results)


def test_state_history():
    """Test state history endpoint"""
    print("\n=== Testing State History ===")
    try:
        response = requests.get(f"{API_BASE}/api/state/history?limit=10", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return print_test("State History", True, f"Count: {data.get('count', 0)}")
        else:
            return print_test("State History", False, f"Status: {response.status_code}")
    except Exception as e:
        return print_test("State History", False, str(e))


def test_frontend_build():
    """Test if frontend is built"""
    print("\n=== Testing Frontend Build ===")
    dist_dir = ROOT_DIR / "dashboard" / "frontend" / "dist"
    index_file = dist_dir / "index.html"

    if index_file.exists():
        return print_test("Frontend Build", True, "dist/index.html exists")
    else:
        return print_test("Frontend Build", False, "dist/index.html not found")


def test_agent_memory():
    """Test agent memory files"""
    print("\n=== Testing Agent Memory ===")
    results = []

    memory_dir = ROOT_DIR / "agent_memory"
    if not memory_dir.exists():
        return print_test("Agent Memory Directory", False, "agent_memory/ not found")

    files_to_check = ["plan.md", "tasks.json"]
    for file_name in files_to_check:
        file_path = memory_dir / file_name
        exists = file_path.exists()
        results.append(print_test(f"Agent Memory {file_name}", exists))

    return all(results)


def test_electron_files():
    """Test Electron app files"""
    print("\n=== Testing Electron App ===")
    results = []

    desktop_dir = ROOT_DIR / "desktop_app"
    if not desktop_dir.exists():
        return print_test("Desktop App Directory", False, "desktop_app/ not found")

    files_to_check = ["main.js", "preload.js", "package.json"]
    for file_name in files_to_check:
        file_path = desktop_dir / file_name
        exists = file_path.exists()
        results.append(print_test(f"Electron {file_name}", exists))

    return all(results)


def main():
    """Run all tests"""
    print("=" * 60)
    print("System3 Ultra - Comprehensive System Test")
    print("=" * 60)

    results = []

    # Test imports
    results.append(test_backend_imports())

    # Test files
    results.append(test_frontend_build())
    results.append(test_agent_memory())
    results.append(test_electron_files())

    # Test backend (if running)
    backend_running = test_backend_running()
    if backend_running:
        results.append(test_ssot_endpoint())
        results.append(test_state_history())
        results.append(test_upgrade_agent_endpoints())
    else:
        print("\n[SKIP] Backend not running - skipping API tests")
        print("      Start backend with: cd dashboard\\backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000")

    # Summary
    print("\n" + "=" * 60)
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
    sys.exit(main())
