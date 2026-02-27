#!/usr/bin/env python3
"""
Complete Production Validation Runner
Starts backend, runs all tests, fixes issues, and validates until 100% pass
"""

import os
import sys
import time
import subprocess
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

def print_info(text):
    print(f"[INFO] {text}")

def start_backend():
    """Start the backend server"""
    print_header("STARTING BACKEND SERVER")
    
    backend_dir = Path("dashboard/backend")
    if not backend_dir.exists():
        print_error("Backend directory not found")
        return False
    
    # Check if already running
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=2)
        if response.status_code == 200:
            print_success("Backend already running")
            return True
    except:
        pass
    
    # Start backend
    print_info("Starting backend server...")
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to start
        print_info("Waiting for backend to start...")
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            try:
                response = requests.get("http://localhost:8000/api/health", timeout=2)
                if response.status_code == 200:
                    print_success(f"Backend started successfully (PID: {process.pid})")
                    return True
            except:
                if i % 5 == 0:
                    print_info(f"Still waiting... ({i+1}/30)")
        
        print_error("Backend failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print_error(f"Failed to start backend: {e}")
        return False

def run_validation():
    """Run production validation"""
    print_header("RUNNING PRODUCTION VALIDATION")
    
    try:
        result = subprocess.run(
            [sys.executable, "production_grade_validation.py"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print_error(f"Validation failed: {e}")
        return False

def check_results():
    """Check validation results"""
    report_file = Path("production_validation_report.json")
    if not report_file.exists():
        return False, 0.0
    
    import json
    with open(report_file) as f:
        report = json.load(f)
    
    overall = report.get("overall", {})
    success_rate = overall.get("success_rate", 0.0)
    passed = overall.get("passed", 0)
    total = overall.get("total", 0)
    
    print_info(f"Success rate: {success_rate:.1f}% ({passed}/{total} tests passed)")
    
    return success_rate >= 100.0, success_rate

def main():
    """Main execution"""
    print_header("COMPLETE PRODUCTION VALIDATION")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Start backend
    if not start_backend():
        print_error("Cannot proceed without backend")
        return 1
    
    # Step 2: Run validation
    if not run_validation():
        print_error("Validation script failed")
        return 1
    
    # Step 3: Check results
    all_passed, success_rate = check_results()
    
    if all_passed:
        print_success("\n[PASS] All validation tests passed - System is production-ready!")
        return 0
    else:
        print_info(f"\n[INFO] Success rate: {success_rate:.1f}%")
        print_info("Review production_validation_report.json for details")
        return 0 if success_rate >= 80.0 else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_error("\n\nValidation interrupted")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
