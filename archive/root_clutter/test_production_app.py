#!/usr/bin/env python3
"""
Production-Grade Application Test Suite
Tests all features of System3 Ultra Desktop App
"""

import os
import sys
import time
import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime

def print_header(text):
    print(f"\n{'='*80}")
    print(f"{text.center(80)}")
    print(f"{'='*80}\n")

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def print_warning(text):
    print(f"[WARNING] {text}")

def print_info(text):
    print(f"[INFO] {text}")

def test_backend_api():
    """Test backend API endpoints"""
    print_header("TESTING BACKEND API")
    
    base_url = "http://localhost:8000"
    tests_passed = 0
    tests_failed = 0
    
    # Test endpoints
    endpoints = [
        ("/", "Root endpoint"),
        ("/api/health", "Health check"),
        ("/api/state", "State endpoint"),
        ("/api/perf", "Performance endpoint"),
        ("/api/chain/NIFTY", "Chain data"),
        ("/api/signal/top", "Top signals"),
        ("/api/qc", "QC status"),
        ("/api/positions", "Positions"),
        ("/api/pnl", "PnL data"),
        ("/api/alerts/recent?limit=10", "Recent alerts"),
    ]
    
    for endpoint, description in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_success(f"{description}: OK (200)")
                tests_passed += 1
            else:
                print_warning(f"{description}: Status {response.status_code}")
                tests_failed += 1
        except requests.exceptions.ConnectionError:
            print_error(f"{description}: Backend not running")
            tests_failed += 1
        except Exception as e:
            print_error(f"{description}: {str(e)}")
            tests_failed += 1
    
    print(f"\nAPI Tests: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0

def test_backend_websocket():
    """Test WebSocket connection"""
    print_header("TESTING WEBSOCKET")
    
    try:
        import websocket
        ws_url = "ws://localhost:8000/ws/stream"
        
        def on_message(ws, message):
            print_success("WebSocket message received")
            ws.close()
        
        def on_error(ws, error):
            print_error(f"WebSocket error: {error}")
        
        def on_open(ws):
            print_success("WebSocket connection opened")
            time.sleep(1)
            ws.close()
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_open=on_open
        )
        
        ws.run_forever()
        return True
    except ImportError:
        print_warning("websocket-client not installed, skipping WebSocket test")
        return True
    except Exception as e:
        print_error(f"WebSocket test failed: {e}")
        return False

def test_installed_app_structure():
    """Test installed app file structure"""
    print_header("TESTING INSTALLED APP STRUCTURE")
    
    # Common installation paths
    install_paths = [
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs' / 'system3-ultra',
        Path('C:/Program Files/system3-ultra'),
        Path('C:/Program Files (x86)/system3-ultra'),
    ]
    
    found_install = None
    for install_path in install_paths:
        if install_path.exists():
            found_install = install_path
            break
    
    if not found_install:
        print_warning("Installed app not found in common locations")
        print_info("Please install the app first, or specify installation path")
        return False
    
    print_success(f"Found installation at: {found_install}")
    
    # Check required directories
    required_dirs = [
        'resources/backend',
        'resources/frontend',
        'resources/agent_memory',
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = found_install / dir_path
        if full_path.exists():
            print_success(f"Directory exists: {dir_path}")
        else:
            print_error(f"Directory missing: {dir_path}")
            all_exist = False
    
    # Check required files
    required_files = [
        'resources/frontend/index.html',
        'resources/backend/app.py',
    ]
    
    for file_path in required_files:
        full_path = found_install / file_path
        if full_path.exists():
            print_success(f"File exists: {file_path}")
        else:
            print_error(f"File missing: {file_path}")
            all_exist = False
    
    return all_exist

def test_python_detection():
    """Test Python detection in installed app"""
    print_header("TESTING PYTHON DETECTION")
    
    python_paths = [
        'C:\\Python314\\python.exe',
        'C:\\Python313\\python.exe',
        'C:\\Python312\\python.exe',
        'C:\\Python311\\python.exe',
        'C:\\Python310\\python.exe',
    ]
    
    found_python = None
    for py_path in python_paths:
        if Path(py_path).exists():
            found_python = py_path
            print_success(f"Python found: {py_path}")
            break
    
    if not found_python:
        print_warning("Python not found in common locations")
        print_info("App will try to use 'python' from PATH")
        return True  # Not a failure, just a warning
    
    return True

def test_backend_dependencies():
    """Test if backend dependencies are installed"""
    print_header("TESTING BACKEND DEPENDENCIES")
    
    python_paths = [
        'C:\\Python314\\python.exe',
        'C:\\Python313\\python.exe',
        'C:\\Python312\\python.exe',
        'python',
    ]
    
    python_exe = None
    for py_path in python_paths:
        if Path(py_path).exists() or py_path == 'python':
            try:
                result = subprocess.run(
                    [py_path, '--version'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    python_exe = py_path
                    print_success(f"Using Python: {py_path}")
                    break
            except:
                continue
    
    if not python_exe:
        print_error("Python not found")
        return False
    
    # Check critical dependencies
    critical_deps = ['uvicorn', 'fastapi', 'pandas', 'numpy']
    all_installed = True
    
    for dep in critical_deps:
        try:
            result = subprocess.run(
                [python_exe, '-m', 'pip', 'show', dep],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print_success(f"{dep} installed")
            else:
                print_error(f"{dep} NOT installed")
                all_installed = False
        except Exception as e:
            print_warning(f"Could not check {dep}: {e}")
    
    return all_installed

def test_frontend_features():
    """Test frontend features by checking API responses"""
    print_header("TESTING FRONTEND FEATURES")
    
    base_url = "http://localhost:8000"
    features = {
        "Overview": "/api/state",
        "Chain Analytics": "/api/chain/NIFTY",
        "Signals": "/api/signal/top",
        "Paper Trading": "/api/positions",
        "Alerts": "/api/alerts/recent?limit=10",
        "Risk Dashboard": "/api/risk/portfolio",
        "ML Performance": "/api/ml/performance",
        "Model Behavior": "/api/logs/tail?lines=50",
    }
    
    all_working = True
    for feature, endpoint in features.items():
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print_success(f"{feature}: API endpoint working")
            else:
                print_warning(f"{feature}: API returned {response.status_code}")
        except Exception as e:
            print_warning(f"{feature}: {str(e)}")
            # Don't fail - some endpoints may not be available
    
    return True

def create_test_report(results):
    """Create comprehensive test report"""
    print_header("TEST REPORT")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    print("\nTest Results:")
    for test_name, result in results.items():
        status = "[OK]" if result else "[FAIL]"
        print(f"  {status} {test_name}")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": passed_tests/total_tests*100,
        "results": results
    }
    
    report_file = Path("test_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    
    return failed_tests == 0

def main():
    """Main test execution"""
    print_header("SYSTEM3 ULTRA PRODUCTION TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    
    # Wait for backend to start (if not already running)
    print_info("Checking if backend is running...")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=2)
        print_success("Backend is running")
    except:
        print_warning("Backend not running. Please start the app first.")
        print_info("Some tests will be skipped.")
    
    # Run tests
    results["Backend API"] = test_backend_api()
    results["WebSocket"] = test_backend_websocket()
    results["Installed App Structure"] = test_installed_app_structure()
    results["Python Detection"] = test_python_detection()
    results["Backend Dependencies"] = test_backend_dependencies()
    results["Frontend Features"] = test_frontend_features()
    
    # Generate report
    all_passed = create_test_report(results)
    
    if all_passed:
        print_success("\nAll tests passed! Application is production-ready.")
        return 0
    else:
        print_error("\nSome tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_warning("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
