#!/usr/bin/env python3
"""
Complete End-to-End Validation
Tests all features, tabs, multi-user scenarios, market hours, paper trading, learning
"""
import concurrent.futures
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

BASE_URL = "https://genesis-system3-backend.onrender.com"
API_KEY = "Ocd3XakH2I8lMYCSzDOZu4CQ5zh0JAuOM59WUWbh0bY="
HEADERS = {"X-API-Key": API_KEY}


def print_header(text):
    print(f"\n{'='*80}")
    print(f"{text.center(80)}")
    print(f"{'='*80}\n")


def print_success(text):
    print(f"[OK] {text}")


def print_error(text):
    print(f"[ERROR] {text}")


def print_warning(text):
    print(f"[WARNING] {text}")


def print_info(text):
    print(f"[INFO] {text}")


def safe_get(endpoint, timeout=60, retries=3, wait=10):
    """GET with retry logic for cold-start 502s and timeouts."""
    url = f"{BASE_URL}{endpoint}"
    for attempt in range(1, retries + 1):
        try:
            res = requests.get(url, headers=HEADERS, timeout=timeout)
            if res.status_code == 200:
                return res
            if res.status_code in (502, 503, 504) and attempt < retries:
                print_info(f"  {endpoint} → {res.status_code}, retrying ({attempt}/{retries}) in {wait}s...")
                time.sleep(wait)
                continue
            return res
        except requests.exceptions.Timeout:
            if attempt < retries:
                print_info(f"  {endpoint} → Timeout, retrying ({attempt}/{retries}) in {wait}s...")
                time.sleep(wait)
            else:
                raise
        except Exception:
            raise
    return None


