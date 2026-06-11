#!/usr/bin/env python3
"""
Comprehensive End-to-End Test for All Dashboard Tabs and Features
Tests all 11 tabs, their APIs, data consistency, and functionality
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

API_BASE = "http://localhost:8000"
OUTPUTS_DIR = Path(__file__).parent / "outputs"
REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

class TabTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tabs": {},
            "apis": {},
            "summary": {
                "total_tabs": 11,
                "tabs_passed": 0,
                "tabs_failed": 0,
                "total_apis": 0,
                "apis_passed": 0,
                "apis_failed": 0,
                "overall": "PENDING"
            }
        }
        self.errors = []

    def test_endpoint(self, method: str, endpoint: str, expected_status: int = 200, 
                     data: Optional[Dict] = None, timeout: int = 5) -> tuple[bool, Any]:
        """Test an API endpoint"""
        url = f"{API_BASE}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=timeout)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            success = response.status_code == expected_status
            try:
                json_data = response.json()
            except:
                json_data = {"raw": response.text[:200]}
            
            return success, json_data
        except requests.exceptions.Timeout:
            return False, {"error": "Request timeout"}
        except requests.exceptions.ConnectionError:
            return False, {"error": "Connection error - backend not running"}
        except Exception as e:
            return False, {"error": str(e)}

    def test_tab(self, tab_name: str, endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test a dashboard tab with its associated endpoints"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}Testing Tab: {tab_name}{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
        
        tab_result = {
            "name": tab_name,
            "endpoints": [],
            "passed": 0,
            "failed": 0,
            "status": "PENDING"
        }
        
        for endpoint_info in endpoints:
            endpoint = endpoint_info["endpoint"]
            method = endpoint_info.get("method", "GET")
            expected_status = endpoint_info.get("expected_status", 200)
            description = endpoint_info.get("description", endpoint)
            data = endpoint_info.get("data")
            
            print(f"  Testing: {description}")
            print(f"    {method} {endpoint}")
            
            success, response_data = self.test_endpoint(method, endpoint, expected_status, data)
            
            endpoint_result = {
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": response_data.get("status_code") if isinstance(response_data, dict) else None,
                "success": success,
                "description": description,
                "response_preview": str(response_data)[:200] if response_data else None
            }
            
            tab_result["endpoints"].append(endpoint_result)
            self.results["apis"][endpoint] = endpoint_result
            self.results["summary"]["total_apis"] += 1
            
            if success:
                tab_result["passed"] += 1
                self.results["summary"]["apis_passed"] += 1
                print(f"    {Colors.GREEN}[PASS]{Colors.RESET}")
            else:
                tab_result["failed"] += 1
                self.results["summary"]["apis_failed"] += 1
                error_msg = response_data.get("error", "Unknown error")
                print(f"    {Colors.RED}[FAIL]: {error_msg}{Colors.RESET}")
                self.errors.append(f"{tab_name} - {endpoint}: {error_msg}")
        
        tab_result["status"] = "PASS" if tab_result["failed"] == 0 else "FAIL"
        if tab_result["status"] == "PASS":
            self.results["summary"]["tabs_passed"] += 1
        else:
            self.results["summary"]["tabs_failed"] += 1
        
        print(f"\n  {Colors.BOLD}Tab Result: {tab_result['status']} ({tab_result['passed']}/{tab_result['passed'] + tab_result['failed']} endpoints){Colors.RESET}")
        
        return tab_result

    def test_all_tabs(self):
        """Test all 11 dashboard tabs"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}COMPREHENSIVE DASHBOARD E2E TEST{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
        
        # Test backend health first
        print(f"{Colors.BLUE}Checking backend health...{Colors.RESET}")
        health_success, health_data = self.test_endpoint("GET", "/api/health")
        if not health_success:
            print(f"{Colors.RED}Backend is not responding! Please start the backend first.{Colors.RESET}")
            return False
        
        print(f"{Colors.GREEN}Backend is healthy!{Colors.RESET}\n")
        
        # Define all tabs and their endpoints
        tabs_config = [
            {
                "name": "Overview",
                "endpoints": [
                    {"endpoint": "/api/state", "description": "SSOT State"},
                    {"endpoint": "/api/health", "description": "Health Check"},
                    {"endpoint": "/api/perf", "description": "Performance Metrics"}
                ]
            },
            {
                "name": "Chain Analytics",
                "endpoints": [
                    {"endpoint": "/api/chain/NIFTY", "description": "NIFTY Chain"},
                    {"endpoint": "/api/chain/BANKNIFTY", "description": "BANKNIFTY Chain"},
                    {"endpoint": "/api/chain/FINNIFTY", "description": "FINNIFTY Chain"}
                ]
            },
            {
                "name": "Signals",
                "endpoints": [
                    {"endpoint": "/api/state", "description": "SSOT State (signals)"},
                    {"endpoint": "/api/signal/top", "description": "Top Signal"},
                    {"endpoint": "/api/qc", "description": "QC Status"}
                ]
            },
            {
                "name": "Paper Trading",
                "endpoints": [
                    {"endpoint": "/api/state", "description": "SSOT State (positions)"},
                    {"endpoint": "/api/positions", "description": "Positions"},
                    {"endpoint": "/api/pnl", "description": "PnL Data"}
                ]
            },
            {
                "name": "Alerts",
                "endpoints": [
                    {"endpoint": "/api/state", "description": "SSOT State (alerts)"},
                    {"endpoint": "/api/alerts/recent", "description": "Recent Alerts"},
                    {"endpoint": "/api/alerts/unread", "description": "Unread Count"}
                ]
            },
            {
                "name": "Risk Dashboard",
                "endpoints": [
                    {"endpoint": "/api/state", "description": "SSOT State (risk)"},
                    {"endpoint": "/api/risk/portfolio", "description": "Portfolio Risk"},
                    {
                        "endpoint": "/api/risk/check-limits",
                        "method": "POST",
                        "description": "Check Risk Limits",
                        "data": {
                            "max_positions": 5,
                            "max_exposure": 100000,
                            "max_loss": -5000,
                            "max_concentration_pct": 50
                        }
                    }
                ]
            },
            {
                "name": "Advanced Charts",
                "endpoints": [
                    {"endpoint": "/api/charting/heatmap/NIFTY?metric=oi", "description": "Heatmap (OI)"},
                    {"endpoint": "/api/charting/iv-surface/NIFTY", "description": "IV Surface"},
                    {"endpoint": "/api/charting/greeks/NIFTY?greek=delta", "description": "Greeks Chart"},
                    {"endpoint": "/api/charting/pcr/NIFTY", "description": "PCR Chart"}
                ]
            },
            {
                "name": "ML Performance",
                "endpoints": [
                    {"endpoint": "/api/state", "description": "SSOT State (model)"},
                    {"endpoint": "/api/ml/performance", "description": "ML Performance"},
                    {"endpoint": "/api/ml/compare", "description": "Model Comparison"}
                ]
            },
            {
                "name": "Model Behavior",
                "endpoints": [
                    {"endpoint": "/api/logs/tail?lines=50", "description": "Runtime Logs"},
                    {"endpoint": "/api/audit/secrets", "description": "Security Audit"},
                    {"endpoint": "/api/qc", "description": "QC Status"}
                ]
            },
            {
                "name": "Control Plane",
                "endpoints": [
                    {"endpoint": "/api/learning/status", "description": "Learning Status"},
                    {"endpoint": "/api/learning/insights", "description": "Learning Insights"},
                    {"endpoint": "/api/forensic/report", "description": "Forensic Report"},
                    {"endpoint": "/api/validation/status", "description": "Validation Status"}
                ]
            },
            {
                "name": "Agent Console",
                "endpoints": [
                    {"endpoint": "/api/agent/status", "description": "Agent Status"},
                    {"endpoint": "/api/agent/memory", "description": "Agent Memory"},
                    {"endpoint": "/api/agent/issues", "description": "Detected Issues"},
                    {"endpoint": "/api/agent/upgrade-plan", "description": "Upgrade Plan"}
                ]
            }
        ]
        
        # Test each tab
        for tab_config in tabs_config:
            tab_result = self.test_tab(tab_config["name"], tab_config["endpoints"])
            self.results["tabs"][tab_config["name"]] = tab_result
        
        # Test SSOT consistency
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}Testing SSOT Consistency{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
        
        ssot_success, ssot_data = self.test_endpoint("GET", "/api/state")
        if ssot_success and isinstance(ssot_data, dict):
            print(f"  {Colors.GREEN}[OK] SSOT endpoint accessible{Colors.RESET}")
            print(f"    State Version: {ssot_data.get('state_version', 'N/A')}")
            print(f"    Data Source: {ssot_data.get('data_source', 'N/A')}")
            print(f"    Broker Connected: {ssot_data.get('broker', {}).get('connected', 'N/A')}")
            print(f"    Positions Count: {len(ssot_data.get('positions', []))}")
            print(f"    Alerts Count: {len(ssot_data.get('alerts', []))}")
        else:
            print(f"  {Colors.RED}[FAIL] SSOT endpoint failed{Colors.RESET}")
        
        # Calculate overall status
        total_tests = self.results["summary"]["total_apis"]
        passed_tests = self.results["summary"]["apis_passed"]
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            if success_rate >= 90:
                self.results["summary"]["overall"] = "PASS"
            elif success_rate >= 70:
                self.results["summary"]["overall"] = "WARN"
            else:
                self.results["summary"]["overall"] = "FAIL"
        
        return True

    def generate_report(self):
        """Generate test report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = REPORTS_DIR / f"comprehensive_e2e_test_{timestamp}.json"
        md_file = REPORTS_DIR / f"comprehensive_e2e_test_{timestamp}.md"
        
        # Save JSON report
        with open(json_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Generate Markdown report
        md_content = f"""# Comprehensive Dashboard E2E Test Report

**Generated:** {datetime.now().isoformat()}

## Summary

- **Total Tabs:** {self.results["summary"]["total_tabs"]}
- **Tabs Passed:** {self.results["summary"]["tabs_passed"]}
- **Tabs Failed:** {self.results["summary"]["tabs_failed"]}
- **Total APIs Tested:** {self.results["summary"]["total_apis"]}
- **APIs Passed:** {self.results["summary"]["apis_passed"]}
- **APIs Failed:** {self.results["summary"]["apis_failed"]}
- **Overall Status:** {self.results["summary"]["overall"]}

## Tab Results

"""
        
        for tab_name, tab_result in self.results["tabs"].items():
            status_icon = "[PASS]" if tab_result["status"] == "PASS" else "[FAIL]"
            md_content += f"### {status_icon} {tab_name}\n\n"
            md_content += f"- **Status:** {tab_result['status']}\n"
            md_content += f"- **Endpoints Passed:** {tab_result['passed']}\n"
            md_content += f"- **Endpoints Failed:** {tab_result['failed']}\n\n"
            
            md_content += "**Endpoints:**\n\n"
            for ep in tab_result["endpoints"]:
                ep_icon = "[OK]" if ep["success"] else "[FAIL]"
                md_content += f"- {ep_icon} `{ep['method']} {ep['endpoint']}` - {ep['description']}\n"
                if not ep["success"]:
                    md_content += f"  - Error: {ep.get('response_preview', 'Unknown error')}\n"
            md_content += "\n"
        
        if self.errors:
            md_content += "## Errors\n\n"
            for error in self.errors:
                md_content += f"- {error}\n"
            md_content += "\n"
        
        md_content += f"""
## Detailed Results

See JSON report: `{json_file.name}`

---
**Test completed at:** {datetime.now().isoformat()}
"""
        
        with open(md_file, "w") as f:
            f.write(md_content)
        
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}Test Report Generated{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
        print(f"JSON: {json_file}")
        print(f"Markdown: {md_file}\n")
        
        return json_file, md_file

    def print_summary(self):
        """Print test summary"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}FINAL SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
        
        summary = self.results["summary"]
        
        print(f"Total Tabs: {summary['total_tabs']}")
        print(f"  {Colors.GREEN}Passed: {summary['tabs_passed']}{Colors.RESET}")
        print(f"  {Colors.RED}Failed: {summary['tabs_failed']}{Colors.RESET}")
        print()
        print(f"Total APIs: {summary['total_apis']}")
        print(f"  {Colors.GREEN}Passed: {summary['apis_passed']}{Colors.RESET}")
        print(f"  {Colors.RED}Failed: {summary['apis_failed']}{Colors.RESET}")
        print()
        
        if summary['total_apis'] > 0:
            success_rate = (summary['apis_passed'] / summary['total_apis']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        overall = summary['overall']
        if overall == "PASS":
            print(f"\n{Colors.GREEN}{Colors.BOLD}Overall: {overall} [PASS]{Colors.RESET}")
        elif overall == "WARN":
            print(f"\n{Colors.YELLOW}{Colors.BOLD}Overall: {overall} [WARN]{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}Overall: {overall} [FAIL]{Colors.RESET}")
        
        if self.errors:
            print(f"\n{Colors.RED}Errors Found: {len(self.errors)}{Colors.RESET}")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more errors")

def main():
    """Main test execution"""
    tester = TabTester()
    
    try:
        success = tester.test_all_tabs()
        if success:
            tester.generate_report()
            tester.print_summary()
            
            # Exit with appropriate code
            if tester.results["summary"]["overall"] == "PASS":
                sys.exit(0)
            elif tester.results["summary"]["overall"] == "WARN":
                sys.exit(1)
            else:
                sys.exit(2)
        else:
            print(f"{Colors.RED}Test execution failed!{Colors.RESET}")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Test failed with error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
