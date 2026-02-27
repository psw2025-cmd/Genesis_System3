"""
Track Desktop App - Monitor installation and startup
"""

import sys
import time
import requests
import subprocess
import psutil
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def check_process(name_pattern):
    """Check if process is running"""
    for proc in psutil.process_iter(["name", "pid", "memory_info"]):
        try:
            if name_pattern.lower() in proc.info["name"].lower():
                return proc.info
        except:
            pass
    return None


def main():
    print("=" * 70)
    print("Desktop App Installation & Tracking")
    print("=" * 70)
    print()

    # Check if EXE exists
    exe_path = Path("desktop_app/dist/win-unpacked/System3 Ultra.exe")
    installer_path = Path("desktop_app/dist/System3 Ultra Setup 1.0.0.exe")

    if not exe_path.exists() and not installer_path.exists():
        print("[ERROR] Desktop app not found")
        return 1

    print("[INFO] Desktop app files found")
    if exe_path.exists():
        print(f"  Portable: {exe_path} ({exe_path.stat().st_size / 1024 / 1024:.1f} MB)")
    if installer_path.exists():
        print(f"  Installer: {installer_path} ({installer_path.stat().st_size / 1024 / 1024:.1f} MB)")
    print()

    # Check if app is running
    print("=== Checking Running Processes ===")
    electron_proc = check_process("electron")
    system3_proc = check_process("System3")
    python_proc = check_process("python")

    if electron_proc:
        print(f"[OK] Electron process running: PID {electron_proc['pid']}")
    else:
        print("[INFO] Electron process not found")

    if system3_proc:
        print(f"[OK] System3 process running: PID {system3_proc['pid']}")
    else:
        print("[INFO] System3 process not found")

    if python_proc:
        print(f"[OK] Python process running: PID {python_proc['pid']}")
    else:
        print("[INFO] Python/Backend process not found")
    print()

    # Check backend
    print("=== Checking Backend ===")
    try:
        r = requests.get("http://localhost:8000/api/health", timeout=5)
        if r.status_code == 200:
            print("[OK] Backend is accessible")
            data = r.json()
            print(f"  Status: {data.get('status', 'N/A')}")
        else:
            print(f"[WARNING] Backend returned status {r.status_code}")
    except Exception as e:
        print(f"[WARNING] Backend not accessible: {str(e)[:50]}")
    print()

    # Check SSOT
    print("=== Checking SSOT ===")
    try:
        r = requests.get("http://localhost:8000/api/state", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"[OK] SSOT is accessible")
            print(f"  State Version: {data.get('state_version')}")
            print(f"  Data Source: {data.get('data_source')}")
            print(f"  Mode: {data.get('mode')}")
        else:
            print(f"[WARNING] SSOT returned status {r.status_code}")
    except Exception as e:
        print(f"[WARNING] SSOT not accessible: {str(e)[:50]}")
    print()

    # Summary
    print("=" * 70)
    print("[INFO] Desktop app tracking complete")
    print()
    print("To run the app:")
    if exe_path.exists():
        print(f"  {exe_path}")
    if installer_path.exists():
        print(f"  {installer_path}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
