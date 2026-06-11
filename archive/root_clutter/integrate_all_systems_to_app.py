#!/usr/bin/env python3
"""
Integrate All Systems to App
Adds API endpoints and ensures all systems are accessible from the dashboard
"""
import sys
import requests
from pathlib import Path

ROOT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8000"

def test_all_endpoints():
    """Test all new endpoints"""
    print("="*80)
    print("TESTING ALL INTEGRATED ENDPOINTS".center(80))
    print("="*80)
    
    endpoints = {
        "Learning Insights": "/api/learning/insights",
        "Learning Status": "/api/learning/status",
        "Forensic Report": "/api/forensic/report",
        "Validation Status": "/api/validation/status",
    }
    
    results = {}
    for name, endpoint in endpoints.items():
        try:
            res = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if res.status_code == 200:
                print(f"[OK] {name}: Working")
                results[name] = True
            else:
                print(f"[WARNING] {name}: Status {res.status_code}")
                results[name] = False
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            results[name] = False
    
    print("\n" + "="*80)
    print("INTEGRATION TEST RESULTS".center(80))
    print("="*80)
    
    for name, result in results.items():
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    all_ok = all(results.values())
    print(f"\n[Overall] All endpoints: {'WORKING' if all_ok else 'SOME FAILED'}")
    
    return all_ok

if __name__ == "__main__":
    test_all_endpoints()
