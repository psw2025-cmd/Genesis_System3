"""
Desktop App Monitor - Continuous tracking of app behavior
"""

import sys
import time
import requests
import psutil
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def get_system3_processes():
    """Get all System3 Ultra processes"""
    processes = []
    for proc in psutil.process_iter(["pid", "name", "memory_info", "create_time"]):
        try:
            if "System3" in proc.info["name"]:
                processes.append(
                    {
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "memory_mb": proc.info["memory_info"].rss / 1024 / 1024,
                        "started": datetime.fromtimestamp(proc.info["create_time"]).strftime("%H:%M:%S"),
                    }
                )
        except:
            pass
    return processes


def check_backend():
    """Check backend status"""
    try:
        r = requests.get("http://localhost:8000/api/health", timeout=3)
        if r.status_code == 200:
            return {"status": "running", "code": 200}
        return {"status": "error", "code": r.status_code}
    except:
        return {"status": "not_accessible", "code": 0}


def check_ssot():
    """Check SSOT status"""
    try:
        r = requests.get("http://localhost:8000/api/state", timeout=3)
        if r.status_code == 200:
            data = r.json()
            return {
                "status": "ok",
                "version": data.get("state_version"),
                "data_source": data.get("data_source"),
                "mode": data.get("mode"),
            }
        return {"status": "error", "code": r.status_code}
    except:
        return {"status": "not_accessible"}


def main():
    print("=" * 70)
    print("Desktop App Monitor - Continuous Tracking")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"\n--- Cycle {cycle} ({datetime.now().strftime('%H:%M:%S')}) ---")

            # Check processes
            processes = get_system3_processes()
            print(f"System3 Processes: {len(processes)}")
            if processes:
                total_memory = sum(p["memory_mb"] for p in processes)
                print(f"  Total Memory: {total_memory:.1f} MB")
                print(f"  PIDs: {', '.join(str(p['pid']) for p in processes[:5])}")

            # Check backend
            backend = check_backend()
            if backend["status"] == "running":
                print(f"Backend: RUNNING (Status: {backend['code']})")
            else:
                print(f"Backend: {backend['status'].upper()}")

            # Check SSOT
            ssot = check_ssot()
            if ssot.get("status") == "ok":
                print(f"SSOT: OK (Version: {ssot.get('version')}, Source: {ssot.get('data_source')})")
            else:
                print(f"SSOT: {ssot.get('status', 'UNKNOWN').upper()}")

            # Wait before next cycle
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n[INFO] Monitoring stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Monitoring error: {e}")


if __name__ == "__main__":
    main()
