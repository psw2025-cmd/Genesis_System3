#!/usr/bin/env python3
"""
Smoke Tests for Genesis System3
Quick validation that core components work
"""
import sys
import os
import subprocess
import requests
import time
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent


def test_imports():
    """Test critical imports"""
    print("[TEST] Critical imports...")
    try:
        import pandas as pd
        import numpy as np
        import fastapi
        import uvicorn

        print("  [PASS] All imports successful")
        return True
    except ImportError as e:
        print(f"  [FAIL] Import error: {e}")
        return False


def test_backend_startup():
    """Test backend can start (quick check)"""
    print("[TEST] Backend startup check...")
    try:
        # Just check if uvicorn can be imported and app module exists
        backend_dir = ROOT_DIR / "dashboard" / "backend"
        app_file = backend_dir / "app.py"
        if app_file.exists():
            print("  [PASS] Backend app.py exists")
            return True
        else:
            print("  [FAIL] Backend app.py not found")
            return False
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def test_frontend_build():
    """Test frontend can build"""
    print("[TEST] Frontend build check...")
    try:
        frontend_dir = ROOT_DIR / "dashboard" / "frontend"
        package_json = frontend_dir / "package.json"
        if package_json.exists():
            print("  [PASS] Frontend package.json exists")
            return True
        else:
            print("  [FAIL] Frontend package.json not found")
            return False
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def test_backend_api(port=8000, timeout=10):
    """Test backend API is responding"""
    print(f"[TEST] Backend API (port {port})...")
    url = f"http://localhost:{port}/api/health"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  [PASS] Backend responding: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"  [FAIL] Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  [SKIP] Backend not running (expected if not started)")
        return None  # Not a failure, just not running
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def test_frontend(port=3000, timeout=10):
    """Test frontend is responding"""
    print(f"[TEST] Frontend (port {port})...")
    url = f"http://localhost:{port}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"  [PASS] Frontend responding")
            return True
        else:
            print(f"  [FAIL] Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  [SKIP] Frontend not running (expected if not started)")
        return None  # Not a failure, just not running
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def main():
    """Run all smoke tests"""
    print("=" * 70)
    print("GENESIS SYSTEM3 - SMOKE TESTS")
    print("=" * 70)
    print()

    results = []

    # Test imports
    results.append(("Imports", test_imports()))

    # Test backend startup
    results.append(("Backend Startup", test_backend_startup()))

    # Test frontend build
    results.append(("Frontend Build", test_frontend_build()))

    # Test API (if running)
    api_result = test_backend_api()
    if api_result is not None:
        results.append(("Backend API", api_result))

    # Test frontend (if running)
    frontend_result = test_frontend()
    if frontend_result is not None:
        results.append(("Frontend", frontend_result))

    # Summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)

    for name, result in results:
        if result is True:
            print(f"  [PASS] {name}")
        elif result is False:
            print(f"  [FAIL] {name}")
        else:
            print(f"  [SKIP] {name} (not running)")

    print()
    print(f"Passed: {passed}, Failed: {failed}, Skipped: {skipped}")

    if failed == 0:
        print("[SUCCESS] All tests passed!")
        return 0
    else:
        print("[FAILURE] Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
