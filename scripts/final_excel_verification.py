"""
Final End-to-End Excel Verification
Tests everything with virtual live data in multiple conditions
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.comprehensive_excel_audit import ExcelComprehensiveAudit
from scripts.enhance_optionchain_with_predictions import EnhancedOptionChainBuilder
from scripts.test_excel_with_virtual_live_data import generate_virtual_live_data


def run_final_verification():
    """Run complete end-to-end verification."""
    print("=" * 80)
    print("  FINAL END-TO-END EXCEL VERIFICATION")
    print("=" * 80)

    # Test 1: Generate virtual data
    print("\n[PHASE 1] Generating Virtual Live Data")
    print("-" * 80)
    virtual_df = generate_virtual_live_data()
    print(f"  Generated: {len(virtual_df)} contracts")

    # Test 2: Build Excel
    print("\n[PHASE 2] Building Excel with All Features")
    print("-" * 80)

    builder = EnhancedOptionChainBuilder()
    df = virtual_df.copy()

    # Add calculations
    df = builder.add_all_calculations(df)
    print(f"  Calculations: {len([c for c in df.columns if c not in virtual_df.columns])} added")

    # Add ML predictions
    df = builder.add_ml_predictions(df)
    print(f"  ML Predictions: {'ml_prediction' in df.columns}")

    # Add trade signals
    df = builder.add_trade_signals(df)
    active_signals = df[df["trade_signal"] != "NO TRADE"]
    print(f"  Trade Signals: {len(active_signals)} active")

    # Fill missing
    df = builder.fill_missing_data(df)

    # Create Excel
    excel_path = ROOT_DIR / "outputs" / "OptionChain_Master_VIRTUAL_TEST.xlsx"
    builder.excel_path = excel_path
    output_path = builder.create_excel_file(df, {})

    # Test 3: Comprehensive Audit
    print("\n[PHASE 3] Comprehensive Audit")
    print("-" * 80)
    auditor = ExcelComprehensiveAudit(excel_path)
    report = auditor.audit_all()

    # Test 4: Verify all cells
    print("\n[PHASE 4] Cell-by-Cell Verification")
    print("-" * 80)

    xl = pd.ExcelFile(excel_path)
    main_sheet = "OptionChain_Data" if "OptionChain_Data" in xl.sheet_names else xl.sheet_names[0]
    df_check = pd.read_excel(xl, sheet_name=main_sheet)

    total_cells = len(df_check) * len(df_check.columns)
    filled_cells = df_check.notna().sum().sum()
    completeness = (filled_cells / total_cells) * 100

    print(f"  Total cells: {total_cells:,}")
    print(f"  Filled cells: {filled_cells:,}")
    print(f"  Completeness: {completeness:.1f}%")

    # Check each column
    print(f"\n  Column Completeness:")
    for col in df_check.columns[:10]:  # First 10 columns
        null_pct = (df_check[col].isna().sum() / len(df_check)) * 100
        print(f"    {col:30s}: {100-null_pct:5.1f}% filled")

    # Test 5: Verify calculations in all rows
    print("\n[PHASE 5] Calculation Verification (All Rows)")
    print("-" * 80)

    calc_errors = 0
    if all(col in df_check.columns for col in ["intrinsic_value", "spot_price", "strike", "option_type"]):
        valid_rows = df_check[
            df_check["intrinsic_value"].notna() & df_check["spot_price"].notna() & df_check["strike"].notna()
        ]

        for idx, row in valid_rows.iterrows():
            spot = row["spot_price"]
            strike = row["strike"]
            opt_type = str(row["option_type"]).upper()
            intrinsic = row["intrinsic_value"]

            if opt_type == "CE":
                expected = max(0, spot - strike)
            else:
                expected = max(0, strike - spot)

            if abs(intrinsic - expected) > 0.01:
                calc_errors += 1

        if calc_errors == 0:
            print(f"  OK: All {len(valid_rows)} intrinsic value calculations correct")
        else:
            print(f"  WARNING: {calc_errors} calculation errors in {len(valid_rows)} rows")

    # Final Report
    print("\n" + "=" * 80)
    print("  FINAL VERIFICATION REPORT")
    print("=" * 80)

    print(f"\nExcel File: {excel_path.name}")
    print(f"  Size: {excel_path.stat().st_size:,} bytes")
    print(f"  Sheets: {len(xl.sheet_names)}")
    print(f"  Rows: {len(df_check):,}")
    print(f"  Columns: {len(df_check.columns)}")
    print(f"  Completeness: {completeness:.1f}%")
    print(f"  Calculation Errors: {calc_errors}")
    print(f"  Active Trade Signals: {len(active_signals)}")

    # Check for required sheets
    required_sheets = ["ML_PREDICTIONS", "TOP_OPPORTUNITIES", "PNL_SUMMARY"]
    missing_sheets = [s for s in required_sheets if s not in xl.sheet_names]

    if missing_sheets:
        print(f"  WARNING: Missing sheets: {missing_sheets}")
    else:
        print(f"  OK: All required sheets present")

    # Overall status
    print("\n" + "=" * 80)
    if completeness > 80 and calc_errors == 0 and len(active_signals) > 0:
        print("  STATUS: EXCELLENT - All tests passed")
    elif completeness > 70 and calc_errors == 0:
        print("  STATUS: GOOD - Minor improvements possible")
    else:
        print("  STATUS: NEEDS ATTENTION")
    print("=" * 80)

    return completeness > 70 and calc_errors == 0


if __name__ == "__main__":
    success = run_final_verification()
    sys.exit(0 if success else 1)
