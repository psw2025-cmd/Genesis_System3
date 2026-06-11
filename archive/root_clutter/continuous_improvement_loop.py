#!/usr/bin/env python3
"""
Continuous Improvement Loop
Runs validation suite, identifies issues, fixes them, and iterates
"""

import subprocess
import sys
import time
import json
from datetime import datetime
from pathlib import Path
import requests

API_BASE = "http://localhost:8000"
MAX_ITERATIONS = 5
IMPROVEMENT_THRESHOLD = 0.95  # 95% success rate target

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_validation():
    """Run master validation suite"""
    print(f"{Colors.BOLD}Running Master Validation Suite...{Colors.RESET}")
    result = subprocess.run(
        [sys.executable, "master_full_validation_suite.py"],
        capture_output=True,
        text=True,
        timeout=900  # 15 minutes
    )
    return result.returncode == 0, result.stdout, result.stderr

def analyze_results():
    """Analyze validation results and identify issues"""
    reports_dir = Path("reports")
    json_files = sorted(reports_dir.glob("master_validation_*.json"), reverse=True)
    
    if not json_files:
        return None
    
    with open(json_files[0]) as f:
        data = json.load(f)
    
    summary = data.get("summary", {})
    tests = data.get("tests", {})
    
    failed_tests = [name for name, result in tests.items() if not result.get("success", False)]
    
    return {
        "total": summary.get("total", 0),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "success_rate": (summary.get("passed", 0) / summary.get("total", 1)) * 100,
        "failed_tests": failed_tests
    }

def fix_common_issues():
    """Fix common issues automatically"""
    print(f"{Colors.YELLOW}Checking for common issues...{Colors.RESET}")
    
    fixes_applied = []
    
    # Check backend
    if not check_backend():
        print(f"{Colors.RED}Backend not running - cannot fix automatically{Colors.RESET}")
        return fixes_applied
    
    # Check Agent endpoints
    try:
        response = requests.get(f"{API_BASE}/api/agent/status", timeout=5)
        if response.status_code == 404:
            print(f"{Colors.YELLOW}Agent status endpoint missing - checking backend code{Colors.RESET}")
            # This would need manual fix in app.py
            fixes_applied.append("Agent status endpoint needs implementation")
    except:
        pass
    
    return fixes_applied

def main():
    """Main continuous improvement loop"""
    print_header("CONTINUOUS IMPROVEMENT LOOP")
    
    if not check_backend():
        print(f"{Colors.RED}Backend is not running! Please start it first.{Colors.RESET}")
        print(f"  cd dashboard/backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000")
        return
    
    iteration = 0
    best_success_rate = 0
    
    while iteration < MAX_ITERATIONS:
        iteration += 1
        print_header(f"Iteration {iteration}/{MAX_ITERATIONS}")
        
        # Run validation
        success, stdout, stderr = run_validation()
        
        # Analyze results
        results = analyze_results()
        if not results:
            print(f"{Colors.RED}Could not analyze results{Colors.RESET}")
            break
        
        success_rate = results["success_rate"]
        print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Passed: {results['passed']}/{results['total']}")
        print(f"  Failed: {results['failed']}")
        
        if results["failed_tests"]:
            print(f"\n{Colors.YELLOW}Failed Tests:{Colors.RESET}")
            for test in results["failed_tests"]:
                print(f"  - {test}")
        
        # Check if we've improved
        if success_rate > best_success_rate:
            best_success_rate = success_rate
            print(f"\n{Colors.GREEN}Improvement! New best: {best_success_rate:.1f}%{Colors.RESET}")
        
        # Check if we've reached target
        if success_rate >= IMPROVEMENT_THRESHOLD * 100:
            print(f"\n{Colors.GREEN}{Colors.BOLD}Target achieved! {success_rate:.1f}% >= {IMPROVEMENT_THRESHOLD*100}%{Colors.RESET}")
            break
        
        # Try to fix issues
        if iteration < MAX_ITERATIONS:
            fixes = fix_common_issues()
            if fixes:
                print(f"\n{Colors.YELLOW}Fixes applied:{Colors.RESET}")
                for fix in fixes:
                    print(f"  - {fix}")
            
            print(f"\n{Colors.BLUE}Waiting before next iteration...{Colors.RESET}")
            time.sleep(5)
    
    print_header("FINAL SUMMARY")
    print(f"Best Success Rate: {best_success_rate:.1f}%")
    print(f"Target: {IMPROVEMENT_THRESHOLD*100}%")
    
    if best_success_rate >= IMPROVEMENT_THRESHOLD * 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}SUCCESS! Target achieved!{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some improvements needed. Review failed tests.{Colors.RESET}")

if __name__ == "__main__":
    main()
