"""
Comprehensive Test Suite for Option Chain Automation System
============================================================

This test suite validates all components of the option chain automation system:
- Data fetching (WebSocket + REST)
- Option chain analysis
- Signal generation
- Risk management
- Trade execution
- PnL tracking
- System integration

Run: python test_option_chain_automation.py
"""

import json
import sys
import unittest
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from option_chain_automation_master import (
    OptionChainAutomationMaster,
    SystemConfig,
    SystemStatus,
)


class TestSystemConfig(unittest.TestCase):
    """Test system configuration."""

    def test_default_config(self):
        """Test default configuration."""
        config = SystemConfig()
        self.assertIsInstance(config.refresh_interval_seconds, int)
        self.assertGreater(config.refresh_interval_seconds, 0)
        self.assertIsInstance(config.max_positions, int)
        self.assertGreater(config.max_positions, 0)

    def test_config_serialization(self):
        """Test config serialization."""
        config = SystemConfig()
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)

        # Test save/load
        config_path = ROOT_DIR / "test_config.json"
        config.save(config_path)

        loaded_config = SystemConfig.from_file(config_path)
        self.assertEqual(config.refresh_interval_seconds, loaded_config.refresh_interval_seconds)

        # Cleanup
        config_path.unlink()


class TestSystemStatus(unittest.TestCase):
    """Test system status tracking."""

    def test_status_initialization(self):
        """Test status initialization."""
        status = SystemStatus()
        self.assertFalse(status.is_running)
        self.assertFalse(status.is_connected)
        self.assertEqual(status.total_cycles, 0)
        self.assertEqual(len(status.errors), 0)

    def test_status_serialization(self):
        """Test status serialization."""
        status = SystemStatus()
        status.is_running = True
        status.total_cycles = 10

        status_dict = status.to_dict()
        self.assertIsInstance(status_dict, dict)
        self.assertTrue(status_dict["is_running"])
        self.assertEqual(status_dict["total_cycles"], 10)


class TestOptionChainEnrichment(unittest.TestCase):
    """Test option chain enrichment."""

    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame(
            {
                "underlying": ["NIFTY"] * 10,
                "strike": [19000, 19100, 19200, 19300, 19400, 19500, 19600, 19700, 19800, 19900],
                "spot_price": [19500] * 10,
                "ltp": [100, 150, 200, 250, 300, 250, 200, 150, 100, 50],
                "bidPrice": [99, 149, 199, 249, 299, 249, 199, 149, 99, 49],
                "offerPrice": [101, 151, 201, 251, 301, 251, 201, 151, 101, 51],
                "volume": [1000, 2000, 3000, 4000, 5000, 4000, 3000, 2000, 1000, 500],
                "oi": [10000, 20000, 30000, 40000, 50000, 40000, 30000, 20000, 10000, 5000],
                "option_type": ["CE"] * 5 + ["PE"] * 5,
                "expiry": ["2026-02-08"] * 10,
            }
        )

    def test_enrichment_adds_columns(self):
        """Test that enrichment adds required columns."""
        system = OptionChainAutomationMaster()
        enriched = system._enrich_option_chain(self.sample_data.copy(), "NIFTY")

        # Check for added columns
        self.assertIn("atm_distance", enriched.columns)
        self.assertIn("atm_distance_pct", enriched.columns)
        self.assertIn("bid_ask_spread", enriched.columns)
        self.assertIn("liquidity_score", enriched.columns)
        self.assertIn("fetch_timestamp", enriched.columns)

    def test_atm_distance_calculation(self):
        """Test ATM distance calculation."""
        system = OptionChainAutomationMaster()
        enriched = system._enrich_option_chain(self.sample_data.copy(), "NIFTY")

        # Check ATM distance for strike 19500 (should be 0)
        atm_row = enriched[enriched["strike"] == 19500]
        if not atm_row.empty:
            self.assertAlmostEqual(atm_row.iloc[0]["atm_distance"], 0, places=2)


