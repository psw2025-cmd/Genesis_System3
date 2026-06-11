#!/usr/bin/env python3
"""
Quick Validation Before Build
Fast validation to ensure everything works before rebuilding
"""
import sys
import requests
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8000"

def test_critical_endpoints():
    """Test critical endpoints"""
    print("="*80)
    print("QUICK VALIDATION BEFORE BUILD".center(80))
    print("="*80)
    
    critical = {
        "Health": "/api/health",
        "Learning Insights": "/api/learning/insights",
        "Learning Status": "/api/learning/status",
        "Forensic Report": "/api/forensic/report",
        "Validation Status": "/api/validation/status"
    }
    
    results = {}
    for name, endpoint in critical.items():
        try:
            res = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if res.status_code == 200:
                print(f"[OK] {name}")
                results[name] = True
            else:
                print(f"[FAIL] {name}: Status {res.status_code}")
                results[name] = False
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            results[name] = False
    
    all_ok = all(results.values())
    print(f"\n[Result] {'ALL PASS' if all_ok else 'SOME FAILED'}")
    return all_ok

if __name__ == "__main__":
    success = test_critical_endpoints()
    sys.exit(0 if success else 1)
