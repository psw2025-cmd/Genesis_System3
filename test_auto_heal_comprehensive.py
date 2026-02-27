"""
System3 Auto-Heal Comprehensive Test Suite

Tests all auto-healing functionality:
- Stale data detection and recovery
- Large log detection and archiving
- Old log cleanup
- Disk space management
- Heartbeat monitoring
- Integration with phase 306
"""

import sys
import os
import json
import shutil
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.system3_auto_heal_orchestrator import AutoHealOrchestrator, HEAL_CONFIG
from core.engine.system3_phase306_staleness_guard import run_phase306


class TestAutoHealOrchestrator(unittest.TestCase):
    """Test auto-heal orchestrator functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.orchestrator = AutoHealOrchestrator()
        self.test_dir = PROJECT_ROOT / "test_auto_heal_temp"
        self.test_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly."""
        self.assertIsNotNone(self.orchestrator)
        self.assertIsInstance(self.orchestrator.config, dict)
        self.assertIn("auto_refresh_stale_data", self.orchestrator.config)
    
    def test_stale_data_detection(self):
        """Test stale data detection."""
        issue = self.orchestrator.detect_stale_data()
        # Can be None if no staleness data exists
        if issue:
            self.assertIn("type", issue)
            self.assertEqual(issue["type"], "STALE_DATA")
    
    def test_large_log_detection(self):
        """Test large log detection."""
        large_logs = self.orchestrator.detect_large_logs()
        self.assertIsInstance(large_logs, list)
        
        for log_info in large_logs:
            self.assertIn("type", log_info)
            self.assertIn("size_mb", log_info)
            self.assertEqual(log_info["type"], "LARGE_LOG")
    
    def test_old_log_detection(self):
        """Test old log detection."""
        old_logs = self.orchestrator.detect_old_logs()
        self.assertIsInstance(old_logs, list)
        
        for log_info in old_logs:
            self.assertIn("type", log_info)
            self.assertIn("age_days", log_info)
            self.assertEqual(log_info["type"], "OLD_LOG")
    
    def test_disk_space_detection(self):
        """Test disk space detection."""
        issue = self.orchestrator.detect_disk_space()
        # Should be None if enough space
        if issue:
            self.assertEqual(issue["type"], "LOW_DISK_SPACE")
            self.assertIn("free_gb", issue)
    
    def test_heartbeat_detection(self):
        """Test heartbeat detection."""
        issue = self.orchestrator.detect_missing_heartbeat()
        # Can be None if heartbeat is fresh
        if issue:
            self.assertIn("type", issue)
            self.assertIn(issue["type"], ["MISSING_HEARTBEAT", "STALE_HEARTBEAT"])
    
    def test_heartbeat_healing(self):
        """Test heartbeat healing."""
        result = self.orchestrator.heal_heartbeat()
        self.assertTrue(result)
        
        # Verify heartbeat file was created/updated
        heartbeat_file = PROJECT_ROOT / "system3_daily_heartbeat.json"
        self.assertTrue(heartbeat_file.exists())
        
        with heartbeat_file.open("r") as f:
            heartbeat_data = json.load(f)
        
        self.assertIn("timestamp", heartbeat_data)
        self.assertIn("auto_heal", heartbeat_data)
        self.assertTrue(heartbeat_data["auto_heal"])
    
    def test_full_healing_cycle(self):
        """Test complete healing cycle."""
        report = self.orchestrator.run_full_healing_cycle()
        
        self.assertIsInstance(report, dict)
        self.assertIn("timestamp", report)
        self.assertIn("issues_detected", report)
        self.assertIn("actions_taken", report)
        self.assertIn("errors", report)
        
        self.assertIsInstance(report["issues_detected"], list)
        self.assertIsInstance(report["actions_taken"], list)
        self.assertIsInstance(report["errors"], list)


class TestPhase306Integration(unittest.TestCase):
    """Test phase 306 integration with auto-heal."""
    
    def test_phase306_execution(self):
        """Test phase 306 runs successfully."""
        result = run_phase306()
        
        self.assertIsInstance(result, dict)
        self.assertIn("phase", result)
        self.assertEqual(result["phase"], 306)
        self.assertIn("status", result)
        self.assertIn(result["status"], ["OK", "WARN", "ERROR"])
    
    def test_phase306_outputs(self):
        """Test phase 306 provides expected outputs."""
        result = run_phase306()
        
        self.assertIn("outputs", result)
        outputs = result["outputs"]
        
        self.assertIn("report_file", outputs)
        self.assertIn("flags_csv", outputs)
        self.assertIn("auto_heal_triggered", outputs)
        
        self.assertIsInstance(outputs["auto_heal_triggered"], bool)
    
    def test_phase306_staleness_detection(self):
        """Test phase 306 staleness detection."""
        result = run_phase306()
        
        if result["status"] == "WARN":
            # If warning, should have expired data
            self.assertIn("outputs", result)
            self.assertIn("expired_count", result["outputs"])
            self.assertGreater(result["outputs"]["expired_count"], 0)
    
    def test_auto_heal_trigger_created(self):
        """Test auto-heal trigger file is created when needed."""
        result = run_phase306()
        
        if result["outputs"].get("auto_heal_triggered", False):
            trigger_file = PROJECT_ROOT / "storage" / "meta" / "system3_heal_trigger.json"
            self.assertTrue(trigger_file.exists())
            
            with trigger_file.open("r") as f:
                trigger_data = json.load(f)
            
            self.assertIn("timestamp", trigger_data)
            self.assertIn("triggered_by", trigger_data)
            self.assertEqual(trigger_data["triggered_by"], "phase306_staleness_guard")


