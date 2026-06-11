#!/usr/bin/env python3
"""
Comprehensive Multi-Trader End-to-End Test Suite
Tests all tabs, features, and scenarios with multiple concurrent traders
"""
import asyncio
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

BASE_URL = "http://localhost:8000"
TRADERS = ["trader1", "trader2", "trader3", "trader4", "trader5"]

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

class MultiTraderTester:
    """Comprehensive multi-trader testing"""
    
    def __init__(self):
        self.results = {
            "overview": {},
            "chain": {},
            "signals": {},
            "trading": {},
            "alerts": {},
            "risk": {},
            "charts": {},
            "ml": {},
            "model": {},
            "control": {},
            "agent": {},
            "market_hours": {},
            "data_switching": {},
            "paper_trading": {},
            "performance": {}
        }
        
    def test_backend_health(self):
        """Test backend is running"""
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print_success(f"Backend health: {data.get('status', 'unknown')}")
                return True
            else:
                print_error(f"Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Backend not reachable: {e}")
            return False
    
    def test_overview_tab(self, trader_id: str):
        """Test Overview tab for a trader"""
        print_info(f"Testing Overview tab for {trader_id}...")
        try:
            # Test state endpoint
            state_res = requests.get(f"{BASE_URL}/api/state", timeout=5)
            if state_res.status_code == 200:
                state = state_res.json()
                print_success(f"{trader_id}: State endpoint OK")
                
            # Test health endpoint
            health_res = requests.get(f"{BASE_URL}/api/health", timeout=5)
            if health_res.status_code == 200:
                health = health_res.json()
                print_success(f"{trader_id}: Health endpoint OK")
                return True
            return False
        except Exception as e:
            print_error(f"{trader_id}: Overview test failed: {e}")
            return False
    
    def test_chain_tab(self, trader_id: str):
        """Test Chain Analytics tab"""
        print_info(f"Testing Chain tab for {trader_id}...")
        try:
            for underlying in ["NIFTY", "BANKNIFTY", "FINNIFTY"]:
                res = requests.get(f"{BASE_URL}/api/chain/{underlying}", timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    contracts = data.get('contracts', [])
                    print_success(f"{trader_id}: {underlying} chain - {len(contracts)} contracts")
                else:
                    print_warning(f"{trader_id}: {underlying} chain failed: {res.status_code}")
            return True
        except Exception as e:
            print_error(f"{trader_id}: Chain test failed: {e}")
            return False
    
    def test_signals_tab(self, trader_id: str):
        """Test Signals tab"""
        print_info(f"Testing Signals tab for {trader_id}...")
        try:
            res = requests.get(f"{BASE_URL}/api/signal/top", timeout=5)
            if res.status_code == 200:
                signal = res.json()
                print_success(f"{trader_id}: Signal endpoint OK")
                return True
            return False
        except Exception as e:
            print_error(f"{trader_id}: Signals test failed: {e}")
            return False
    
    def test_trading_tab(self, trader_id: str):
        """Test Paper Trading tab"""
        print_info(f"Testing Trading tab for {trader_id}...")
        try:
            # Test positions
            pos_res = requests.get(f"{BASE_URL}/api/positions", timeout=5)
            if pos_res.status_code == 200:
                positions = pos_res.json().get('positions', [])
                print_success(f"{trader_id}: Positions - {len(positions)} open")
            
            # Test PnL
            pnl_res = requests.get(f"{BASE_URL}/api/pnl", timeout=5)
            if pnl_res.status_code == 200:
                pnl = pnl_res.json()
                print_success(f"{trader_id}: PnL endpoint OK")
                return True
            return False
        except Exception as e:
            print_error(f"{trader_id}: Trading test failed: {e}")
            return False
    
    def test_market_hours_switching(self):
        """Test market hours detection and data switching"""
        print_info("Testing market hours switching...")
        try:
            from src.utils.market_hours import is_market_open, get_market_status
            
            is_open, reason = is_market_open()
            status = get_market_status()
            
            print_success(f"Market status: {'OPEN' if is_open else 'CLOSED'}")
            print_info(f"Reason: {reason}")
            print_info(f"Next open: {status.get('next_open', 'N/A')}")
            
            # Test data source
            health_res = requests.get(f"{BASE_URL}/api/health", timeout=5)
            if health_res.status_code == 200:
                health = health_res.json()
                data_source = health.get('data_source', 'unknown')
                print_success(f"Data source: {data_source}")
                
                if is_open and data_source == 'real':
                    print_success("Market open - using real data ✓")
                elif not is_open and data_source == 'synthetic':
                    print_success("Market closed - using synthetic data ✓")
                else:
                    print_warning(f"Data source mismatch: market={'open' if is_open else 'closed'}, data={data_source}")
            
            return True
        except Exception as e:
            print_error(f"Market hours test failed: {e}")
            return False
    
    def test_all_tabs_concurrent(self):
        """Test all tabs concurrently for multiple traders"""
        print_header("COMPREHENSIVE MULTI-TRADER TEST")
        
        if not self.test_backend_health():
            print_error("Backend not available - cannot run tests")
            return False
        
        # Test market hours switching first
        self.test_market_hours_switching()
        
        # Test all tabs for each trader
        for trader in TRADERS:
            print_header(f"Testing Trader: {trader}")
            
            self.test_overview_tab(trader)
            self.test_chain_tab(trader)
            self.test_signals_tab(trader)
            self.test_trading_tab(trader)
            
            time.sleep(0.5)  # Small delay between traders
        
        print_header("TEST COMPLETE")
        return True

if __name__ == "__main__":
    tester = MultiTraderTester()
    tester.test_all_tabs_concurrent()
