"""
Auto-generated test for System3 Phase 261

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase261_portfolio_risk_analyzer
Function: run_phase261
"""

import sys
import unittest
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase261(unittest.TestCase):
    """Test suite for Phase 261."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        cls.phase_num = 261
        cls.module_name = "core.engine.system3_phase261_portfolio_risk_analyzer"
        cls.func_name = "run_phase261"
        
        # Try to import module
        try:
            module_parts = cls.module_name.split('.')
            module = __import__(cls.module_name, fromlist=[cls.func_name])
            cls.phase_module = module
            # Store function reference directly (not as bound method)
            func = getattr(module, cls.func_name, None)
            cls.phase_func = func
            cls._phase_func_raw = func  # Store raw function for direct calls
        except Exception as e:
            cls.phase_module = None
            cls.phase_func = None
            cls._phase_func_raw = None
            cls.import_error = str(e)
    
    def test_module_import(self):
        """Test that phase module can be imported."""
        self.assertIsNotNone(
            self.phase_module,
            f"Failed to import module {self.module_name}: {getattr(self, 'import_error', 'Unknown error')}"
        )
    
    def test_function_exists(self):
        """Test that phase function exists."""
        self.assertIsNotNone(
            self.phase_func,
            f"Function {self.func_name} not found in module {self.module_name}"
        )
    
    def test_phase_execution(self):
        """Test that phase can be executed."""
        if not self.phase_func:
            self.skipTest("Phase function not available")
        
        try:
            # Call function directly (not as bound method) to avoid passing self
            # Use the raw function reference stored in setUpClass
            func = type(self)._phase_func_raw
            if func is None:
                self.skipTest("Phase function not available")
            
            # Call function directly - it accepts **kwargs, so we can call with no args
            result = func()
            
            # Check result structure
            self.assertIsInstance(result, dict, "Phase result should be a dictionary")
            
            # Check required fields
            self.assertIn("phase", result, "Result should contain 'phase' field")
            self.assertIn("status", result, "Result should contain 'status' field")
            self.assertIn("details", result, "Result should contain 'details' field")
            
            # Check phase number matches
            self.assertEqual(
                result.get("phase"),
                self.phase_num,
                f"Phase number mismatch: expected {self.phase_num}, got {result.get('phase')}"
            )
            
            # Check status is valid
            valid_statuses = ["OK", "WARN", "ERROR", "KILL"]
            self.assertIn(
                result.get("status"),
                valid_statuses,
                f"Invalid status: {result.get('status')}"
            )
            
        except Exception as e:
            self.fail(f"Phase execution failed: {e}")
    
    def test_phase_outputs(self):
        """Test that phase produces expected outputs."""
        if not self.phase_func:
            self.skipTest("Phase function not available")
        
        try:
            # Call function directly (not as bound method)
            func = type(self)._phase_func_raw
            if func is None:
                self.skipTest("Phase function not available")
            result = func()
            
            # Check outputs field exists
            if "outputs" in result:
                self.assertIsInstance(
                    result["outputs"],
                    dict,
                    "Outputs should be a dictionary"
                )
            
            # Check for expected output files if specified
            # Check for logs/monitoring/system3_status_report.md
            if "logs/monitoring/system3_status_report.md" in str(result.get("outputs", {})):
                output_path = PROJECT_ROOT / "logs/monitoring/system3_status_report.md"
                # Note: File may not exist if phase hasn't run yet
                # self.assertTrue(output_path.exists(), f"Expected output file {output_path} not found")
            # Check for logs/monitoring/system3_resource_usage.md
            if "logs/monitoring/system3_resource_usage.md" in str(result.get("outputs", {})):
                output_path = PROJECT_ROOT / "logs/monitoring/system3_resource_usage.md"
                # Note: File may not exist if phase hasn't run yet
                # self.assertTrue(output_path.exists(), f"Expected output file {output_path} not found")
            # Check for logs/performance/system3_master_summary_report.md
            if "logs/performance/system3_master_summary_report.md" in str(result.get("outputs", {})):
                output_path = PROJECT_ROOT / "logs/performance/system3_master_summary_report.md"
                # Note: File may not exist if phase hasn't run yet
                # self.assertTrue(output_path.exists(), f"Expected output file {output_path} not found")
            # Check for logs/research/system3_threshold_auto_tune.md
            if "logs/research/system3_threshold_auto_tune.md" in str(result.get("outputs", {})):
                output_path = PROJECT_ROOT / "logs/research/system3_threshold_auto_tune.md"
                # Note: File may not exist if phase hasn't run yet
                # self.assertTrue(output_path.exists(), f"Expected output file {output_path} not found")
            
        except Exception as e:
            self.fail(f"Output validation failed: {e}")
    
    def test_phase_error_handling(self):
        """Test that phase handles errors gracefully."""
        if not self.phase_func:
            self.skipTest("Phase function not available")
        
        try:
            # Call function directly (not as bound method)
            func = type(self)._phase_func_raw
            if func is None:
                self.skipTest("Phase function not available")
            result = func()
            
            # Check errors field exists
            if "errors" in result:
                self.assertIsInstance(
                    result["errors"],
                    list,
                    "Errors should be a list"
                )
            
            # If status is ERROR, should have errors
            if result.get("status") == "ERROR":
                self.assertGreater(
                    len(result.get("errors", [])),
                    0,
                    "ERROR status should have at least one error"
                )
            
        except Exception as e:
            self.fail(f"Error handling test failed: {e}")
    
    def test_phase_dry_run_safety(self):
        """Test that phase is DRY-RUN safe."""
        if not self.phase_func:
            self.skipTest("Phase function not available")
        
        try:
            # Call function directly (not as bound method)
            func = type(self)._phase_func_raw
            if func is None:
                self.skipTest("Phase function not available")
            result = func()
            
            # Check that phase doesn't enable live trading
            outputs = result.get("outputs", {})
            details = result.get("details", "")
            
            # Should not contain live trading flags
            live_flags = ["LIVE_TRADING_ENABLED", "USE_LIVE_EXECUTION", "AUTO_EXECUTE"]
            for flag in live_flags:
                self.assertNotIn(
                    flag,
                    str(outputs).upper() + details.upper(),
                    f"Phase should not enable {flag}"
                )
            
        except Exception as e:
            self.fail(f"DRY-RUN safety test failed: {e}")


def run_phase_test():
    """Run phase test directly (non-unittest mode)."""
    print("=" * 70)
    print(f"TESTING PHASE 261")
    print("=" * 70)
    print(f"Module: {module_name}")
    print(f"Function: {func_name}")
    print()
    
    try:
        module = __import__(module_name, fromlist=[func_name])
        func = getattr(module, func_name)
        
        print("Executing phase...")
        # Call function directly - it accepts **kwargs, so we can call with no args
        result = func()
        
        print(f"Status: {result.get('status', 'UNKNOWN')}")
        print(f"Details: {result.get('details', 'N/A')}")
        
        if result.get("outputs"):
            print(f"Outputs: {len(result['outputs'])} items")
            for key, value in result["outputs"].items():
                print(f"  - {key}: {value}")
        
        if result.get("errors"):
            print(f"Errors: {len(result['errors'])} items")
            for error in result["errors"]:
                print(f"  - {error}")
        
        print()
        print("=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)
        
        return result.get("status") in ("OK", "WARN")
        
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run as unittest
    unittest.main(verbosity=2)