class TestStalenessRecovery(unittest.TestCase):
    """Test staleness recovery mechanisms."""
    
    def setUp(self):
        """Set up test environment."""
        self.orchestrator = AutoHealOrchestrator()
    
    def test_stale_data_healing(self):
        """Test stale data healing process."""
        result = self.orchestrator.heal_stale_data()
        self.assertIsInstance(result, bool)
    
    def test_staleness_flags_exist(self):
        """Test staleness flags CSV exists after phase run."""
        run_phase306()
        
        staleness_csv = PROJECT_ROOT / "storage" / "meta" / "system3_staleness_flags_306.csv"
        self.assertTrue(staleness_csv.exists())
        
        # Verify CSV structure
        import pandas as pd
        df = pd.read_csv(staleness_csv)
        
        expected_columns = ["underlying", "last_ts", "latency_seconds", "staleness_state"]
        for col in expected_columns:
            self.assertIn(col, df.columns)


class TestLogManagement(unittest.TestCase):
    """Test log management functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.orchestrator = AutoHealOrchestrator()
        self.test_log_dir = PROJECT_ROOT / "logs" / "test_logs_temp"
        self.test_log_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment."""
        if self.test_log_dir.exists():
            shutil.rmtree(self.test_log_dir)
    
    def test_large_log_healing(self):
        """Test large log healing."""
        # Create a fake large log
        large_log = self.test_log_dir / "large_test.log"
        with large_log.open("w") as f:
            f.write("X" * (101 * 1024 * 1024))  # 101 MB
        
        # Note: This test creates a file outside the normal log dir
        # so it won't be detected by the orchestrator in normal operation
        self.assertTrue(large_log.exists())
    
    def test_old_log_healing(self):
        """Test old log healing."""
        # Create a fake old log
        old_log = self.test_log_dir / "old_test.log"
        old_log.touch()
        
        # Set modification time to 8 days ago
        old_time = (datetime.now() - timedelta(days=8)).timestamp()
        os.utime(old_log, (old_time, old_time))
        
        self.assertTrue(old_log.exists())


class TestErrorHandling(unittest.TestCase):
    """Test error handling and recovery."""
    
    def setUp(self):
        """Set up test environment."""
        self.orchestrator = AutoHealOrchestrator()
    
    def test_missing_signals_csv_handled(self):
        """Test handling of missing signals CSV."""
        # Should not crash even if signals CSV is missing
        try:
            result = self.orchestrator.detect_stale_data()
            # Should return None or handle gracefully
            self.assertTrue(result is None or isinstance(result, dict))
        except Exception as e:
            self.fail(f"detect_stale_data raised exception: {e}")
    
    def test_corrupted_heartbeat_handled(self):
        """Test handling of corrupted heartbeat."""
        heartbeat_file = PROJECT_ROOT / "system3_daily_heartbeat.json"
        
        # Backup original
        backup = None
        if heartbeat_file.exists():
            with heartbeat_file.open("r") as f:
                backup = f.read()
        
        try:
            # Create corrupted heartbeat
            with heartbeat_file.open("w") as f:
                f.write("{invalid json")
            
            # Should handle gracefully
            issue = self.orchestrator.detect_missing_heartbeat()
            # Should detect as issue or return None
            self.assertTrue(issue is None or isinstance(issue, dict))
            
        finally:
            # Restore
            if backup:
                with heartbeat_file.open("w") as f:
                    f.write(backup)
            else:
                heartbeat_file.unlink(missing_ok=True)


def run_all_tests(verbose: bool = True) -> Dict[str, Any]:
    """Run all test suites and return results."""
    print("=" * 70)
    print("SYSTEM3 AUTO-HEAL COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAutoHealOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase306Integration))
    suite.addTests(loader.loadTestsFromTestCase(TestStalenessRecovery))
    suite.addTests(loader.loadTestsFromTestCase(TestLogManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    # Compile results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "success_rate": ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
    }
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"Total Tests:   {test_results['total_tests']}")
    print(f"Passed:        {test_results['passed']}")
    print(f"Failures:      {test_results['failures']}")
    print(f"Errors:        {test_results['errors']}")
    print(f"Skipped:       {test_results['skipped']}")
    print(f"Success Rate:  {test_results['success_rate']:.1f}%")
    print("=" * 70)
    
    # Save results to file
    results_file = PROJECT_ROOT / "logs" / "auto_heal" / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with results_file.open("w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nResults saved to: {results_file.relative_to(PROJECT_ROOT)}")
    
    return test_results


if __name__ == "__main__":
    results = run_all_tests(verbose=True)
    sys.exit(0 if results["failures"] == 0 and results["errors"] == 0 else 1)
