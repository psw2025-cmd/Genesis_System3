"""
Continuous Auto Agent - Self-Triggering Every 2 Minutes
Acts as if user is sending "check all and correct" every 2 minutes
"""

import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
import pytz
import os

ROOT_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"

API_BASE = "http://localhost:8000"


class ContinuousAutoAgent:
    def __init__(self):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.cycle = 0
        self.actions_taken = []

    def print_status(self, msg):
        """Print with timestamp"""
        now = datetime.now(self.ist).strftime("%H:%M:%S")
        print(f"[{now}] {msg}")

    def check_and_fix_backend(self):
        """Check backend, start if needed"""
        try:
            r = requests.get(f"{API_BASE}/api/health", timeout=5)
            if r.status_code == 200:
                self.print_status("[OK] Backend running")
                return True
        except:
            pass

        self.print_status("[FIX] Starting backend...")
        try:
            subprocess.Popen(
                ["python", str(ROOT_DIR / "dashboard" / "backend" / "app.py")],
                cwd=str(ROOT_DIR / "dashboard" / "backend"),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(5)
            self.actions_taken.append("Started backend")
            return True
        except:
            return False

    def check_and_fix_dashboard(self):
        """Check dashboard, start if needed (Streamlit 8501 per Run-All, or simple server 8080)."""
        for port in (8501, 8080):
            try:
                r = requests.get(f"http://localhost:{port}", timeout=5)
                if r.status_code == 200:
                    self.print_status(f"[OK] Dashboard running on {port}")
                    return True
            except Exception:
                pass

        self.print_status("[FIX] Starting dashboard...")
        try:
            subprocess.Popen(
                ["python", "-m", "http.server", "8080"],
                cwd=str(ROOT_DIR / "dashboard"),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(3)
            self.actions_taken.append("Started dashboard")
            return True
        except:
            return False

    def check_and_fix_main_system(self):
        """Check main system, start if needed"""
        health_file = OUTPUTS_DIR / "health.json"
        if health_file.exists():
            age = time.time() - health_file.stat().st_mtime
            if age < 60:
                self.print_status("[OK] Main system active")
                return True

        self.print_status("[FIX] Starting main system...")
        try:
            bat_file = ROOT_DIR / "RUN_FULL_SYSTEM_PRODUCTION.bat"
            if bat_file.exists():
                subprocess.Popen(
                    ["cmd", "/c", str(bat_file)],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(10)
                self.actions_taken.append("Started main system")
                return True
        except:
            pass
        return False

    def check_data_freshness(self):
        """Check and refresh data if stale"""
        chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
        if chain_file.exists():
            age = time.time() - chain_file.stat().st_mtime
            if age > 300:  # 5 minutes
                self.print_status("[FIX] Refreshing stale data...")
                try:
                    subprocess.run(
                        ["python", str(ROOT_DIR / "scripts" / "generate_synthetic_live_data.py")],
                        cwd=str(ROOT_DIR),
                        timeout=30,
                        capture_output=True,
                    )
                    self.actions_taken.append("Refreshed chain data")
                except:
                    pass

    def check_paper_trading(self):
        """Check paper trading status"""
        pnl_file = OUTPUTS_DIR / "paper_pnl_summary.json"
        if pnl_file.exists():
            with open(pnl_file) as f:
                data = json.load(f)
            pnl = data.get("total_pnl", 0)
            trades = data.get("total_trades", 0)
            win_rate = data.get("win_rate", 0)

            if trades == 0:
                self.print_status("[WARN] No paper trades executed yet")
            else:
                status = "PROFIT" if pnl >= 0 else "LOSS"
                self.print_status(f"[{status}] PnL: Rs{pnl:.2f} | Trades: {trades} | Win: {win_rate:.1f}%")
            return data
        return None

    def check_dashboard_data(self):
        """Check if dashboard has data"""
        try:
            r = requests.get(f"{API_BASE}/api/chain/NIFTY", timeout=5)
            if r.status_code == 200:
                data = r.json()
                if data.get("total_contracts", 0) == 0:
                    self.print_status("[FIX] Dashboard has no data, refreshing...")
                    self.check_data_freshness()
        except:
            pass

    def run_cycle(self):
        """Run one complete check and fix cycle"""
        self.cycle += 1
        os.system("cls" if os.name == "nt" else "clear")

        print("=" * 80)
        print(" " * 20 + "CONTINUOUS AUTO AGENT")
        print(" " * 25 + "Self-Triggering Every 2 Minutes")
        print(" " * 30 + "Goal: Maximum Profit")
        print("=" * 80)
        print()

        now = datetime.now(self.ist)
        print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"Cycle: #{self.cycle}")
        print()
        print("-" * 80)
        print("CHECKING AND FIXING ALL SYSTEMS...")
        print("-" * 80)
        print()

        self.actions_taken = []

        # Check and fix all systems
        self.check_and_fix_backend()
        self.check_and_fix_dashboard()
        self.check_and_fix_main_system()
        self.check_data_freshness()
        self.check_dashboard_data()

        # Check paper trading
        print()
        print("-" * 80)
        print("PAPER TRADING STATUS")
        print("-" * 80)
        pnl_data = self.check_paper_trading()

        # Summary
        print()
        print("-" * 80)
        print("CYCLE SUMMARY")
        print("-" * 80)
        print(f"Actions Taken: {len(self.actions_taken)}")
        if self.actions_taken:
            for action in self.actions_taken:
                print(f"  [FIXED] {action}")
        else:
            print("  [OK] All systems running, no fixes needed")

        print()
        print("=" * 80)
        print(f"Next check in 2 minutes... (Press Ctrl+C to stop)")
        print("=" * 80)

    def run_continuous(self):
        """Run continuously every 2 minutes"""
        while True:
            try:
                self.run_cycle()
                time.sleep(120)  # 2 minutes
            except KeyboardInterrupt:
                print("\n\nStopped by user.")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}")
                time.sleep(120)


if __name__ == "__main__":
    agent = ContinuousAutoAgent()
    agent.run_continuous()
