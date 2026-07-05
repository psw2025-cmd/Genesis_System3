"""
Restart Backend with All Fixes Applied
Kills existing backend and restarts with new code
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent


def kill_backend():
    """Kill existing backend processes"""
    import psutil

    killed = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info.get("cmdline", [])
            if cmdline and any("uvicorn" in str(c).lower() or "app.py" in str(c) for c in cmdline):
                if "dashboard" in str(cmdline) or "backend" in str(cmdline):
                    proc.kill()
                    killed.append(proc.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return killed


def start_backend():
    """Start backend with new code"""
    backend_dir = ROOT_DIR / "dashboard" / "backend"
    os.chdir(backend_dir)

    # Start backend
    cmd = [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(backend_dir))
    return process


def main():
    """Main function"""
    print("=" * 70)
    print("RESTARTING BACKEND WITH ALL FIXES")
    print("=" * 70)

    # Kill existing backend
    print("\n[1] Killing existing backend processes...")
    killed = kill_backend()
    if killed:
        print(f"   Killed {len(killed)} process(es): {killed}")
        time.sleep(2)
    else:
        print("   No existing backend processes found")

    # Start backend
    print("\n[2] Starting backend with fixes...")
    process = start_backend()
    print(f"   Backend started (PID: {process.pid})")
    print("   Waiting for startup...")
    time.sleep(5)

    # Check if backend is running
    print("\n[3] Verifying backend is running...")
    import requests

    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running and responding")
            data = response.json()
            print(f"   Total PnL: ₹{data.get('total_pnl', 0):.2f}")
        else:
            print(f"   ⚠️ Backend responded with status {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Backend not responding yet: {e}")
        print("   Wait a few more seconds and check manually")

    print("\n" + "=" * 70)
    print("BACKEND RESTART COMPLETE")
    print("=" * 70)
    print("\nNew endpoints available:")
    print("  - GET /api/trades/today")
    print("  - GET /api/trades/history?date=YYYY-MM-DD&start_time=HH:MM&end_time=HH:MM")
    print("\nBackend running in background (PID: {})".format(process.pid))
    print("Check logs for any errors\n")


if __name__ == "__main__":
    main()
