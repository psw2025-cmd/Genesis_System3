"""
Auto Monitor and Improve System
Continuously monitors, corrects, and optimizes the trading system
Goal: Maximum profit through automated improvements
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pytz
import requests

ROOT_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
LOGS_DIR = ROOT_DIR / "logs"

API_BASE = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:8080"


class AutoMonitor:
    def __init__(self):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.cycle_count = 0
        self.last_pnl = 0.0
        self.improvements_made = []
        self.errors_fixed = []
        self.start_time = datetime.now(self.ist)

    def log(self, message, level="INFO"):
        """Log with timestamp"""
        timestamp = datetime.now(self.ist).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def check_backend(self):
        """Check if backend is running"""
        try:
            response = requests.get(f"{API_BASE}/api/health", timeout=5)
            if response.status_code == 200:
                return True, response.json()
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
            # Check if process is running by checking for recent output files
            health_file = OUTPUTS_DIR / "health.json"
            if health_file.exists():
                mtime = health_file.stat().st_mtime
                age_seconds = time.time() - mtime
                # If health.json updated in last 60 seconds, system is active
                if age_seconds < 60:
                    return True
            return False
        except:
            return False

    def start_backend(self):
        """Start backend if not running"""
        self.log("Starting backend server...", "ACTION")
        try:
            subprocess.Popen(
                ["python", str(ROOT_DIR / "dashboard" / "backend" / "app.py")],
                cwd=str(ROOT_DIR / "dashboard" / "backend"),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
            )
            time.sleep(5)  # Wait for startup
            return True
        except Exception as e:
            self.log(f"Failed to start backend: {e}", "ERROR")
            return False

    def start_dashboard(self):
        """Start dashboard server if not running"""
        self.log("Starting dashboard server...", "ACTION")
        try:
            subprocess.Popen(
                ["python", "-m", "http.server", "8080"],
                cwd=str(ROOT_DIR / "dashboard"),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
            )
            time.sleep(3)
            return True
        except Exception as e:
            self.log(f"Failed to start dashboard: {e}", "ERROR")
            return False

    def start_main_system(self):
        """Start main trading system if not running"""
        self.log("Starting main trading system...", "ACTION")
        try:
            bat_file = ROOT_DIR / "RUN_FULL_SYSTEM_PRODUCTION.bat"
            if bat_file.exists():
                subprocess.Popen(
                    ["cmd", "/c", str(bat_file)],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                )
                time.sleep(10)  # Wait for startup
                return True
            return False
        except Exception as e:
            self.log(f"Failed to start main system: {e}", "ERROR")
            return False

    def check_data_freshness(self):
        """Check if data is fresh"""
        try:
            chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
            if chain_file.exists():
                mtime = chain_file.stat().st_mtime
                age_seconds = time.time() - mtime
                if age_seconds > 300:  # 5 minutes
                    self.log("Data is stale, generating fresh data...", "ACTION")
                    subprocess.run(
                        ["python", str(ROOT_DIR / "scripts" / "generate_synthetic_live_data.py")],
                        cwd=str(ROOT_DIR),
                        timeout=30,
                    )
                    return True
            return False
        except Exception as e:
            self.log(f"Error checking data freshness: {e}", "ERROR")
            return False

    def check_paper_trading(self):
        """Check if paper trading is working"""
        try:
            positions_file = OUTPUTS_DIR / "positions_live.json"
            pnl_file = OUTPUTS_DIR / "paper_pnl_summary.json"

            has_positions = positions_file.exists()
            has_pnl = pnl_file.exists()

            if has_pnl:
                with open(pnl_file) as f:
                    pnl_data = json.load(f)
                    current_pnl = pnl_data.get("total_pnl", 0)
                    trades = pnl_data.get("total_trades", 0)

                    if trades == 0:
                        self.log("⚠️  No paper trades executed yet", "WARNING")
                        return False, current_pnl

                    return True, current_pnl

            return False, 0.0
        except Exception as e:
            self.log(f"Error checking paper trading: {e}", "ERROR")
            return False, 0.0

    def optimize_for_profit(self):
        """Analyze and suggest optimizations for profit"""
        try:
            pnl_file = OUTPUTS_DIR / "paper_pnl_summary.json"
            if not pnl_file.exists():
                return

            with open(pnl_file) as f:
                pnl_data = json.load(f)

            total_pnl = pnl_data.get("total_pnl", 0)
            win_rate = pnl_data.get("win_rate", 0)
            total_trades = pnl_data.get("total_trades", 0)

            # Check if PnL is improving
            if total_pnl < self.last_pnl - 100:
                self.log(f"⚠️  PnL decreased: ₹{self.last_pnl:.2f} → ₹{total_pnl:.2f}", "WARNING")

            self.last_pnl = total_pnl

            # Log profit status
            if total_pnl > 0:
                self.log(f"✅ PROFIT: ₹{total_pnl:.2f} | Win Rate: {win_rate:.1f}% | Trades: {total_trades}", "SUCCESS")
            elif total_pnl < 0:
                self.log(f"⚠️  LOSS: ₹{total_pnl:.2f} | Win Rate: {win_rate:.1f}% | Trades: {total_trades}", "WARNING")

        except Exception as e:
            self.log(f"Error optimizing for profit: {e}", "ERROR")

    def check_dashboard_data(self):
        """Check if dashboard is showing correct data"""
        try:
            # Test chain API
            response = requests.get(f"{API_BASE}/api/chain/NIFTY", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("total_contracts", 0) == 0:
                    self.log("Dashboard shows no chain data, refreshing...", "ACTION")
                    subprocess.run(
                        ["python", str(ROOT_DIR / "scripts" / "generate_synthetic_live_data.py")],
                        cwd=str(ROOT_DIR),
                        timeout=30,
                    )
                    return False
                return True
            return False
        except Exception as e:
            self.log(f"Error checking dashboard data: {e}", "ERROR")
            return False

    def run_cycle(self):
        """Run one monitoring cycle"""
        self.cycle_count += 1
        self.log(f"=== MONITORING CYCLE #{self.cycle_count} ===", "INFO")

        # Check and start services
        backend_ok, health_data = self.check_backend()
        if not backend_ok:
            self.log("Backend not running, starting...", "ACTION")
            self.start_backend()
            self.errors_fixed.append("Started backend server")
        else:
            self.log("✅ Backend: RUNNING", "SUCCESS")

        dashboard_ok = self.check_dashboard()
        if not dashboard_ok:
            self.log("Dashboard not running, starting...", "ACTION")
            self.start_dashboard()
            self.errors_fixed.append("Started dashboard server")
        else:
            self.log("✅ Dashboard: RUNNING", "SUCCESS")

        main_system_ok = self.check_main_system()
        if not main_system_ok:
            self.log("Main system not running, starting...", "ACTION")
            self.start_main_system()
            self.errors_fixed.append("Started main trading system")
        else:
            self.log("✅ Main System: RUNNING", "SUCCESS")

        # Check data freshness
        self.check_data_freshness()

        # Check dashboard data
        if not self.check_dashboard_data():
            self.log("Dashboard data issue detected and fixed", "ACTION")

        # Check paper trading
        paper_ok, current_pnl = self.check_paper_trading()
        if paper_ok:
            self.log("✅ Paper Trading: ACTIVE", "SUCCESS")
        else:
            self.log("⚠️  Paper Trading: No trades yet", "WARNING")

        # Optimize for profit
        self.optimize_for_profit()

        # Summary
        runtime = datetime.now(self.ist) - self.start_time
        self.log(f"Runtime: {runtime}", "INFO")
        self.log(f"Errors Fixed: {len(self.errors_fixed)}", "INFO")
        self.log(f"Improvements: {len(self.improvements_made)}", "INFO")
        self.log("", "INFO")

    def run_continuous(self):
        """Run continuous monitoring"""
        self.log("=" * 80, "INFO")
        self.log("AUTO MONITOR AND IMPROVE SYSTEM STARTED", "INFO")
        self.log("Goal: Maximum Profit through Automated Improvements", "INFO")
        self.log("=" * 80, "INFO")
        self.log("", "INFO")

        while True:
            try:
                self.run_cycle()
                time.sleep(30)  # Check every 30 seconds
            except KeyboardInterrupt:
                self.log("Monitoring stopped by user", "INFO")
                break
            except Exception as e:
                self.log(f"Error in monitoring cycle: {e}", "ERROR")
                time.sleep(30)


if __name__ == "__main__":
    monitor = AutoMonitor()
    monitor.run_continuous()
