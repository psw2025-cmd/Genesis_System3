"""
Micro-Level Monitor - Monitors everything at ultra-fine detail
Checks all components, data flow, auto-triggers, and provides proof
"""

import json
import sys
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
from src.utils.market_hours import get_market_status, is_market_open

IST = pytz.timezone("Asia/Kolkata")


class MicroLevelMonitor:
    """Ultra-fine monitoring of all system components."""

    def __init__(self):
        self.monitoring_start = datetime.now(IST)
        self.checks_performed = 0
        self.warnings_found = []
        self.errors_found = []
        self.data_snapshots = []
        self.trigger_events = []

    def check_file_exists_and_fresh(self, filepath: Path, max_age_seconds: int = 60) -> Dict:
        """Check if file exists and is fresh."""
        result = {
            "file": str(filepath),
            "exists": False,
            "fresh": False,
            "age_seconds": None,
            "size_bytes": 0,
            "status": "MISSING",
        }

        if filepath.exists():
            result["exists"] = True
            result["size_bytes"] = filepath.stat().st_size

            age = datetime.now().timestamp() - filepath.stat().st_mtime
            result["age_seconds"] = round(age, 2)

            if age <= max_age_seconds:
                result["fresh"] = True
                result["status"] = "FRESH"
            else:
                result["status"] = "STALE"
        else:
            result["status"] = "MISSING"

        return result

    def check_data_files(self) -> Dict:
        """Check all critical data files."""
        print("[MICRO CHECK] Data Files...")

        outputs_dir = ROOT_DIR / "outputs"
        outputs_dir.mkdir(exist_ok=True)

        files_to_check = {
            "chain_raw_live.csv": 60,  # Should update every 5s, max 60s old
            "pnl_live.json": 60,
            "positions_live.json": 60,
            "paper_trades_live.csv": 300,  # Can be older if no trades
            "top_trade_signal.json": 60,
            "qc_report_live.json": 60,
            "underlying_rank_live.csv": 60,
            "market_status.json": 60,
        }

        results = {}
        all_ok = True

        for filename, max_age in files_to_check.items():
            filepath = outputs_dir / filename
            check_result = self.check_file_exists_and_fresh(filepath, max_age)
            results[filename] = check_result

            if check_result["status"] == "MISSING":
                print(f"  ⚠️  {filename}: MISSING")
                self.warnings_found.append(f"{filename} is missing")
                all_ok = False
            elif check_result["status"] == "STALE":
                print(f"  ⚠️  {filename}: STALE ({check_result['age_seconds']}s old)")
                self.warnings_found.append(f"{filename} is stale ({check_result['age_seconds']}s old)")
                all_ok = False
            else:
                print(
                    f"  ✅ {filename}: FRESH ({check_result['age_seconds']}s old, {check_result['size_bytes']} bytes)"
                )

        return {"all_ok": all_ok, "results": results, "files_checked": len(files_to_check)}

    def check_data_content(self) -> Dict:
        """Check data content for correctness."""
        print("[MICRO CHECK] Data Content...")

        outputs_dir = ROOT_DIR / "outputs"
        issues = []

        # Check PnL file
        pnl_file = outputs_dir / "pnl_live.json"
        if pnl_file.exists():
            try:
                with open(pnl_file, "r", encoding="utf-8") as f:
                    pnl_data = json.load(f)

                required_fields = ["total_pnl", "total_trades", "win_rate", "open_positions"]
                missing = [f for f in required_fields if f not in pnl_data]

                if missing:
                    issues.append(f"PnL file missing fields: {missing}")
                    print(f"  ⚠️  PnL file missing fields: {missing}")
                else:
                    print(f"  ✅ PnL file: All required fields present")
                    print(f"     Total PnL: Rs {pnl_data.get('total_pnl', 0):.2f}")
                    print(f"     Total Trades: {pnl_data.get('total_trades', 0)}")
                    print(f"     Win Rate: {pnl_data.get('win_rate', 0):.1f}%")
            except Exception as e:
                issues.append(f"PnL file error: {e}")
                print(f"  ❌ PnL file error: {e}")

        # Check positions file
        positions_file = outputs_dir / "positions_live.json"
        if positions_file.exists():
            try:
                with open(positions_file, "r", encoding="utf-8") as f:
                    pos_data = json.load(f)

                if "open_positions" not in pos_data:
                    issues.append("Positions file missing 'open_positions' field")
                    print(f"  ⚠️  Positions file structure issue")
                else:
                    open_count = len(pos_data.get("open_positions", []))
                    print(f"  ✅ Positions file: {open_count} open positions")
            except Exception as e:
                issues.append(f"Positions file error: {e}")
                print(f"  ❌ Positions file error: {e}")

        # Check chain data
        chain_file = outputs_dir / "chain_raw_live.csv"
        if chain_file.exists():
            try:
                df = pd.read_csv(chain_file, nrows=5)  # Just check structure
                required_cols = ["underlying", "strike", "option_type", "ltp"]
                missing_cols = [c for c in required_cols if c not in df.columns]

                if missing_cols:
                    issues.append(f"Chain file missing columns: {missing_cols}")
                    print(f"  ⚠️  Chain file missing columns: {missing_cols}")
                else:
                    print(f"  ✅ Chain file: Structure correct")
            except Exception as e:
                issues.append(f"Chain file error: {e}")
                print(f"  ❌ Chain file error: {e}")

        return {"all_ok": len(issues) == 0, "issues": issues}

    def check_auto_triggers(self) -> Dict:
        """Check if auto-triggers are working."""
        print("[MICRO CHECK] Auto-Triggers...")

        outputs_dir = ROOT_DIR / "outputs"
        triggers_ok = True

        # Check if data is updating (auto-trigger indicator)
        chain_file = outputs_dir / "chain_raw_live.csv"
        if chain_file.exists():
            # Get file modification times
            mtime1 = chain_file.stat().st_mtime
            time.sleep(6)  # Wait 6 seconds
            if chain_file.exists():
                mtime2 = chain_file.stat().st_mtime

                if mtime2 > mtime1:
                    print(f"  ✅ Data auto-updating: File updated ({mtime2 - mtime1:.1f}s)")
                    self.trigger_events.append(
                        {
                            "type": "DATA_UPDATE",
                            "timestamp": datetime.now(IST).isoformat(),
                            "file": "chain_raw_live.csv",
                        }
                    )
                else:
                    print(f"  ⚠️  Data not auto-updating: File not changed")
                    self.warnings_found.append("Data file not auto-updating")
                    triggers_ok = False
            else:
                print(f"  ⚠️  Data file disappeared")
                triggers_ok = False
        else:
            print(f"  ⚠️  Data file not found")
            triggers_ok = False

        # Check market status auto-detection
        now = datetime.now(IST)
        is_open, reason = is_market_open(now)
        print(f"  ✅ Market detection: {'OPEN' if is_open else 'CLOSED'} - {reason}")

        return {"all_ok": triggers_ok, "data_updating": triggers_ok, "market_detection": True}

    def check_components(self) -> Dict:
        """Check all system components."""
        print("[MICRO CHECK] System Components...")

        components_ok = True

        # Check imports
        try:
            from src.trading.paper_executor import PaperExecutor

            executor = PaperExecutor()
            summary = executor.get_positions_summary()
            print(f"  ✅ Paper Executor: Working")
        except Exception as e:
            print(f"  ❌ Paper Executor: {e}")
            self.errors_found.append(f"Paper Executor: {e}")
            components_ok = False

        try:
            from src.trading.pnl_tracker import PnLTracker

            tracker = PnLTracker()
            print(f"  ✅ PnL Tracker: Working")
        except Exception as e:
            print(f"  ❌ PnL Tracker: {e}")
            self.errors_found.append(f"PnL Tracker: {e}")
            components_ok = False

        try:
            from src.storage.trade_history import TradeHistoryStore

            store = TradeHistoryStore()
            print(f"  ✅ Trade History: Working")
        except Exception as e:
            print(f"  ❌ Trade History: {e}")
            self.errors_found.append(f"Trade History: {e}")
            components_ok = False

        return {"all_ok": components_ok}

    def monitor_continuously(self, duration_minutes: int = 5, check_interval: int = 10):
        """Monitor continuously and check for issues."""
        print("=" * 80)
        print("  MICRO-LEVEL CONTINUOUS MONITORING")
        print("=" * 80)
        print()
        print(f"Monitoring Duration: {duration_minutes} minutes")
        print(f"Check Interval: {check_interval} seconds")
        print()
        print("Monitoring all components, data flow, and auto-triggers...")
        print()

        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        check_count = 0

        while datetime.now() < end_time:
            check_count += 1
            self.checks_performed += 1

            now = datetime.now(IST)
            print(f"[CHECK {check_count}] {now.strftime('%H:%M:%S IST')}")
            print("-" * 80)

            # Check data files
            file_check = self.check_data_files()
            print()

            # Check data content
            content_check = self.check_data_content()
            print()

            # Check auto-triggers
            trigger_check = self.check_auto_triggers()
            print()

            # Check components
            component_check = self.check_components()
            print()

            # Summary for this check
            all_ok = (
                file_check["all_ok"]
                and content_check["all_ok"]
                and trigger_check["all_ok"]
                and component_check["all_ok"]
            )

            if all_ok:
                print(f"  ✅ ALL CHECKS PASSED")
            else:
                print(f"  ⚠️  SOME ISSUES FOUND")

            print()
            print("=" * 80)
            print()

            # Wait for next check
            if datetime.now() < end_time:
                time.sleep(check_interval)

        # Final summary
        self.print_final_summary()

    def print_final_summary(self):
        """Print final monitoring summary."""
        print("=" * 80)
        print("  MONITORING SUMMARY")
        print("=" * 80)
        print()
        print(f"  Checks Performed: {self.checks_performed}")
        print(f"  Warnings Found: {len(self.warnings_found)}")
        print(f"  Errors Found: {len(self.errors_found)}")
        print(f"  Trigger Events: {len(self.trigger_events)}")
        print()

        if self.warnings_found:
            print("  WARNINGS:")
            for i, warning in enumerate(self.warnings_found[:10], 1):
                print(f"    {i}. {warning}")
            print()

        if self.errors_found:
            print("  ERRORS:")
            for i, error in enumerate(self.errors_found[:10], 1):
                print(f"    {i}. {error}")
            print()

        if len(self.warnings_found) == 0 and len(self.errors_found) == 0:
            print("  ✅ NO WARNINGS OR ERRORS FOUND")
            print("  ✅ ALL SYSTEMS WORKING CORRECTLY")
        else:
            print(f"  ⚠️  {len(self.warnings_found)} WARNINGS, {len(self.errors_found)} ERRORS")

        print()
        print("=" * 80)

        # Save monitoring report
        report = {
            "monitoring_start": self.monitoring_start.isoformat(),
            "monitoring_end": datetime.now(IST).isoformat(),
            "checks_performed": self.checks_performed,
            "warnings": self.warnings_found,
            "errors": self.errors_found,
            "trigger_events": self.trigger_events,
            "status": "PASS" if (len(self.warnings_found) == 0 and len(self.errors_found) == 0) else "FAIL",
        }

        outputs_dir = ROOT_DIR / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        report_file = outputs_dir / "micro_monitoring_report.json"

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)
            print(f"  Report saved: {report_file}")
        except Exception as e:
            print(f"  Failed to save report: {e}")


def main():
    """Run micro-level monitoring."""
    import argparse

    parser = argparse.ArgumentParser(description="Micro-Level Monitor")
    parser.add_argument("--duration", type=int, default=5, help="Monitor for N minutes (default: 5)")
    parser.add_argument("--interval", type=int, default=10, help="Check interval in seconds (default: 10)")

    args = parser.parse_args()

    monitor = MicroLevelMonitor()
    monitor.monitor_continuously(duration_minutes=args.duration, check_interval=args.interval)

    return 0 if (len(monitor.warnings_found) == 0 and len(monitor.errors_found) == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
