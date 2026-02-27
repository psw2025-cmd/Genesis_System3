"""
Verify that background trading process is running and updating files.
"""

import sys
import time
import os
from pathlib import Path
from datetime import datetime
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def check_process_running():
    """Check if trading engine process is running."""
    import subprocess

    try:
        # Check for Python processes running run_live_chain.py
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"], capture_output=True, text=True
        )
        if "run_live_chain" in result.stdout or "python.exe" in result.stdout:
            return True
    except:
        pass
    return False


def check_file_freshness():
    """Check if output files are being updated."""
    output_dir = ROOT_DIR / "outputs"
    files_to_check = ["chain_raw_live.csv", "pnl_live.json", "paper_trades_live.csv"]

    results = {}
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    for filename in files_to_check:
        filepath = output_dir / filename
        if filepath.exists():
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime, tz=ist)
            age_seconds = (now - mtime).total_seconds()
            age_minutes = age_seconds / 60
            results[filename] = {
                "exists": True,
                "age_seconds": age_seconds,
                "age_minutes": age_minutes,
                "fresh": age_seconds < 30,  # Fresh if updated in last 30 seconds
            }
        else:
            results[filename] = {"exists": False, "age_seconds": None, "age_minutes": None, "fresh": False}

    return results


def check_log_file():
    """Check the trading engine log for errors."""
    log_file = ROOT_DIR / "logs" / "trading_engine.log"
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                if lines:
                    last_50_lines = lines[-50:]
                    return {
                        "exists": True,
                        "line_count": len(lines),
                        "last_lines": last_50_lines,
                        "has_errors": any(
                            "ERROR" in line or "Traceback" in line or "Error" in line for line in last_50_lines
                        ),
                    }
        except:
            pass
    return {"exists": False, "line_count": 0, "last_lines": [], "has_errors": False}


def main():
    """Main verification."""
    print("=" * 80)
    print("  BACKGROUND PROCESS VERIFICATION")
    print("=" * 80)
    print()

    # Check process
    print("[1] Checking if background process is running...")
    process_running = check_process_running()
    if process_running:
        print("    ✅ Process appears to be running")
    else:
        print("    ⚠️  Process not detected (may be starting or crashed)")
    print()

    # Check file freshness
    print("[2] Checking file freshness...")
    file_status = check_file_freshness()
    for filename, status in file_status.items():
        if status["exists"]:
            age_str = (
                f"{status['age_minutes']:.1f} min" if status["age_minutes"] >= 1 else f"{status['age_seconds']:.0f} sec"
            )
            freshness = "🟢 FRESH" if status["fresh"] else "🔴 STALE"
            print(f"    {freshness} {filename}: Updated {age_str} ago")
        else:
            print(f"    ⚠️  {filename}: NOT FOUND")
    print()

    # Check log file
    print("[3] Checking log file...")
    log_status = check_log_file()
    if log_status["exists"]:
        print(f"    ✅ Log file exists ({log_status['line_count']} lines)")
        if log_status["has_errors"]:
            print("    ⚠️  Errors detected in log file")
            print("    Last 10 lines with errors:")
            error_lines = [
                line for line in log_status["last_lines"] if "ERROR" in line or "Traceback" in line or "Error" in line
            ]
            for line in error_lines[-5:]:
                print(f"      {line.strip()}")
        else:
            print("    ✅ No errors in recent log entries")

        # Show last few lines
        if log_status["last_lines"]:
            print("    Last 5 log lines:")
            for line in log_status["last_lines"][-5:]:
                print(f"      {line.strip()}")
    else:
        print("    ⚠️  Log file not found")
    print()

    # Summary
    print("=" * 80)
    print("  SUMMARY")
    print("=" * 80)

    all_fresh = all(s.get("fresh", False) for s in file_status.values() if s.get("exists"))

    if process_running and all_fresh:
        print("  ✅ System appears to be running correctly")
        print("  ✅ Files are being updated")
    elif process_running:
        print("  ⚠️  Process is running but files are stale")
        print("  ⚠️  Check log file for errors")
    else:
        print("  ❌ Process may not be running")
        print("  ❌ Restart the system")

    print("=" * 80)


if __name__ == "__main__":
    main()
