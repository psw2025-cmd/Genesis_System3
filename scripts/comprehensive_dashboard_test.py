"""
Comprehensive Dashboard Test - Multi-User Simulation
Tests all dashboard tabs and simulates multiple traders/users
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List

import requests

API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"


class DashboardTester:
    def __init__(self):
        self.issues = []
        self.results = {"api_tests": {}, "frontend_tests": {}, "multi_user_tests": {}, "issues": []}

    def log_issue(self, component: str, issue: str, severity: str = "MEDIUM"):
        """Log an issue"""
        issue_data = {
            "component": component,
            "issue": issue,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
        }
        self.issues.append(issue_data)
        self.results["issues"].append(issue_data)
        print(f"  [ISSUE-{severity}] {component}: {issue}")

    def test_api_endpoint(self, endpoint: str, expected_fields: List[str] = None) -> Dict[str, Any]:
        """Test an API endpoint"""
        try:
            url = f"{API_BASE}{endpoint}"
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                self.log_issue(f"API:{endpoint}", f"Status code {response.status_code}", "HIGH")
                return {"status": "FAIL", "error": f"Status {response.status_code}"}

            data = response.json()

            # Check expected fields
            if expected_fields:
                missing = [f for f in expected_fields if f not in data]
                if missing:
                    self.log_issue(f"API:{endpoint}", f"Missing fields: {missing}", "MEDIUM")

            return {"status": "PASS", "data": data}
        except Exception as e:
            self.log_issue(f"API:{endpoint}", str(e), "HIGH")
            return {"status": "FAIL", "error": str(e)}

    def test_frontend_page(self, route: str) -> Dict[str, Any]:
        """Test a frontend page"""
        try:
            url = f"{FRONTEND_BASE}{route}"
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                self.log_issue(f"Frontend:{route}", f"Status code {response.status_code}", "HIGH")
                return {"status": "FAIL", "error": f"Status {response.status_code}"}

            # Check if page contains expected content
            content = response.text
            if len(content) < 100:
                self.log_issue(f"Frontend:{route}", "Page content too short", "MEDIUM")

            return {"status": "PASS", "content_length": len(content)}
        except Exception as e:
            self.log_issue(f"Frontend:{route}", str(e), "HIGH")
            return {"status": "FAIL", "error": str(e)}

    def simulate_user_session(self, user_id: int) -> Dict[str, Any]:
        """Simulate a user session accessing all pages"""
        session_results = {
            "user_id": user_id,
            "start_time": datetime.now().isoformat(),
            "pages_accessed": [],
            "errors": [],
        }

        pages = ["/", "/chain", "/signals", "/trading", "/model", "/control"]

        for page in pages:
            try:
                result = self.test_frontend_page(page)
                session_results["pages_accessed"].append({"page": page, "status": result["status"]})
                if result["status"] == "FAIL":
                    session_results["errors"].append(f"{page}: {result.get('error', 'Unknown')}")
                time.sleep(0.5)  # Simulate user reading time
            except Exception as e:
                session_results["errors"].append(f"{page}: {str(e)}")

        # Test API endpoints
        endpoints = ["/api/health", "/api/chain/NIFTY", "/api/signal/top", "/api/positions", "/api/pnl"]

        for endpoint in endpoints:
            try:
                result = self.test_api_endpoint(endpoint)
                if result["status"] == "FAIL":
                    session_results["errors"].append(f"{endpoint}: {result.get('error', 'Unknown')}")
                time.sleep(0.2)
            except Exception as e:
                session_results["errors"].append(f"{endpoint}: {str(e)}")

        session_results["end_time"] = datetime.now().isoformat()
        return session_results

    def test_all_api_endpoints(self):
        """Test all API endpoints"""
        print("\n[TEST 1] Testing All API Endpoints...")

        endpoints = {
            "/api/health": ["status", "market_status", "data_source"],
            "/api/qc": ["status"],
            "/api/signal/top": ["action"],
            "/api/positions": ["positions"],
            "/api/pnl": ["summary"],
            "/api/perf": ["current"],
            "/api/chain/NIFTY": ["underlying", "contracts", "spot"],
            "/api/chain/BANKNIFTY": ["underlying", "contracts", "spot"],
            "/api/chain/FINNIFTY": ["underlying", "contracts", "spot"],
            "/api/chain/MIDCPNIFTY": ["underlying", "contracts", "spot"],
            "/api/chain/SENSEX": ["underlying", "contracts", "spot"],
        }

        for endpoint, expected_fields in endpoints.items():
            result = self.test_api_endpoint(endpoint, expected_fields)
            self.results["api_tests"][endpoint] = result
            if result["status"] == "PASS":
                print(f"  [PASS] {endpoint}")
            else:
                print(f"  [FAIL] {endpoint}: {result.get('error', 'Unknown')}")

    def test_all_frontend_pages(self):
        """Test all frontend pages"""
        print("\n[TEST 2] Testing All Frontend Pages...")

        pages = {
            "/": "Overview",
            "/chain": "Chain Analytics",
            "/signals": "Signals",
            "/trading": "Paper Trading",
            "/model": "Model Behavior",
            "/control": "Control Plane",
        }

        for route, name in pages.items():
            result = self.test_frontend_page(route)
            self.results["frontend_tests"][route] = result
            if result["status"] == "PASS":
                print(f"  [PASS] {name} ({route})")
            else:
                print(f"  [FAIL] {name} ({route}): {result.get('error', 'Unknown')}")

    def test_multi_user_access(self, num_users: int = 5):
        """Simulate multiple users accessing dashboard concurrently"""
        print(f"\n[TEST 3] Simulating {num_users} Concurrent Users...")

        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(self.simulate_user_session, i + 1) for i in range(num_users)]

            user_results = []
            for future in as_completed(futures):
                result = future.result()
                user_results.append(result)

                if result["errors"]:
                    print(f"  [WARN] User {result['user_id']}: {len(result['errors'])} errors")
                    for error in result["errors"]:
                        print(f"     - {error}")
                else:
                    print(f"  [PASS] User {result['user_id']}: All pages accessed successfully")

        self.results["multi_user_tests"] = {
            "num_users": num_users,
            "sessions": user_results,
            "total_errors": sum(len(r["errors"]) for r in user_results),
        }

    def test_data_consistency(self):
        """Test data consistency across multiple requests"""
        print("\n[TEST 4] Testing Data Consistency...")

        # Test same endpoint multiple times
        results = []
        for i in range(5):
            result = self.test_api_endpoint("/api/health")
            if result["status"] == "PASS":
                results.append(result["data"])
            time.sleep(0.5)

        if len(results) < 3:
            self.log_issue("Data Consistency", "Failed to get consistent responses", "HIGH")
            return

        # Check if data_source is consistent
        data_sources = [r.get("data_source") for r in results if "data_source" in r]
        if len(set(data_sources)) > 1:
            self.log_issue("Data Consistency", "Data source switching unexpectedly", "MEDIUM")
        else:
            print(f"  [PASS] Data source consistent: {data_sources[0] if data_sources else 'N/A'}")

        # Check if market_status is consistent
        market_statuses = [r.get("market_status") for r in results if "market_status" in r]
        if len(set(market_statuses)) > 1:
            self.log_issue("Data Consistency", "Market status inconsistent", "MEDIUM")
        else:
            print(f"  [PASS] Market status consistent: {market_statuses[0] if market_statuses else 'N/A'}")

    def test_chain_data_quality(self):
        """Test quality of chain data"""
        print("\n[TEST 5] Testing Chain Data Quality...")

        underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY"]

        for underlying in underlyings:
            result = self.test_api_endpoint(f"/api/chain/{underlying}")

            if result["status"] == "PASS":
                data = result["data"]

                # Check required fields
                required = ["underlying", "spot", "pcr", "contracts", "total_contracts"]
                missing = [f for f in required if f not in data]
                if missing:
                    self.log_issue(f"Chain:{underlying}", f"Missing fields: {missing}", "HIGH")
                    continue

                # Check data quality
                if data["total_contracts"] == 0:
                    self.log_issue(f"Chain:{underlying}", "No contracts returned", "MEDIUM")

                if data["spot"] <= 0:
                    self.log_issue(f"Chain:{underlying}", f"Invalid spot price: {data['spot']}", "HIGH")

                if len(data["contracts"]) == 0 and data["total_contracts"] > 0:
                    self.log_issue(f"Chain:{underlying}", "Contracts array empty but total_contracts > 0", "MEDIUM")

                # Check contract structure
                if len(data["contracts"]) > 0:
                    contract = data["contracts"][0]
                    required_contract_fields = ["strike", "option_type", "ltp"]
                    missing_fields = [f for f in required_contract_fields if f not in contract]
                    if missing_fields:
                        self.log_issue(f"Chain:{underlying}", f"Contract missing fields: {missing_fields}", "MEDIUM")

                print(f"  [PASS] {underlying}: {data['total_contracts']} contracts, Spot: {data['spot']:.2f}")
            else:
                print(f"  [FAIL] {underlying}: {result.get('error', 'Unknown')}")

    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("COMPREHENSIVE DASHBOARD TEST - MULTI-USER SIMULATION")
        print("=" * 60)

        self.test_all_api_endpoints()
        self.test_all_frontend_pages()
        self.test_multi_user_access(num_users=5)
        self.test_data_consistency()
        self.test_chain_data_quality()

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        total_issues = len(self.issues)
        high_issues = len([i for i in self.issues if i["severity"] == "HIGH"])
        medium_issues = len([i for i in self.issues if i["severity"] == "MEDIUM"])

        print(f"\nTotal Issues Found: {total_issues}")
        print(f"  - HIGH Severity: {high_issues}")
        print(f"  - MEDIUM Severity: {medium_issues}")

        if total_issues == 0:
            print("\n[SUCCESS] ALL TESTS PASSED - DASHBOARD IS PRODUCTION READY!")
        else:
            print("\n[ISSUES] ISSUES FOUND - REVIEW BELOW:")
            for issue in self.issues:
                print(f"\n  [{issue['severity']}] {issue['component']}")
                print(f"    {issue['issue']}")

        # Save results
        results_file = "outputs/audit/dashboard_comprehensive_test.json"
        import os

        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\n[INFO] Full results saved to: {results_file}")

        return total_issues == 0


if __name__ == "__main__":
    tester = DashboardTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
