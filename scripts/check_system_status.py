"""
Quick System Status Check - Shows what's actually happening
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Fix Unicode
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

IST = pytz.timezone("Asia/Kolkata")


def check_status():
    """Check current system status."""
    outputs_dir = ROOT_DIR / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("  SYSTEM STATUS CHECK")
    print("=" * 80)
    print()
    print(f"Current Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
    print()

    # Check files
    print("[FILE STATUS]")
    print("-" * 80)

    files_to_check = {
        "chain_raw_live.csv": 60,
        "pnl_live.json": 60,
        "positions_live.json": 60,
        "top_trade_signal.json": 60,
    }

    all_ok = True

    for filename, max_age in files_to_check.items():
        filepath = outputs_dir / filename
        if filepath.exists():
            age_seconds = datetime.now().timestamp() - filepath.stat().st_mtime
            age_minutes = age_seconds / 60
            size = filepath.stat().st_size

            if age_seconds < max_age:
                status = "✅ FRESH"
            else:
                status = "⚠️  STALE"
                all_ok = False

            print(f"  {status} {filename}")
            print(f"     Age: {age_minutes:.1f} minutes ({age_seconds:.1f} seconds)")
            print(f"     Size: {size:,} bytes")
            print(f"     Last Modified: {datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%H:%M:%S')}")

            # Check content
            if filename.endswith(".json"):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if data:
                        print(f"     Content: Valid ({len(data)} keys)")
                    else:
                        print(f"     Content: ⚠️  EMPTY")
                        all_ok = False
                except Exception as e:
                    print(f"     Content: ❌ ERROR - {e}")
                    all_ok = False
        else:
            print(f"  ❌ MISSING {filename}")
            all_ok = False

        print()

    # Check if system is updating
    print("[AUTO-UPDATE CHECK]")
    print("-" * 80)

    chain_file = outputs_dir / "chain_raw_live.csv"
    if chain_file.exists():
        print("  Monitoring chain_raw_live.csv for updates (10 seconds)...")
        import time

        mtime_before = chain_file.stat().st_mtime
        size_before = chain_file.stat().st_size

        time.sleep(10)

        if chain_file.exists():
            mtime_after = chain_file.stat().st_mtime
            size_after = chain_file.stat().st_size

            if mtime_after > mtime_before:
                print(f"  ✅ FILE IS UPDATING")
                print(f"     Updated during monitoring period")
                print(f"     Size change: {size_before:,} → {size_after:,} bytes")
            else:
                print(f"  ⚠️  FILE NOT UPDATING")
                print(f"     No changes detected in 10 seconds")
                print(f"     System may be stopped or stuck")
                all_ok = False
        else:
            print(f"  ❌ FILE DISAPPEARED")
            all_ok = False
    else:
        print(f"  ❌ FILE NOT FOUND")
        all_ok = False

    print()
    print("=" * 80)
    print()

    if all_ok:
        print("  ✅ ALL SYSTEMS WORKING - NO WARNINGS")
    else:
        print("  ⚠️  ISSUES FOUND - System needs attention")
        print()
        print("  RECOMMENDED ACTIONS:")
        print("    1. Check if trading system window is running")
        print("    2. Check for errors in trading system window")
        print("    3. Restart trading system if needed")
        print("    4. Verify market hours (system may be in virtual mode)")

    print()
    print("=" * 80)

    return all_ok


if __name__ == "__main__":
    sys.exit(0 if check_status() else 1)
