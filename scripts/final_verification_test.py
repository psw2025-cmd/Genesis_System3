"""
Final verification test - Run system and verify all components work correctly.
"""

import json
import sys
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


def check_file_updates(outputs_dir, initial_times):
    """Check if files have been updated."""
    files_to_check = [
        "chain_raw_live.csv",
        "underlying_rank_live.csv",
        "top_trade_signal.json",
        "qc_report_live.json",
        "pnl_live.json",
    ]

    updated_files = []
    stale_files = []

    for filename in files_to_check:
        filepath = outputs_dir / filename
        if filepath.exists():
            current_time = filepath.stat().st_mtime
            initial_time = initial_times.get(filename, 0)

            if current_time > initial_time:
                age = time.time() - current_time
                updated_files.append(
                    {"filename": filename, "age_seconds": age, "size_kb": filepath.stat().st_size / 1024}
                )
            else:
                stale_files.append(filename)
        else:
            stale_files.append(filename)

    return updated_files, stale_files


def main():
    print("=" * 80)
    print("  FINAL VERIFICATION TEST")
    print("=" * 80)
    print()

    outputs_dir = ROOT_DIR / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    # Get initial file timestamps
    print("[1] Checking initial file states...")
    initial_times = {}
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
            initial_times[filename] = filepath.stat().st_mtime
            age = time.time() - initial_times[filename]
            print(f"    [OK] {filename}: exists ({age/60:.1f} min old)")
        else:
            initial_times[filename] = 0
            print(f"    [MISS] {filename}: not found")
    print()

    # Initialize runner
    print("[2] Initializing system...")
    try:
        runner = LiveChainRunner(
            refresh_interval=5, use_websocket=False, prefer_weekly=True, sim_mode=False, ignore_market_hours=True
        )
        print("    [OK] System initialized")
        print()
    except Exception as e:
        print(f"    [ERROR] Initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Run 2 cycles
    print("[3] Running 2 cycles to verify system...")
    print("    Watch for export messages...")
    print()
    print("=" * 80)

    try:
        # Run for 2 cycles (approximately 10-15 seconds)
        results = runner.run(duration_minutes=None, max_cycles=2)

        print()
        print("=" * 80)
        print("[4] Checking file updates...")
        print("=" * 80)

        # Wait a moment for file writes to complete
        time.sleep(2)

        # Check if files were updated
        updated_files, stale_files = check_file_updates(outputs_dir, initial_times)

        print("\nUpdated Files:")
        if updated_files:
            for file_info in updated_files:
                print(
                    f"  [OK] {file_info['filename']}: Updated ({file_info['age_seconds']:.1f}s ago, {file_info['size_kb']:.1f} KB)"
                )
        else:
            print("  [NONE] No files were updated")

        print("\nStale/Missing Files:")
        if stale_files:
            for filename in stale_files:
                print(f"  [ISSUE] {filename}: Not updated or missing")
        else:
            print("  [OK] All files updated")

        # Analyze updated files
        print("\n[5] Analyzing updated files...")
        if updated_files:
            for file_info in updated_files:
                filename = file_info["filename"]
                filepath = outputs_dir / filename

                if filename.endswith(".csv"):
                    try:
                        df = pd.read_csv(filepath)
                        print(f"\n  {filename}:")
                        print(f"    Rows: {len(df)}")
                        print(f"    Columns: {len(df.columns)}")
                        if "timestamp_ist" in df.columns:
                            latest = df["timestamp_ist"].iloc[-1] if len(df) > 0 else "N/A"
                            print(f"    Latest timestamp: {latest}")
                    except Exception as e:
                        print(f"    [ERROR] Failed to read: {e}")

                elif filename.endswith(".json"):
                    try:
                        with open(filepath, "r") as f:
                            data = json.load(f)
                        print(f"\n  {filename}:")
                        if isinstance(data, dict):
                            for key, value in list(data.items())[:5]:
                                print(f"    {key}: {value}")
                    except Exception as e:
                        print(f"    [ERROR] Failed to read: {e}")

        print()
        print("=" * 80)
        print("  VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Cycles completed: {runner.cycle_count}")
        print(f"Files updated: {len(updated_files)}/{len(files_to_check)}")
        print(f"Files stale/missing: {len(stale_files)}")

        if len(updated_files) == len(files_to_check):
            print("\n[SUCCESS] All files updated correctly!")
            return True
        elif len(updated_files) > 0:
            print("\n[PARTIAL] Some files updated, some issues remain")
            return False
        else:
            print("\n[FAILURE] No files were updated")
            return False

    except KeyboardInterrupt:
        print("\n[INFO] Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
