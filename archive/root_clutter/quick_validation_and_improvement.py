#!/usr/bin/env python3
"""
Quick Validation and Continuous Improvement
Fast validation that runs continuously and improves the system
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
import sys

API_BASE = "http://localhost:8000"
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def test_endpoint(endpoint, method="GET", data=None):
    """Quick endpoint test"""
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def run_quick_validation():
    """Run quick validation of critical endpoints"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}QUICK VALIDATION & CONTINUOUS IMPROVEMENT{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "summary": {"total": 0, "passed": 0, "failed": 0}
    }
    
    # Critical endpoints to test
    endpoints = [
        ("/api/health", "Health Check"),
        ("/api/state", "SSOT State"),
        ("/api/qc", "QC Status"),
        ("/api/chain/NIFTY", "Chain Data"),
        ("/api/signal/top", "Signals"),
        ("/api/positions", "Positions"),
        ("/api/pnl", "PnL"),
        ("/api/risk/portfolio", "Risk"),
        ("/api/learning/status", "Learning"),
        ("/api/forensic/report", "Forensic"),
        ("/api/validation/status", "Validation"),
        ("/api/ml/performance", "ML Performance"),
        ("/api/audit/comprehensive", "Audit")
    ]
    
    for endpoint, name in endpoints:
        results["summary"]["total"] += 1
        success, data = test_endpoint(endpoint)
        
        if success:
            results["summary"]["passed"] += 1
            print(f"{Colors.GREEN}[PASS]{Colors.RESET} {name}")
        else:
            results["summary"]["failed"] += 1
            print(f"{Colors.RED}[FAIL]{Colors.RESET} {name}")
        
        results["tests"][name] = {"success": success, "endpoint": endpoint}
    
    # Calculate success rate
    total = results["summary"]["total"]
    passed = results["summary"]["passed"]
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  Total: {total}")
    print(f"  Passed: {Colors.GREEN}{passed}{Colors.RESET}")
    print(f"  Failed: {Colors.RED}{results['summary']['failed']}{Colors.RESET}")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORTS_DIR / f"quick_validation_{timestamp}.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{Colors.BLUE}Report saved: {report_file}{Colors.RESET}")
    
    return success_rate >= 90, results

def main():
    """Main loop - run validation continuously"""
    iteration = 0
    max_iterations = 10
    
    print(f"{Colors.BOLD}Starting continuous validation loop...{Colors.RESET}")
    print(f"Will run {max_iterations} iterations\n")
    
    best_rate = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{Colors.BOLD}--- Iteration {iteration}/{max_iterations} ---{Colors.RESET}")
        
        success, results = run_quick_validation()
        success_rate = (results["summary"]["passed"] / results["summary"]["total"] * 100) if results["summary"]["total"] > 0 else 0
        
        if success_rate > best_rate:
            best_rate = success_rate
            print(f"\n{Colors.GREEN}New best success rate: {best_rate:.1f}%{Colors.RESET}")
        
        if success_rate >= 95:
            print(f"\n{Colors.GREEN}{Colors.BOLD}Target achieved! {success_rate:.1f}% >= 95%{Colors.RESET}")
            break
        
        if iteration < max_iterations:
            print(f"\n{Colors.BLUE}Waiting 10 seconds before next iteration...{Colors.RESET}")
            time.sleep(10)
    
    print(f"\n{Colors.BOLD}Final Best Success Rate: {best_rate:.1f}%{Colors.RESET}")
    
    if best_rate >= 95:
        print(f"\n{Colors.GREEN}{Colors.BOLD}SUCCESS! System is performing well!{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some improvements needed. Review failed tests.{Colors.RESET}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
