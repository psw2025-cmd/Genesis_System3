"""
E2E Self-Test for System3 Ultra
Validates all critical systems and outputs PASS/FAIL report
"""
import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

ROOT_DIR = Path(__file__).parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
REPORTS_DIR = ROOT_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_status(message: str, status: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status == "OK":
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {timestamp} - {message}")
    elif status == "ERROR":
        print(f"{Colors.RED}[ERROR]{Colors.RESET} {timestamp} - {message}")
    elif status == "WARN":
        print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {timestamp} - {message}")
    else:
        print(f"{Colors.BLUE}[INFO]{Colors.RESET} {timestamp} - {message}")

def test_api_health() -> Dict[str, Any]:
    """Test API health endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            return {"status": "PASS", "data": response.json()}
        return {"status": "FAIL", "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_broker_login() -> Dict[str, Any]:
    """Test broker login (if credentials available)"""
    try:
        # First check if credentials are available
        import os
        from dotenv import load_dotenv
        from pathlib import Path
        
        env_path = Path(__file__).parent / "config" / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        else:
            root_env = Path(__file__).parent / ".env"
            if root_env.exists():
                load_dotenv(root_env)
        
        has_creds = all([
            os.getenv("ANGELONE_API_KEY"),
            os.getenv("ANGELONE_CLIENT_ID"),
            os.getenv("ANGELONE_TOTP"),
            os.getenv("ANGELONE_PIN") or os.getenv("ANGELONE_PASSWORD")
        ])
        
        if not has_creds:
            return {"status": "WARN", "message": "Broker credentials not found in environment"}
        
        # Test actual broker connection
        try:
            from core.brokers.angel_one.broker import AngelOneBroker
            broker = AngelOneBroker(allow_data_only=True)
            profile = broker.get_profile()
            
            if profile and profile.get("status"):
                return {
                    "status": "PASS",
                    "data": {
                        "connected": True,
                        "client_code": profile.get("data", {}).get("clientcode", "N/A")
                    }
                }
            else:
                return {"status": "FAIL", "error": "Profile fetch failed"}
        except Exception as e:
            return {"status": "FAIL", "error": str(e)[:200]}
        
        # Fallback to API endpoint check
        response = requests.get("http://localhost:8000/api/broker/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("connected"):
                return {"status": "PASS", "data": data}
            return {"status": "WARN", "message": f"Broker disconnected: {data.get('error', 'Unknown')}"}
        return {"status": "FAIL", "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_state_consistency() -> Dict[str, Any]:
    """Test state consistency (SSOT)"""
    try:
        response = requests.get("http://localhost:8000/api/state", timeout=5)
        if response.status_code == 200:
            state = response.json()
            
            # Check required fields
            required = ["state_version", "data_source", "broker", "positions", "qc"]
            missing = [f for f in required if f not in state]
            
            if missing:
                return {"status": "FAIL", "error": f"Missing fields: {missing}"}
            
            # Check state_version is present and numeric
            if not isinstance(state.get("state_version"), int):
                return {"status": "FAIL", "error": "state_version must be integer"}
            
            return {"status": "PASS", "data": {
                "state_version": state.get("state_version"),
                "data_source": state.get("data_source"),
                "positions_count": len(state.get("positions", [])),
                "qc_status": state.get("qc", {}).get("status")
            }}
        return {"status": "FAIL", "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_qc_consistency() -> Dict[str, Any]:
    """Test QC consistency across endpoints"""
    try:
        state_res = requests.get("http://localhost:8000/api/state", timeout=5)
        qc_res = requests.get("http://localhost:8000/api/qc", timeout=5)
        
        if state_res.status_code != 200 or qc_res.status_code != 200:
            return {"status": "FAIL", "error": "Endpoints not accessible"}
        
        state_qc = state_res.json().get("qc", {})
        qc_data = qc_res.json()
        
        # Compare QC status
        state_status = state_qc.get("status")
        qc_status = qc_data.get("status")
        
        if state_status != qc_status:
            return {"status": "FAIL", "error": f"QC mismatch: state={state_status}, qc={qc_status}"}
        
        return {"status": "PASS", "data": {"qc_status": state_status}}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_position_reconciliation() -> Dict[str, Any]:
    """Test position reconciliation"""
    try:
        response = requests.get("http://localhost:8000/api/state", timeout=5)
        if response.status_code == 200:
            state = response.json()
            positions = state.get("positions", [])
            positions_source = state.get("positions_source", "UNKNOWN")
            reconciliation = state.get("reconciliation", {})
            
            mismatches = reconciliation.get("mismatches", [])
            if mismatches:
                return {"status": "FAIL", "error": f"Position mismatches found: {len(mismatches)}", "data": mismatches}
            
            return {"status": "PASS", "data": {
                "positions_count": len(positions),
                "positions_source": positions_source,
                "reconciliation_status": reconciliation.get("status", "OK")
            }}
        return {"status": "FAIL", "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_alert_timestamps() -> Dict[str, Any]:
    """Test alert timestamps are valid"""
    try:
        response = requests.get("http://localhost:8000/api/alerts", timeout=5)
        if response.status_code == 200:
            data = response.json()
            alerts = data.get("alerts", [])
            
            invalid = []
            for alert in alerts:
                ts_iso = alert.get("ts_iso")
                if not ts_iso:
                    invalid.append({"alert": alert.get("message", "unknown"), "issue": "Missing ts_iso"})
                else:
                    try:
                        datetime.fromisoformat(ts_iso.replace('Z', '+00:00'))
                    except:
                        invalid.append({"alert": alert.get("message", "unknown"), "issue": f"Invalid ts_iso: {ts_iso}"})
            
            if invalid:
                return {"status": "FAIL", "error": f"Invalid timestamps: {len(invalid)}", "data": invalid}
            
            return {"status": "PASS", "data": {"alerts_count": len(alerts)}}
        return {"status": "FAIL", "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_greeks_availability() -> Dict[str, Any]:
    """Test Greeks are calculated or flagged as unavailable"""
    try:
        response = requests.get("http://localhost:8000/api/state", timeout=5)
        if response.status_code == 200:
            state = response.json()
            risk = state.get("risk", {})
            greeks = risk.get("greeks", {})
            
            # Check if greeks are all zero (bad) or None/unavailable (acceptable)
            delta = greeks.get("delta", 0)
            gamma = greeks.get("gamma", 0)
            theta = greeks.get("theta", 0)
            vega = greeks.get("vega", 0)
            
            # If all are exactly 0, that's suspicious (should be None or calculated)
            if delta == 0 and gamma == 0 and theta == 0 and vega == 0:
                positions = state.get("positions", [])
                if positions:
                    # If there are positions but greeks are 0, that's a problem
                    return {"status": "WARN", "message": "Greeks are zero but positions exist", "data": greeks}
            
            return {"status": "PASS", "data": greeks}
        return {"status": "FAIL", "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def main():
    """Run E2E self-test"""
    print_status("=" * 80, "INFO")
    print_status("E2E SELF-TEST - System3 Ultra", "INFO")
    print_status("=" * 80, "INFO")
    
    results = {}
    
    # Test 1: API Health
    print_status("\n[1/7] Testing API Health...", "INFO")
    results["api_health"] = test_api_health()
    if results["api_health"]["status"] == "PASS":
        print_status("API Health: PASS", "OK")
    else:
        print_status(f"API Health: FAIL - {results['api_health'].get('error')}", "ERROR")
    
    # Test 2: Broker Login
    print_status("\n[2/7] Testing Broker Login...", "INFO")
    results["broker_login"] = test_broker_login()
    if results["broker_login"]["status"] == "PASS":
        print_status("Broker Login: PASS", "OK")
    elif results["broker_login"]["status"] == "WARN":
        print_status(f"Broker Login: WARN - {results['broker_login'].get('message')}", "WARN")
    else:
        print_status(f"Broker Login: FAIL - {results['broker_login'].get('error')}", "ERROR")
    
    # Test 3: State Consistency
    print_status("\n[3/7] Testing State Consistency (SSOT)...", "INFO")
    results["state_consistency"] = test_state_consistency()
    if results["state_consistency"]["status"] == "PASS":
        print_status("State Consistency: PASS", "OK")
    else:
        print_status(f"State Consistency: FAIL - {results['state_consistency'].get('error')}", "ERROR")
    
    # Test 4: QC Consistency
    print_status("\n[4/7] Testing QC Consistency...", "INFO")
    results["qc_consistency"] = test_qc_consistency()
    if results["qc_consistency"]["status"] == "PASS":
        print_status("QC Consistency: PASS", "OK")
    else:
        print_status(f"QC Consistency: FAIL - {results['qc_consistency'].get('error')}", "ERROR")
    
    # Test 5: Position Reconciliation
    print_status("\n[5/7] Testing Position Reconciliation...", "INFO")
    results["position_reconciliation"] = test_position_reconciliation()
    if results["position_reconciliation"]["status"] == "PASS":
        print_status("Position Reconciliation: PASS", "OK")
    else:
        print_status(f"Position Reconciliation: FAIL - {results['position_reconciliation'].get('error')}", "ERROR")
    
    # Test 6: Alert Timestamps
    print_status("\n[6/7] Testing Alert Timestamps...", "INFO")
    results["alert_timestamps"] = test_alert_timestamps()
    if results["alert_timestamps"]["status"] == "PASS":
        print_status("Alert Timestamps: PASS", "OK")
    else:
        print_status(f"Alert Timestamps: FAIL - {results['alert_timestamps'].get('error')}", "ERROR")
    
    # Test 7: Greeks Availability
    print_status("\n[7/7] Testing Greeks Availability...", "INFO")
    results["greeks_availability"] = test_greeks_availability()
    if results["greeks_availability"]["status"] == "PASS":
        print_status("Greeks Availability: PASS", "OK")
    elif results["greeks_availability"]["status"] == "WARN":
        print_status(f"Greeks Availability: WARN - {results['greeks_availability'].get('message')}", "WARN")
    else:
        print_status(f"Greeks Availability: FAIL - {results['greeks_availability'].get('error')}", "ERROR")
    
    # Summary
    print_status("\n" + "=" * 80, "INFO")
    print_status("E2E SELF-TEST SUMMARY", "INFO")
    print_status("=" * 80, "INFO")
    
    passed = sum(1 for r in results.values() if r["status"] == "PASS")
    failed = sum(1 for r in results.values() if r["status"] == "FAIL")
    warned = sum(1 for r in results.values() if r["status"] == "WARN")
    total = len(results)
    
    print_status(f"Total Tests: {total}", "INFO")
    print_status(f"Passed: {passed}", "OK" if passed == total else "INFO")
    if warned > 0:
        print_status(f"Warnings: {warned}", "WARN")
    if failed > 0:
        print_status(f"Failed: {failed}", "ERROR")
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORTS_DIR / f"e2e_selftest_{timestamp}.json"
    md_file = REPORTS_DIR / f"e2e_selftest_{timestamp}.md"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "warned": warned,
            "overall": "PASS" if failed == 0 else "FAIL"
        },
        "results": results
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate markdown report
    md_content = f"""# E2E Self-Test Report

Generated: {datetime.now().isoformat()}

## Summary

- **Total Tests**: {total}
- **Passed**: {passed}
- **Failed**: {failed}
- **Warnings**: {warned}
- **Overall**: {"PASS" if failed == 0 else "FAIL"}

## Detailed Results

"""
    
    for test_name, result in results.items():
        status_icon = "[OK]" if result["status"] == "PASS" else "[FAIL]" if result["status"] == "FAIL" else "[WARN]"
        md_content += f"### {status_icon} {test_name.replace('_', ' ').title()}\n\n"
        md_content += f"- Status: {result['status']}\n"
        if "error" in result:
            md_content += f"- Error: {result['error']}\n"
        if "message" in result:
            md_content += f"- Message: {result['message']}\n"
        if "data" in result:
            md_content += f"- Data: {json.dumps(result['data'], indent=2)}\n"
        md_content += "\n"
    
    with open(md_file, 'w') as f:
        f.write(md_content)
    
    print_status(f"\nReport saved to: {report_file}", "INFO")
    print_status(f"Markdown report: {md_file}", "INFO")
    
    if failed == 0:
        print_status("\nALL TESTS PASSED", "OK")
        return 0
    else:
        print_status(f"\n{failed} TEST(S) FAILED", "ERROR")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nTest interrupted", "WARN")
        sys.exit(1)
    except Exception as e:
        print_status(f"\nFATAL ERROR: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
