"""
Run and monitor the entire system, checking all components and resolving issues.
"""

import json
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytz

# Fix Unicode encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.run_live_chain import LiveChainRunner
from src.utils.market_hours import is_market_open


def check_output_files():
    """Check if output files exist and are recent."""
    outputs_dir = ROOT_DIR / "outputs"
    files_status = {}

    files_to_check = [
        "chain_raw_live.csv",
        "underlying_rank_live.csv",
        "top_trade_signal.json",
        "qc_report_live.json",
        "pnl_live.json",
    ]

    for filename in files_to_check:
        filepath = outputs_dir / filename
        if filepath.exists():
            age = time.time() - filepath.stat().st_mtime
            files_status[filename] = {
                "exists": True,
                "age_seconds": age,
                "age_minutes": age / 60,
                "size_kb": filepath.stat().st_size / 1024,
            }
        else:
            files_status[filename] = {"exists": False}

    return files_status


def monitor_system(duration_minutes=5):
    """Monitor the system for specified duration."""
    print("=" * 80)
    print("  SYSTEM MONITORING AND RESOLUTION")
    print("=" * 80)
    print()

    # Check market hours
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    market_open, reason = is_market_open(now)

    print(f"[1] Market Status Check")
    print(f"    Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"    Status: {'OPEN' if market_open else 'CLOSED'}")
    print(f"    Reason: {reason}")
    print()

    # Initialize runner
    print("[2] Initializing System...")
    try:
        runner = LiveChainRunner(
            refresh_interval=5,
            use_websocket=False,  # Use REST for reliability
            prefer_weekly=True,
            sim_mode=False,
            ignore_market_hours=True,  # Run regardless of market hours
        )
        print("    [OK] System initialized")
        print()
    except Exception as e:
        print(f"    [ERROR] Initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Check initial output files
    print("[3] Checking Initial Output Files...")
    initial_files = check_output_files()
    for filename, status in initial_files.items():
        if status.get("exists"):
            print(f"    [OK] {filename} exists ({status['age_minutes']:.1f} min old, {status['size_kb']:.1f} KB)")
        else:
            print(f"    [MISS] {filename} not found")
    print()

    # Run system
    print(f"[4] Running System for {duration_minutes} minutes...")
    print(f"    Watch for cycle messages below...")
    print()
    print("=" * 80)

    start_time = time.time()
    issues_found = []

    try:
        # Run in a separate thread to monitor
        results = []

        def run_system():
            nonlocal results
            try:
                results = runner.run(duration_minutes=duration_minutes, max_cycles=None)
            except Exception as e:
                issues_found.append(f"System run error: {e}")

        system_thread = threading.Thread(target=run_system, daemon=True)
        system_thread.start()

        # Monitor while running
        check_interval = 10  # Check every 10 seconds
        elapsed = 0
        last_cycle_count = 0

        while elapsed < duration_minutes * 60:
            time.sleep(check_interval)
            elapsed = time.time() - start_time

            # Check cycle progress
            current_cycle = runner.cycle_count
            if current_cycle > last_cycle_count:
                print(f"[MONITOR] Cycle {current_cycle} completed (elapsed: {elapsed/60:.1f} min)")
                last_cycle_count = current_cycle

            # Check output files
            files = check_output_files()
            for filename, status in files.items():
                if status.get("exists"):
                    age_min = status["age_minutes"]
                    if age_min > 2:  # File older than 2 minutes
                        issues_found.append(f"{filename} is stale ({age_min:.1f} min old)")

        # Wait for thread to complete
        system_thread.join(timeout=5)

    except KeyboardInterrupt:
        print("\n[INFO] Monitoring interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Monitoring error: {e}")
        import traceback

        traceback.print_exc()

    print()
    print("=" * 80)
    print("[5] Final Status Check")
    print("=" * 80)

    # Check final output files
    final_files = check_output_files()
    print("\nOutput Files Status:")
    for filename, status in final_files.items():
        if status.get("exists"):
            age_min = status["age_minutes"]
            size_kb = status["size_kb"]
            status_icon = "[OK]" if age_min < 1 else "[STALE]"
            print(f"  {status_icon} {filename}: {age_min:.1f} min old, {size_kb:.1f} KB")

            # Analyze CSV files
            if filename.endswith(".csv") and age_min < 1:
                try:
                    df = pd.read_csv(ROOT_DIR / "outputs" / filename)
                    print(f"      Rows: {len(df)}, Columns: {len(df.columns)}")
                except:
                    pass
        else:
            print(f"  [MISS] {filename}: Not found")

    # Check for issues
    print("\nIssues Found:")
    if issues_found:
        for issue in issues_found:
            print(f"  [ISSUE] {issue}")
    else:
        print("  [OK] No issues found")

    # Summary
    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80)
    print(f"Total cycles completed: {runner.cycle_count}")
    print(f"Monitoring duration: {elapsed/60:.1f} minutes")
    print(f"Output files: {sum(1 for f in final_files.values() if f.get('exists'))}/5")
    print(f"Issues found: {len(issues_found)}")
    print()

    return len(issues_found) == 0


if __name__ == "__main__":
    success = monitor_system(duration_minutes=3)  # Run for 3 minutes
    sys.exit(0 if success else 1)
