"""
Comprehensive Broker Credentials Validation and Test
Validates credentials, TOTP, and tests broker connection
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Load environment
from dotenv import load_dotenv
env_path = ROOT_DIR / "config" / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try root .env
    root_env = ROOT_DIR / ".env"
    if root_env.exists():
        load_dotenv(root_env)

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

def validate_credentials() -> Dict[str, Any]:
    """Validate credentials are present"""
    print_status("Validating credentials...", "INFO")
    
    required = {
        "ANGELONE_API_KEY": os.getenv("ANGELONE_API_KEY", "").strip(),
        "ANGELONE_CLIENT_ID": os.getenv("ANGELONE_CLIENT_ID", "").strip(),
        "ANGELONE_PIN": os.getenv("ANGELONE_PIN", "").strip(),
        "ANGELONE_PASSWORD": os.getenv("ANGELONE_PASSWORD", "").strip(),
        "ANGELONE_TOTP": os.getenv("ANGELONE_TOTP", "").strip()
    }
    
    result = {
        "all_present": False,
        "missing": [],
        "present": [],
        "pin_or_password": False
    }
    
    for key, value in required.items():
        if value:
            result["present"].append(key)
        else:
            if key != "ANGELONE_PASSWORD":  # Password is optional if PIN is set
                result["missing"].append(key)
    
    # Check if PIN or PASSWORD is set
    if required["ANGELONE_PIN"] or required["ANGELONE_PASSWORD"]:
        result["pin_or_password"] = True
        if "ANGELONE_PIN" in result["missing"]:
            result["missing"].remove("ANGELONE_PIN")
        if "ANGELONE_PASSWORD" in result["missing"]:
            result["missing"].remove("ANGELONE_PASSWORD")
    
    result["all_present"] = len(result["missing"]) == 0
    
    if result["all_present"]:
        print_status("All credentials present", "OK")
        for key in result["present"]:
            if key != "ANGELONE_PASSWORD":  # Don't show password
                masked = required[key][:4] + "***" if len(required[key]) > 4 else "***"
                print_status(f"  {key}: {masked}", "OK")
    else:
        print_status(f"Missing credentials: {', '.join(result['missing'])}", "ERROR")
    
    return result

def test_totp_generation() -> Dict[str, Any]:
    """Test TOTP generation"""
    print_status("Testing TOTP generation...", "INFO")
    
    try:
        import pyotp
        totp_secret = os.getenv("ANGELONE_TOTP", "").strip()
        
        if not totp_secret:
            return {"status": "FAIL", "error": "TOTP secret not found"}
        
        try:
            totp = pyotp.TOTP(totp_secret)
            code = totp.now()
            
            if len(code) == 6 and code.isdigit():
                print_status(f"TOTP generated successfully: {code}", "OK")
                return {"status": "PASS", "code_length": len(code), "is_valid": True}
            else:
                return {"status": "FAIL", "error": f"Invalid TOTP code format: {code}"}
        except Exception as e:
            return {"status": "FAIL", "error": f"TOTP generation failed: {e}"}
    except ImportError:
        return {"status": "FAIL", "error": "pyotp not installed"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_broker_connection() -> Dict[str, Any]:
    """Test broker connection"""
    print_status("Testing broker connection...", "INFO")
    
    try:
        from core.brokers.angel_one.broker import AngelOneBroker
        
        try:
            broker = AngelOneBroker(allow_data_only=True)
            print_status("Broker initialized successfully", "OK")
            
            # Test profile fetch
            print_status("Fetching profile...", "INFO")
            profile = broker.get_profile()
            
            if profile and profile.get("status"):
                clientcode = profile.get("data", {}).get("clientcode", "N/A")
                print_status(f"Profile fetched: Client Code = {clientcode}", "OK")
                return {
                    "status": "PASS",
                    "connected": True,
                    "profile": {
                        "status": profile.get("status"),
                        "clientcode": clientcode
                    }
                }
            else:
                return {"status": "FAIL", "error": "Profile fetch returned invalid response"}
        except Exception as e:
            error_msg = str(e)
            print_status(f"Broker connection failed: {error_msg[:200]}", "ERROR")
            return {"status": "FAIL", "error": error_msg, "connected": False}
    except ImportError as e:
        return {"status": "FAIL", "error": f"Broker module import failed: {e}"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_broker_api_calls() -> Dict[str, Any]:
    """Test broker API calls (read-only)"""
    print_status("Testing broker API calls...", "INFO")
    
    try:
        from core.brokers.angel_one.broker import AngelOneBroker
        broker = AngelOneBroker(allow_data_only=True)
        
        # Test LTP fetch
        print_status("Testing LTP fetch for SBIN-EQ...", "INFO")
        ltp = broker.get_ltp("NSE", "SBIN-EQ", "3045")
        
        if ltp:
            ltp_value = ltp.get("data", {}).get("ltp")
            if ltp_value:
                print_status(f"LTP fetched: SBIN-EQ = {ltp_value}", "OK")
                return {
                    "status": "PASS",
                    "ltp_test": {
                        "symbol": "SBIN-EQ",
                        "ltp": ltp_value
                    }
                }
            else:
                return {"status": "WARN", "message": "LTP response received but value not found"}
        else:
            return {"status": "WARN", "message": "LTP fetch returned None"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def main():
    """Main validation and test"""
    print_status("=" * 80, "INFO")
    print_status("BROKER CREDENTIALS VALIDATION AND TEST", "INFO")
    print_status("=" * 80, "INFO")
    
    results = {}
    
    # Step 1: Validate credentials
    print_status("\n[STEP 1] Validating credentials...", "INFO")
    creds_result = validate_credentials()
    results["credentials"] = creds_result
    
    if not creds_result["all_present"]:
        print_status("CRITICAL: Missing credentials. Cannot proceed with broker test.", "ERROR")
        return 1
    
    # Step 2: Test TOTP generation
    print_status("\n[STEP 2] Testing TOTP generation...", "INFO")
    totp_result = test_totp_generation()
    results["totp"] = totp_result
    if totp_result["status"] != "PASS":
        print_status(f"TOTP test failed: {totp_result.get('error')}", "ERROR")
        return 1
    
    # Step 3: Test broker connection
    print_status("\n[STEP 3] Testing broker connection...", "INFO")
    connection_result = test_broker_connection()
    results["connection"] = connection_result
    if connection_result["status"] != "PASS":
        print_status(f"Connection test failed: {connection_result.get('error')}", "ERROR")
        return 1
    
    # Step 4: Test API calls
    print_status("\n[STEP 4] Testing broker API calls...", "INFO")
    api_result = test_broker_api_calls()
    results["api_calls"] = api_result
    
    # Summary
    print_status("\n" + "=" * 80, "INFO")
    print_status("VALIDATION SUMMARY", "INFO")
    print_status("=" * 80, "INFO")
    
    all_passed = all([
        results["credentials"]["all_present"],
        results["totp"]["status"] == "PASS",
        results["connection"]["status"] == "PASS"
    ])
    
    print_status(f"Credentials: {'PASS' if creds_result['all_present'] else 'FAIL'}", 
                 "OK" if creds_result['all_present'] else "ERROR")
    print_status(f"TOTP Generation: {totp_result['status']}", 
                 "OK" if totp_result['status'] == "PASS" else "ERROR")
    print_status(f"Broker Connection: {connection_result['status']}", 
                 "OK" if connection_result['status'] == "PASS" else "ERROR")
    print_status(f"API Calls: {api_result['status']}", 
                 "OK" if api_result['status'] == "PASS" else "WARN")
    
    # Save results
    report_file = ROOT_DIR / "outputs" / "broker_validation_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "all_passed": all_passed,
            "credentials_valid": creds_result["all_present"],
            "totp_valid": totp_result["status"] == "PASS",
            "connection_valid": connection_result["status"] == "PASS",
            "api_calls_valid": api_result["status"] == "PASS"
        },
        "results": results
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print_status(f"\nReport saved to: {report_file}", "INFO")
    
    if all_passed:
        print_status("\nALL VALIDATIONS PASSED - Broker is ready", "OK")
        return 0
    else:
        print_status("\nVALIDATION FAILED - Check errors above", "ERROR")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nValidation interrupted", "WARN")
        sys.exit(1)
    except Exception as e:
        print_status(f"\nFATAL ERROR: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
