"""
System3 Autorun Integration Test Suite

Tests START_AUTORUN_AND_WATCHDOG.bat integration with all safety checks
in various scenarios.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any, List, Tuple

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
META_DIR = PROJECT_ROOT / "storage" / "meta"
THRESHOLDS_JSON = META_DIR / "system3_live_thresholds.json"
BATCH_FILE = PROJECT_ROOT / "START_AUTORUN_AND_WATCHDOG.bat"

# Test results
TEST_RESULTS: List[Dict[str, Any]] = []


def log_test(name: str, status: str, details: str = ""):
    """Log test result."""
    result = {
        "name": name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    TEST_RESULTS.append(result)
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{status_icon} {name}: {status}")
    if details:
        print(f"   {details}")


def test_file_exists(file_path: Path, description: str) -> bool:
    """Test if file exists."""
    if file_path.exists():
        log_test(f"File exists: {description}", "PASS", str(file_path))
        return True
    else:
        log_test(f"File exists: {description}", "FAIL", f"Missing: {file_path}")
        return False


def test_thresholds_json_structure() -> bool:
    """Test thresholds JSON structure."""
    try:
        if not THRESHOLDS_JSON.exists():
            log_test("Thresholds JSON exists", "FAIL", "File not found")
            return False
        
        with THRESHOLDS_JSON.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Check structure
        checks = []
        if "global" in data:
            checks.append("global key exists")
            if "buy" in data["global"] and "sell" in data["global"]:
                checks.append("global thresholds present")
        else:
            log_test("Thresholds JSON structure", "FAIL", "Missing 'global' key")
            return False
        
        if "per_underlying" in data:
            checks.append("per_underlying key exists")
        else:
            log_test("Thresholds JSON structure", "FAIL", "Missing 'per_underlying' key")
            return False
        
        log_test("Thresholds JSON structure", "PASS", ", ".join(checks))
        return True
        
    except json.JSONDecodeError as e:
        log_test("Thresholds JSON structure", "FAIL", f"Invalid JSON: {e}")
        return False
    except Exception as e:
        log_test("Thresholds JSON structure", "FAIL", f"Error: {e}")
        return False


def test_batch_file_structure() -> bool:
    """Test batch file structure."""
    if not BATCH_FILE.exists():
        log_test("Batch file exists", "FAIL", "START_AUTORUN_AND_WATCHDOG.bat not found")
        return False
    
    try:
        content = BATCH_FILE.read_text(encoding="utf-8")
        
        checks = []
        
        # Check for pre-market checks
        if "validate_live_thresholds.py" in content:
            checks.append("threshold validation check")
        else:
            log_test("Batch file structure", "FAIL", "Missing threshold validation check")
            return False
        
        if "pre_market_signal_dryrun.py" in content:
            checks.append("pre-market dry-run check")
        else:
            log_test("Batch file structure", "FAIL", "Missing pre-market dry-run check")
            return False
        
        if "system3_signal_engine_self_test.py" in content:
            checks.append("self-test check")
        else:
            log_test("Batch file structure", "FAIL", "Missing self-test check")
            return False
        
        # Check for error handling
        if "ERRORLEVEL" in content:
            checks.append("error handling")
        else:
            log_test("Batch file structure", "WARN", "No error handling found")
        
        # Check for watchdog start
        if "system3_watchdog.py" in content:
            checks.append("watchdog start")
        else:
            log_test("Batch file structure", "WARN", "Watchdog start not found")
        
        # Check for master start
        if "system3_autorun_master.py" in content:
            checks.append("master start")
        else:
            log_test("Batch file structure", "FAIL", "Master start not found")
            return False
        
        log_test("Batch file structure", "PASS", ", ".join(checks))
        return True
        
    except Exception as e:
        log_test("Batch file structure", "FAIL", f"Error reading file: {e}")
        return False


def test_validation_modules_exist() -> bool:
    """Test validation modules exist."""
    modules = [
        ("core/validation/validate_live_thresholds.py", "Threshold validation"),
        ("core/validation/pre_market_signal_dryrun.py", "Pre-market dry-run"),
        ("core/engine/system3_signal_engine_self_test.py", "Self-test"),
        ("core/validation/post_close_signal_audit.py", "Post-close audit"),
    ]
    
    all_exist = True
    for module_path, description in modules:
        full_path = PROJECT_ROOT / module_path
        if full_path.exists():
            log_test(f"Module exists: {description}", "PASS", str(module_path))
        else:
            log_test(f"Module exists: {description}", "FAIL", f"Missing: {module_path}")
            all_exist = False
    
    return all_exist


def test_autorun_master_integration() -> bool:
    """Test autorun master has post-close audit integration."""
    master_file = PROJECT_ROOT / "system3_autorun_master.py"
    
    if not master_file.exists():
        log_test("Autorun master integration", "FAIL", "Master file not found")
        return False
    
    try:
        content = master_file.read_text(encoding="utf-8")
        
        if "post_close_signal_audit" in content:
            log_test("Autorun master integration", "PASS", "Post-close audit integrated")
            return True
        else:
            log_test("Autorun master integration", "FAIL", "Post-close audit not integrated")
            return False
            
    except Exception as e:
        log_test("Autorun master integration", "FAIL", f"Error: {e}")
        return False


def test_python_paths() -> bool:
    """Test Python paths in batch file."""
    if not BATCH_FILE.exists():
        return False
    
    try:
        content = BATCH_FILE.read_text(encoding="utf-8")
        
        # Check for canonical Python path
        if r"C:\Genesis_System3\venv\Scripts\python.exe" in content:
            log_test("Python paths", "PASS", "Canonical Python path used")
            return True
        elif "python.exe" in content:
            log_test("Python paths", "WARN", "Python path may not be canonical")
            return True
        else:
            log_test("Python paths", "FAIL", "No Python path found")
            return False
            
    except Exception as e:
        log_test("Python paths", "FAIL", f"Error: {e}")
        return False


def test_error_handling() -> bool:
    """Test error handling in batch file."""
    if not BATCH_FILE.exists():
        return False
    
    try:
        content = BATCH_FILE.read_text(encoding="utf-8")
        
        checks = []
        
        # Check for exit codes
        if "ERRORLEVEL" in content:
            checks.append("error level checking")
        else:
            log_test("Error handling", "WARN", "No ERRORLEVEL checks found")
        
        # Check for exit on failure
        if "exit /b 1" in content or "exit /b 0" in content:
            checks.append("exit codes")
        else:
            log_test("Error handling", "WARN", "No exit codes found")
        
        # Check for error messages
        if "FAILED" in content or "DO NOT START" in content:
            checks.append("error messages")
        else:
            log_test("Error handling", "WARN", "No error messages found")
        
        if checks:
            log_test("Error handling", "PASS", ", ".join(checks))
            return True
        else:
            log_test("Error handling", "WARN", "Limited error handling")
            return True
            
    except Exception as e:
        log_test("Error handling", "FAIL", f"Error: {e}")
        return False


def test_workflow_sequence() -> bool:
    """Test workflow sequence is correct."""
    if not BATCH_FILE.exists():
        return False
    
    try:
        content = BATCH_FILE.read_text(encoding="utf-8")
        
        # Expected sequence
        sequence = [
            "validate_live_thresholds.py",
            "pre_market_signal_dryrun.py",
            "system3_signal_engine_self_test.py",
            "system3_watchdog.py",
            "system3_autorun_master.py"
        ]
        
        positions = []
        for item in sequence:
            pos = content.find(item)
            if pos == -1:
                log_test("Workflow sequence", "FAIL", f"Missing: {item}")
                return False
            positions.append((pos, item))
        
        # Check order
        for i in range(len(positions) - 1):
            if positions[i][0] > positions[i+1][0]:
                log_test("Workflow sequence", "FAIL", 
                        f"Wrong order: {positions[i][1]} after {positions[i+1][1]}")
                return False
        
        log_test("Workflow sequence", "PASS", "All checks in correct order")
        return True
        
    except Exception as e:
        log_test("Workflow sequence", "FAIL", f"Error: {e}")
        return False


def generate_test_report() -> str:
    """Generate test report."""
    total = len(TEST_RESULTS)
    passed = sum(1 for r in TEST_RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in TEST_RESULTS if r["status"] == "FAIL")
    warned = sum(1 for r in TEST_RESULTS if r["status"] == "WARN")
    
    lines = [
        "# System3 Autorun Integration Test Report\n",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "\n## Summary\n",
        f"- **Total Tests**: {total}\n",
        f"- **Passed**: {passed} ✅\n",
        f"- **Failed**: {failed} ❌\n",
        f"- **Warnings**: {warned} ⚠️\n",
        "\n## Test Results\n",
        "| Test | Status | Details |\n",
        "|------|--------|---------|\n"
    ]
    
    for result in TEST_RESULTS:
        status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
        lines.append(
            f"| {result['name']} | {status_icon} {result['status']} | {result['details']} |\n"
        )
    
    # Overall verdict
    lines.append("\n## Overall Verdict\n")
    if failed == 0:
        lines.append("✅ **ALL TESTS PASSED** - Integration is ready\n")
    elif failed <= 2:
        lines.append("⚠️ **MOSTLY PASSED** - Minor issues detected\n")
    else:
        lines.append("❌ **TESTS FAILED** - Issues need to be fixed\n")
    
    return "".join(lines)


def main() -> int:
    """Run all tests."""
    print("=" * 80)
    print("SYSTEM3 AUTORUN INTEGRATION TEST SUITE")
    print("=" * 80)
    print()
    
    # Run tests
    print("Running tests...\n")
    
    test_file_exists(BATCH_FILE, "START_AUTORUN_AND_WATCHDOG.bat")
    test_file_exists(THRESHOLDS_JSON, "system3_live_thresholds.json")
    test_batch_file_structure()
    test_thresholds_json_structure()
    test_validation_modules_exist()
    test_autorun_master_integration()
    test_python_paths()
    test_error_handling()
    test_workflow_sequence()
    
    # Generate report
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total = len(TEST_RESULTS)
    passed = sum(1 for r in TEST_RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in TEST_RESULTS if r["status"] == "FAIL")
    warned = sum(1 for r in TEST_RESULTS if r["status"] == "WARN")
    
    print(f"Total: {total} | Passed: {passed} ✅ | Failed: {failed} ❌ | Warnings: {warned} ⚠️")
    print()
    
    # Save report
    report_path = PROJECT_ROOT / "docs" / "SYSTEM3_AUTORUN_INTEGRATION_TEST_REPORT.md"
    report = generate_test_report()
    
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to: {report_path}")
    except Exception as e:
        print(f"Failed to save report: {e}")
    
    # Final verdict
    print("\n" + "=" * 80)
    if failed == 0:
        print("✅ ALL TESTS PASSED - Integration is ready")
        return 0
    else:
        print(f"❌ {failed} TEST(S) FAILED - Review issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

