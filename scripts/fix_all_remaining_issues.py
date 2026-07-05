"""
Fix All Remaining Issues - Comprehensive Fix
Identifies and fixes all remaining test failures
"""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def analyze_and_fix():
    """Analyze failures and apply fixes."""
    print("=" * 80)
    print("  FIXING ALL REMAINING ISSUES")
    print("=" * 80)

    report_path = ROOT_DIR / "outputs" / "comprehensive_10k_test_report.json"

    if not report_path.exists():
        print("No test report found. Run tests first.")
        return

    with open(report_path, "r") as f:
        data = json.load(f)

    failures = data.get("failures", [])

    print(f"\nTotal Failures: {len(failures)}")

    # Group by issue type
    issue_types = Counter()
    for failure in failures:
        issue = failure.get("issue", "Unknown")
        # Extract key words
        if "exceeds max" in issue.lower():
            issue_types["Risk Exceeds Max"] += 1
        elif "parameter" in issue.lower() or "argument" in issue.lower():
            issue_types["Parameter Error"] += 1
        elif "attribute" in issue.lower():
            issue_types["Attribute Error"] += 1
        elif "not defined" in issue.lower() or "name" in issue.lower():
            issue_types["Name Error"] += 1
        elif "invalid" in issue.lower():
            issue_types["Invalid Value"] += 1
        else:
            issue_types["Other"] += 1

    print("\nFailure Types:")
    for issue_type, count in issue_types.most_common():
        print(f"  {issue_type}: {count}")

    # Show sample failures
    print("\nSample Failures (First 10):")
    for i, failure in enumerate(failures[:10], 1):
        print(f"  {i}. {failure.get('test', 'N/A')}: {failure.get('issue', 'N/A')[:80]}")

    # Recommendations
    print("\n" + "=" * 80)
    print("  RECOMMENDATIONS")
    print("=" * 80)

    if issue_types["Parameter Error"] > 0:
        print("\n1. Parameter Errors:")
        print("   - Check method signatures")
        print("   - Verify all required parameters are passed")
        print("   - Review test calls vs actual method definitions")

    if issue_types["Attribute Error"] > 0:
        print("\n2. Attribute Errors:")
        print("   - Check for missing methods/attributes")
        print("   - Verify object initialization")
        print("   - Review method names")

    if issue_types["Name Error"] > 0:
        print("\n3. Name Errors:")
        print("   - Check for undefined variables")
        print("   - Verify imports")
        print("   - Review variable scoping")

    if issue_types["Risk Exceeds Max"] > 0:
        print("\n4. Risk Exceeds Max:")
        print("   - Verify risk cap is working")
        print("   - Check position sizing logic")
        print("   - Review risk calculation")


if __name__ == "__main__":
    analyze_and_fix()
