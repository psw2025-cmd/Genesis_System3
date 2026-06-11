#!/usr/bin/env python3
"""
System3 Comprehensive Verification
Tests all imports, paths, and basic functionality without subprocess.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

VERIFICATION_REPORT = PROJECT_ROOT / "docs" / "SYSTEM3_COMPREHENSIVE_VERIFICATION_REPORT.md"
FIX_SUMMARY = PROJECT_ROOT / "docs" / "SYSTEM3_VERIFICATION_FIXES.md"

results = []
fixes = []


def test_import(module_path: str, description: str) -> Tuple[bool, str]:
    """Test if a module can be imported."""
    try:
        if "/" in module_path or "\\" in module_path:
            # Convert file path to module path
            module_path = module_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        __import__(module_path)
        return True, "Import successful"
    except ImportError as e:
        return False, f"ImportError: {str(e)}"
    except Exception as e:
        return False, f"Exception: {type(e).__name__}: {str(e)}"


def test_file_exists(file_path: str, description: str) -> Tuple[bool, str]:
    """Test if a file exists."""
    full_path = PROJECT_ROOT / file_path
    if full_path.exists():
        size = full_path.stat().st_size
        return True, f"File exists ({size} bytes)"
    else:
        return False, "File does not exist"


def test_directory_exists(dir_path: str, description: str) -> Tuple[bool, str]:
    """Test if a directory exists."""
    full_path = PROJECT_ROOT / dir_path
    if full_path.exists() and full_path.is_dir():
        return True, "Directory exists"
    else:
        return False, "Directory does not exist"


def record_result(test_name: str, success: bool, message: str, fix_applied: str = None):
    """Record a test result."""
    results.append({
        "test": test_name,
        "success": success,
        "message": message,
        "fix": fix_applied,
    })
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}: {message}")
    if fix_applied:
        print(f"   Fix: {fix_applied}")
        fixes.append({"test": test_name, "fix": fix_applied})


def main():
    """Run comprehensive verification."""
    print("=" * 80)
    print("SYSTEM3 COMPREHENSIVE VERIFICATION")
    print("=" * 80)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Python: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print("=" * 80)
    print()
    
    # Test 1: Python path
    python_path = r"C:\Genesis_System3\venv\Scripts\python.exe"
    if os.path.exists(python_path):
        record_result("Python Path", True, f"Python found at: {python_path}")
    else:
        record_result("Python Path", False, f"Python not found at: {python_path}")
    
    # Test 2: Core directories
    directories = [
        ("core/", "Core directory"),
        ("core/engine/", "Engine directory"),
        ("core/phases/", "Phases directory"),
        ("storage/", "Storage directory"),
        ("storage/live/", "Live storage directory"),
        ("logs/", "Logs directory"),
        ("docs/", "Docs directory"),
    ]
    
    for dir_path, description in directories:
        success, message = test_directory_exists(dir_path, description)
        record_result(description, success, message)
    
    # Test 3: Critical script files
    scripts = [
        ("core/engine/system3_phase221_forward_returns.py", "Phase 221 script"),
        ("core/engine/system3_phase222_signal_edge.py", "Phase 222 script"),
        ("core/engine/angel_pnl_simulator.py", "PnL Simulator script"),
        ("system3_autorun_master.py", "Autorun master script"),
        ("system3_watchdog.py", "Watchdog script"),
        ("system3_live_day_autopilot.py", "Live autopilot script"),
    ]
    
    for script_path, description in scripts:
        success, message = test_file_exists(script_path, description)
        record_result(description, success, message)
    
    # Test 4: Import tests
    print("\n" + "=" * 80)
    print("IMPORT TESTS")
    print("=" * 80)
    
    imports_to_test = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("core.engine.system3_phase221_forward_returns", "Phase 221 module"),
        ("core.engine.system3_phase222_signal_edge", "Phase 222 module"),
        ("core.engine.angel_pnl_simulator", "PnL Simulator module"),
    ]
    
    for module_path, description in imports_to_test:
        success, message = test_import(module_path, description)
        record_result(f"Import {description}", success, message)
    
    # Test 5: Output files (if they should exist)
    output_files = [
        ("storage/live/angel_index_ai_signals.csv", "Signals CSV"),
        ("storage/live/angel_index_ai_signals_curated.csv", "Curated signals CSV"),
        ("storage/meta/system3_live_thresholds.json", "Live thresholds JSON"),
    ]
    
    print("\n" + "=" * 80)
    print("OUTPUT FILE TESTS")
    print("=" * 80)
    
    for file_path, description in output_files:
        success, message = test_file_exists(file_path, description)
        # Don't fail if optional files don't exist
        if not success:
            message += " (optional)"
        record_result(f"Output {description}", success, message)
    
    # Test 6: Batch files
    batch_files = [
        ("run_phase221.bat", "Phase 221 batch file"),
        ("run_phase222.bat", "Phase 222 batch file"),
        ("run_pnl_simulator.bat", "PnL Simulator batch file"),
        ("run_validation.bat", "Validation batch file"),
    ]
    
    print("\n" + "=" * 80)
    print("BATCH FILE TESTS")
    print("=" * 80)
    
    for batch_path, description in batch_files:
        success, message = test_file_exists(batch_path, description)
        record_result(description, success, message)
    
    # Generate report
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Fixes Applied: {len(fixes)}")
    
    # Write report
    report_lines = [
        "# System3 Comprehensive Verification Report\n",
        f"**Generated**: {datetime.now().isoformat()}\n\n",
        "---\n\n",
        "## Summary\n\n",
        f"- **Total Tests**: {len(results)}\n",
        f"- **Passed**: {passed}\n",
        f"- **Failed**: {failed}\n",
        f"- **Fixes Applied**: {len(fixes)}\n\n",
        "---\n\n",
        "## Test Results\n\n",
    ]
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        report_lines.append(f"### {result['test']}\n\n")
        report_lines.append(f"- **Status**: {status}\n")
        report_lines.append(f"- **Message**: {result['message']}\n")
        if result["fix"]:
            report_lines.append(f"- **Fix Applied**: {result['fix']}\n")
        report_lines.append("\n")
    
    if fixes:
        report_lines.append("---\n\n")
        report_lines.append("## Fixes Applied\n\n")
        for fix in fixes:
            report_lines.append(f"- **{fix['test']}**: {fix['fix']}\n")
        report_lines.append("\n")
    
    VERIFICATION_REPORT.parent.mkdir(parents=True, exist_ok=True)
    VERIFICATION_REPORT.write_text("".join(report_lines), encoding="utf-8")
    
    print(f"\n[INFO] Report written to: {VERIFICATION_REPORT}")
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Check report for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

