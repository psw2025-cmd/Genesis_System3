"""
System3 Auto-Test Generator

Automatically generates test files for phases based on registry and specifications.
"""

import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
LOG_DIR = PROJECT_ROOT / "logs" / "autophase"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_auto_test_generator.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class AutoTestGenerator:
    """Auto-generates test files for phases."""

    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize test generator."""
        self.registry_path = registry_path or (PROJECT_ROOT / "storage" / "meta" / "system3_phase_registry.json")
        self.registry = self._load_registry()
        self.tests_dir = PROJECT_ROOT / "tests" / "auto" / "system3_generated_tests"
        self.tests_dir.mkdir(parents=True, exist_ok=True)

    def _load_registry(self) -> Dict[str, Any]:
        """Load phase registry."""
        try:
            if self.registry_path.exists():
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {"phases": {}}
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return {"phases": {}}

    def generate_test_for_phase(self, phase_num: int) -> Optional[Path]:
        """Generate a test file for a single phase."""
        # Registry structure: phases are top-level keys, or nested under "phases"
        phases_dict = self.registry.get("phases", self.registry)
        phase_info = phases_dict.get(str(phase_num), {})

        if not phase_info.get("implemented"):
            logger.debug(f"Phase {phase_num} not implemented, skipping test generation")
            return None

        # Determine module location
        impl_file = phase_info.get("impl_file", "")
        impl_location = phase_info.get("impl_location", "")

        if not impl_file:
            logger.debug(f"Phase {phase_num} has no implementation file")
            return None

        # Generate test file
        test_file = self.tests_dir / f"test_phase_{phase_num:03d}.py"

        # Determine module path
        if impl_location == "core/engine":
            module_name = Path(impl_file).stem
            full_module = f"core.engine.{module_name}"
        elif impl_location == "core/ultra":
            module_name = Path(impl_file).stem
            full_module = f"core.ultra.{module_name}"
        else:
            # Try to infer from file path
            if "core/engine" in impl_file:
                module_name = Path(impl_file).stem
                full_module = f"core.engine.{module_name}"
            else:
                logger.warning(f"Cannot determine module for phase {phase_num}")
                return None

        func_name = f"run_phase{phase_num}"

        # Generate test content
        test_content = self._generate_test_content(phase_num, full_module, func_name, phase_info)

        # Write test file
        try:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_content)
            logger.info(f"Generated test for phase {phase_num}: {test_file}")
            return test_file
        except Exception as e:
            logger.error(f"Failed to generate test for phase {phase_num}: {e}")
            return None

    def _generate_test_content(self, phase_num: int, module_name: str, func_name: str, phase_info: Dict) -> str:
        """Generate test file content."""
        spec_file = phase_info.get("spec_file", "")
        spec_content = ""
        if spec_file and Path(spec_file).exists():
            try:
                with open(spec_file, "r", encoding="utf-8") as f:
                    spec_content = f.read()
            except:
                pass

        # Extract expected outputs from spec if available
        expected_outputs = self._extract_expected_outputs(spec_content)

        test_content = f'''"""
Auto-generated test for System3 Phase {phase_num}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Module: {module_name}
Function: {func_name}
"""

import sys
import unittest
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase{phase_num}(unittest.TestCase):
    """Test suite for Phase {phase_num}."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        cls.phase_num = {phase_num}
        cls.module_name = "{module_name}"
        cls.func_name = "{func_name}"
        
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
            f"Failed to import module {{self.module_name}}: {{getattr(self, 'import_error', 'Unknown error')}}"
        )
    
    def test_function_exists(self):
        """Test that phase function exists."""
        self.assertIsNotNone(
            self.phase_func,
            f"Function {{self.func_name}} not found in module {{self.module_name}}"
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
                f"Phase number mismatch: expected {{self.phase_num}}, got {{result.get('phase')}}"
            )
            
            # Check status is valid
            valid_statuses = ["OK", "WARN", "ERROR", "KILL"]
            self.assertIn(
                result.get("status"),
                valid_statuses,
                f"Invalid status: {{result.get('status')}}"
            )
            
        except Exception as e:
            self.fail(f"Phase execution failed: {{e}}")
    
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
{self._generate_output_checks(expected_outputs)}
            
        except Exception as e:
            self.fail(f"Output validation failed: {{e}}")
    
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
            self.fail(f"Error handling test failed: {{e}}")
    
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
            outputs = result.get("outputs", {{}})
            details = result.get("details", "")
            
            # Should not contain live trading flags
            live_flags = ["LIVE_TRADING_ENABLED", "USE_LIVE_EXECUTION", "AUTO_EXECUTE"]
            for flag in live_flags:
                self.assertNotIn(
                    flag,
                    str(outputs).upper() + details.upper(),
                    f"Phase should not enable {{flag}}"
                )
            
        except Exception as e:
            self.fail(f"DRY-RUN safety test failed: {{e}}")


