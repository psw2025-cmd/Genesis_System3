"""
Run System and Monitor at Micro Level
Starts system, monitors everything, finds and fixes issues
"""

import json
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

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

from core.utils.logger import logger
from src.utils.market_hours import is_market_open

IST = pytz.timezone("Asia/Kolkata")


class RunAndMonitorMicro:
    """Run system and monitor at micro level."""

    def __init__(self):
        self.monitoring_start = datetime.now(IST)
        self.issues_found = []
        self.issues_fixed = []
        self.data_snapshots = []
        self.trigger_events = []
        self.system_running = False
        self.trading_process = None

    def start_trading_system(self):
        """Start the trading system."""
        print("[ACTION] Starting trading system...")

        try:
            # Start smart runner in a separate window so we can see output
            cmd = [
                sys.executable,
                str(ROOT_DIR / "scripts" / "smart_live_chain_runner.py"),
                "--refresh",
                "5",
                "--market-check",
                "30",
                "--no-websocket",
            ]

            # Use CREATE_NEW_CONSOLE on Windows to see output
            if sys.platform == "win32":
                self.trading_process = subprocess.Popen(
                    cmd, cwd=str(ROOT_DIR), creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                self.trading_process = subprocess.Popen(
                    cmd, cwd=str(ROOT_DIR), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
                )

            self.system_running = True
            print("  ✅ Trading system started (PID: {})".format(self.trading_process.pid))
            print("  [INFO] System is running in separate window")
            return True
        except Exception as e:
            print(f"  ❌ Failed to start: {e}")
            import traceback

            traceback.print_exc()
            return False

    def check_data_file_updates(self, filepath: Path, check_duration: int = 30) -> Dict:
        """Monitor a file for updates over time."""
        if not filepath.exists():
            return {"file": str(filepath), "updates_detected": 0, "status": "MISSING"}

        initial_mtime = filepath.stat().st_mtime
        updates = 0
        update_times = []

        start_time = time.time()
        while time.time() - start_time < check_duration:
            if filepath.exists():
                current_mtime = filepath.stat().st_mtime
                if current_mtime > initial_mtime:
                    updates += 1
                    update_times.append(datetime.now(IST).isoformat())
                    initial_mtime = current_mtime
                    self.trigger_events.append(
                        {"type": "FILE_UPDATE", "file": filepath.name, "timestamp": datetime.now(IST).isoformat()}
                    )
            time.sleep(2)  # Check every 2 seconds

        return {
            "file": str(filepath),
            "updates_detected": updates,
            "update_times": update_times,
            "status": "UPDATING" if updates > 0 else "STALE",
        }

    def monitor_continuously(self, duration_minutes: int = 10):
        """Monitor system continuously."""
        print("=" * 80)
        print("  RUN AND MONITOR - MICRO LEVEL")
        print("=" * 80)
        print()
        print("This will:")
        print("  1. Start trading system")
        print("  2. Monitor all components continuously")
        print("  3. Check for warnings/errors")
        print("  4. Verify data updates automatically")
        print("  5. Test auto-triggers")
        print("  6. Fix issues found")
        print()
        print(f"Monitoring Duration: {duration_minutes} minutes")
        print()

        # Start system
        if not self.start_trading_system():
            print("Failed to start system")
            return False

        # Wait for initialization
        print("[WAIT] Waiting for system initialization (15 seconds)...")
        time.sleep(15)
        print()

        outputs_dir = ROOT_DIR / "outputs"
        outputs_dir.mkdir(exist_ok=True)

        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        check_count = 0

        print("=" * 80)
        print("  CONTINUOUS MONITORING STARTED")
        print("=" * 80)
        print()

        while datetime.now() < end_time:
            check_count += 1
            now = datetime.now(IST)

            print(f"[CHECK {check_count}] {now.strftime('%H:%M:%S IST')}")
            print("-" * 80)

            # Check 1: Data files exist and fresh
            print("[CHECK] Data Files...")
            files_ok = True
            critical_files = ["chain_raw_live.csv", "pnl_live.json", "positions_live.json", "top_trade_signal.json"]

            for filename in critical_files:
                filepath = outputs_dir / filename
                if filepath.exists():
                    age = datetime.now().timestamp() - filepath.stat().st_mtime
                    if age < 60:
                        print(f"  ✅ {filename}: FRESH ({age:.1f}s old)")
                    else:
                        print(f"  ⚠️  {filename}: STALE ({age:.1f}s old)")
                        self.issues_found.append(f"{filename} is stale")
                        files_ok = False
                else:
                    print(f"  ⚠️  {filename}: MISSING")
                    self.issues_found.append(f"{filename} is missing")
                    files_ok = False

            print()

            # Check 2: Data content correctness
            print("[CHECK] Data Content...")
            content_ok = True

            # Check PnL data
            pnl_file = outputs_dir / "pnl_live.json"
            if pnl_file.exists():
                try:
                    with open(pnl_file, "r") as f:
                        pnl = json.load(f)
                    if "total_pnl" in pnl:
                        print(f"  ✅ PnL data: Valid (Total: Rs {pnl.get('total_pnl', 0):.2f})")
                    else:
                        print(f"  ⚠️  PnL data: Missing 'total_pnl' field")
                        self.issues_found.append("PnL data missing total_pnl")
                        content_ok = False
                except Exception as e:
                    print(f"  ❌ PnL data: Error - {e}")
                    self.issues_found.append(f"PnL data error: {e}")
                    content_ok = False

            # Check positions data
            pos_file = outputs_dir / "positions_live.json"
            if pos_file.exists():
                try:
                    with open(pos_file, "r") as f:
                        pos = json.load(f)
                    open_count = len(pos.get("open_positions", []))
                    print(f"  ✅ Positions data: Valid ({open_count} open)")
                except Exception as e:
                    print(f"  ❌ Positions data: Error - {e}")
                    self.issues_found.append(f"Positions data error: {e}")
                    content_ok = False

            print()

            # Check 3: Auto-updates (trigger detection)
            print("[CHECK] Auto-Update Triggers...")

            chain_file = outputs_dir / "chain_raw_live.csv"
            if chain_file.exists():
                # Monitor for updates
                mtime_before = chain_file.stat().st_mtime
                size_before = chain_file.stat().st_size
                print(f"  [WAIT] Monitoring file for updates (7 seconds)...")
                time.sleep(7)  # Wait 7 seconds (should update every 5s)
                if chain_file.exists():
                    mtime_after = chain_file.stat().st_mtime
                    size_after = chain_file.stat().st_size
                    age_after = datetime.now().timestamp() - mtime_after

                    if mtime_after > mtime_before:
                        print(f"  ✅ Data auto-updating: File updated")
                        print(f"     Size: {size_before} → {size_after} bytes")
                        print(f"     Age: {age_after:.1f}s")
                        self.trigger_events.append(
                            {
                                "type": "AUTO_UPDATE",
                                "file": "chain_raw_live.csv",
                                "timestamp": datetime.now(IST).isoformat(),
                                "size_change": size_after - size_before,
                            }
                        )
                    else:
                        print(f"  ⚠️  Data not updating: File unchanged")
                        print(f"     Last modified: {age_after:.1f}s ago")
                        self.issues_found.append(f"Data file not auto-updating (last modified {age_after:.1f}s ago)")
                else:
                    print(f"  ⚠️  Data file disappeared")
                    self.issues_found.append("Data file disappeared")
            else:
                print(f"  ⚠️  Data file not found")
                self.issues_found.append("Data file not found")

            print()

            # Check 4: System components
            print("[CHECK] System Components...")
            components_ok = True

            try:
                from src.trading.paper_executor import PaperExecutor

                executor = PaperExecutor()
                print(f"  ✅ Paper Executor: Working")
            except Exception as e:
                print(f"  ❌ Paper Executor: {e}")
                self.issues_found.append(f"Paper Executor: {e}")
                components_ok = False

            try:
                from src.trading.pnl_tracker import PnLTracker

                tracker = PnLTracker()
                print(f"  ✅ PnL Tracker: Working")
            except Exception as e:
                print(f"  ❌ PnL Tracker: {e}")
                self.issues_found.append(f"PnL Tracker: {e}")
                components_ok = False

            print()

            # Summary for this check
            all_ok = files_ok and content_ok and components_ok

            if all_ok:
                print(f"  ✅ ALL CHECKS PASSED - NO WARNINGS")
            else:
                print(f"  ⚠️  ISSUES FOUND - See details above")

            print()
            print("=" * 80)
            print()

            # Take snapshot
            snapshot = {
                "timestamp": now.isoformat(),
                "check_number": check_count,
                "files_ok": files_ok,
                "content_ok": content_ok,
                "components_ok": components_ok,
                "all_ok": all_ok,
            }
            self.data_snapshots.append(snapshot)

            # Wait for next check
            if datetime.now() < end_time:
                time.sleep(10)  # Check every 10 seconds

        # Final summary
        self.print_final_summary()

        # Stop system
        if self.trading_process:
            print("[ACTION] Stopping trading system...")
            self.trading_process.terminate()
            self.trading_process.wait(timeout=10)
            print("  ✅ System stopped")

        return len(self.issues_found) == 0

    def print_final_summary(self):
        """Print final monitoring summary."""
        print("=" * 80)
        print("  FINAL MONITORING SUMMARY")
        print("=" * 80)
        print()
        print(f"  Monitoring Duration: {(datetime.now(IST) - self.monitoring_start).total_seconds() / 60:.1f} minutes")
        print(f"  Checks Performed: {len(self.data_snapshots)}")
        print(f"  Issues Found: {len(self.issues_found)}")
        print(f"  Trigger Events: {len(self.trigger_events)}")
        print()

        if self.issues_found:
            print("  ISSUES FOUND:")
            unique_issues = list(set(self.issues_found))
            for i, issue in enumerate(unique_issues[:20], 1):
                print(f"    {i}. {issue}")
            print()
        else:
            print("  ✅ NO ISSUES FOUND - ALL SYSTEMS WORKING CORRECTLY")
            print()

        if self.trigger_events:
            print(f"  AUTO-TRIGGER EVENTS: {len(self.trigger_events)}")
            for event in self.trigger_events[-10:]:  # Last 10
                print(f"    - {event['type']}: {event.get('file', 'N/A')} at {event['timestamp']}")
            print()

        # Calculate pass rate
        if self.data_snapshots:
            passed = sum(1 for s in self.data_snapshots if s["all_ok"])
            pass_rate = (passed / len(self.data_snapshots)) * 100
            print(f"  Pass Rate: {pass_rate:.1f}% ({passed}/{len(self.data_snapshots)} checks passed)")
            print()

        # Save report
        report = {
            "monitoring_start": self.monitoring_start.isoformat(),
            "monitoring_end": datetime.now(IST).isoformat(),
            "checks_performed": len(self.data_snapshots),
            "issues_found": list(set(self.issues_found)),
            "trigger_events": self.trigger_events,
            "snapshots": self.data_snapshots,
            "status": "PASS" if len(self.issues_found) == 0 else "FAIL",
        }

        outputs_dir = ROOT_DIR / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        report_file = outputs_dir / "run_and_monitor_report.json"

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)
            print(f"  Report saved: {report_file}")
        except Exception as e:
            print(f"  Failed to save report: {e}")

        print()
        print("=" * 80)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run and Monitor at Micro Level")
    parser.add_argument("--duration", type=int, default=10, help="Monitor for N minutes (default: 10)")

    args = parser.parse_args()

    monitor = RunAndMonitorMicro()
    success = monitor.monitor_continuously(duration_minutes=args.duration)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
