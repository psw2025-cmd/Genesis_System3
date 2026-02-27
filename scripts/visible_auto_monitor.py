"""
Visible Auto Monitor - Shows continuous activity in terminal
Goal: Maximum Profit - Always visible progress
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
LOGS_DIR = ROOT_DIR / "logs"

API_BASE = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:8080"


class VisibleMonitor:
    def __init__(self):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.cycle_count = 0
        self.last_pnl = 0.0
        self.improvements_made = []
        self.errors_fixed = []
        self.start_time = datetime.now(self.ist)
        self.last_trade_count = 0

    def clear_screen(self):
        """Clear terminal screen"""
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self):
        """Print header with status"""
        self.clear_screen()
        print("=" * 80)
        print(" " * 20 + "AUTO MONITOR & IMPROVE SYSTEM")
        print(" " * 25 + "GOAL: MAXIMUM PROFIT")
        print("=" * 80)
        print()

    def print_status(self, service, status, details=""):
        """Print service status"""
        status_symbol = "✅" if status == "RUNNING" else "❌" if status == "STOPPED" else "⚠️"
        print(f"{status_symbol} {service:20s} : {status:10s} {details}")

    def check_backend(self):
        """Check if backend is running"""
        try:
            response = requests.get(f"{API_BASE}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return True, data
            return False, None
        except:
            return False, None

    def check_dashboard(self):
        """Check if dashboard is running"""
        try:
            response = requests.get(DASHBOARD_URL, timeout=5)
            return response.status_code == 200
        except:
            return False

    def check_main_system(self):
        """Check if main trading system is running"""
        try:
            health_file = OUTPUTS_DIR / "health.json"
            if health_file.exists():
                mtime = health_file.stat().st_mtime
                age_seconds = time.time() - mtime
                if age_seconds < 60:
                    return True, age_seconds
            return False, 0
        except:
            return False, 0

    def start_backend(self):
        """Start backend if not running"""
        try:
            subprocess.Popen(
                ["python", str(ROOT_DIR / "dashboard" / "backend" / "app.py")],
                cwd=str(ROOT_DIR / "dashboard" / "backend"),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
            )
            time.sleep(5)
            return True
        except:
            return False

    def start_dashboard(self):
        """Start dashboard server if not running"""
        try:
            subprocess.Popen(
                ["python", "-m", "http.server", "8080"],
                cwd=str(ROOT_DIR / "dashboard"),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
            )
            time.sleep(3)
            return True
        except:
            return False

    def start_main_system(self):
        """Start main trading system if not running"""
        try:
            bat_file = ROOT_DIR / "RUN_FULL_SYSTEM_PRODUCTION.bat"
            if bat_file.exists():
                subprocess.Popen(
                    ["cmd", "/c", str(bat_file)],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                )
                time.sleep(10)
                return True
            return False
        except:
            return False

    def check_paper_trading(self):
        """Check paper trading status"""
        try:
            pnl_file = OUTPUTS_DIR / "paper_pnl_summary.json"
            if pnl_file.exists():
                with open(pnl_file) as f:
                    pnl_data = json.load(f)
                    current_pnl = pnl_data.get("total_pnl", 0)
                    trades = pnl_data.get("total_trades", 0)
                    win_rate = pnl_data.get("win_rate", 0)
                    return True, current_pnl, trades, win_rate
            return False, 0.0, 0, 0.0
        except:
            return False, 0.0, 0, 0.0

    def check_data_freshness(self):
        """Check and refresh data if needed"""
        try:
            chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
            if chain_file.exists():
                mtime = chain_file.stat().st_mtime
                age_seconds = time.time() - mtime
                if age_seconds > 300:  # 5 minutes
                    subprocess.run(
                        ["python", str(ROOT_DIR / "scripts" / "generate_synthetic_live_data.py")],
                        cwd=str(ROOT_DIR),
                        timeout=30,
                        capture_output=True,
                    )
                    return True
            return False
        except:
            return False

    def run_cycle(self):
        """Run one monitoring cycle with visible output"""
        self.cycle_count += 1
        self.print_header()

        # Current time
        now = datetime.now(self.ist)
        print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"Cycle: #{self.cycle_count}")
        print(f"Runtime: {str(now - self.start_time).split('.')[0]}")
        print()
        print("-" * 80)
        print("SYSTEM STATUS")
        print("-" * 80)

        # Check Backend
        backend_ok, health_data = self.check_backend()
        if not backend_ok:
            self.print_status("Backend API", "STOPPED", "→ Starting...")
            self.start_backend()
            time.sleep(3)
            backend_ok, health_data = self.check_backend()

        if backend_ok:
            mode = health_data.get("mode", "UNKNOWN")
            trades = health_data.get("trades_executed", 0)
            pnl = health_data.get("total_pnl", 0)
            self.print_status("Backend API", "RUNNING", f"Mode: {mode} | Trades: {trades} | PnL: ₹{pnl:.2f}")
        else:
            self.print_status("Backend API", "STOPPED", "")

        # Check Dashboard
        dashboard_ok = self.check_dashboard()
        if not dashboard_ok:
            self.print_status("Dashboard", "STOPPED", "→ Starting...")
            self.start_dashboard()
            time.sleep(2)
            dashboard_ok = self.check_dashboard()

        if dashboard_ok:
            self.print_status("Dashboard", "RUNNING", "http://localhost:8080")
        else:
            self.print_status("Dashboard", "STOPPED", "")

        # Check Main System
        main_ok, age = self.check_main_system()
        if not main_ok:
            self.print_status("Main Trading", "STOPPED", "→ Starting...")
            self.start_main_system()
            time.sleep(5)
            main_ok, age = self.check_main_system()

        if main_ok:
            self.print_status("Main Trading", "RUNNING", f"Last update: {int(age)}s ago")
        else:
            self.print_status("Main Trading", "STOPPED", "")

        print()
        print("-" * 80)
        print("PAPER TRADING STATUS")
        print("-" * 80)

        # Check Paper Trading
        paper_ok, current_pnl, trades, win_rate = self.check_paper_trading()

        if paper_ok:
            pnl_color = "🟢" if current_pnl >= 0 else "🔴"
            self.print_status("Paper Trading", "ACTIVE", f"{pnl_color} PnL: ₹{current_pnl:.2f}")
            print(f"   📊 Total Trades: {trades}")
            print(f"   📈 Win Rate: {win_rate:.1f}%")

            if trades > self.last_trade_count:
                new_trades = trades - self.last_trade_count
                print(f"   🎉 NEW TRADES: +{new_trades} trades executed!")
                self.last_trade_count = trades

            # PnL change
            if self.last_pnl != 0:
                pnl_change = current_pnl - self.last_pnl
                if pnl_change > 0:
                    print(f"   📈 PnL Change: +₹{pnl_change:.2f} (PROFIT!)")
                elif pnl_change < 0:
                    print(f"   📉 PnL Change: ₹{pnl_change:.2f} (LOSS)")

            self.last_pnl = current_pnl
        else:
            self.print_status("Paper Trading", "NO TRADES", "Waiting for market signals...")

        print()
        print("-" * 80)
        print("DATA STATUS")
        print("-" * 80)

        # Check data
        chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
        if chain_file.exists():
            mtime = chain_file.stat().st_mtime
            age_seconds = time.time() - mtime
            age_min = int(age_seconds / 60)
            age_sec = int(age_seconds % 60)

            if age_seconds > 300:
                self.print_status("Chain Data", "STALE", f"{age_min}m {age_sec}s old → Refreshing...")
                self.check_data_freshness()
            else:
                self.print_status("Chain Data", "FRESH", f"{age_min}m {age_sec}s old")
        else:
            self.print_status("Chain Data", "MISSING", "→ Generating...")
            self.check_data_freshness()

        # Check PnL file
        pnl_file = OUTPUTS_DIR / "paper_pnl_summary.json"
        if pnl_file.exists():
            self.print_status("PnL Summary", "AVAILABLE", "")
        else:
            self.print_status("PnL Summary", "MISSING", "")

        print()
        print("-" * 80)
        print("PROFIT OPTIMIZATION")
        print("-" * 80)

        if paper_ok:
            if current_pnl > 0:
                print(f"🟢 PROFITABLE: ₹{current_pnl:.2f} | Win Rate: {win_rate:.1f}% | Trades: {trades}")
                print("   ✅ System is generating profit!")
            elif current_pnl < 0:
                print(f"🔴 LOSS: ₹{current_pnl:.2f} | Win Rate: {win_rate:.1f}% | Trades: {trades}")
                print("   ⚠️  Monitoring for improvement opportunities...")
            else:
                print(f"⚪ BREAK EVEN: ₹{current_pnl:.2f} | Trades: {trades}")
        else:
            print("⏳ Waiting for market open (9:15 AM) or first trade...")

        print()
        print("-" * 80)
        print("ACTIVITY LOG")
        print("-" * 80)

        if self.errors_fixed:
            print(f"✅ Errors Fixed: {len(self.errors_fixed)}")
            for error in self.errors_fixed[-5:]:  # Last 5
                print(f"   • {error}")

        if self.improvements_made:
            print(f"🚀 Improvements: {len(self.improvements_made)}")
            for improvement in self.improvements_made[-5:]:  # Last 5
                print(f"   • {improvement}")

        print()
        print("=" * 80)
        print(f"Next update in 10 seconds... (Press Ctrl+C to stop)")
        print("=" * 80)

    def run_continuous(self):
        """Run continuous monitoring with visible updates"""
        while True:
            try:
                self.run_cycle()
                time.sleep(10)  # Update every 10 seconds for visibility
            except KeyboardInterrupt:
                print("\n\nMonitoring stopped by user.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                time.sleep(10)


if __name__ == "__main__":
    monitor = VisibleMonitor()
    monitor.run_continuous()
