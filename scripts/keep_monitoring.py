"""
Keep Monitoring - Continuously monitor and restart if needed
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

IST = pytz.timezone("Asia/Kolkata")


def check_file_updating(filepath: Path, check_seconds: int = 15) -> bool:
    """Check if file is updating."""
    if not filepath.exists():
        return False

    mtime_before = filepath.stat().st_mtime
    time.sleep(check_seconds)

    if not filepath.exists():
        return False

    mtime_after = filepath.stat().st_mtime
    return mtime_after > mtime_before


def restart_system():
    """Restart the trading system."""
    print(f"[{datetime.now(IST).strftime('%H:%M:%S')}] Restarting system...")

    # Kill existing
    subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], capture_output=True, shell=True)
    time.sleep(2)

    # Start new
    cmd = [
        sys.executable,
        str(ROOT_DIR / "scripts" / "smart_live_chain_runner.py"),
        "--refresh",
        "5",
        "--market-check",
        "30",
        "--no-websocket",
    ]

    subprocess.Popen(
        cmd, cwd=str(ROOT_DIR), creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )

    print(f"[{datetime.now(IST).strftime('%H:%M:%S')}] System restarted")
    time.sleep(30)  # Wait for initialization


def main():
    """Keep monitoring and maintaining system."""
    print("=" * 80)
    print("  KEEP SYSTEM RUNNING - AUTO MONITOR")
    print("=" * 80)
    print()
    print("Monitoring system and keeping it running...")
    print("Press Ctrl+C to stop")
    print()

    outputs_dir = ROOT_DIR / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    chain_file = outputs_dir / "chain_raw_live.csv"
    check_count = 0
    last_restart = datetime.now()

    try:
        while True:
            check_count += 1
            now = datetime.now(IST)

            # Check every 2 minutes
            if check_count % 24 == 0:  # Every 2 minutes (24 * 5 seconds)
                print(f"[{now.strftime('%H:%M:%S')}] Check #{check_count} - Verifying system...")

                # Check if file is updating
                if chain_file.exists():
                    age = (datetime.now().timestamp() - chain_file.stat().st_mtime) / 60

                    if age > 2:  # File older than 2 minutes
                        print(f"  ⚠️  File stale ({age:.1f} min old) - Restarting...")
                        restart_system()
                        last_restart = datetime.now()
                    else:
                        print(f"  ✅ System OK (file {age:.1f} min old)")
                else:
                    print(f"  ⚠️  File missing - Restarting...")
                    restart_system()
                    last_restart = datetime.now()

            time.sleep(5)  # Check every 5 seconds

    except KeyboardInterrupt:
        print()
        print("Monitoring stopped")


if __name__ == "__main__":
    main()
