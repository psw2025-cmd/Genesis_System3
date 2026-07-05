"""
Complete System Verification - Final Check
"""

import sys
import time
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

API_BASE = "http://localhost:8000"
ROOT_DIR = Path(__file__).parent.parent


def check(name, condition, details=""):
    if condition:
        print(f"[PASS] {name}")
        if details:
            print(f"      {details}")
        return True
    else:
        print(f"[FAIL] {name}")
        if details:
            print(f"      {details}")
        return False


def main():
    print("=" * 70)
    print("System3 Ultra - Complete Verification")
    print("=" * 70)
    print()

    results = []

    # 1. Python & pip
    print("=== Python Environment ===")
    try:
        import subprocess

        python_ver = subprocess.check_output(["python", "--version"], stderr=subprocess.STDOUT).decode().strip()
        pip_ver = (
            subprocess.check_output(["python", "-m", "pip", "--version"], stderr=subprocess.STDOUT).decode().strip()
        )
        results.append(check("Python", True, python_ver))
        results.append(check("pip", True, pip_ver))
    except Exception as e:
        results.append(check("Python/pip", False, str(e)))

    # 2. Backend
    print("\n=== Backend Service ===")
    try:
        r = requests.get(f"{API_BASE}/api/health", timeout=5)
        results.append(check("Backend Running", r.status_code == 200, f"Status: {r.status_code}"))
    except Exception as e:
        results.append(check("Backend Running", False, str(e)))
        print("\n[ERROR] Backend not running. Cannot continue.")
        return 1

    # 3. SSOT
    print("\n=== SSOT System ===")
    try:
        r = requests.get(f"{API_BASE}/api/state", timeout=5)
        if r.status_code == 200:
            data = r.json()
            results.append(check("SSOT Endpoint", True, f"Version: {data.get('state_version')}"))
            results.append(check("SSOT Data Complete", len(data.keys()) >= 10, f"Fields: {len(data.keys())}"))
        else:
            results.append(check("SSOT Endpoint", False, f"Status: {r.status_code}"))
    except Exception as e:
        results.append(check("SSOT Endpoint", False, str(e)))

    # 4. State History
    try:
        r = requests.get(f"{API_BASE}/api/state/history?limit=5", timeout=5)
        results.append(check("State History", r.status_code == 200, f"Count: {r.json().get('count', 0)}"))
    except Exception as e:
        results.append(check("State History", False, str(e)))

    # 5. Upgrade Agent
    print("\n=== Upgrade Agent ===")
    endpoints = [
        ("/api/agent/memory", "Agent Memory"),
        ("/api/agent/issues", "Agent Issues"),
        ("/api/agent/upgrade-plan", "Upgrade Plan"),
    ]
    for ep, name in endpoints:
        try:
            r = requests.get(f"{API_BASE}{ep}", timeout=15)
            results.append(check(name, r.status_code == 200, f"Status: {r.status_code}"))
        except Exception as e:
            results.append(check(name, False, str(e)[:50]))

    # 6. Core Endpoints
    print("\n=== Core Endpoints ===")
    core_eps = [
        "/api/positions",
        "/api/pnl",
        "/api/qc",
        "/api/signal/top",
        "/api/risk/portfolio",
    ]
    for ep in core_eps:
        try:
            r = requests.get(f"{API_BASE}{ep}", timeout=5)
            results.append(check(f"Endpoint {ep}", r.status_code in [200, 404], f"Status: {r.status_code}"))
        except Exception as e:
            results.append(check(f"Endpoint {ep}", False, str(e)[:50]))

    # 7. Files
    print("\n=== File Structure ===")
    files_to_check = [
        (ROOT_DIR / "dashboard" / "frontend" / "dist" / "index.html", "Frontend Build"),
        (ROOT_DIR / "agent_memory" / "tasks.json", "Agent Memory"),
        (ROOT_DIR / "desktop_app" / "main.js", "Electron Main"),
        (ROOT_DIR / "desktop_app" / "package.json", "Electron Config"),
    ]
    for file_path, name in files_to_check:
        results.append(check(name, file_path.exists(), str(file_path)))

    # Summary
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All systems operational!")
        print("\nSystem is ready for:")
        print("  - Dashboard access: http://localhost:3000")
        print("  - API access: http://localhost:8000")
        print("  - Desktop app build: cd desktop_app && npm run build:win")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
