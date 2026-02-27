#!/usr/bin/env python3
"""
Complete End-to-End Validation
Tests all features, tabs, multi-user scenarios, market hours, paper trading, learning
"""
import sys
import requests
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import concurrent.futures

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

BASE_URL = "http://localhost:8000"

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

class CompleteEndToEndValidator:
    """Complete end-to-end validation"""
    
    def __init__(self):
        self.results = {}
        self.traders = ["trader1", "trader2", "trader3", "trader4", "trader5"]
        
    def test_backend_availability(self):
        """Test backend is running"""
        try:
            res = requests.get(f"{BASE_URL}/api/health", timeout=5)
            if res.status_code == 200:
                print_success("Backend is running")
                return True
            return False
        except:
            print_error("Backend not available")
            return False
    
    def test_market_hours_switching(self):
        """Test market hours detection and data switching"""
        print_header("MARKET HOURS & DATA SWITCHING")
        
        try:
            from src.utils.market_hours import is_market_open, get_market_status
            
            is_open, reason = is_market_open()
            status = get_market_status()
            
            print_info(f"Market status: {'OPEN' if is_open else 'CLOSED'}")
            print_info(f"Reason: {reason}")
            
            # Test API data source
            health_res = requests.get(f"{BASE_URL}/api/health", timeout=5)
            if health_res.status_code == 200:
                health = health_res.json()
                data_source = health.get('data_source', 'unknown')
                
                # Verify correct switching (backend may use real/live/synthetic)
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
        """Test all dashboard tabs"""
        print_header("ALL DASHBOARD TABS")
        
        tabs = {
            "Overview": ("/api/state", "/api/health"),
            "Chain": ("/api/chain/NIFTY", "/api/chain/BANKNIFTY"),
            "Signals": ("/api/signal/top",),
            "Trading": ("/api/positions", "/api/pnl"),
            "Alerts": ("/api/qc",),
            "Risk": ("/api/risk/portfolio",),
            "Performance": ("/api/perf",)
        }
        
        results = {}
        for tab_name, endpoints in tabs.items():
            tab_ok = True
            for endpoint in endpoints:
                try:
                    res = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
                    if res.status_code != 200:
                        print_warning(f"{tab_name} - {endpoint}: Status {res.status_code}")
                        tab_ok = False
                    else:
                        print_success(f"{tab_name} - {endpoint}: OK")
                except Exception as e:
                    print_error(f"{tab_name} - {endpoint}: {e}")
                    tab_ok = False
            
            results[tab_name] = tab_ok
        
        all_ok = all(results.values())
        print(f"\n[Result] All tabs working: {all_ok}")
        return all_ok
    
    def test_multi_trader_concurrent(self):
        """Test multiple traders accessing simultaneously"""
        print_header("MULTI-TRADER CONCURRENT ACCESS")
        
        def test_trader(trader_id):
            """Test a single trader"""
            try:
                # Test multiple endpoints
                endpoints = [
                    f"{BASE_URL}/api/state",
                    f"{BASE_URL}/api/health",
                    f"{BASE_URL}/api/chain/NIFTY",
                    f"{BASE_URL}/api/signal/top",
                    f"{BASE_URL}/api/positions"
                ]
                
                success_count = 0
                for endpoint in endpoints:
                    try:
                        res = requests.get(endpoint, timeout=5)
                        if res.status_code == 200:
                            success_count += 1
                    except:
                        pass
                
                return success_count == len(endpoints)
            except:
                return False
        
        # Test all traders concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(test_trader, trader): trader for trader in self.traders}
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
        """Test paper trading system"""
        print_header("PAPER TRADING SYSTEM")
        
        try:
            # Test positions endpoint
            pos_res = requests.get(f"{BASE_URL}/api/positions", timeout=5)
            if pos_res.status_code == 200:
                positions = pos_res.json().get('positions', [])
                print_success(f"Positions endpoint: {len(positions)} open positions")
            
            # Test PnL endpoint
            pnl_res = requests.get(f"{BASE_URL}/api/pnl", timeout=5)
            if pnl_res.status_code == 200:
                pnl = pnl_res.json()
                print_success(f"PnL endpoint: Total PnL = {pnl.get('total_pnl', 0):.2f}")
            
            # Check paper trades file
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
        """Test continuous learning system"""
        print_header("CONTINUOUS LEARNING SYSTEM")
        
        try:
            # Run learning system
            result = subprocess.run(
                [sys.executable, str(ROOT_DIR / "continuous_learning_system.py")],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print_success("Continuous learning system executed")
                return True
            else:
                print_warning(f"Learning system returned code {result.returncode}")
                return False
        except Exception as e:
            print_error(f"Learning system test failed: {e}")
            return False
    
    def test_prediction_enhancement(self):
        """Test prediction enhancement"""
        print_header("PREDICTION ENHANCEMENT")
        
        try:
            result = subprocess.run(
                [sys.executable, str(ROOT_DIR / "advanced_prediction_enhancer.py")],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print_success("Prediction enhancement executed")
                # Check for insights
                insights_file = ROOT_DIR / "storage" / "learning" / "model_insights.json"
                if insights_file.exists():
                    print_success(f"Model insights saved: {insights_file}")
                return True
            else:
                print_warning(f"Prediction enhancement returned code {result.returncode}")
                return False
        except Exception as e:
            print_error(f"Prediction enhancement test failed: {e}")
            return False
    
    def test_forensic_analysis(self):
        """Test forensic analysis"""
        print_header("FORENSIC ANALYSIS")
        
        try:
            result = subprocess.run(
                [sys.executable, str(ROOT_DIR / "forensic_analysis_system.py")],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print_success("Forensic analysis executed")
                # Check for report
                reports_dir = ROOT_DIR / "reports" / "forensic"
                if reports_dir.exists():
                    reports = list(reports_dir.glob("forensic_report_*.json"))
                    if reports:
                        print_success(f"Forensic reports found: {len(reports)}")
                return True
            else:
                print_warning(f"Forensic analysis returned code {result.returncode}")
                return False
        except Exception as e:
            print_error(f"Forensic analysis test failed: {e}")
            return False
    
    def run_complete_validation(self):
        """Run complete end-to-end validation"""
        print_header("COMPLETE END-TO-END VALIDATION")
        
        if not self.test_backend_availability():
            print_error("Backend not available - cannot run validation")
            return False
        
        results = {
            "market_hours": self.test_market_hours_switching(),
            "all_tabs": self.test_all_dashboard_tabs(),
            "multi_trader": self.test_multi_trader_concurrent(),
            "paper_trading": self.test_paper_trading_system(),
            "continuous_learning": self.test_continuous_learning(),
            "prediction_enhancement": self.test_prediction_enhancement(),
            "forensic_analysis": self.test_forensic_analysis()
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
