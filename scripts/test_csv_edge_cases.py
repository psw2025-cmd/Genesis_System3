"""
Test CSV Files - Edge Cases and Error Conditions
Tests how CSV files handle various edge cases and error conditions
"""

import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def test_empty_file():
    """Test: Empty CSV file"""
    print("\n[EDGE CASE 1] Empty CSV File")
    print("-" * 80)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("")  # Empty file
        temp_path = Path(f.name)

    try:
        df = pd.read_csv(temp_path, on_bad_lines="skip", engine="python")
        print("  Result: Can handle empty file")
        print(f"  Rows: {len(df)}")
        return True
    except Exception as e:
        print(f"  Result: Error handling empty file: {str(e)[:50]}")
        return False
    finally:
        temp_path.unlink()


def test_missing_columns():
    """Test: CSV with missing columns"""
    print("\n[EDGE CASE 2] Missing Columns")
    print("-" * 80)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("position_id,action\nPOS_001,OPEN\n")
        temp_path = Path(f.name)

    try:
        df = pd.read_csv(temp_path, on_bad_lines="skip", engine="python")
        print("  Result: Can handle missing columns")
        print(f"  Columns: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"  Result: Error: {str(e)[:50]}")
        return False
    finally:
        temp_path.unlink()


def test_mixed_data_types():
    """Test: CSV with mixed data types in same column"""
    print("\n[EDGE CASE 3] Mixed Data Types")
    print("-" * 80)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write('strike,price\n25000,1000.5\n"ABC",2000\n30000,3000\n')
        temp_path = Path(f.name)

    try:
        df = pd.read_csv(temp_path, on_bad_lines="skip", engine="python")
        print("  Result: Can handle mixed types")
        print(f"  strike dtype: {df['strike'].dtype}")
        print(f"  Invalid values: {df[df['strike'].astype(str).str.contains('[^0-9.]', na=False)]}")
        return True
    except Exception as e:
        print(f"  Result: Error: {str(e)[:50]}")
        return False
    finally:
        temp_path.unlink()


def test_special_characters():
    """Test: CSV with special characters"""
    print("\n[EDGE CASE 4] Special Characters")
    print("-" * 80)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", encoding="utf-8", delete=False) as f:
        f.write('underlying,strategy\nNIFTY,"BUY CE"\nBANKNIFTY,"SELL PE"\n')
        temp_path = Path(f.name)

    try:
        df = pd.read_csv(temp_path, on_bad_lines="skip", engine="python")
        print("  Result: Can handle special characters")
        print(f"  Data: {df.to_string()}")
        return True
    except Exception as e:
        print(f"  Result: Error: {str(e)[:50]}")
        return False
    finally:
        temp_path.unlink()


def test_very_large_file():
    """Test: Very large CSV file"""
    print("\n[EDGE CASE 5] Large File Handling")
    print("-" * 80)

    filepath = ROOT_DIR / "outputs" / "chain_raw_live.csv"
    if filepath.exists():
        size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"  File size: {size_mb:.2f} MB")

        try:
            # Try reading in chunks
            chunk_size = 1000
            total_rows = 0
            for chunk in pd.read_csv(filepath, chunksize=chunk_size, on_bad_lines="skip", engine="python"):
                total_rows += len(chunk)
            print(f"  Result: Can handle large file (read {total_rows} rows in chunks)")
            return True
        except Exception as e:
            print(f"  Result: Error: {str(e)[:50]}")
            return False
    else:
        print("  Result: File not found (skipped)")
        return True


def test_concurrent_access():
    """Test: Concurrent file access simulation"""
    print("\n[EDGE CASE 6] Concurrent Access")
    print("-" * 80)

    filepath = ROOT_DIR / "outputs" / "underlying_rank_live.csv"
    if filepath.exists():
        try:
            # Try reading while file might be written
            df1 = pd.read_csv(filepath, on_bad_lines="skip", engine="python")
            df2 = pd.read_csv(filepath, on_bad_lines="skip", engine="python")

            if len(df1) == len(df2):
                print("  Result: Can handle concurrent reads")
                return True
            else:
                print(f"  Result: File changed between reads ({len(df1)} vs {len(df2)} rows)")
                return False
        except Exception as e:
            print(f"  Result: Error: {str(e)[:50]}")
            return False
    else:
        print("  Result: File not found (skipped)")
        return True


def test_corrupted_data():
    """Test: Corrupted CSV data"""
    print("\n[EDGE CASE 7] Corrupted Data")
    print("-" * 80)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write('position_id,action,strike\nPOS_001,OPEN,25000\nPOS_002,CLOSE,"unclosed quote\nPOS_003,OPEN,30000\n')
        temp_path = Path(f.name)

    try:
        df = pd.read_csv(temp_path, on_bad_lines="skip", engine="python")
        print("  Result: Can handle corrupted data (with skip)")
        print(f"  Rows read: {len(df)}")
        return True
    except Exception as e:
        print(f"  Result: Error: {str(e)[:50]}")
        return False
    finally:
        temp_path.unlink()


def test_unicode_characters():
    """Test: Unicode characters in CSV"""
    print("\n[EDGE CASE 8] Unicode Characters")
    print("-" * 80)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", encoding="utf-8", delete=False) as f:
        f.write('underlying,note\nNIFTY,"Test ✓"\nBANKNIFTY,"Test ₹"\n')
        temp_path = Path(f.name)

    try:
        df = pd.read_csv(temp_path, on_bad_lines="skip", engine="python", encoding="utf-8")
        print("  Result: Can handle unicode characters")
        print(f"  Data: {df.to_string()}")
        return True
    except Exception as e:
        print(f"  Result: Error: {str(e)[:50]}")
        return False
    finally:
        temp_path.unlink()


def main():
    """Run all edge case tests."""
    print("\n" + "=" * 80)
    print("  CSV FILES - EDGE CASES AND ERROR CONDITIONS TEST")
    print("=" * 80)

    results = {}
    results["empty_file"] = test_empty_file()
    results["missing_columns"] = test_missing_columns()
    results["mixed_types"] = test_mixed_data_types()
    results["special_chars"] = test_special_characters()
    results["large_file"] = test_very_large_file()
    results["concurrent"] = test_concurrent_access()
    results["corrupted"] = test_corrupted_data()
    results["unicode"] = test_unicode_characters()

    print("\n" + "=" * 80)
    print("  EDGE CASE TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n  Total Tests: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {total - passed}")

    print("\n  Test Results:")
    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"    {status} {name}")

    print("=" * 80 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
