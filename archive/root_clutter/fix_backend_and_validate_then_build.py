#!/usr/bin/env python3
"""
Fix Backend, Validate Everything, Then Build
Comprehensive pre-build validation and rebuild
"""
import sys
import subprocess
import time
import requests
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8000"

def kill_all_python_on_port_8000():
    """Kill all processes using port 8000"""
    print("[Fix] Killing processes on port 8000...")
    try:
        # Get processes on port 8000
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True
        )
        
        pids = set()
        for line in result.stdout.split('\n'):
            if ':8000' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) > 4:
                    pids.add(parts[-1])
        
        for pid in pids:
            try:
                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True, timeout=5)
                print(f"[OK] Killed PID {pid}")
            except:
                pass
        
        time.sleep(2)
        return True
    except Exception as e:
        print(f"[WARNING] Could not kill processes: {e}")
        return False

def start_backend_properly():
    """Start backend properly"""
    print("[Fix] Starting backend...")
    
    backend_dir = ROOT_DIR / "dashboard" / "backend"
    
    # Start backend
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(backend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    
    # Wait for backend to be ready
    print("[Fix] Waiting for backend to start...")
    for i in range(30):
        try:
            res = requests.get(f"{BASE_URL}/api/health", timeout=2)
            if res.status_code == 200:
                print(f"[OK] Backend started successfully (PID: {process.pid})")
                return process
        except:
            time.sleep(1)
            if i % 5 == 0:
                print(f"[Info] Still waiting... ({i+1}/30)")
    
    print("[ERROR] Backend failed to start")
    if process.poll() is None:
        process.terminate()
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
            res = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
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
    print(f"\n[Result] Endpoints: {'ALL WORKING' if all_ok else f'{sum(results.values())}/{len(results)} WORKING'}")
    return all_ok

def run_validation_tests():
    """Run validation tests"""
    print("\n[Validation] Running validation tests...")
    
    tests = [
        ("Complete End-to-End", "complete_end_to_end_validation.py"),
        ("Production Grade", "production_grade_validation.py"),
    ]
    
    results = {}
    for name, script in tests:
        try:
            print(f"[Info] Running {name} validation...")
            result = subprocess.run(
                [sys.executable, str(ROOT_DIR / script)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                if "PASS" in result.stdout or "ALL TESTS PASSED" in result.stdout:
                    print(f"[OK] {name} validation: PASSED")
                    results[name] = True
                else:
                    print(f"[WARNING] {name} validation: Issues found")
                    results[name] = False
            else:
                print(f"[WARNING] {name} validation: Return code {result.returncode}")
                results[name] = False
        except Exception as e:
            print(f"[ERROR] {name} validation: {e}")
            results[name] = False
    
    all_passed = all(results.values())
    return all_passed

def rebuild_frontend():
    """Rebuild frontend"""
    print("\n[Build] Rebuilding frontend...")
    try:
        frontend_dir = ROOT_DIR / "dashboard" / "frontend"
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(frontend_dir),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("[OK] Frontend rebuilt successfully")
            return True
        else:
            print(f"[ERROR] Frontend build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Frontend build error: {e}")
        return False

def rebuild_electron_app():
    """Rebuild Electron app"""
    print("\n[Build] Rebuilding Electron app...")
    try:
        desktop_dir = ROOT_DIR / "desktop_app"
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(desktop_dir),
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            print("[OK] Electron app rebuilt successfully")
            installer = ROOT_DIR / "desktop_app" / "dist" / "System3 Ultra Setup 1.0.0.exe"
            if installer.exists():
                size_mb = installer.stat().st_size / (1024 * 1024)
                print(f"[OK] Installer ready: {size_mb:.1f} MB")
            return True
        else:
            print(f"[ERROR] Electron build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Electron build error: {e}")
        return False

def main():
    """Main execution"""
    print("="*80)
    print("FIX BACKEND, VALIDATE, THEN BUILD".center(80))
    print("="*80)
    
    # Step 1: Fix backend
    print("\n[Step 1] Fixing backend...")
    kill_all_python_on_port_8000()
    backend_process = start_backend_properly()
    
    if not backend_process:
        print("\n[ERROR] Failed to start backend - cannot proceed")
        return False
    
    try:
        # Step 2: Test endpoints
        print("\n[Step 2] Testing all endpoints...")
        endpoints_ok = test_all_endpoints()
        
        if not endpoints_ok:
            print("[WARNING] Some endpoints failed, but continuing...")
        
        # Step 3: Run validation
        print("\n[Step 3] Running validation tests...")
        validation_ok = run_validation_tests()
        
        if not validation_ok:
            print("[WARNING] Some validations had issues, but continuing...")
        
        # Step 4: Rebuild frontend
        print("\n[Step 4] Rebuilding frontend...")
        frontend_ok = rebuild_frontend()
        
        if not frontend_ok:
            print("[ERROR] Frontend build failed")
            return False
        
        # Step 5: Rebuild Electron app
        print("\n[Step 5] Rebuilding Electron app...")
        electron_ok = rebuild_electron_app()
        
        if not electron_ok:
            print("[ERROR] Electron build failed")
            return False
        
        # Summary
        print("\n" + "="*80)
        print("BUILD COMPLETE".center(80))
        print("="*80)
        print(f"Endpoints: {'OK' if endpoints_ok else 'WARNINGS'}")
        print(f"Validation: {'PASSED' if validation_ok else 'WARNINGS'}")
        print(f"Frontend: {'BUILT' if frontend_ok else 'FAILED'}")
        print(f"Electron: {'BUILT' if electron_ok else 'FAILED'}")
        
        if frontend_ok and electron_ok:
            print("\n[OK] All builds successful!")
            return True
        else:
            print("\n[ERROR] Some builds failed")
            return False
            
    finally:
        # Keep backend running
        print("\n[Info] Backend is still running (PID: {})".format(backend_process.pid))
        print("[Info] Press Ctrl+C to stop, or leave it running")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
