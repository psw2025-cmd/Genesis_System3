"""
Run Complete Verification - Multiple Test Runs
"""

import sys
import subprocess
from pathlib import Path
import json

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def run_tests():
    """Run all tests and collect results."""
    print("=" * 80)
    print("  COMPLETE VERIFICATION - MULTIPLE TEST RUNS")
    print("=" * 80)

    results = []

    # Run 1: Comprehensive 10K Test Suite
    print("\n[RUN 1] Comprehensive 10K Test Suite")
    result = subprocess.run(
        [sys.executable, "scripts/comprehensive_10k_test_suite.py"], cwd=ROOT_DIR, capture_output=True, text=True
    )

    # Parse results
    report_path = ROOT_DIR / "outputs" / "comprehensive_10k_test_report.json"
    if report_path.exists():
        with open(report_path, "r") as f:
            data = json.load(f)
        results.append(
            {
                "name": "10K Test Suite",
                "total": data.get("total_tests", 0),
                "passed": data.get("total_passed", 0),
                "failed": data.get("total_failed", 0),
                "rate": data.get("pass_rate", 0),
            }
        )
        print(
            f"  Results: {data.get('total_passed', 0)}/{data.get('total_tests', 0)} passed ({data.get('pass_rate', 0):.2f}%)"
        )

    # Run 2: System Test
    print("\n[RUN 2] Comprehensive System Test")
    result = subprocess.run(
        [sys.executable, "scripts/comprehensive_system_test.py"], cwd=ROOT_DIR, capture_output=True, text=True
    )
    results.append(
        {"name": "System Test", "code": result.returncode, "status": "PASS" if result.returncode == 0 else "FAIL"}
    )
    print(f"  Status: {'PASS' if result.returncode == 0 else 'FAIL'}")

    # Run 3: Validator
    print("\n[RUN 3] Complete System Validator")
    result = subprocess.run(
        [sys.executable, "scripts/complete_system_validator.py"], cwd=ROOT_DIR, capture_output=True, text=True
    )
    results.append(
        {"name": "Validator", "code": result.returncode, "status": "PASS" if result.returncode == 0 else "FAIL"}
    )
    print(f"  Status: {'PASS' if result.returncode == 0 else 'FAIL'}")

    # Summary
    print("\n" + "=" * 80)
    print("  FINAL SUMMARY")
    print("=" * 80)

    for r in results:
        if "total" in r:
            print(f"\n{r['name']}:")
            print(f"  Passed: {r['passed']}/{r['total']}")
            print(f"  Failed: {r['failed']}")
            print(f"  Pass Rate: {r['rate']:.2f}%")
        else:
            print(f"\n{r['name']}: {r['status']}")

    # Overall status
    all_passed = all((r.get("failed", 0) == 0) or (r.get("status") == "PASS") for r in results)

    if all_passed:
        print("\n  STATUS: ALL TESTS PASSED")
    else:
        print("\n  STATUS: SOME TESTS FAILED - REVIEW REQUIRED")


if __name__ == "__main__":
    run_tests()
