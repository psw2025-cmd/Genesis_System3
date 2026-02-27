"""
Verify Tri-State System is Working
Shows proof that files are updating in all modes
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import json
import pandas as pd
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


def verify_files():
    """Verify all files are updating correctly."""
    outputs_dir = ROOT_DIR / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("  TRI-STATE SYSTEM VERIFICATION")
    print("=" * 80)
    print()
    print(f"Current Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
    print()

    # Check chain_raw_live.csv
    print("[1] chain_raw_live.csv")
    print("-" * 80)
    chain_file = outputs_dir / "chain_raw_live.csv"
    if chain_file.exists():
        age = datetime.now().timestamp() - chain_file.stat().st_mtime
        size = chain_file.stat().st_size

        print(f"  ✅ File exists")
        print(f"  Age: {age:.1f} seconds")
        print(f"  Size: {size:,} bytes")

        # Check content
        try:
            df = pd.read_csv(chain_file, nrows=1)
            if "status" in df.columns and len(df) > 0:
                status = df["status"].iloc[0]
                print(f"  Status: {status}")
                if status == "MARKET_CLOSED":
                    print(f"  Mode: HEARTBEAT (OK - System active)")
                else:
                    print(f"  Mode: DATA (OK - System active)")
            else:
                print(f"  Mode: DATA (OK - System active)")
        except Exception as e:
            print(f"  ⚠️  Error reading file: {e}")

        # Monitor for updates
        print()
        print("  Monitoring for 10 seconds to verify updates...")
        mtime_before = chain_file.stat().st_mtime
        time.sleep(10)

        if chain_file.exists():
            mtime_after = chain_file.stat().st_mtime
            if mtime_after > mtime_before:
                print(f"  ✅ FILE UPDATED during monitoring!")
                print(f"     Proof: System is actively writing files")
            else:
                print(f"  ⚠️  File not updated (may be in initialization)")
    else:
        print(f"  ❌ File not found")

    print()

    # Check qc_report_live.json
    print("[2] qc_report_live.json")
    print("-" * 80)
    qc_file = outputs_dir / "qc_report_live.json"
    if qc_file.exists():
        age = datetime.now().timestamp() - qc_file.stat().st_mtime
        print(f"  ✅ File exists")
        print(f"  Age: {age:.1f} seconds")

        try:
            with open(qc_file, "r") as f:
                qc_data = json.load(f)
            print(f"  Status: {qc_data.get('status', 'N/A')}")
            print(f"  Mode: {qc_data.get('mode', 'N/A')}")
            print(f"  Timestamp: {qc_data.get('timestamp', 'N/A')}")
        except Exception as e:
            print(f"  ⚠️  Error reading: {e}")
    else:
        print(f"  ❌ File not found")

    print()

    # Check top_trade_signal.json
    print("[3] top_trade_signal.json")
    print("-" * 80)
    signal_file = outputs_dir / "top_trade_signal.json"
    if signal_file.exists():
        age = datetime.now().timestamp() - signal_file.stat().st_mtime
        print(f"  ✅ File exists")
        print(f"  Age: {age:.1f} seconds")

        try:
            with open(signal_file, "r") as f:
                signal_data = json.load(f)
            print(f"  Action: {signal_data.get('action', 'N/A')}")
            print(f"  Mode: {signal_data.get('mode', 'N/A')}")
            print(f"  Timestamp: {signal_data.get('timestamp', 'N/A')}")
        except Exception as e:
            print(f"  ⚠️  Error reading: {e}")
    else:
        print(f"  ❌ File not found")

    print()

    # Check logs for SIM_MODE
    print("[4] Log Verification")
    print("-" * 80)
    log_file = ROOT_DIR / "logs" / f"{datetime.now(IST).strftime('%Y-%m-%d')}.log"
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                sim_mode_lines = [
                    l for l in lines[-100:] if "SIM_MODE ACTIVE" in l or "SIMULATION mode" in l or "MARKET_CLOSED" in l
                ]
                if sim_mode_lines:
                    print(f"  ✅ Found {len(sim_mode_lines)} relevant log entries")
                    print(f"  Latest entries:")
                    for line in sim_mode_lines[-3:]:
                        print(f"    {line.strip()[:100]}")
                else:
                    print(f"  ⚠️  No SIM_MODE entries found in recent logs")
        except Exception as e:
            print(f"  ⚠️  Error reading logs: {e}")
    else:
        print(f"  ⚠️  Log file not found")

    print()
    print("=" * 80)
    print("  VERIFICATION COMPLETE")
    print("=" * 80)
    print()
    print("If files are updating, system is working correctly!")
    print()


if __name__ == "__main__":
    verify_files()