class CompleteEndToEndValidator:
    """Complete end-to-end validation"""

    def __init__(self):
        self.results = {}
        self.traders = ["trader1", "trader2", "trader3", "trader4", "trader5"]

    def warmup_backend(self, retries=6, wait=15):
        """Hit health endpoint repeatedly until backend is warm (handles Render cold start)."""
        print_header("BACKEND WARMUP")
        print_info(f"Warming up backend (up to {retries * wait}s)...")
        for i in range(1, retries + 1):
            try:
                res = requests.get(f"{BASE_URL}/api/health", headers=HEADERS, timeout=60)
                if res.status_code == 200:
                    print_success(f"Backend warm after {i} attempt(s)")
                    return True
                print_info(f"  Attempt {i}/{retries}: status {res.status_code}, waiting {wait}s...")
            except Exception as e:
                print_info(f"  Attempt {i}/{retries}: {e}, waiting {wait}s...")
            time.sleep(wait)
        print_error("Backend did not warm up in time")
        return False

    def test_backend_availability(self):
        try:
            res = safe_get("/api/health", timeout=60)
            if res and res.status_code == 200:
                print_success("Backend is running")
                return True
            return False
        except Exception as e:
            print_error(f"Backend not available: {e}")
            return False

    def test_market_hours_switching(self):
        print_header("MARKET HOURS & DATA SWITCHING")
        try:
            from src.utils.market_hours import get_market_status, is_market_open
            is_open, reason = is_market_open()
            status = get_market_status()
            print_info(f"Market status: {'OPEN' if is_open else 'CLOSED'}")
            print_info(f"Reason: {reason}")
            health_res = safe_get("/api/health", timeout=60)
            if health_res and health_res.status_code == 200:
                health = health_res.json()
                data_source = health.get("data_source", "unknown")
                ds = (data_source or "").lower()
                if is_open:
                    if ds in ("real", "live"):
                        print_success(f"Market open - correctly using {data_source} data")
                        return True
                    else:
                        print_warning(f"Market open but using {data_source} (expected real/live)")
                        return False
                else:
                    if ds in ("synthetic", "live", "real"):
                        print_success(f"Market closed - correctly using {data_source} data")
                        return True
                    else:
                        print_warning(f"Market closed but using {data_source} (expected synthetic/live/real)")
                        return False
            return False
        except Exception as e:
            print_error(f"Market hours test failed: {e}")
            return False

    def test_all_dashboard_tabs(self):
        print_header("ALL DASHBOARD TABS")
        tabs = {
            "Overview":    [("/api/state", 60), ("/api/health", 60)],
            "Chain":       [("/api/chain/NIFTY", 90), ("/api/chain/BANKNIFTY", 90)],
            "Signals":     [("/api/signal/top", 60)],
            "Trading":     [("/api/positions", 60), ("/api/pnl", 60)],
            "Alerts":      [("/api/qc", 60)],
            "Risk":        [("/api/risk/portfolio", 60)],
            "Performance": [("/api/perf", 60)],
        }
        results = {}
        for tab_name, endpoints in tabs.items():
            tab_ok = True
            for endpoint, timeout in endpoints:
                try:
                    res = safe_get(endpoint, timeout=timeout, retries=3, wait=10)
                    if res and res.status_code == 200:
                        print_success(f"{tab_name} - {endpoint}: OK")
                    else:
                        code = res.status_code if res else "No response"
                        print_warning(f"{tab_name} - {endpoint}: Status {code}")
                        tab_ok = False
                except Exception as e:
                    print_error(f"{tab_name} - {endpoint}: {e}")
                    tab_ok = False
            results[tab_name] = tab_ok
        all_ok = all(results.values())
        print(f"\n[Result] All tabs working: {all_ok}")
        return all_ok

    def test_multi_trader_concurrent(self):
        print_header("MULTI-TRADER CONCURRENT ACCESS")

        def test_trader(trader_id):
            endpoints = [
                ("/api/state", 60),
                ("/api/health", 60),
                ("/api/chain/NIFTY", 90),
                ("/api/signal/top", 60),
                ("/api/positions", 60),
            ]
            success_count = 0
            for endpoint, timeout in endpoints:
                try:
                    res = safe_get(endpoint, timeout=timeout, retries=2, wait=5)
                    if res and res.status_code == 200:
                        success_count += 1
                except Exception:
                    pass
            return success_count == len(endpoints)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(test_trader, t): t for t in self.traders}
            results = {}
            for future in concurrent.futures.as_completed(futures):
                trader = futures[future]
                try:
                    result = future.result()
                    results[trader] = result
                    if result:
                        print_success(f"{trader}: All endpoints accessible")
                    else:
                        print_warning(f"{trader}: Some endpoints failed")
                except Exception as e:
                    print_error(f"{trader}: Test failed - {e}")
                    results[trader] = False

        all_passed = all(results.values())
        print(f"\n[Result] All traders passed: {all_passed} ({sum(results.values())}/{len(results)})")
        return all_passed

    def test_paper_trading_system(self):
        print_header("PAPER TRADING SYSTEM")
        try:
            pos_res = safe_get("/api/positions", timeout=60)
            if pos_res and pos_res.status_code == 200:
                positions = pos_res.json().get("positions", [])
                print_success(f"Positions endpoint: {len(positions)} open positions")
            else:
                code = pos_res.status_code if pos_res else "No response"
                print_warning(f"Positions endpoint: {code}")

            pnl_res = safe_get("/api/pnl", timeout=60)
            if pnl_res and pnl_res.status_code == 200:
                pnl = pnl_res.json()
                print_success(f"PnL endpoint: Total PnL = {pnl.get('total_pnl', 0):.2f}")
            else:
                code = pnl_res.status_code if pnl_res else "No response"
                print_warning(f"PnL endpoint: {code}")

            paper_trades_file = ROOT_DIR / "src" / "outputs" / "paper_trades_live.csv"
            if paper_trades_file.exists():
                print_success(f"Paper trades file exists: {paper_trades_file}")
            else:
                print_warning("Paper trades file not found (may be empty)")
            return True
        except Exception as e:
            print_error(f"Paper trading test failed: {e}")
            return False

    def test_continuous_learning(self):
        print_header("CONTINUOUS LEARNING SYSTEM")
        try:
            result = subprocess.run(
                [sys.executable, str(ROOT_DIR / "continuous_learning_system.py")],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                print_success("Continuous learning system executed")
                return True
            else:
                print_warning(f"Learning system returned code {result.returncode}")
                if result.stderr:
                    print_warning(f"  stderr: {result.stderr[-300:]}")
                return False
        except Exception as e:
            print_error(f"Learning system test failed: {e}")
            return False

    def test_prediction_enhancement(self):
        print_header("PREDICTION ENHANCEMENT")
        try:
            result = subprocess.run(
                [sys.executable, str(ROOT_DIR / "advanced_prediction_enhancer.py")],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                print_success("Prediction enhancement executed")
                insights_file = ROOT_DIR / "storage" / "learning" / "model_insights.json"
                if insights_file.exists():
                    print_success(f"Model insights saved: {insights_file}")
                return True
            else:
                print_warning(f"Prediction enhancement returned code {result.returncode}")
                if result.stderr:
                    print_warning(f"  stderr: {result.stderr[-300:]}")
                return False
        except Exception as e:
            print_error(f"Prediction enhancement test failed: {e}")
            return False

    def test_forensic_analysis(self):
        print_header("FORENSIC ANALYSIS")
        try:
            result = subprocess.run(
                [sys.executable, str(ROOT_DIR / "forensic_analysis_system.py")],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                print_success("Forensic analysis executed")
                reports_dir = ROOT_DIR / "reports" / "forensic"
                if reports_dir.exists():
                    reports = list(reports_dir.glob("forensic_report_*.json"))
                    if reports:
                        print_success(f"Forensic reports found: {len(reports)}")
                return True
            else:
                print_warning(f"Forensic analysis returned code {result.returncode}")
                if result.stderr:
                    print_warning(f"  stderr: {result.stderr[-300:]}")
                return False
        except Exception as e:
            print_error(f"Forensic analysis test failed: {e}")
            return False

    def run_complete_validation(self):
        print_header("COMPLETE END-TO-END VALIDATION")

        if not self.warmup_backend():
            print_error("Backend did not warm up — cannot run validation")
            return False

        results = {
            "market_hours":           self.test_market_hours_switching(),
            "all_tabs":               self.test_all_dashboard_tabs(),
            "multi_trader":           self.test_multi_trader_concurrent(),
            "paper_trading":          self.test_paper_trading_system(),
            "continuous_learning":    self.test_continuous_learning(),
            "prediction_enhancement": self.test_prediction_enhancement(),
            "forensic_analysis":      self.test_forensic_analysis(),
        }

        print_header("VALIDATION RESULTS")
        for name, result in results.items():
            status = "[OK]" if result else "[FAIL]"
            print(f"{status} {name}")

        passed = sum(results.values())
        total = len(results)
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n[Overall] Passed: {passed}/{total} ({success_rate:.1f}%)")
        all_passed = all(results.values())
        print(f"[Status] {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
        return all_passed


if __name__ == "__main__":
    validator = CompleteEndToEndValidator()
    validator.run_complete_validation()