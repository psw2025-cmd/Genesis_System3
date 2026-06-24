"""
Combined Auto System - FIXED VERSION
Checks, fixes, verifies against online, and optimizes
Goal: Maximum Profit
FIXED: Data correction with backup and safety checks
"""

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pytz
import requests

ROOT_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"

API_BASE = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:8080"


class CombinedAutoSystem:
    def __init__(self):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.cycle = 0
        self.total_fixes = 0
        self.total_verifications = 0

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def log(self, msg, level="INFO"):
        now = datetime.now(self.ist).strftime("%H:%M:%S")
        symbols = {"INFO": "[*]", "OK": "[OK]", "FIX": "[FIX]", "WARN": "[!]", "ERR": "[X]", "VERIFY": "[VERIFY]"}
        print(f"[{now}] {symbols.get(level, '[*]')} {msg}")

    def check_and_fix_backend(self):
        try:
            r = requests.get(f"{API_BASE}/api/health", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.log(f"Backend: RUNNING | PnL: Rs{data.get('total_pnl', 0):.2f}", "OK")
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
            return False, None

    def check_and_fix_dashboard(self):
        try:
            r = requests.get(DASHBOARD_URL, timeout=5)
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
            return False

    def get_online_price_yahoo(self, underlying):
        """Get price from Yahoo Finance"""
        try:
            url_map = {
                "NIFTY": "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=1d",
                "BANKNIFTY": "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEBANK?interval=1d",
            }
            url = url_map.get(underlying)
            if not url:
                return None

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if "chart" in data and "result" in data["chart"]:
                    result = data["chart"]["result"]
                    if result:
                        price = result[0].get("meta", {}).get("regularMarketPrice")
                        if price:
                            return float(price)
        except Exception as e:
            self.log(f"Yahoo fetch error for {underlying}: {str(e)}", "ERR")
        return None

    def get_online_price_nse(self, underlying):
        """Get price from NSE (alternative source)"""
        try:
            # NSE API endpoint (if available)
            # This is a placeholder - actual NSE API may require different endpoints
            symbol_map = {"NIFTY": "NIFTY 50", "BANKNIFTY": "NIFTY BANK"}
            # For now, return None - can be implemented if NSE API is available
            return None
        except:
            return None

    def verify_online_price(self, underlying):
        """Verify spot price from online - try multiple sources"""
        self.total_verifications += 1

        # Try Yahoo first
        price_yahoo = self.get_online_price_yahoo(underlying)
        if price_yahoo:
            self.log(f"{underlying} Yahoo Price: Rs{price_yahoo:.2f}", "VERIFY")
            return price_yahoo

        # Try NSE as backup
        price_nse = self.get_online_price_nse(underlying)
        if price_nse:
            self.log(f"{underlying} NSE Price: Rs{price_nse:.2f}", "VERIFY")
            return price_nse

        return None

    def backup_chain_file(self, chain_file):
        """Create timestamped backup of chain file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = chain_file.parent / f"{chain_file.name}.bak_{timestamp}"
            shutil.copy2(chain_file, backup_file)
            return backup_file
        except Exception as e:
            self.log(f"Backup failed: {str(e)}", "WARN")
            return None

    def correct_spot_price_in_chain(self, underlying, correct_price, dashboard_spot):
        """Correct spot price in chain_raw_live.csv with backup and logging"""
        try:
            chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
            if not chain_file.exists():
                self.log(f"Chain file not found: {chain_file}", "WARN")
                return False

            # Create backup before modification
            backup_file = self.backup_chain_file(chain_file)
            if backup_file:
                self.log(f"Backup created: {backup_file.name}", "INFO")

            # Calculate difference
            diff = abs(correct_price - dashboard_spot)
            diff_pct = (diff / correct_price) * 100 if correct_price > 0 else 0

            # Log the correction
            self.log(
                f"Correcting {underlying}: Rs{dashboard_spot:.2f} -> Rs{correct_price:.2f} (diff: {diff_pct:.2f}%)",
                "FIX",
            )

            # Read and update CSV
            import csv

            rows = []
            fieldnames = None

            with open(chain_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    # Skip status rows
                    if "status" in str(row.get("strike", "")).lower() or "market" in str(row.get("strike", "")).lower():
                        rows.append(row)
                        continue

                    # Update spot price for matching underlying
                    row_underlying = row.get("underlying", "").upper()
                    if row_underlying == underlying.upper():
                        old_spot = row.get("spot_price", "0")
                        row["spot_price"] = str(correct_price)
                        # Log individual row updates (first few only)
                        if len([r for r in rows if r.get("underlying", "").upper() == underlying.upper()]) < 3:
                            self.log(f"  Updated row: spot_price {old_spot} -> {correct_price}", "INFO")
                    rows.append(row)

            # Write back
            if rows and fieldnames:
                with open(chain_file, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)

                # Log summary
                updated_count = len([r for r in rows if r.get("underlying", "").upper() == underlying.upper()])
                self.log(f"{underlying} CORRECTED: {updated_count} rows updated", "OK")
                return True
        except Exception as e:
            self.log(f"Error correcting spot price: {str(e)}", "ERR")
        return False

    def verify_dashboard_data(self):
        """Verify dashboard data against online sources"""
        self.log("Verifying dashboard data against online sources...", "VERIFY")

        underlyings = ["NIFTY", "BANKNIFTY"]
        verified = 0
        corrected = 0

        for underlying in underlyings:
            try:
                # Get dashboard data
                r = requests.get(f"{API_BASE}/api/chain/{underlying}", timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    dashboard_spot = data.get("spot", 0)

                    if dashboard_spot > 0:
                        # Get online price
                        online_spot = self.verify_online_price(underlying)

                        if online_spot:
                            diff = abs(dashboard_spot - online_spot)
                            diff_pct = (diff / online_spot) * 100 if online_spot > 0 else 0

                            if diff_pct > 1.0:
                                self.log(
                                    f"{underlying} DISCREPANCY: Dashboard Rs{dashboard_spot:.2f} vs Online Rs{online_spot:.2f} ({diff_pct:.2f}%)",
                                    "WARN",
                                )
                                # Auto-correct with backup
                                if self.correct_spot_price_in_chain(underlying, online_spot, dashboard_spot):
                                    corrected += 1
                                    self.total_fixes += 1
                            else:
                                self.log(f"{underlying} VERIFIED: Rs{dashboard_spot:.2f} matches online", "OK")
                                verified += 1
                        else:
                            self.log(f"{underlying} Online price unavailable - skipping correction", "WARN")
            except Exception as e:
                self.log(f"Error verifying {underlying}: {str(e)}", "ERR")

        if corrected > 0:
            self.log(f"Corrected {corrected} spot price(s) from online sources", "FIX")

        return verified

    def check_paper_trading(self):
        pnl_file = OUTPUTS_DIR / "paper_pnl_summary.json"
        if pnl_file.exists():
            with open(pnl_file) as f:
                data = json.load(f)
            pnl = data.get("total_pnl", 0)
            trades = data.get("total_trades", 0)
            win_rate = data.get("win_rate", 0)
            open_positions = data.get("open_positions", 0)

            if trades == 0:
                self.log("Paper Trading: NO TRADES YET", "WARN")
            else:
                status = "PROFIT" if pnl >= 0 else "LOSS"
                self.log(
                    f"Paper Trading: {status} | PnL: Rs{pnl:.2f} | Trades: {trades} | Win: {win_rate:.1f}% | Open: {open_positions}",
                    "OK" if pnl >= 0 else "WARN",
                )
            return data
        return None

    def run_cycle(self):
        self.cycle += 1
        self.clear()

        print("=" * 80)
        print(" " * 25 + "COMBINED AUTO SYSTEM")
        print(" " * 20 + "Check, Fix, Verify Online, Optimize")
        print(" " * 30 + "Goal: Maximum Profit")
        print("=" * 80)
        print()

        now = datetime.now(self.ist)
        print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"Cycle: #{self.cycle} | Fixes: {self.total_fixes} | Verifications: {self.total_verifications}")
        print()

        print("-" * 80)
        print("SYSTEM CHECKS")
        print("-" * 80)
        print()
        backend_ok, backend_data = self.check_and_fix_backend()
        dashboard_ok = self.check_and_fix_dashboard()
        print()

        print("-" * 80)
        print("ONLINE VERIFICATION")
        print("-" * 80)
        print()
        verified = self.verify_dashboard_data()
        print()

        print("-" * 80)
        print("PAPER TRADING")
        print("-" * 80)
        print()
        pnl_data = self.check_paper_trading()
        print()

        print("-" * 80)
        print("SUMMARY")
        print("-" * 80)
        print(f"Systems: {'OK' if backend_ok and dashboard_ok else 'ISSUES'}")
        print(f"Online Verified: {verified}/2")
        print(f"Total Fixes: {self.total_fixes}")
        print()
        print("=" * 80)
        print(f"Next cycle in 2 minutes... (Press Ctrl+C to stop)")
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
    system = CombinedAutoSystem()
    system.run_continuous()
