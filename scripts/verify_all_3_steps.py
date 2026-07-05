"""
Verify All 3 Steps: Frontend, Dashboard Access, Desktop Build
"""

import os
import sys
import time
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


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
    print("System3 Ultra - All 3 Steps Verification")
    print("=" * 70)
    print()

    results = []

    # STEP 1: Frontend
    print("=== STEP 1: Frontend ===")
    try:
        r = requests.get("http://localhost:3000", timeout=5)
        results.append(check("Frontend Running", r.status_code == 200, f"Status: {r.status_code}"))
    except Exception as e:
        results.append(check("Frontend Running", False, str(e)[:50]))

    # STEP 2: Dashboard Access
    print("\n=== STEP 2: Dashboard Access ===")
    try:
        r1 = requests.get("http://localhost:8000/api/health", timeout=5)
        results.append(check("Backend API", r1.status_code == 200, f"Status: {r1.status_code}"))
    except Exception as e:
        results.append(check("Backend API", False, str(e)[:50]))

    try:
        r2 = requests.get("http://localhost:8000/api/state", timeout=5)
        if r2.status_code == 200:
            data = r2.json()
            results.append(check("SSOT Endpoint", True, f"Version: {data.get('state_version')}"))
        else:
            results.append(check("SSOT Endpoint", False, f"Status: {r2.status_code}"))
    except Exception as e:
        results.append(check("SSOT Endpoint", False, str(e)[:50]))

    # STEP 3: Desktop App Build
    print("\n=== STEP 3: Desktop App Build ===")
    dist_dir = Path("desktop_app/dist")
    exe_exists = (dist_dir / "win-unpacked" / "System3 Ultra.exe").exists()
    portable_exists = (dist_dir / "System3 Ultra.exe").exists()

    if exe_exists:
        results.append(check("Desktop App EXE", True, "win-unpacked/System3 Ultra.exe"))
    elif portable_exists:
        results.append(check("Desktop App Portable", True, "System3 Ultra.exe"))
    else:
        results.append(check("Desktop App Build", False, "EXE not found"))

    # Summary
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} steps passed")

    if passed == total:
        print("\n[SUCCESS] All 3 steps completed successfully!")
        print("\nAccess:")
        print("  Frontend: http://localhost:3000")
        print("  Backend:  http://localhost:8000")
        if exe_exists or portable_exists:
            print("  Desktop:  desktop_app/dist/")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} step(s) need attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())
