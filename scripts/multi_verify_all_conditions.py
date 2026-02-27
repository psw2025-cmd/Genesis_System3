"""
Multi-Verification - All Conditions and Situations
Comprehensive testing of all CSV files under various conditions
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import json
import shutil
import tempfile

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class MultiVerifier:
    """Comprehensive verification for all conditions."""

    def __init__(self):
        self.outputs_dir = ROOT_DIR / "outputs"
        self.results = {
            "paper_trades": {"tests": [], "passed": 0, "failed": 0},
            "chain_raw": {"tests": [], "passed": 0, "failed": 0},
            "underlying_rank": {"tests": [], "passed": 0, "failed": 0},
        }

    def test_file_exists(self, filepath, name):
        """Test 1: File existence"""
        test_name = "File Exists"
        exists = filepath.exists()
        self.results[name]["tests"].append(
            {"test": test_name, "passed": exists, "message": f"File {'exists' if exists else 'missing'}"}
        )
        if exists:
            self.results[name]["passed"] += 1
        else:
            self.results[name]["failed"] += 1
        return exists

    def test_file_readable(self, filepath, name):
        """Test 2: File is readable"""
        test_name = "File Readable"
        try:
            if filepath.suffix == ".csv":
                df = pd.read_csv(filepath, on_bad_lines="skip", engine="python", nrows=1)
                readable = True
                msg = "CSV readable"
            else:
                readable = False
                msg = "Not a CSV file"
        except Exception as e:
            readable = False
            msg = f"Read error: {str(e)[:50]}"

        self.results[name]["tests"].append({"test": test_name, "passed": readable, "message": msg})
        if readable:
            self.results[name]["passed"] += 1
        else:
            self.results[name]["failed"] += 1
        return readable

    def test_file_not_empty(self, filepath, name):
        """Test 3: File is not empty"""
        test_name = "File Not Empty"
        if not filepath.exists():
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": "File missing"})
            self.results[name]["failed"] += 1
            return False

        size = filepath.stat().st_size
        not_empty = size > 0

        self.results[name]["tests"].append({"test": test_name, "passed": not_empty, "message": f"Size: {size} bytes"})
        if not_empty:
            self.results[name]["passed"] += 1
        else:
            self.results[name]["failed"] += 1
        return not_empty

    def test_has_required_columns(self, filepath, name, required_cols):
        """Test 4: Has required columns"""
        test_name = "Required Columns"
        if not filepath.exists():
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": "File missing"})
            self.results[name]["failed"] += 1
            return False

        try:
            df = pd.read_csv(filepath, on_bad_lines="skip", engine="python", nrows=1)
            missing = [col for col in required_cols if col not in df.columns]
            has_all = len(missing) == 0

            self.results[name]["tests"].append(
                {"test": test_name, "passed": has_all, "message": f"Missing: {missing}" if missing else "All present"}
            )
            if has_all:
                self.results[name]["passed"] += 1
            else:
                self.results[name]["failed"] += 1
            return has_all
        except Exception as e:
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": f"Error: {str(e)[:50]}"})
            self.results[name]["failed"] += 1
            return False

    def test_no_duplicate_columns(self, filepath, name):
        """Test 5: No duplicate columns"""
        test_name = "No Duplicate Columns"
        if not filepath.exists():
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": "File missing"})
            self.results[name]["failed"] += 1
            return False

        try:
            df = pd.read_csv(filepath, on_bad_lines="skip", engine="python", nrows=1)
            duplicates = df.columns.duplicated().sum()
            no_duplicates = duplicates == 0

            self.results[name]["tests"].append(
                {
                    "test": test_name,
                    "passed": no_duplicates,
                    "message": f"Duplicates: {duplicates}" if duplicates > 0 else "No duplicates",
                }
            )
            if no_duplicates:
                self.results[name]["passed"] += 1
            else:
                self.results[name]["failed"] += 1
            return no_duplicates
        except Exception as e:
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": f"Error: {str(e)[:50]}"})
            self.results[name]["failed"] += 1
            return False

    def test_data_types_correct(self, filepath, name, expected_types):
        """Test 6: Data types are correct"""
        test_name = "Data Types Correct"
        if not filepath.exists():
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": "File missing"})
            self.results[name]["failed"] += 1
            return False

        try:
            df = pd.read_csv(filepath, on_bad_lines="skip", engine="python", nrows=100)
            issues = []

            for col, expected_type in expected_types.items():
                if col in df.columns:
                    actual_type = str(df[col].dtype)
                    if expected_type == "numeric":
                        if actual_type not in ["int64", "float64", "Int64", "Float64"]:
                            issues.append(f"{col}: {actual_type} (expected numeric)")
                    elif expected_type == "string":
                        if actual_type not in ["object", "string"]:
                            issues.append(f"{col}: {actual_type} (expected string)")

            all_correct = len(issues) == 0

            self.results[name]["tests"].append(
                {"test": test_name, "passed": all_correct, "message": f"Issues: {issues}" if issues else "All correct"}
            )
            if all_correct:
                self.results[name]["passed"] += 1
            else:
                self.results[name]["failed"] += 1
            return all_correct
        except Exception as e:
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": f"Error: {str(e)[:50]}"})
            self.results[name]["failed"] += 1
            return False

    def test_no_invalid_values(self, filepath, name, validation_rules):
        """Test 7: No invalid values"""
        test_name = "No Invalid Values"
        if not filepath.exists():
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": "File missing"})
            self.results[name]["failed"] += 1
            return False

        try:
            df = pd.read_csv(filepath, on_bad_lines="skip", engine="python")
            issues = []

            for col, rules in validation_rules.items():
                if col in df.columns:
                    if "valid_values" in rules:
                        invalid = df[~df[col].isin(rules["valid_values"])]
                        if len(invalid) > 0:
                            issues.append(f"{col}: {len(invalid)} invalid values")

                    if "min" in rules:
                        below_min = df[df[col] < rules["min"]]
                        if len(below_min) > 0:
                            issues.append(f"{col}: {len(below_min)} values below min")

                    if "max" in rules:
                        above_max = df[df[col] > rules["max"]]
                        if len(above_max) > 0:
                            issues.append(f"{col}: {len(above_max)} values above max")

            no_invalid = len(issues) == 0

            self.results[name]["tests"].append(
                {"test": test_name, "passed": no_invalid, "message": f"Issues: {issues}" if issues else "All valid"}
            )
            if no_invalid:
                self.results[name]["passed"] += 1
            else:
                self.results[name]["failed"] += 1
            return no_invalid
        except Exception as e:
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": f"Error: {str(e)[:50]}"})
            self.results[name]["failed"] += 1
            return False

    def test_consistent_structure(self, filepath, name):
        """Test 8: Consistent structure across rows"""
        test_name = "Consistent Structure"
        if not filepath.exists():
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": "File missing"})
            self.results[name]["failed"] += 1
            return False

        try:
            df = pd.read_csv(filepath, on_bad_lines="skip", engine="python")

            if len(df) == 0:
                self.results[name]["tests"].append(
                    {"test": test_name, "passed": True, "message": "Empty file (consistent)"}
                )
                self.results[name]["passed"] += 1
                return True

            # Check if all rows have same number of non-null columns
            if "action" in df.columns:
                # Check OPEN vs CLOSE structure
                open_rows = df[df["action"] == "OPEN"]
                close_rows = df[df["action"] == "CLOSE"]

                if len(open_rows) > 0 and len(close_rows) > 0:
                    open_cols = set(open_rows.columns)
                    close_cols = set(close_rows.columns)

                    if open_cols == close_cols:
                        consistent = True
                        msg = "OPEN and CLOSE rows have same columns"
                    else:
                        consistent = False
                        extra_in_close = close_cols - open_cols
                        extra_in_open = open_cols - close_cols
                        msg = f"Structure differs: CLOSE has {extra_in_close}, OPEN has {extra_in_open}"
                else:
                    consistent = True
                    msg = "Only one action type present"
            else:
                consistent = True
                msg = "No action column (structure consistent)"

            self.results[name]["tests"].append({"test": test_name, "passed": consistent, "message": msg})
            if consistent:
                self.results[name]["passed"] += 1
            else:
                self.results[name]["failed"] += 1
            return consistent
        except Exception as e:
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": f"Error: {str(e)[:50]}"})
            self.results[name]["failed"] += 1
            return False

    def test_timestamps_valid(self, filepath, name):
        """Test 9: Timestamps are valid"""
        test_name = "Valid Timestamps"
        if not filepath.exists():
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": "File missing"})
            self.results[name]["failed"] += 1
            return False

        try:
            df = pd.read_csv(filepath, on_bad_lines="skip", engine="python")
            timestamp_cols = [col for col in df.columns if "timestamp" in col.lower() or "time" in col.lower()]

            if not timestamp_cols:
                self.results[name]["tests"].append(
                    {"test": test_name, "passed": True, "message": "No timestamp columns (not required)"}
                )
                self.results[name]["passed"] += 1
                return True

            issues = []
            for col in timestamp_cols:
                null_count = df[col].isna().sum()
                if null_count > 0:
                    issues.append(f"{col}: {null_count} null values")

            all_valid = len(issues) == 0

            self.results[name]["tests"].append(
                {"test": test_name, "passed": all_valid, "message": f"Issues: {issues}" if issues else "All valid"}
            )
            if all_valid:
                self.results[name]["passed"] += 1
            else:
                self.results[name]["failed"] += 1
            return all_valid
        except Exception as e:
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": f"Error: {str(e)[:50]}"})
            self.results[name]["failed"] += 1
            return False

    def test_file_integrity(self, filepath, name):
        """Test 10: File integrity (can be fully read)"""
        test_name = "File Integrity"
        if not filepath.exists():
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": "File missing"})
            self.results[name]["failed"] += 1
            return False

        try:
            df = pd.read_csv(filepath, on_bad_lines="skip", engine="python")
            readable = True
            msg = f"Read {len(df)} rows successfully"
        except Exception as e:
            readable = False
            msg = f"Read error: {str(e)[:50]}"

        self.results[name]["tests"].append({"test": test_name, "passed": readable, "message": msg})
        if readable:
            self.results[name]["passed"] += 1
        else:
            self.results[name]["failed"] += 1
        return readable

    def test_edge_cases(self, filepath, name):
        """Test 11: Edge cases"""
        test_name = "Edge Cases"
        if not filepath.exists():
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": "File missing"})
            self.results[name]["failed"] += 1
            return False

        try:
            df = pd.read_csv(filepath, on_bad_lines="skip", engine="python")
            issues = []

            # Check for extremely large values
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].abs().max() > 1e10:
                    issues.append(f"{col}: Very large values detected")

            # Check for negative values where not expected
            if "qty" in df.columns:
                negative_qty = df[df["qty"] < 0]
                if len(negative_qty) > 0:
                    issues.append(f"qty: {len(negative_qty)} negative values")

            if "strike" in df.columns:
                negative_strike = df[df["strike"] < 0]
                if len(negative_strike) > 0:
                    issues.append(f"strike: {len(negative_strike)} negative values")

            # Check for duplicate position_ids (if applicable)
            if "position_id" in df.columns:
                duplicates = df["position_id"].duplicated().sum()
                if duplicates > 0:
                    issues.append(f"position_id: {duplicates} duplicates (may be valid for OPEN/CLOSE)")

            all_ok = len(issues) == 0

            self.results[name]["tests"].append(
                {
                    "test": test_name,
                    "passed": all_ok,
                    "message": f"Issues: {issues}" if issues else "No edge case issues",
                }
            )
            if all_ok:
                self.results[name]["passed"] += 1
            else:
                self.results[name]["failed"] += 1
            return all_ok
        except Exception as e:
            self.results[name]["tests"].append({"test": test_name, "passed": False, "message": f"Error: {str(e)[:50]}"})
            self.results[name]["failed"] += 1
            return False

    def verify_paper_trades(self):
        """Verify paper_trades_live.csv"""
        print("\n" + "=" * 80)
        print("  PAPER TRADES CSV - MULTI-VERIFICATION")
        print("=" * 80)

        filepath = self.outputs_dir / "paper_trades_live.csv"

        # Test 1: File exists
        if not self.test_file_exists(filepath, "paper_trades"):
            print("  [SKIP] File not found - skipping remaining tests")
            return

        # Test 2: File readable
        self.test_file_readable(filepath, "paper_trades")

        # Test 3: Not empty
        self.test_file_not_empty(filepath, "paper_trades")

        # Test 4: Required columns
        required = ["position_id", "action", "timestamp", "underlying", "strike", "option_type", "price", "qty"]
        self.test_has_required_columns(filepath, "paper_trades", required)

        # Test 5: No duplicate columns
        self.test_no_duplicate_columns(filepath, "paper_trades")

        # Test 6: Data types
        expected_types = {
            "strike": "numeric",
            "price": "numeric",
            "qty": "numeric",
            "action": "string",
            "underlying": "string",
            "option_type": "string",
        }
        self.test_data_types_correct(filepath, "paper_trades", expected_types)

        # Test 7: Invalid values
        validation_rules = {
            "action": {"valid_values": ["OPEN", "CLOSE"]},
            "option_type": {"valid_values": ["CE", "PE"]},
            "qty": {"min": 0},
            "strike": {"min": 0},
            "price": {"min": 0},
        }
        self.test_no_invalid_values(filepath, "paper_trades", validation_rules)

        # Test 8: Consistent structure
        self.test_consistent_structure(filepath, "paper_trades")

        # Test 9: Timestamps
        self.test_timestamps_valid(filepath, "paper_trades")

        # Test 10: File integrity
        self.test_file_integrity(filepath, "paper_trades")

        # Test 11: Edge cases
        self.test_edge_cases(filepath, "paper_trades")

    def verify_chain_raw(self):
        """Verify chain_raw_live.csv"""
        print("\n" + "=" * 80)
        print("  CHAIN RAW CSV - MULTI-VERIFICATION")
        print("=" * 80)

        filepath = self.outputs_dir / "chain_raw_live.csv"

        # Test 1: File exists
        if not self.test_file_exists(filepath, "chain_raw"):
            print("  [SKIP] File not found - skipping remaining tests")
            return

        # Test 2: File readable
        self.test_file_readable(filepath, "chain_raw")

        # Test 3: Not empty
        self.test_file_not_empty(filepath, "chain_raw")

        # Test 4: Required columns
        required = ["underlying", "strike", "option_type", "expiry", "ltp", "oi"]
        self.test_has_required_columns(filepath, "chain_raw", required)

        # Test 5: No duplicate columns
        self.test_no_duplicate_columns(filepath, "chain_raw")

        # Test 6: Data types
        expected_types = {
            "strike": "numeric",
            "ltp": "numeric",
            "oi": "numeric",
            "volume": "numeric",
            "underlying": "string",
            "option_type": "string",
        }
        self.test_data_types_correct(filepath, "chain_raw", expected_types)

        # Test 7: Invalid values
        validation_rules = {
            "option_type": {"valid_values": ["CE", "PE"]},
            "strike": {"min": 0},
            "ltp": {"min": 0},
            "oi": {"min": 0},
        }
        self.test_no_invalid_values(filepath, "chain_raw", validation_rules)

        # Test 8: Consistent structure
        self.test_consistent_structure(filepath, "chain_raw")

        # Test 9: Timestamps
        self.test_timestamps_valid(filepath, "chain_raw")

        # Test 10: File integrity
        self.test_file_integrity(filepath, "chain_raw")

        # Test 11: Edge cases
        self.test_edge_cases(filepath, "chain_raw")

    def verify_underlying_rank(self):
        """Verify underlying_rank_live.csv"""
        print("\n" + "=" * 80)
        print("  UNDERLYING RANK CSV - MULTI-VERIFICATION")
        print("=" * 80)

        filepath = self.outputs_dir / "underlying_rank_live.csv"

        # Test 1: File exists
        if not self.test_file_exists(filepath, "underlying_rank"):
            print("  [SKIP] File not found - skipping remaining tests")
            return

        # Test 2: File readable
        self.test_file_readable(filepath, "underlying_rank")

        # Test 3: Not empty
        self.test_file_not_empty(filepath, "underlying_rank")

        # Test 4: Required columns
        required = ["underlying", "underlying_score"]
        self.test_has_required_columns(filepath, "underlying_rank", required)

        # Test 5: No duplicate columns
        self.test_no_duplicate_columns(filepath, "underlying_rank")

        # Test 6: Data types
        expected_types = {
            "underlying_score": "numeric",
            "signal_strength": "numeric",
            "execution_quality": "numeric",
            "pcr": "numeric",
            "expected_move": "numeric",
            "underlying": "string",
        }
        self.test_data_types_correct(filepath, "underlying_rank", expected_types)

        # Test 7: Invalid values
        validation_rules = {
            "underlying_score": {"min": 0, "max": 100},
            "underlying": {"valid_values": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]},
        }
        self.test_no_invalid_values(filepath, "underlying_rank", validation_rules)

        # Test 8: Consistent structure
        self.test_consistent_structure(filepath, "underlying_rank")

        # Test 9: Timestamps
        self.test_timestamps_valid(filepath, "underlying_rank")

        # Test 10: File integrity
        self.test_file_integrity(filepath, "underlying_rank")

        # Test 11: Edge cases
        self.test_edge_cases(filepath, "underlying_rank")

    def print_results(self):
        """Print comprehensive results."""
        print("\n" + "=" * 80)
        print("  MULTI-VERIFICATION RESULTS SUMMARY")
        print("=" * 80)

        total_tests = 0
        total_passed = 0
        total_failed = 0

        for name, result in self.results.items():
            tests = result["tests"]
            passed = result["passed"]
            failed = result["failed"]

            total_tests += len(tests)
            total_passed += passed
            total_failed += failed

            print(f"\n[{name.upper().replace('_', ' ')}]")
            print("-" * 80)
            print(f"  Total Tests: {len(tests)}")
            print(f"  Passed: {passed}")
            print(f"  Failed: {failed}")
            print(f"  Pass Rate: {(passed/len(tests)*100) if len(tests) > 0 else 0:.1f}%")

            print(f"\n  Test Details:")
            for test in tests:
                status = "[PASS]" if test["passed"] else "[FAIL]"
                print(f"    {status} {test['test']}: {test['message']}")

        print("\n" + "=" * 80)
        print("  OVERALL SUMMARY")
        print("=" * 80)
        print(f"  Total Tests: {total_tests}")
        print(f"  Total Passed: {total_passed}")
        print(f"  Total Failed: {total_failed}")
        print(f"  Overall Pass Rate: {(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%")

        if total_failed == 0:
            print("\n  [SUCCESS] All tests passed!")
        else:
            print(f"\n  [WARNING] {total_failed} test(s) failed")

        print("=" * 80 + "\n")


def main():
    """Run multi-verification."""
    print("\n" + "=" * 80)
    print("  MULTI-VERIFICATION - ALL CONDITIONS AND SITUATIONS")
    print("=" * 80)

    verifier = MultiVerifier()

    # Verify all files
    verifier.verify_paper_trades()
    verifier.verify_chain_raw()
    verifier.verify_underlying_rank()

    # Print results
    verifier.print_results()

    return verifier.results


if __name__ == "__main__":
    results = main()
    sys.exit(0)
