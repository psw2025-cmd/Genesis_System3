"""
Comprehensive CSV Verification - All Conditions and Situations
Runs all verification tests and scenarios
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def main():
    """Run all verification tests."""
    print("\n" + "=" * 80)
    print("  COMPREHENSIVE CSV VERIFICATION - ALL CONDITIONS")
    print("=" * 80)

    # Import and run all verification modules
    from scripts.multi_verify_all_conditions import MultiVerifier
    from scripts.test_csv_edge_cases import main as test_edge_cases
    from scripts.test_csv_write_scenarios import main as test_write_scenarios

    print("\n" + "=" * 80)
    print("  PHASE 1: MULTI-VERIFICATION (All Conditions)")
    print("=" * 80)
    verifier = MultiVerifier()
    verifier.verify_paper_trades()
    verifier.verify_chain_raw()
    verifier.verify_underlying_rank()
    verifier.print_results()

    print("\n" + "=" * 80)
    print("  PHASE 2: EDGE CASES TEST")
    print("=" * 80)
    edge_results = test_edge_cases()

    print("\n" + "=" * 80)
    print("  PHASE 3: WRITE SCENARIOS TEST")
    print("=" * 80)
    write_results = test_write_scenarios()

    print("\n" + "=" * 80)
    print("  FINAL SUMMARY")
    print("=" * 80)

    # Calculate overall results
    multi_passed = sum(1 for r in verifier.results.values() if r["failed"] == 0)
    multi_total = len(verifier.results)

    print(f"\nMulti-Verification: {multi_passed}/{multi_total} files passed all tests")
    print(f"Edge Cases: {'PASS' if edge_results else 'FAIL'}")
    print(f"Write Scenarios: {'PASS' if write_results else 'FAIL'}")

    overall_pass = (multi_passed == multi_total) and edge_results and write_results

    if overall_pass:
        print("\n  [SUCCESS] All comprehensive tests passed!")
    else:
        print("\n  [WARNING] Some tests failed - review details above")

    print("=" * 80 + "\n")

    return overall_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
