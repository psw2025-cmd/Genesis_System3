"""
Analyze OptionChain_Master_v3_AI_FINAL.xlsx
Check structure, missing data, and requirements
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def analyze_excel_file():
    """Analyze the Excel file structure and data."""
    excel_path = ROOT_DIR / "outputs" / "OptionChain_Master_v3_AI_FINAL.xlsx"

    if not excel_path.exists():
        print(f"ERROR: File not found: {excel_path}")
        return None

    print("=" * 80)
    print("  ANALYZING OPTIONCHAIN_MASTER_V3_AI_FINAL.XLSX")
    print("=" * 80)

    try:
        # Read Excel file
        xl = pd.ExcelFile(excel_path)

        print(f"\nFile: {excel_path.name}")
        print(f"Size: {excel_path.stat().st_size:,} bytes")
        print(f"Sheets: {xl.sheet_names}")

        analysis = {}

        for sheet_name in xl.sheet_names:
            print(f"\n{'='*80}")
            print(f"  SHEET: {sheet_name}")
            print("=" * 80)

            df = pd.read_excel(xl, sheet_name=sheet_name)

            print(f"\nRows: {len(df):,}")
            print(f"Columns: {len(df.columns)}")

            print(f"\nColumn Names:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i:2d}. {col}")

            # Check for missing data
            print(f"\nMissing Data Analysis:")
            missing_data = df.isnull().sum()
            missing_pct = (missing_data / len(df)) * 100

            critical_missing = []
            for col in df.columns:
                missing_count = missing_data[col]
                missing_percent = missing_pct[col]
                if missing_percent > 50:  # More than 50% missing
                    critical_missing.append((col, missing_count, missing_percent))
                    print(f"  ⚠️  {col:30s}: {missing_count:5d} ({missing_percent:5.1f}%) - CRITICAL")
                elif missing_percent > 10:  # More than 10% missing
                    print(f"  ⚠️  {col:30s}: {missing_count:5d} ({missing_percent:5.1f}%) - WARNING")
                elif missing_count > 0:
                    print(f"  ✓   {col:30s}: {missing_count:5d} ({missing_percent:5.1f}%)")

            # Data types
            print(f"\nData Types:")
            for col in df.columns:
                dtype = df[col].dtype
                print(f"  {col:30s}: {str(dtype):15s}")

            # Sample data
            print(f"\nSample Data (first 3 rows):")
            print(df.head(3).to_string())

            analysis[sheet_name] = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "missing_data": missing_data.to_dict(),
                "missing_pct": missing_pct.to_dict(),
                "critical_missing": critical_missing,
                "dtypes": df.dtypes.to_dict(),
            }

        return analysis

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = analyze_excel_file()
    if result:
        print("\n" + "=" * 80)
        print("  ANALYSIS COMPLETE")
        print("=" * 80)
