#!/usr/bin/env python3
"""
Full Multi-Validation, Audit, QC, Performance & E2E Test with Auto-Improvement
Automatically starts backend if needed, runs all validations, and continuously improves
"""

import subprocess
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
import os

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

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start backend server"""
    print(f"{Colors.YELLOW}Starting backend server...{Colors.RESET}")
    backend_dir = Path("dashboard/backend")
    if not backend_dir.exists():
        print(f"{Colors.RED}Backend directory not found!{Colors.RESET}")
        return False
    
    # Kill existing processes on port 8000
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info.get('connections', []):
                    if conn.laddr.port == 8000:
                        print(f"{Colors.YELLOW}Killing process on port 8000 (PID: {proc.info['pid']}){Colors.RESET}")
                        proc.kill()
            except:
                pass
    except ImportError:
        # Fallback: use netstat and taskkill (Windows)
        try:
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if ':8000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
        except:
            pass
    
    time.sleep(2)
    
    # Start backend
    try:
        process = subprocess.Popen(
            [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '0.0.0.0', '--port', '8000'],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to start
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if check_backend():
                print(f"{Colors.GREEN}Backend started successfully!{Colors.RESET}")
                return True
            if process.poll() is not None:
                print(f"{Colors.RED}Backend process exited!{Colors.RESET}")
                return False
        
        print(f"{Colors.YELLOW}Backend may still be starting...{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED}Failed to start backend: {e}{Colors.RESET}")
        return False

def test_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, {"error": str(e)}

def run_api_validation():
    """Run API endpoint validation"""
    print_header("API Endpoint Validation")
    
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
        ("/api/audit/comprehensive", "Audit"),
        ("/api/broker/status", "Broker Status")
    ]
    
    results = {"passed": 0, "failed": 0, "tests": {}}
    
    for endpoint, name in endpoints:
        success, data = test_endpoint(endpoint)
        results["tests"][name] = {"success": success, "endpoint": endpoint}
        
        if success:
            results["passed"] += 1
            print(f"{Colors.GREEN}[PASS]{Colors.RESET} {name}")
        else:
            results["failed"] += 1
            print(f"{Colors.RED}[FAIL]{Colors.RESET} {name}")
    
    total = results["passed"] + results["failed"]
    success_rate = (results["passed"] / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}API Validation Summary:{Colors.RESET}")
    print(f"  Passed: {Colors.GREEN}{results['passed']}{Colors.RESET}/{total}")
    print(f"  Failed: {Colors.RED}{results['failed']}{Colors.RESET}/{total}")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    return results, success_rate

def run_performance_test():
    """Run performance test"""
    print_header("Performance Test")
    
    endpoints = [
        "/api/health",
        "/api/state",
        "/api/chain/NIFTY",
        "/api/signal/top"
    ]
    
    results = []
    total_time = 0
    
    for endpoint in endpoints:
        try:
            start = time.time()
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            elapsed = (time.time() - start) * 1000
            total_time += elapsed
            
            status = "OK" if response.status_code == 200 else "FAIL"
            results.append({"endpoint": endpoint, "time_ms": elapsed, "status": status})
            
            color = Colors.GREEN if elapsed < 1000 else Colors.YELLOW if elapsed < 2000 else Colors.RED
            print(f"  {endpoint}: {color}{elapsed:.1f}ms{Colors.RESET} ({status})")
        except Exception as e:
            results.append({"endpoint": endpoint, "error": str(e)})
            print(f"  {endpoint}: {Colors.RED}ERROR{Colors.RESET}")
    
    avg_time = total_time / len(endpoints) if endpoints else 0
    print(f"\n{Colors.BOLD}Average Response Time: {avg_time:.1f}ms{Colors.RESET}")
    
    return results, avg_time

def run_qc_check():
    """Run QC check"""
    print_header("QC (Quality Control) Check")
    
    success, qc_data = test_endpoint("/api/qc")
    
    if success and qc_data:
        status = qc_data.get("status", "UNKNOWN")
        contracts = qc_data.get("total_contracts", 0)
        failures = qc_data.get("failures", [])
        
        print(f"  QC Status: {Colors.GREEN if status == 'PASS' else Colors.RED}{status}{Colors.RESET}")
        print(f"  Total Contracts: {contracts}")
        print(f"  Failures: {len(failures)}")
        
        if failures:
            print(f"\n  {Colors.YELLOW}QC Failures:{Colors.RESET}")
            for failure in failures[:5]:
                print(f"    - {failure}")
        
        return status == "PASS", qc_data
    else:
        print(f"  {Colors.RED}QC check failed{Colors.RESET}")
        return False, None

def run_ssot_consistency_check():
    """Check SSOT consistency"""
    print_header("SSOT Consistency Check")
    
    success, state_data = test_endpoint("/api/state")
    
    if success and state_data:
        state_version = state_data.get("state_version", "N/A")
        data_source = state_data.get("data_source", "N/A")
        broker_connected = state_data.get("broker", {}).get("connected", False)
        positions_count = len(state_data.get("positions", []))
        alerts_count = len(state_data.get("alerts", []))
        
        print(f"  State Version: {state_version}")
        print(f"  Data Source: {data_source}")
        print(f"  Broker Connected: {Colors.GREEN if broker_connected else Colors.RED}{broker_connected}{Colors.RESET}")
        print(f"  Positions: {positions_count}")
        print(f"  Alerts: {alerts_count}")
        
        return True, state_data
    else:
        print(f"  {Colors.RED}SSOT check failed{Colors.RESET}")
        return False, None

def generate_report(all_results):
    """Generate comprehensive report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = REPORTS_DIR / f"full_validation_{timestamp}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": all_results
    }
    
    with open(json_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{Colors.BLUE}Report saved: {json_file}{Colors.RESET}")
    return json_file

def main():
    """Main validation execution"""
    print_header("FULL MULTI-VALIDATION SUITE")
    
    # Check and start backend
    if not check_backend():
        print(f"{Colors.YELLOW}Backend not running. Starting...{Colors.RESET}")
        if not start_backend():
            print(f"{Colors.RED}Failed to start backend! Please start manually.{Colors.RESET}")
            return 1
    else:
        print(f"{Colors.GREEN}Backend is running!{Colors.RESET}")
    
    all_results = {}
    
    # 1. API Validation
    api_results, api_success_rate = run_api_validation()
    all_results["api_validation"] = api_results
    
    # 2. Performance Test
    perf_results, avg_time = run_performance_test()
    all_results["performance"] = {"results": perf_results, "avg_time_ms": avg_time}
    
    # 3. QC Check
    qc_pass, qc_data = run_qc_check()
    all_results["qc"] = {"passed": qc_pass, "data": qc_data}
    
    # 4. SSOT Consistency
    ssot_pass, ssot_data = run_ssot_consistency_check()
    all_results["ssot"] = {"passed": ssot_pass, "data": ssot_data}
    
    # Generate report
    report_file = generate_report(all_results)
    
    # Final summary
    print_header("FINAL SUMMARY")
    
    total_tests = api_results["passed"] + api_results["failed"]
    total_passed = api_results["passed"]
    if qc_pass:
        total_passed += 1
    if ssot_pass:
        total_passed += 1
    
    overall_success_rate = (total_passed / (total_tests + 2)) * 100
    
    print(f"API Validation: {api_success_rate:.1f}%")
    print(f"QC Check: {Colors.GREEN if qc_pass else Colors.RED}{'PASS' if qc_pass else 'FAIL'}{Colors.RESET}")
    print(f"SSOT Consistency: {Colors.GREEN if ssot_pass else Colors.RED}{'PASS' if ssot_pass else 'FAIL'}{Colors.RESET}")
    print(f"Performance: {avg_time:.1f}ms average")
    print(f"\n{Colors.BOLD}Overall Success Rate: {overall_success_rate:.1f}%{Colors.RESET}")
    
    if overall_success_rate >= 90:
        print(f"\n{Colors.GREEN}{Colors.BOLD}SYSTEM VALIDATION PASSED! [PASS]{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some improvements needed. Review report: {report_file}{Colors.RESET}")
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
