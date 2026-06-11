"""
Test Suite for Ultimate AI Controller

Comprehensive testing of all AI Controller functionality.
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, time as dt_time

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from system3_ultimate_ai_controller import (
    DecisionEngine,
    HealthMonitor,
    AutoExecutor,
    UltimateAIController,
    SystemState,
)


class TestDecisionEngine(unittest.TestCase):
    """Test AI decision making engine."""
    
    def setUp(self):
        self.engine = DecisionEngine()
    
    def test_initialization(self):
        """Test engine initializes correctly."""
        self.assertIsInstance(self.engine, DecisionEngine)
        self.assertEqual(self.engine.state, SystemState.INITIALIZING)
    
    def test_context_analysis(self):
        """Test context analysis."""
        context = self.engine.analyze_context()
        
        self.assertIn("timestamp", context)
        self.assertIn("current_time", context)
        self.assertIn("is_market_hours", context)
        self.assertIn("is_pre_market", context)
        self.assertIn("is_weekend", context)
        
        self.assertIsInstance(context["is_market_hours"], bool)
        self.assertIsInstance(context["is_weekend"], bool)
    
    def test_decision_making(self):
        """Test AI decision making."""
        decision = self.engine.decide_action()
        
        self.assertIn("timestamp", decision)
        self.assertIn("context", decision)
        self.assertIn("actions", decision)
        self.assertIn("priority", decision)
        
        self.assertIsInstance(decision["actions"], list)
        self.assertIn(decision["priority"], ["low", "normal", "high", "critical"])


class TestHealthMonitor(unittest.TestCase):
    """Test health monitoring system."""
    
    def setUp(self):
        self.monitor = HealthMonitor()
    
    def test_initialization(self):
        """Test monitor initializes."""
        self.assertIsInstance(self.monitor, HealthMonitor)
        self.assertEqual(self.monitor.health_score, 100)
    
    def test_health_check(self):
        """Test health check execution."""
        health = self.monitor.check_system_health()
        
        self.assertIn("timestamp", health)
        self.assertIn("checks", health)
        self.assertIn("overall_score", health)
        self.assertIn("status", health)
        
        self.assertIsInstance(health["checks"], dict)
        self.assertGreaterEqual(health["overall_score"], 0)
        self.assertLessEqual(health["overall_score"], 100)
        self.assertIn(health["status"], ["healthy", "warning", "critical", "unknown"])


class TestAutoExecutor(unittest.TestCase):
    """Test automatic execution engine."""
    
    def setUp(self):
        self.executor = AutoExecutor()
    
    def test_initialization(self):
        """Test executor initializes."""
        self.assertIsInstance(self.executor, AutoExecutor)
        self.assertIsInstance(self.executor.execution_log, list)
        self.assertIsInstance(self.executor.running_processes, dict)


class TestUltimateAIController(unittest.TestCase):
    """Test ultimate AI controller."""
    
    def setUp(self):
        self.controller = UltimateAIController()
    
    def test_initialization(self):
        """Test controller initializes."""
        self.assertIsInstance(self.controller, UltimateAIController)
        self.assertIsInstance(self.controller.decision_engine, DecisionEngine)
        self.assertIsInstance(self.controller.health_monitor, HealthMonitor)
        self.assertIsInstance(self.controller.executor, AutoExecutor)
        self.assertFalse(self.controller.running)


def run_tests():
    """Run all tests."""
    print("=" * 70)
    print("ULTIMATE AI CONTROLLER - TEST SUITE")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDecisionEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestAutoExecutor))
    suite.addTests(loader.loadTestsFromTestCase(TestUltimateAIController))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run:  {result.testsRun}")
    print(f"Passed:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:   {len(result.failures)}")
    print(f"Errors:     {len(result.errors)}")
    print("=" * 70)
    
    return 0 if (len(result.failures) == 0 and len(result.errors) == 0) else 1


if __name__ == "__main__":
    sys.exit(run_tests())
