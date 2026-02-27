"""
Comprehensive App Verification and Fix Script
Tests all tabs, features, and fixes issues found
"""
import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Color codes for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_status(message: str, status: str = "INFO"):
    """Print colored status message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status == "OK":
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {timestamp} - {message}")
    elif status == "ERROR":
        print(f"{Colors.RED}[ERROR]{Colors.RESET} {timestamp} - {message}")
    elif status == "WARN":
        print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {timestamp} - {message}")
    elif status == "INFO":
        print(f"{Colors.BLUE}[INFO]{Colors.RESET} {timestamp} - {message}")
    else:
        print(f"{timestamp} - {message}")

def check_backend_running() -> bool:
    """Check if backend is running on port 8000"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_backend() -> bool:
    """Start the backend server"""
    print_status("Starting backend server...", "INFO")
    backend_dir = ROOT_DIR / "dashboard" / "backend"
    
    # Kill any existing backend
    try:
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                      capture_output=True, timeout=5)
        time.sleep(2)
    except:
        pass
    
    # Start backend
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to start
        for i in range(30):
            if check_backend_running():
                print_status("Backend started successfully", "OK")
                return True
            time.sleep(1)
        
        print_status("Backend failed to start within 30 seconds", "ERROR")
        return False
    except Exception as e:
        print_status(f"Failed to start backend: {e}", "ERROR")
        return False

