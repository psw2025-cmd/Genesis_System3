#!/usr/bin/env python3
"""Restart backend and test all endpoints"""
import sys
import subprocess
import time
import requests
from pathlib import Path

ROOT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8000"

# Kill existing
print("Stopping existing backend...")
subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq *uvicorn*"], 
               capture_output=True, timeout=5)
time.sleep(3)

# Start backend
print("Starting backend...")
backend_dir = ROOT_DIR / "dashboard" / "backend"
process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=str(backend_dir),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for backend
print("Waiting for backend...")
for i in range(30):
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if r.status_code == 200:
            print("Backend started!")
            break
    except:
        time.sleep(1)
else:
    print("Backend failed to start")
    sys.exit(1)

# Test endpoints
print("\nTesting endpoints...")
endpoints = {
    "Learning Insights": "/api/learning/insights",
    "Learning Status": "/api/learning/status",
    "Forensic Report": "/api/forensic/report",
    "Validation Status": "/api/validation/status"
}

all_ok = True
for name, endpoint in endpoints.items():
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        if r.status_code == 200:
            print(f"[OK] {name}")
        else:
            print(f"[FAIL] {name}: {r.status_code}")
            all_ok = False
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        all_ok = False

if all_ok:
    print("\n[SUCCESS] All endpoints working!")
else:
    print("\n[FAIL] Some endpoints failed")
    sys.exit(1)
