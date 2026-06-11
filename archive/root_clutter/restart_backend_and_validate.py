#!/usr/bin/env python3
"""
Restart Backend and Validate All Endpoints
Ensures backend is running with all new endpoints
"""
import sys
import subprocess
import time
import requests
from pathlib import Path

ROOT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8000"

def kill_backend_processes():
    """Kill any existing backend processes"""
    print("[Restart] Stopping existing backend processes...")
    try:
        # Find Python processes on port 8000
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True
        )
        
        # Find process using port 8000
        for line in result.stdout.split('\n'):
            if ':8000' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    try:
                        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                        print(f"[OK] Killed process {pid}")
                    except:
                        pass
    except:
        pass

def start_backend():
    """Start backend server"""
    print("[Restart] Starting backend server...")
    
    backend_dir = ROOT_DIR / "dashboard" / "backend"
    
    # Start backend in background
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(backend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for backend to start
    print("[Restart] Waiting for backend to start...")
    for i in range(30):
        try:
            res = requests.get(f"{BASE_URL}/api/health", timeout=2)
            if res.status_code == 200:
                print("[OK] Backend started successfully")
                return process
        except:
            time.sleep(1)
    
    print("[ERROR] Backend failed to start")
    return None

def test_all_endpoints():
    """Test all endpoints"""
    print("\n[Validation] Testing all endpoints...")
    
    endpoints = {
        "Health": "/api/health",
        "State": "/api/state",
        "Learning Insights": "/api/learning/insights",
        "Learning Status": "/api/learning/status",
        "Forensic Report": "/api/forensic/report",
        "Validation Status": "/api/validation/status",
        "Chain NIFTY": "/api/chain/NIFTY",
        "Signal Top": "/api/signal/top",
        "Positions": "/api/positions",
        "PnL": "/api/pnl"
    }
    
    results = {}
    for name, endpoint in endpoints.items():
        try:
            res = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if res.status_code == 200:
                print(f"[OK] {name}")
                results[name] = True
            else:
                print(f"[WARNING] {name}: Status {res.status_code}")
                results[name] = False
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            results[name] = False
    
    all_ok = all(results.values())
    print(f"\n[Result] All endpoints: {'WORKING' if all_ok else 'SOME FAILED'}")
    
    return all_ok

if __name__ == "__main__":
    print("="*80)
    print("RESTART BACKEND AND VALIDATE".center(80))
    print("="*80)
    
    # Kill existing processes
    kill_backend_processes()
    time.sleep(2)
    
    # Start backend
    process = start_backend()
    
    if process:
        # Test endpoints
        success = test_all_endpoints()
        
        if success:
            print("\n[OK] All endpoints working - Backend ready!")
        else:
            print("\n[WARNING] Some endpoints failed - Check backend logs")
        
        print("\n[Info] Backend is running. Press Ctrl+C to stop.")
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n[Info] Stopping backend...")
            process.terminate()
    else:
        print("\n[ERROR] Failed to start backend")
        sys.exit(1)
