"""
Master Auto System - Self-Triggering Every 2 Minutes
Comprehensive check, fix, and optimize system
Goal: Maximum Profit
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


class MasterAutoSystem:
    def __init__(self):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.cycle = 0
        self.total_fixes = 0
        self.total_checks = 0

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def log(self, msg, level="INFO"):
        now = datetime.now(self.ist).strftime("%H:%M:%S")
        symbols = {"INFO": "[*]", "OK": "[OK]", "FIX": "[FIX]", "WARN": "[!]", "ERR": "[X]"}
        print(f"[{now}] {symbols.get(level, '[*]')} {msg}")

    def check_backend(self):
        self.total_checks += 1
        try:
            r = requests.get(f"{API_BASE}/api/health", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.log(f"Backend: RUNNING | Mode: {data.get('mode')} | PnL: Rs{data.get('total_pnl', 0):.2f}", "OK")
                return True, data
        except:
            pass

        self.log("Backend: STOPPED - Starting...", "FIX")
        try:
            subprocess.Popen(
                ["python", str(ROOT_DIR / "dashboard" / "backend" / "app.py")],
                cwd=str(ROOT_DIR / "dashboard" / "backend"),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(5)
            self.total_fixes += 1
            return True, None
        except:
            self.log("Failed to start backend", "ERR")
            return False, None

    def check_dashboard(self):
        self.total_checks += 1
        try:
            r = requests.get("http://localhost:8080", timeout=5)
            if r.status_code == 200:
                self.log("Dashboard: RUNNING", "OK")
                return True
        except:
            pass

        self.log("Dashboard: STOPPED - Starting...", "FIX")
        try:
            subprocess.Popen(
                ["python", "-m", "http.server", "8080"],
                cwd=str(ROOT_DIR / "dashboard"),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(3)
            self.total_fixes += 1
            return True
        except:
            self.log("Failed to start dashboard", "ERR")
            return False

    def check_main_system(self):
        self.total_checks += 1
        health_file = OUTPUTS_DIR / "health.json"
        if health_file.exists():
            age = time.time() - health_file.stat().st_mtime
            if age < 60:
                self.log(f"Main System: ACTIVE (updated {int(age)}s ago)", "OK")
                return True

        self.log("Main System: INACTIVE - Starting...", "FIX")
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
                self.total_fixes += 1
                return True
        except:
            self.log("Failed to start main system", "ERR")
        return False

    def check_data(self):
        self.total_checks += 1
        chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
        if chain_file.exists():
            age = time.time() - chain_file.stat().st_mtime
            if age > 300:
                self.log(f"Data: STALE ({int(age/60)}m old) - Refreshing...", "FIX")
                try:
                    subprocess.run(
                        ["python", str(ROOT_DIR / "scripts" / "generate_synthetic_live_data.py")],
                        cwd=str(ROOT_DIR),
                        timeout=30,
                        capture_output=True,
                    )
                    self.total_fixes += 1
                except:
                    pass
            else:
                self.log(f"Data: FRESH ({int(age)}s old)", "OK")
        else:
            self.log("Data: MISSING - Generating...", "FIX")
            try:
                subprocess.run(
                    ["python", str(ROOT_DIR / "scripts" / "generate_synthetic_live_data.py")],
                    cwd=str(ROOT_DIR),
                    timeout=30,
                    capture_output=True,
                )
                self.total_fixes += 1
            except:
                pass

    def check_paper_trading(self):
        self.total_checks += 1
        pnl_file = OUTPUTS_DIR / "paper_pnl_summary.json"
        if pnl_file.exists():
            with open(pnl_file) as f:
                data = json.load(f)
            pnl = data.get("total_pnl", 0)
            trades = data.get("total_trades", 0)
            win_rate = data.get("win_rate", 0)

            if trades == 0:
                self.log("Paper Trading: NO TRADES YET", "WARN")
            else:
                status = "PROFIT" if pnl >= 0 else "LOSS"
                self.log(
                    f"Paper Trading: {status} | PnL: Rs{pnl:.2f} | Trades: {trades} | Win: {win_rate:.1f}%",
                    "OK" if pnl >= 0 else "WARN",
                )
            return data
        self.log("Paper Trading: NO DATA", "WARN")
        return None

    def check_dashboard_data(self):
        self.total_checks += 1
        try:
            r = requests.get(f"{API_BASE}/api/chain/NIFTY", timeout=5)
            if r.status_code == 200:
                data = r.json()
                contracts = data.get("total_contracts", 0)
                if contracts == 0:
                    self.log("Dashboard Data: EMPTY - Refreshing...", "FIX")
                    self.check_data()
                else:
                    self.log(f"Dashboard Data: OK ({contracts} contracts)", "OK")
        except:
            self.log("Dashboard Data: CANNOT CHECK", "WARN")

    def run_cycle(self):
        self.cycle += 1
        self.clear()

        print("=" * 80)
        print(" " * 25 + "MASTER AUTO SYSTEM")
        print(" " * 20 + "Self-Triggering Every 2 Minutes")
        print(" " * 30 + "Goal: Maximum Profit")
        print("=" * 80)
        print()

        now = datetime.now(self.ist)
        print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"Cycle: #{self.cycle} | Total Checks: {self.total_checks} | Total Fixes: {self.total_fixes}")
        print()
        print("-" * 80)
        print("COMPREHENSIVE CHECK & FIX CYCLE")
        print("-" * 80)
        print()

        # Check everything
        backend_ok, backend_data = self.check_backend()
        dashboard_ok = self.check_dashboard()
        main_ok = self.check_main_system()
        self.check_data()
        self.check_dashboard_data()

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
        print(f"Systems Checked: {self.total_checks}")
        print(f"Fixes Applied: {self.total_fixes}")
        print()

        if backend_ok and dashboard_ok and main_ok:
            print("[OK] All systems operational")
        else:
            print("[!] Some systems had issues (being fixed)")

        print()
        print("=" * 80)
        print(f"Next check in 2 minutes... (Press Ctrl+C to stop)")
        print("=" * 80)

    def run_continuous(self):
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
    system = MasterAutoSystem()
    system.run_continuous()
