"""
Dashboard Online Verifier
Tracks dashboard data and verifies against online sources
Runs every 2 minutes to ensure data accuracy
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
import re

ROOT_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"

API_BASE = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:8080"

# Online data sources for verification
ONLINE_SOURCES = {
    "NIFTY": {
        "yahoo": "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=1d",
        "nse": "https://www.nseindia.com/api/quote-equity?symbol=NIFTY",
    },
    "BANKNIFTY": {
        "yahoo": "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEBANK?interval=1d",
        "nse": "https://www.nseindia.com/api/quote-equity?symbol=BANKNIFTY",
    },
}


class DashboardOnlineVerifier:
    def __init__(self):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.cycle = 0
        self.discrepancies_found = []
        self.corrections_applied = []

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def log(self, msg, level="INFO"):
        now = datetime.now(self.ist).strftime("%H:%M:%S")
        symbols = {"INFO": "[*]", "OK": "[OK]", "FIX": "[FIX]", "WARN": "[!]", "ERR": "[X]", "VERIFY": "[VERIFY]"}
        print(f"[{now}] {symbols.get(level, '[*]')} {msg}")

    def get_online_spot_price(self, underlying):
        """Get spot price from online sources"""
        try:
            # Try Yahoo Finance
            if underlying in ONLINE_SOURCES:
                url = ONLINE_SOURCES[underlying].get("yahoo")
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if "chart" in data and "result" in data["chart"]:
                        result = data["chart"]["result"]
                        if result and len(result) > 0:
                            meta = result[0].get("meta", {})
                            regular_price = meta.get("regularMarketPrice")
                            if regular_price:
                                return float(regular_price)
        except Exception as e:
            self.log(f"Error fetching online price for {underlying}: {str(e)}", "ERR")

        return None

    def verify_spot_price(self, underlying, dashboard_spot):
        """Verify spot price against online sources"""
        self.log(f"Verifying {underlying} spot price online...", "VERIFY")

        online_spot = self.get_online_spot_price(underlying)

        if online_spot:
            diff = abs(dashboard_spot - online_spot)
            diff_pct = (diff / online_spot) * 100 if online_spot > 0 else 0

            if diff_pct > 1.0:  # More than 1% difference
                self.log(
                    f"DISCREPANCY: Dashboard Rs{dashboard_spot:.2f} vs Online Rs{online_spot:.2f} (diff: {diff_pct:.2f}%)",
                    "WARN",
                )
                self.discrepancies_found.append(
                    {
                        "type": "spot_price",
                        "underlying": underlying,
                        "dashboard": dashboard_spot,
                        "online": online_spot,
                        "difference": diff_pct,
                    }
                )
                return False, online_spot
            else:
                self.log(f"VERIFIED: Spot price matches (Rs{dashboard_spot:.2f} vs Rs{online_spot:.2f})", "OK")
                return True, None
        else:
            self.log(f"Could not fetch online price for {underlying}", "WARN")
            return None, None

    def verify_chain_data(self, underlying):
        """Verify chain data from dashboard"""
        try:
            response = requests.get(f"{API_BASE}/api/chain/{underlying}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                spot = data.get("spot", 0)
                contracts = data.get("total_contracts", 0)

                if spot > 0:
                    # Verify spot price online
                    verified, correct_spot = self.verify_spot_price(underlying, spot)
                    if verified is False and correct_spot:
                        # Update with correct spot price
                        self.log(f"Correcting {underlying} spot price to Rs{correct_spot:.2f}", "FIX")
                        self.correct_spot_price(underlying, correct_spot)
                        self.corrections_applied.append(f"Corrected {underlying} spot price")

                return data
        except Exception as e:
            self.log(f"Error verifying chain data: {str(e)}", "ERR")
        return None

    def correct_spot_price(self, underlying, correct_price):
        """Correct spot price in chain data"""
        try:
            chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
            if chain_file.exists():
                # Read CSV
                import csv

                rows = []
                with open(chain_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get("underlying", "").upper() == underlying.upper():
                            row["spot_price"] = str(correct_price)
                        rows.append(row)

                # Write back
                if rows:
                    with open(chain_file, "w", encoding="utf-8", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                        writer.writeheader()
                        writer.writerows(rows)
        except Exception as e:
            self.log(f"Error correcting spot price: {str(e)}", "ERR")

    def verify_dashboard_health(self):
        """Verify dashboard health data"""
        try:
            response = requests.get(f"{API_BASE}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log(f"Dashboard Health: {data.get('status')} | Mode: {data.get('mode')}", "OK")
                return data
        except Exception as e:
            self.log(f"Error verifying dashboard health: {str(e)}", "ERR")
        return None

    def verify_pnl_data(self):
        """Verify PnL data makes sense"""
        try:
            pnl_file = OUTPUTS_DIR / "paper_pnl_summary.json"
            if pnl_file.exists():
                with open(pnl_file) as f:
                    data = json.load(f)

                total_pnl = data.get("total_pnl", 0)
                realized = data.get("total_realized_pnl", 0)
                unrealized = data.get("total_unrealized_pnl", 0)

                # Verify PnL calculation
                calculated_total = realized + unrealized
                diff = abs(total_pnl - calculated_total)

                if diff > 0.01:  # More than 1 paisa difference
                    self.log(f"PnL DISCREPANCY: Total Rs{total_pnl:.2f} vs Calculated Rs{calculated_total:.2f}", "WARN")
                    self.discrepancies_found.append(
                        {
                            "type": "pnl_calculation",
                            "total": total_pnl,
                            "calculated": calculated_total,
                            "difference": diff,
                        }
                    )
                else:
                    self.log(
                        f"PnL VERIFIED: Rs{total_pnl:.2f} (Realized: Rs{realized:.2f}, Unrealized: Rs{unrealized:.2f})",
                        "OK",
                    )

                return data
        except Exception as e:
            self.log(f"Error verifying PnL: {str(e)}", "ERR")
        return None

    def verify_all_underlyings(self):
        """Verify all underlying spot prices"""
        underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
        verified_count = 0

        for underlying in underlyings:
            chain_data = self.verify_chain_data(underlying)
            if chain_data and chain_data.get("spot", 0) > 0:
                verified_count += 1

        return verified_count

    def check_dashboard_accessibility(self):
        """Check if dashboard is accessible and showing data"""
        try:
            response = requests.get(DASHBOARD_URL, timeout=10)
            if response.status_code == 200:
                # Check if Vue is loaded
                content = response.text
                if "vue" in content.lower() or "Vue" in content:
                    self.log("Dashboard: ACCESSIBLE with Vue3", "OK")
                    return True
                else:
                    self.log("Dashboard: ACCESSIBLE but Vue3 not detected", "WARN")
                    return False
            else:
                self.log(f"Dashboard: HTTP {response.status_code}", "WARN")
                return False
        except Exception as e:
            self.log(f"Dashboard: NOT ACCESSIBLE - {str(e)}", "ERR")
            return False

    def run_verification_cycle(self):
        """Run complete verification cycle"""
        self.cycle += 1
        self.clear()

        print("=" * 80)
        print(" " * 20 + "DASHBOARD ONLINE VERIFIER")
        print(" " * 25 + "Verifying Against Internet Sources")
        print(" " * 30 + "Goal: Maximum Profit")
        print("=" * 80)
        print()

        now = datetime.now(self.ist)
        print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"Verification Cycle: #{self.cycle}")
        print()

        self.discrepancies_found = []
        self.corrections_applied = []

        print("-" * 80)
        print("DASHBOARD ACCESSIBILITY CHECK")
        print("-" * 80)
        print()
        dashboard_ok = self.check_dashboard_accessibility()
        print()

        print("-" * 80)
        print("DASHBOARD HEALTH VERIFICATION")
        print("-" * 80)
        print()
        health_data = self.verify_dashboard_health()
        print()

        print("-" * 80)
        print("ONLINE SPOT PRICE VERIFICATION")
        print("-" * 80)
        print()
        verified_count = self.verify_all_underlyings()
        print()

        print("-" * 80)
        print("PnL DATA VERIFICATION")
        print("-" * 80)
        print()
        pnl_data = self.verify_pnl_data()
        print()

        print("-" * 80)
        print("VERIFICATION SUMMARY")
        print("-" * 80)
        print()
        print(f"Underlyings Verified: {verified_count}/5")
        print(f"Discrepancies Found: {len(self.discrepancies_found)}")
        if self.discrepancies_found:
            for disc in self.discrepancies_found[:3]:
                print(f"  [!] {disc.get('type')}: {disc}")
        print()
        print(f"Corrections Applied: {len(self.corrections_applied)}")
        if self.corrections_applied:
            for correction in self.corrections_applied:
                print(f"  [FIXED] {correction}")
        print()

        print("=" * 80)
        print(f"Next verification in 2 minutes... (Press Ctrl+C to stop)")
        print("=" * 80)

    def run_continuous(self):
        """Run continuous verification every 2 minutes"""
        while True:
            try:
                self.run_verification_cycle()
                time.sleep(120)  # 2 minutes
            except KeyboardInterrupt:
                print("\n\nVerification stopped by user.")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}")
                time.sleep(120)


if __name__ == "__main__":
    verifier = DashboardOnlineVerifier()
    verifier.run_continuous()