def test_endpoint(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """Test an API endpoint"""
    url = f"http://localhost:8000{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}
        
        return {
            "status": "ok" if response.status_code == 200 else "error",
            "status_code": response.status_code,
            "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            "message": f"Status {response.status_code}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "status_code": None
        }

def verify_all_tabs() -> Dict[str, Any]:
    """Verify all dashboard tabs work correctly"""
    print_status("=" * 80, "INFO")
    print_status("VERIFYING ALL DASHBOARD TABS", "INFO")
    print_status("=" * 80, "INFO")
    
    results = {
        "overview": None,
        "chain": None,
        "signals": None,
        "trading": None,
        "alerts": None,
        "risk": None,
        "ml": None,
        "model": None,
        "control": None,
        "agent": None
    }
    
    # Test Overview tab endpoints
    print_status("Testing Overview tab...", "INFO")
    state_result = test_endpoint("/api/state")
    perf_result = test_endpoint("/api/perf")
    results["overview"] = {
        "state": state_result,
        "perf": perf_result,
        "status": "ok" if state_result["status"] == "ok" and perf_result["status"] == "ok" else "error"
    }
    if results["overview"]["status"] == "ok":
        print_status("Overview tab: OK", "OK")
    else:
        print_status(f"Overview tab: ERROR - {state_result.get('message')} / {perf_result.get('message')}", "ERROR")
    
    # Test Chain tab endpoints
    print_status("Testing Chain tab...", "INFO")
    chain_result = test_endpoint("/api/chain/NIFTY")
    results["chain"] = {
        "chain": chain_result,
        "status": "ok" if chain_result["status"] == "ok" else "error"
    }
    if results["chain"]["status"] == "ok":
        print_status("Chain tab: OK", "OK")
    else:
        print_status(f"Chain tab: ERROR - {chain_result.get('message')}", "ERROR")
    
    # Test Signals tab endpoints
    print_status("Testing Signals tab...", "INFO")
    signals_result = test_endpoint("/api/signals")
    results["signals"] = {
        "signals": signals_result,
        "status": "ok" if signals_result["status"] == "ok" else "error"
    }
    if results["signals"]["status"] == "ok":
        print_status("Signals tab: OK", "OK")
    else:
        print_status(f"Signals tab: ERROR - {signals_result.get('message')}", "ERROR")
    
    # Test Trading tab endpoints
    print_status("Testing Trading tab...", "INFO")
    positions_result = test_endpoint("/api/positions")
    pnl_result = test_endpoint("/api/pnl")
    results["trading"] = {
        "positions": positions_result,
        "pnl": pnl_result,
        "status": "ok" if positions_result["status"] == "ok" and pnl_result["status"] == "ok" else "error"
    }
    if results["trading"]["status"] == "ok":
        print_status("Trading tab: OK", "OK")
    else:
        print_status(f"Trading tab: ERROR - {positions_result.get('message')} / {pnl_result.get('message')}", "ERROR")
    
    # Test Alerts tab endpoints
    print_status("Testing Alerts tab...", "INFO")
    alerts_result = test_endpoint("/api/alerts")
    results["alerts"] = {
        "alerts": alerts_result,
        "status": "ok" if alerts_result["status"] == "ok" else "error"
    }
    if results["alerts"]["status"] == "ok":
        print_status("Alerts tab: OK", "OK")
    else:
        print_status(f"Alerts tab: ERROR - {alerts_result.get('message')}", "ERROR")
    
    # Test Risk tab endpoints
    print_status("Testing Risk tab...", "INFO")
    risk_result = test_endpoint("/api/risk")
    # Risk endpoint may return ERROR status but still be functional
    if risk_result.get("status_code") == 200:
        results["risk"] = {
            "risk": risk_result,
            "status": "ok"
        }
        print_status("Risk tab: OK", "OK")
    else:
        # Try portfolio endpoint as fallback
        risk_portfolio = test_endpoint("/api/risk/portfolio")
        results["risk"] = {
            "risk": risk_result,
            "risk_portfolio": risk_portfolio,
            "status": "ok" if risk_portfolio.get("status_code") == 200 else "error"
        }
        if results["risk"]["status"] == "ok":
            print_status("Risk tab: OK (via portfolio endpoint)", "OK")
        else:
            print_status(f"Risk tab: ERROR - {risk_result.get('message')}", "ERROR")
    
    # Test ML tab endpoints
    print_status("Testing ML tab...", "INFO")
    ml_result = test_endpoint("/api/ml/performance")
    results["ml"] = {
        "ml": ml_result,
        "status": "ok" if ml_result["status"] == "ok" else "error"
    }
    if results["ml"]["status"] == "ok":
        print_status("ML tab: OK", "OK")
    else:
        print_status(f"ML tab: ERROR - {ml_result.get('message')}", "ERROR")
    
    # Test Model tab endpoints
    print_status("Testing Model tab...", "INFO")
    model_result = test_endpoint("/api/model/behavior")
    results["model"] = {
        "model": model_result,
        "status": "ok" if model_result["status"] == "ok" else "error"
    }
    if results["model"]["status"] == "ok":
        print_status("Model tab: OK", "OK")
    else:
        print_status(f"Model tab: ERROR - {model_result.get('message')}", "ERROR")
    
    # Test Control Plane tab endpoints
    print_status("Testing Control Plane tab...", "INFO")
    learning_status = test_endpoint("/api/learning/status")
    forensic_report = test_endpoint("/api/forensic/report")
    validation_status = test_endpoint("/api/validation/status")
    results["control"] = {
        "learning": learning_status,
        "forensic": forensic_report,
        "validation": validation_status,
        "status": "ok" if all(r["status"] == "ok" for r in [learning_status, forensic_report, validation_status]) else "error"
    }
    if results["control"]["status"] == "ok":
        print_status("Control Plane tab: OK", "OK")
    else:
        print_status(f"Control Plane tab: ERROR", "ERROR")
    
    # Test Agent tab endpoints
    print_status("Testing Agent tab...", "INFO")
    agent_result = test_endpoint("/api/agent/status")
    results["agent"] = {
        "agent": agent_result,
        "status": "ok" if agent_result["status"] == "ok" else "error"
    }
    if results["agent"]["status"] == "ok":
        print_status("Agent tab: OK", "OK")
    else:
        print_status(f"Agent tab: ERROR - {agent_result.get('message')}", "ERROR")
    
    return results

def check_broker_connectivity() -> Dict[str, Any]:
    """Check broker connectivity and credentials"""
    print_status("Checking broker connectivity...", "INFO")
    
    result = {
        "available": False,
        "connected": False,
        "credentials_present": False,
        "error": None,
        "details": {}
    }
    
    # Check if SmartApi is available
    try:
        from SmartApi.smartConnect import SmartConnect
        result["available"] = True
        result["details"]["smartapi"] = "INSTALLED"
    except ImportError:
        result["details"]["smartapi"] = "NOT_INSTALLED"
        result["error"] = "SmartApi not installed"
        return result
    
    # Check credentials
    required_env_vars = [
        "ANGELONE_API_KEY",
        "ANGELONE_CLIENT_ID",
        "ANGELONE_PIN",
        "ANGELONE_TOTP"
    ]
    
    missing_creds = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_creds.append(var)
    
    if missing_creds:
        result["error"] = f"Missing credentials: {', '.join(missing_creds)}"
        result["details"]["missing_credentials"] = missing_creds
        return result
    
    result["credentials_present"] = True
    
    # Try to initialize broker
    try:
        from core.brokers.angel_one.broker import AngelOneBroker
        broker = AngelOneBroker(allow_data_only=True)
        result["connected"] = True
        result["details"]["broker_init"] = "SUCCESS"
        print_status("Broker connection: SUCCESS", "OK")
    except Exception as e:
        result["error"] = str(e)
        result["details"]["broker_init"] = f"FAILED: {str(e)[:200]}"
        print_status(f"Broker connection: FAILED - {str(e)[:200]}", "ERROR")
    
    return result

def fix_broker_status_in_backend():
    """Update backend to check and report broker status correctly"""
    print_status("Fixing broker status in backend...", "INFO")
    
    backend_app = ROOT_DIR / "dashboard" / "backend" / "app.py"
    if not backend_app.exists():
        print_status("Backend app.py not found", "ERROR")
        return False
    
    # Read current app.py
    with open(backend_app, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if broker connectivity check exists
    if "check_broker_connectivity" in content or "broker.*connected" in content:
        print_status("Broker connectivity check already exists", "OK")
        return True
    
    # Add broker connectivity endpoint
    broker_endpoint = '''
@app.get("/api/broker/status")
async def get_broker_status():
    """Get broker connection status"""
    try:
        from core.brokers.angel_one.broker import AngelOneBroker
        broker = AngelOneBroker(allow_data_only=True)
        return {
            "connected": True,
            "name": "AngelOne",
            "status": "connected",
            "latency_ms": None,
            "last_ok": datetime.now().isoformat()
        }
    except ImportError:
        return {
            "connected": False,
            "name": "AngelOne",
            "status": "not_available",
            "error": "SmartApi not installed",
            "latency_ms": None,
            "last_ok": None
        }
    except Exception as e:
        return {
            "connected": False,
            "name": "AngelOne",
            "status": "disconnected",
            "error": str(e)[:200],
            "latency_ms": None,
            "last_ok": None
        }
'''
    
    # Find where to insert (after other endpoints)
    if "@app.get" in content and "/api/health" in content:
        # Insert after health endpoint
        insert_pos = content.find("@app.get(\"/api/health\")")
        if insert_pos > 0:
            # Find end of health endpoint function
            next_def = content.find("\n@app.", insert_pos + 100)
            if next_def > 0:
                content = content[:next_def] + broker_endpoint + "\n" + content[next_def:]
                with open(backend_app, 'w', encoding='utf-8') as f:
                    f.write(content)
                print_status("Added broker status endpoint", "OK")
                return True
    
    print_status("Could not auto-add broker endpoint - manual fix may be needed", "WARN")
    return False

def update_runtime_state_broker_check():
    """Update runtime state store to check broker connectivity"""
    print_status("Updating runtime state store for broker check...", "INFO")
    
    state_store = ROOT_DIR / "dashboard" / "backend" / "runtime_state_store.py"
    if not state_store.exists():
        print_status("Runtime state store not found", "ERROR")
        return False
    
    with open(state_store, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if broker check method exists
    if "def _check_broker_connectivity" in content:
        print_status("Broker connectivity check already exists in state store", "OK")
        return True
    
    # Add broker connectivity check method
    broker_check_method = '''
    def _check_broker_connectivity(self) -> Dict[str, Any]:
        """Check broker connectivity and return status"""
        try:
            from core.brokers.angel_one.broker import AngelOneBroker
            broker = AngelOneBroker(allow_data_only=True)
            return {
                "connected": True,
                "name": "AngelOne",
                "status": "connected",
                "latency_ms": None,
                "last_ok": datetime.now().isoformat()
            }
        except ImportError:
            return {
                "connected": False,
                "name": "AngelOne",
                "status": "not_available",
                "error": "SmartApi not installed",
                "latency_ms": None,
                "last_ok": None
            }
        except Exception as e:
            return {
                "connected": False,
                "name": "AngelOne",
                "status": "disconnected",
                "error": str(e)[:200],
                "latency_ms": None,
                "last_ok": None
            }
'''
    
    # Find where to insert (in the class, after _initialize_state)
    if "def _initialize_state" in content:
        insert_pos = content.find("def _initialize_state")
        if insert_pos > 0:
            # Find end of _initialize_state method
            next_def = content.find("\n    def ", insert_pos + 200)
            if next_def > 0:
                content = content[:next_def] + broker_check_method + "\n" + content[next_def:]
                
                # Also update the state update to call this method
                if "def update_state" in content:
                    # Find update_state method and add broker check call
                    update_pos = content.find("def update_state")
                    if update_pos > 0:
                        # Look for where broker status is set
                        broker_update = 'self._state["broker"] = self._check_broker_connectivity()'
                        if broker_update not in content:
                            # Find where broker is updated and replace
                            pattern = 'self._state\["broker"\]\["connected"\]'
                            if pattern in content:
                                # Replace the broker update section
                                import re
                                broker_section = re.search(r'self\._state\["broker"\].*?=.*?\n', content[update_pos:update_pos+2000], re.DOTALL)
                                if broker_section:
                                    old_section = broker_section.group(0)
                                    new_section = f'        self._state["broker"] = self._check_broker_connectivity()\n'
                                    content = content.replace(old_section, new_section, 1)
                
                with open(state_store, 'w', encoding='utf-8') as f:
                    f.write(content)
                print_status("Updated runtime state store with broker check", "OK")
                return True
    
    print_status("Could not auto-update state store - manual fix may be needed", "WARN")
    return False

def main():
    """Main verification and fix function"""
    print_status("=" * 80, "INFO")
    print_status("COMPREHENSIVE APP VERIFICATION AND FIX", "INFO")
    print_status("=" * 80, "INFO")
    
    # Step 1: Check/Start Backend
    print_status("\n[STEP 1] Checking backend...", "INFO")
    if not check_backend_running():
        if not start_backend():
            print_status("CRITICAL: Backend not running and could not start", "ERROR")
            return 1
    else:
        print_status("Backend is running", "OK")
    
    # Step 2: Check Broker Connectivity
    print_status("\n[STEP 2] Checking broker connectivity...", "INFO")
    broker_status = check_broker_connectivity()
    if broker_status["connected"]:
        print_status("Broker is connected", "OK")
    elif broker_status["credentials_present"]:
        print_status(f"Broker not connected: {broker_status.get('error', 'Unknown error')}", "WARN")
    else:
        print_status(f"Broker credentials missing: {broker_status.get('error', 'Unknown error')}", "WARN")
        print_status("NOTE: Broker will show as DISCONNECTED until credentials are configured", "INFO")
    
    # Step 3: Fix Broker Status in Backend
    print_status("\n[STEP 3] Fixing broker status reporting...", "INFO")
    fix_broker_status_in_backend()
    update_runtime_state_broker_check()
    
    # Step 4: Verify All Tabs
    print_status("\n[STEP 4] Verifying all dashboard tabs...", "INFO")
    tab_results = verify_all_tabs()
    
    # Step 5: Summary
    print_status("\n" + "=" * 80, "INFO")
    print_status("VERIFICATION SUMMARY", "INFO")
    print_status("=" * 80, "INFO")
    
    total_tabs = len(tab_results)
    working_tabs = sum(1 for r in tab_results.values() if r and r.get("status") == "ok")
    
    print_status(f"Total Tabs: {total_tabs}", "INFO")
    print_status(f"Working Tabs: {working_tabs}", "OK" if working_tabs == total_tabs else "WARN")
    print_status(f"Broker Status: {'CONNECTED' if broker_status['connected'] else 'DISCONNECTED'}", 
                 "OK" if broker_status['connected'] else "WARN")
    
    # Detailed results
    print_status("\nDetailed Results:", "INFO")
    for tab_name, result in tab_results.items():
        if result and result.get("status") == "ok":
            print_status(f"  {tab_name.upper()}: OK", "OK")
        else:
            print_status(f"  {tab_name.upper()}: ERROR", "ERROR")
            if result:
                for key, value in result.items():
                    if key != "status" and isinstance(value, dict) and value.get("status") != "ok":
                        print_status(f"    - {key}: {value.get('message', 'Unknown error')}", "ERROR")
    
    # Save results
    results_file = ROOT_DIR / "outputs" / "app_verification_results.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "broker_status": broker_status,
            "tab_results": tab_results,
            "summary": {
                "total_tabs": total_tabs,
                "working_tabs": working_tabs,
                "broker_connected": broker_status["connected"]
            }
        }, f, indent=2)
    
    print_status(f"\nResults saved to: {results_file}", "INFO")
    
    if working_tabs == total_tabs:
        print_status("\n✅ ALL TABS VERIFIED SUCCESSFULLY", "OK")
        return 0
    else:
        print_status(f"\nWARNING: {total_tabs - working_tabs} TAB(S) NEED ATTENTION", "WARN")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nVerification interrupted by user", "WARN")
        sys.exit(1)
    except Exception as e:
        print_status(f"\nFATAL ERROR: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
