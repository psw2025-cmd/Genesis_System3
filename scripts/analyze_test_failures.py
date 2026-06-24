"""
Analyze Test Failures - Identify Root Causes
"""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def analyze_failures():
    """Analyze test failures."""
    report_path = ROOT_DIR / "outputs" / "comprehensive_10k_test_report.json"

    if not report_path.exists():
        print("Test report not found. Run tests first.")
        return

    with open(report_path, "r") as f:
        data = json.load(f)

    failures = data.get("failures", [])

    print("=" * 80)
    print("  TEST FAILURE ANALYSIS")
    print("=" * 80)

    print(f"\nTotal Tests: {data.get('total_tests', 0)}")
    print(f"Passed: {data.get('total_passed', 0)}")
    print(f"Failed: {data.get('total_failed', 0)}")
    print(f"Pass Rate: {data.get('pass_rate', 0):.2f}%")

    # Group failures by test type
    test_types = Counter()
    issue_types = Counter()

    for failure in failures:
        test_name = failure.get("test", "Unknown")
        issue = failure.get("issue", "Unknown")

        # Extract test suite name
        if "Position Sizing" in test_name:
            test_types["Position Sizing"] += 1
        elif "Risk Management" in test_name:
            test_types["Risk Management"] += 1
        elif "Strategy Engine" in test_name:
            test_types["Strategy Engine"] += 1
        elif "Paper Executor" in test_name:
            test_types["Paper Executor"] += 1
        elif "PnL Tracker" in test_name:
            test_types["PnL Tracker"] += 1
        elif "End-to-End" in test_name:
            test_types["End-to-End"] += 1
        elif "Configuration" in test_name:
            test_types["Configuration"] += 1
        elif "Edge Case" in test_name:
            test_types["Edge Cases"] += 1

        # Extract issue type
        if "exceeds max" in issue.lower():
            issue_types["Risk Exceeds Max"] += 1
        elif "quantity" in issue.lower() and "0" in issue:
            issue_types["Quantity is 0"] += 1
        elif "invalid" in issue.lower():
            issue_types["Invalid Values"] += 1
        elif "error" in issue.lower() or "exception" in issue.lower():
            issue_types["Exceptions"] += 1
        elif "missing" in issue.lower():
            issue_types["Missing Data"] += 1
        else:
            issue_types["Other"] += 1

    print("\n" + "=" * 80)
    print("  FAILURES BY TEST SUITE")
    print("=" * 80)
    for test_type, count in test_types.most_common():
        print(f"  {test_type}: {count}")

    print("\n" + "=" * 80)
    print("  FAILURES BY ISSUE TYPE")
    print("=" * 80)
    for issue_type, count in issue_types.most_common():
        print(f"  {issue_type}: {count}")

    # Show sample failures
    print("\n" + "=" * 80)
    print("  SAMPLE FAILURES (First 20)")
    print("=" * 80)
    for i, failure in enumerate(failures[:20], 1):
        print(f"\n{i}. {failure.get('test', 'N/A')}")
        print(f"   Issue: {failure.get('issue', 'N/A')}")

    # Recommendations
    print("\n" + "=" * 80)
    print("  RECOMMENDATIONS")
    print("=" * 80)

    if issue_types["Risk Exceeds Max"] > 0:
        print("\n1. Risk Exceeds Max:")
        print("   - Review risk calculation logic")
        print("   - Check max_risk_per_trade_pct limits")
        print("   - Validate position sizing constraints")

    if issue_types["Quantity is 0"] > 0:
        print("\n2. Quantity is 0:")
        print("   - Check position sizing calculation")
        print("   - Verify lot_size handling")
        print("   - Ensure minimum quantity constraints")

    if issue_types["Exceptions"] > 0:
        print("\n3. Exceptions:")
        print("   - Review error handling")
        print("   - Add input validation")
        print("   - Check for None/NaN values")

    if issue_types["Invalid Values"] > 0:
        print("\n4. Invalid Values:")
        print("   - Add input validation")
        print("   - Check for edge cases")
        print("   - Validate data types")


if __name__ == "__main__":
    analyze_failures()