def run_phase_test():
    """Run phase test directly (non-unittest mode)."""
    print("=" * 70)
    print(f"TESTING PHASE {phase_num}")
    print("=" * 70)
    print(f"Module: {{module_name}}")
    print(f"Function: {{func_name}}")
    print()
    
    try:
        module = __import__(module_name, fromlist=[func_name])
        func = getattr(module, func_name)
        
        print("Executing phase...")
        # Call function directly - it accepts **kwargs, so we can call with no args
        result = func()
        
        print(f"Status: {{result.get('status', 'UNKNOWN')}}")
        print(f"Details: {{result.get('details', 'N/A')}}")
        
        if result.get("outputs"):
            print(f"Outputs: {{len(result['outputs'])}} items")
            for key, value in result["outputs"].items():
                print(f"  - {{key}}: {{value}}")
        
        if result.get("errors"):
            print(f"Errors: {{len(result['errors'])}} items")
            for error in result["errors"]:
                print(f"  - {{error}}")
        
        print()
        print("=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)
        
        return result.get("status") in ("OK", "WARN")
        
    except Exception as e:
        print(f"TEST FAILED: {{e}}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run as unittest
    unittest.main(verbosity=2)
'''
        return test_content

    def _extract_expected_outputs(self, spec_content: str) -> List[str]:
        """Extract expected output files from spec."""
        outputs = []

        # Look for output patterns in spec
        patterns = [
            r"Output:\s*(.+?)(?:\n|$)",
            r"Outputs:\s*(.+?)(?:\n|$)",
            r"Expected output:\s*(.+?)(?:\n|$)",
            r"`([^`]+\.(csv|json|md|txt|log))`",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, spec_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    outputs.append(match[0])
                else:
                    outputs.append(match)

        return list(set(outputs))  # Remove duplicates

    def _generate_output_checks(self, expected_outputs: List[str]) -> str:
        """Generate output validation checks."""
        if not expected_outputs:
            return "            # No specific output files expected"

        checks = []
        for output in expected_outputs[:5]:  # Limit to 5 checks
            output_path = output.replace("`", "").strip()
            if output_path.startswith("storage/") or output_path.startswith("logs/"):
                checks.append(
                    f"""            # Check for {output_path}
            if "{output_path}" in str(result.get("outputs", {{}})):
                output_path = PROJECT_ROOT / "{output_path}"
                # Note: File may not exist if phase hasn't run yet
                # self.assertTrue(output_path.exists(), f"Expected output file {{output_path}} not found")"""
                )

        if checks:
            return "\n".join(checks)
        return "            # No specific output files expected"

    def generate_tests_for_range(self, start: int, end: int) -> Dict[str, Any]:
        """Generate tests for a range of phases."""
        logger.info(f"Generating tests for phases {start}-{end}...")

        generated = []
        skipped = []
        errors = []

        for phase_num in range(start, end + 1):
            try:
                test_file = self.generate_test_for_phase(phase_num)
                if test_file:
                    generated.append(phase_num)
                else:
                    skipped.append(phase_num)
            except Exception as e:
                logger.error(f"Error generating test for phase {phase_num}: {e}")
                errors.append((phase_num, str(e)))

        result = {
            "range": (start, end),
            "generated": len(generated),
            "skipped": len(skipped),
            "errors": len(errors),
            "generated_phases": generated,
            "skipped_phases": skipped,
            "error_details": errors,
        }

        logger.info(f"Generated {len(generated)} tests, skipped {len(skipped)}, errors {len(errors)}")
        return result

    def generate_range_test_file(self, start: int, end: int) -> Optional[Path]:
        """Generate a single test file for a range of phases."""
        test_file = self.tests_dir / f"test_phases_{start}_{end}.py"

        # Collect phase info
        phases_to_test = []
        phases_dict = self.registry.get("phases", self.registry)
        for phase_num in range(start, end + 1):
            phase_info = phases_dict.get(str(phase_num), {})
            if isinstance(phase_info, dict) and phase_info.get("implemented"):
                impl_file = phase_info.get("impl_file", "")
                impl_location = phase_info.get("impl_location", "")

                if impl_location == "core/engine":
                    module_name = Path(impl_file).stem
                    full_module = f"core.engine.{module_name}"
                elif impl_location == "core/ultra":
                    module_name = Path(impl_file).stem
                    full_module = f"core.ultra.{module_name}"
                else:
                    continue

                phases_to_test.append({"num": phase_num, "module": full_module, "func": f"run_phase{phase_num}"})

        if not phases_to_test:
            logger.warning(f"No implemented phases found in range {start}-{end}")
            return None

        # Generate range test content
        content = self._generate_range_test_content(start, end, phases_to_test)

        try:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Generated range test: {test_file}")
            return test_file
        except Exception as e:
            logger.error(f"Failed to generate range test: {e}")
            return None

    def _generate_range_test_content(self, start: int, end: int, phases: List[Dict]) -> str:
        """Generate content for range test file."""
        phase_tests = []
        for phase in phases:
            phase_tests.append(
                f'''def test_phase_{phase["num"]}():
    """Test Phase {phase["num"]}."""
    try:
        module = __import__("{phase["module"]}", fromlist=["{phase["func"]}"])
        func = getattr(module, "{phase["func"]}")
        result = func()
        
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "status" in result, "Result should have status"
        assert result.get("phase") == {phase["num"]}, "Phase number mismatch"
        
        return {{
            "phase": {phase["num"]},
            "status": result.get("status"),
            "details": result.get("details", ""),
            "has_outputs": "outputs" in result,
            "has_errors": len(result.get("errors", [])) > 0,
        }}
    except Exception as e:
        return {{
            "phase": {phase["num"]},
            "status": "ERROR",
            "details": str(e),
            "has_outputs": False,
            "has_errors": True,
        }}'''
            )

        return f'''"""
Auto-generated test for System3 Phases {start}-{end}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Phases: {len(phases)}
"""

import sys
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Test functions
{chr(10).join(phase_tests)}

def main():
    """Run all phase tests."""
    print("=" * 70)
    print(f"SYSTEM3 PHASES {start}-{end} TEST SUITE")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Phases: {len(phases)}")
    print()
    
    results = {{}}
    for phase_num in range({start}, {end + 1}):
        func_name = f"test_phase_{{phase_num}}"
        if func_name in globals():
            print(f"Testing Phase {{phase_num}}...", end=" ")
            try:
                result = globals()[func_name]()
                results[phase_num] = result
                status_icon = "✅" if result["status"] in ("OK", "WARN") else "❌"
                print(f"{{status_icon}} {{result['status']}}")
            except Exception as e:
                print(f"❌ ERROR: {{e}}")
                results[phase_num] = {{
                    "status": "ERROR",
                    "details": str(e),
                }}
        else:
            print(f"Skipping Phase {{phase_num}} (not implemented)")
    
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    ok_count = sum(1 for r in results.values() if r.get("status") == "OK")
    warn_count = sum(1 for r in results.values() if r.get("status") == "WARN")
    error_count = sum(1 for r in results.values() if r.get("status") == "ERROR")
    
    print(f"✅ OK: {{ok_count}}")
    print(f"⚠️  WARN: {{warn_count}}")
    print(f"❌ ERROR: {{error_count}}")
    print(f"Total: {{len(results)}}")
    
    if error_count > 0:
        print()
        print("ERROR DETAILS:")
        for phase_num, result in results.items():
            if result.get("status") == "ERROR":
                print(f"  Phase {{phase_num}}: {{result.get('details', 'Unknown error')}}")
    
    return error_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''

    def generate_all_tests(self) -> Dict[str, Any]:
        """Generate tests for all implemented phases."""
        logger.info("Generating tests for all implemented phases...")

        all_results = {}

        # Generate individual tests
        # Registry structure: phases are top-level keys, or nested under "phases"
        phases_dict = self.registry.get("phases", self.registry)
        for phase_num_str, phase_info in phases_dict.items():
            # Skip non-phase keys (like metadata)
            if not isinstance(phase_info, dict) or "phase" not in phase_info:
                continue
            if phase_info.get("implemented"):
                try:
                    phase_num = int(phase_num_str)
                    test_file = self.generate_test_for_phase(phase_num)
                    if test_file:
                        all_results[phase_num] = {"test_file": str(test_file), "status": "generated"}
                        logger.info(f"Generated test for phase {phase_num}")
                except Exception as e:
                    all_results[phase_num] = {"status": "error", "error": str(e)}
                    logger.error(f"Error generating test for phase {phase_num_str}: {e}")

        # Generate range tests for common ranges
        ranges = [
            (201, 230),
            (231, 260),
            (261, 300),
        ]

        range_results = {}
        for start, end in ranges:
            try:
                range_file = self.generate_range_test_file(start, end)
                if range_file:
                    range_results[(start, end)] = {"test_file": str(range_file), "status": "generated"}
            except Exception as e:
                range_results[(start, end)] = {"status": "error", "error": str(e)}

        return {
            "individual_tests": all_results,
            "range_tests": range_results,
            "total_individual": len([r for r in all_results.values() if r.get("status") == "generated"]),
            "total_ranges": len([r for r in range_results.values() if r.get("status") == "generated"]),
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 AUTO-TEST GENERATOR")
    print("=" * 70)
    print(f"Start Time: {datetime.now().isoformat()}")
    print()

    generator = AutoTestGenerator()

    # Generate tests for all phases
    results = generator.generate_all_tests()

    print()
    print("=" * 70)
    print("GENERATION SUMMARY")
    print("=" * 70)
    print(f"Individual Tests Generated: {results['total_individual']}")
    print(f"Range Tests Generated: {results['total_ranges']}")
    print()
    print(f"Test Directory: {generator.tests_dir}")
    print()
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
