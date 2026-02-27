#!/usr/bin/env python3
"""
Master Full Validation Suite
Runs comprehensive multi-validation, audit, QC, performance, and E2E tests
"""

import subprocess
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import requests

# Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
API_BASE = "http://localhost:8000"

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}[PASS] {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}[FAIL] {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.RESET}")

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_script(script_path, description):
    """Run a validation script"""
    print(f"\n{Colors.BOLD}Running: {description}{Colors.RESET}")
    print(f"Script: {script_path}")
    
    if not Path(script_path).exists():
        print_error(f"Script not found: {script_path}")
        return False, None
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for comprehensive tests
        )
        
        if result.returncode == 0:
            print_success(f"{description} completed")
            return True, result.stdout
        else:
            print_error(f"{description} failed")
            print(f"Error: {result.stderr[:500]}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print_error(f"{description} timed out")
        return False, "Timeout"
    except Exception as e:
        print_error(f"{description} error: {e}")
        return False, str(e)

class MasterValidator:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
    
    def run_all_validations(self):
        """Run all validation tests"""
        print_header("MASTER FULL VALIDATION SUITE")
        
        # Check backend first
        print(f"\n{Colors.BOLD}Checking backend...{Colors.RESET}")
        if not check_backend():
            print_error("Backend is not running! Please start the backend first.")
            print(f"  Start with: cd dashboard/backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000")
            return False
        print_success("Backend is running")
        
        # 1. Production Grade Validation
        self.run_test(
            "production_grade_zero_errors_validation.py",
            "Production Grade Zero Errors Validation"
        )
        
        # 2. Comprehensive Pre-Build Validation
        self.run_test(
            "comprehensive_pre_build_validation.py",
            "Comprehensive Pre-Build Validation"
        )
        
        # 3. E2E Self Test
        self.run_test(
            "e2e_selftest.py",
            "E2E Self Test"
        )
        
        # 4. Comprehensive E2E Test (All Tabs)
        self.run_test(
            "comprehensive_e2e_test_all_tabs.py",
            "Comprehensive E2E Test (All Tabs)"
        )
        
        # 5. QC Audit
        self.run_test(
            "comprehensive_qc_audit.py",
            "Comprehensive QC Audit"
        )
        
        # 6. Multi-Validation Audit (via API)
        self.run_api_test("Multi-Validation Audit", "/api/audit/comprehensive")
        
        # 7. Performance Test
        self.run_performance_test()
        
        # 8. Dashboard Validation
        dashboard_script = Path("scripts/comprehensive_dashboard_validation.py")
        if dashboard_script.exists():
            self.run_test(
                str(dashboard_script),
                "Comprehensive Dashboard Validation"
            )
        
        # Generate final report
        self.generate_report()
        self.print_summary()
        
        return self.results["summary"]["failed"] == 0
    
    def run_test(self, script_path, description):
        """Run a test script"""
        self.results["summary"]["total"] += 1
        success, output = run_script(script_path, description)
        
        self.results["tests"][description] = {
            "script": script_path,
            "success": success,
            "output": output[:1000] if output else None,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
    
    def run_api_test(self, description, endpoint):
        """Run an API test"""
        self.results["summary"]["total"] += 1
        print(f"\n{Colors.BOLD}Testing API: {description}{Colors.RESET}")
        print(f"Endpoint: {endpoint}")
        
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=30)
            if response.status_code == 200:
                data = response.json()
                print_success(f"{description} - API responded")
                self.results["tests"][description] = {
                    "endpoint": endpoint,
                    "success": True,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                }
                self.results["summary"]["passed"] += 1
                return True
            else:
                print_error(f"{description} - Status {response.status_code}")
                self.results["tests"][description] = {
                    "endpoint": endpoint,
                    "success": False,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                }
                self.results["summary"]["failed"] += 1
                return False
        except Exception as e:
            print_error(f"{description} - Error: {e}")
            self.results["tests"][description] = {
                "endpoint": endpoint,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results["summary"]["failed"] += 1
            return False
    
    def run_performance_test(self):
        """Run performance test"""
        self.results["summary"]["total"] += 1
        print(f"\n{Colors.BOLD}Running Performance Test{Colors.RESET}")
        
        endpoints = [
            "/api/health",
            "/api/state",
            "/api/chain/NIFTY",
            "/api/signal/top",
            "/api/positions",
            "/api/pnl"
        ]
        
        results = []
        total_time = 0
        
        for endpoint in endpoints:
            try:
                start = time.time()
                response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
                elapsed = time.time() - start
                total_time += elapsed
                
                results.append({
                    "endpoint": endpoint,
                    "status": response.status_code,
                    "time_ms": elapsed * 1000,
                    "success": response.status_code == 200
                })
                
                if response.status_code == 200:
                    print_success(f"{endpoint}: {elapsed*1000:.1f}ms")
                else:
                    print_error(f"{endpoint}: Status {response.status_code}")
            except Exception as e:
                results.append({
                    "endpoint": endpoint,
                    "error": str(e),
                    "success": False
                })
                print_error(f"{endpoint}: {e}")
        
        avg_time = (total_time / len(endpoints)) * 1000 if endpoints else 0
        
        self.results["tests"]["Performance Test"] = {
            "success": all(r.get("success", False) for r in results),
            "results": results,
            "average_time_ms": avg_time,
            "timestamp": datetime.now().isoformat()
        }
        
        if avg_time < 1000:
            print_success(f"Performance: Average {avg_time:.1f}ms (Excellent)")
            self.results["summary"]["passed"] += 1
        elif avg_time < 2000:
            print_warning(f"Performance: Average {avg_time:.1f}ms (Good)")
            self.results["summary"]["passed"] += 1
            self.results["summary"]["warnings"] += 1
        else:
            print_error(f"Performance: Average {avg_time:.1f}ms (Slow)")
            self.results["summary"]["failed"] += 1
    
    def generate_report(self):
        """Generate final report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = REPORTS_DIR / f"master_validation_{timestamp}.json"
        md_file = REPORTS_DIR / f"master_validation_{timestamp}.md"
        
        # Save JSON
        with open(json_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Generate Markdown
        summary = self.results["summary"]
        md_content = f"""# Master Full Validation Suite Report

**Generated:** {datetime.now().isoformat()}

## Summary

- **Total Tests:** {summary['total']}
- **Passed:** {summary['passed']}
- **Failed:** {summary['failed']}
- **Warnings:** {summary['warnings']}
- **Success Rate:** {(summary['passed']/summary['total']*100) if summary['total'] > 0 else 0:.1f}%

## Test Results

"""
        
        for test_name, test_result in self.results["tests"].items():
            status = "[PASS]" if test_result.get("success") else "[FAIL]"
            md_content += f"### {status} {test_name}\n\n"
            md_content += f"- **Status:** {'PASS' if test_result.get('success') else 'FAIL'}\n"
            md_content += f"- **Timestamp:** {test_result.get('timestamp', 'N/A')}\n"
            
            if "endpoint" in test_result:
                md_content += f"- **Endpoint:** {test_result['endpoint']}\n"
            if "script" in test_result:
                md_content += f"- **Script:** {test_result['script']}\n"
            if "average_time_ms" in test_result:
                md_content += f"- **Average Time:** {test_result['average_time_ms']:.1f}ms\n"
            
            md_content += "\n"
        
        md_content += f"""
## Detailed Results

See JSON report: `{json_file.name}`

---
**Report generated at:** {datetime.now().isoformat()}
"""
        
        with open(md_file, "w") as f:
            f.write(md_content)
        
        print(f"\n{Colors.BOLD}Report Generated:{Colors.RESET}")
        print(f"  JSON: {json_file}")
        print(f"  Markdown: {md_file}")
    
    def print_summary(self):
        """Print final summary"""
        print_header("FINAL SUMMARY")
        
        summary = self.results["summary"]
        total = summary["total"]
        passed = summary["passed"]
        failed = summary["failed"]
        warnings = summary["warnings"]
        
        print(f"Total Tests: {total}")
        print(f"  {Colors.GREEN}Passed: {passed}{Colors.RESET}")
        print(f"  {Colors.RED}Failed: {failed}{Colors.RESET}")
        if warnings > 0:
            print(f"  {Colors.YELLOW}Warnings: {warnings}{Colors.RESET}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED! [PASS]{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}{failed} TEST(S) FAILED [FAIL]{Colors.RESET}")

def main():
    """Main execution"""
    validator = MasterValidator()
    
    try:
        success = validator.run_all_validations()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Validation interrupted by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Validation failed with error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
