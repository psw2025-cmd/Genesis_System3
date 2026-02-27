"""
Multi-Test Runner - Run tests multiple times and verify
"""

import sys
from pathlib import Path
import subprocess
import json
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def run_test_suite():
    """Run comprehensive test suite."""
    print("=" * 80)
    print("  RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    result = subprocess.run(
        [sys.executable, "scripts/comprehensive_10k_test_suite.py"], cwd=ROOT_DIR, capture_output=True, text=True
    )

    return result.returncode, result.stdout, result.stderr


def run_system_test():
    """Run comprehensive system test."""
    print("\n" + "=" * 80)
    print("  RUNNING COMPREHENSIVE SYSTEM TEST")
    print("=" * 80)

    result = subprocess.run(
        [sys.executable, "scripts/comprehensive_system_test.py"], cwd=ROOT_DIR, capture_output=True, text=True
    )

    return result.returncode, result.stdout, result.stderr


def run_validator():
    """Run complete system validator."""
    print("\n" + "=" * 80)
    print("  RUNNING COMPLETE SYSTEM VALIDATOR")
    print("=" * 80)

    result = subprocess.run(
        [sys.executable, "scripts/complete_system_validator.py"], cwd=ROOT_DIR, capture_output=True, text=True
    )

    return result.returncode, result.stdout, result.stderr


def check_test_results():
    """Check test results from JSON."""
    report_path = ROOT_DIR / "outputs" / "comprehensive_10k_test_report.json"

    if not report_path.exists():
        return None

    with open(report_path, "r") as f:
        data = json.load(f)

    return data


def main():
    """Run all tests multiple times."""
    print("=" * 80)
    print("  MULTI-TEST RUNNER - COMPREHENSIVE VERIFICATION")
    print("=" * 80)

    results = []

    # Run test suite
    print("\n[TEST RUN 1] Comprehensive 10K Test Suite")
    code, stdout, stderr = run_test_suite()
    print(stdout)
    if stderr:
        print("STDERR:", stderr)

    test_data = check_test_results()
    if test_data:
        print(f"\n  Results: {test_data.get('total_passed', 0)}/{test_data.get('total_tests', 0)} passed")
        print(f"  Pass Rate: {test_data.get('pass_rate', 0):.2f}%")
        results.append(("10K Test Suite", test_data))

    # Run system test
    print("\n[TEST RUN 2] Comprehensive System Test")
    code, stdout, stderr = run_system_test()
    print(stdout)
    if stderr:
        print("STDERR:", stderr)
    results.append(("System Test", {"code": code}))

    # Run validator
    print("\n[TEST RUN 3] Complete System Validator")
    code, stdout, stderr = run_validator()
    print(stdout)
    if stderr:
        print("STDERR:", stderr)
    results.append(("Validator", {"code": code}))

    # Summary
    print("\n" + "=" * 80)
    print("  FINAL SUMMARY")
    print("=" * 80)

    for name, data in results:
        if isinstance(data, dict) and "total_tests" in data:
            passed = data.get("total_passed", 0)
            total = data.get("total_tests", 0)
            rate = data.get("pass_rate", 0)
            print(f"\n{name}:")
            print(f"  Passed: {passed}/{total}")
            print(f"  Pass Rate: {rate:.2f}%")
            if data.get("total_failed", 0) > 0:
                print(f"  Failed: {data.get('total_failed', 0)}")
        else:
            code = data.get("code", 0)
            status = "PASS" if code == 0 else "FAIL"
            print(f"\n{name}: {status}")

    # Overall status
    all_passed = all(
        (isinstance(d, dict) and d.get("total_failed", 0) == 0) or (isinstance(d, dict) and d.get("code", 0) == 0)
        for _, d in results
    )

    if all_passed:
        print("\n  STATUS: ALL TESTS PASSED")
    else:
        print("\n  STATUS: SOME TESTS FAILED - REVIEW REQUIRED")


if __name__ == "__main__":
    main()
