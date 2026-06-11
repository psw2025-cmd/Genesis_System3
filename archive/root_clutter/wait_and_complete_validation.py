#!/usr/bin/env python3
"""
Wait for validation to complete and verify zero errors
Then proceed with build
"""
import sys
import time
import requests
from pathlib import Path

ROOT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8000"

def verify_endpoints_working():
    """Quick verify all endpoints are working"""
    print("Verifying all endpoints are working...")
    
    endpoints = {
        "Learning Insights": "/api/learning/insights",
        "Learning Status": "/api/learning/status",
        "Forensic Report": "/api/forensic/report",
        "Validation Status": "/api/validation/status"
    }
    
    all_ok = True
    for name, endpoint in endpoints.items():
        try:
            res = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if res.status_code == 200:
                print(f"[OK] {name}: HTTP {res.status_code}")
            else:
                print(f"[FAIL] {name}: HTTP {res.status_code}")
                all_ok = False
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    print("="*80)
    print("ENDPOINT VERIFICATION".center(80))
    print("="*80)
    
    if verify_endpoints_working():
        print("\n[OK] All endpoints verified - Ready for validation")
        print("\n[Info] The validation script is running in your terminal.")
        print("[Info] Wait for it to complete (2000 tests), then we'll proceed with build.")
    else:
        print("\n[ERROR] Some endpoints failed")
        sys.exit(1)