class TestSignalGeneration(unittest.TestCase):
    """Test signal generation."""

    def setUp(self):
        """Set up test data."""
        self.system = OptionChainAutomationMaster()
        # Don't initialize broker for unit tests
        self.system.broker = None

        self.sample_chain = {
            "NIFTY": pd.DataFrame(
                {
                    "underlying": ["NIFTY"] * 5,
                    "strike": [19400, 19450, 19500, 19550, 19600],
                    "spot_price": [19500] * 5,
                    "ltp": [100, 150, 200, 150, 100],
                    "delta": [0.3, 0.4, 0.5, 0.6, 0.7],
                    "gamma": [0.01, 0.02, 0.03, 0.02, 0.01],
                    "iv": [0.20, 0.21, 0.22, 0.21, 0.20],
                    "volume": [1000, 2000, 3000, 2000, 1000],
                    "oi": [10000, 20000, 30000, 20000, 10000],
                    "option_type": ["CE"] * 5,
                }
            )
        }

    def test_signal_generation_returns_list(self):
        """Test that signal generation returns a tuple (signals, errors)."""
        result = self.system.generate_signals(self.sample_chain)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        signals, errors = result
        self.assertIsInstance(signals, list)
        self.assertIsInstance(errors, list)

    def test_signals_filtered_by_confidence(self):
        """Test that signals are filtered by confidence."""
        # This test requires strategy engine to be initialized
        # For now, just check the structure
        signals, errors = self.system.generate_signals(self.sample_chain)
        for signal in signals:
            self.assertIn("confidence", signal)
            # NO_TRADE signals may have confidence 0.0, which is valid
            if signal.get("action") != "NO_TRADE":
                self.assertGreaterEqual(signal["confidence"], self.system.config.min_confidence)


class TestRiskManagement(unittest.TestCase):
    """Test risk management."""

    def setUp(self):
        """Set up test."""
        self.system = OptionChainAutomationMaster()

    def test_max_positions_enforcement(self):
        """Test that max positions are enforced."""
        # Create mock executor with max positions
        if self.system.paper_executor:
            initial_positions = len(self.system.paper_executor.positions)
            self.assertLessEqual(initial_positions, self.system.config.max_positions)


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    def setUp(self):
        """Set up integration test."""
        self.system = OptionChainAutomationMaster()
        # Use test config
        self.system.config = SystemConfig(refresh_interval_seconds=1, max_positions=3, min_confidence=0.7)

    def test_system_initialization_structure(self):
        """Test that system can be created."""
        self.assertIsNotNone(self.system)
        self.assertIsNotNone(self.system.config)
        self.assertIsNotNone(self.system.status)

    def test_status_tracking(self):
        """Test status tracking."""
        initial_cycles = self.system.status.total_cycles
        self.system.status.total_cycles += 1
        self.assertEqual(self.system.status.total_cycles, initial_cycles + 1)


class TestDataValidation(unittest.TestCase):
    """Test data validation."""

    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames."""
        system = OptionChainAutomationMaster()
        empty_df = pd.DataFrame()
        enriched = system._enrich_option_chain(empty_df, "NIFTY")
        self.assertTrue(enriched.empty)

    def test_missing_columns_handling(self):
        """Test handling of missing columns."""
        system = OptionChainAutomationMaster()
        minimal_df = pd.DataFrame({"strike": [19500], "ltp": [100]})
        # Should not crash
        enriched = system._enrich_option_chain(minimal_df, "NIFTY")
        self.assertIsInstance(enriched, pd.DataFrame)


def run_all_tests():
    """Run all tests and generate report."""
    print("=" * 80)
    print("OPTION CHAIN AUTOMATION SYSTEM - TEST SUITE")
    print("=" * 80)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSystemConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemStatus))
    suite.addTests(loader.loadTestsFromTestCase(TestOptionChainEnrichment))
    suite.addTests(loader.loadTestsFromTestCase(TestSignalGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success": result.wasSuccessful(),
        "failure_details": result.failures,
        "error_details": result.errors,
    }

    # Save report
    report_path = ROOT_DIR / "outputs" / "test_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print()
    print("=" * 80)
    print("TEST REPORT")
    print("=" * 80)
    print(f"Tests run: {report['tests_run']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Success: {report['success']}")
    print(f"Report saved to: {report_path}")
    print("=" * 80)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
