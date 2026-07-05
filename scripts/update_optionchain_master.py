"""
Automated OptionChain Master Update Script
Fetches fresh data, rebuilds Excel, verifies, and shows performance
"""

import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.engine.fetch_all_indices_option_chain import fetch_all_indices_option_chain

# Use enhanced builder with predictions
try:
    from scripts.enhance_optionchain_with_predictions import EnhancedOptionChainBuilder

    USE_ENHANCED = True
except:
    from scripts.build_production_optionchain_master import OptionChainMasterBuilder

    USE_ENHANCED = False
from scripts.verify_optionchain_master import verify_excel_file


def update_optionchain_master(force_fetch: bool = False):
    """
    Complete update process: Fetch -> Build -> Verify -> Report

    Args:
        force_fetch: If True, always fetch fresh data. If False, use existing CSV if recent.
    """
    print("=" * 80)
    print("  OPTIONCHAIN MASTER - AUTOMATED UPDATE")
    print("=" * 80)

    start_time = time.time()
    ist = pytz.timezone("Asia/Kolkata")
    timestamp = datetime.now(ist)

    print(f"\nStart Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S IST')}")

    results = {
        "fetch_status": None,
        "fetch_time": 0,
        "build_status": None,
        "build_time": 0,
        "verify_status": None,
        "verify_time": 0,
        "total_time": 0,
        "rows": 0,
        "columns": 0,
        "completeness": 0,
    }

    # Step 1: Fetch fresh data
    print("\n" + "-" * 80)
    print("STEP 1: Fetching Fresh Option Chain Data")
    print("-" * 80)

    csv_path = ROOT_DIR / "outputs" / "chain_raw_live.csv"

    should_fetch = force_fetch
    if not force_fetch and csv_path.exists():
        # Check if CSV is recent (within last 5 minutes)
        file_age = time.time() - csv_path.stat().st_mtime
        if file_age > 300:  # 5 minutes
            should_fetch = True
            print(f"  CSV file is {file_age/60:.1f} minutes old - fetching fresh data")
        else:
            print(f"  Using existing CSV (age: {file_age:.0f} seconds)")

    if should_fetch:
        fetch_start = time.time()
        try:
            print("  Fetching option chain for all indices...")
            fetch_all_indices_option_chain()
            results["fetch_status"] = "SUCCESS"
            print("  Fetch completed successfully")
        except Exception as e:
            results["fetch_status"] = f"ERROR: {str(e)}"
            print(f"  ERROR during fetch: {e}")
            # Continue anyway with existing data
        results["fetch_time"] = time.time() - fetch_start
    else:
        results["fetch_status"] = "SKIPPED (using existing)"
        results["fetch_time"] = 0

    # Step 2: Build Excel file
    print("\n" + "-" * 80)
    print("STEP 2: Building Production Excel File")
    print("-" * 80)

    build_start = time.time()
    try:
        if USE_ENHANCED:
            builder = EnhancedOptionChainBuilder()
            print("  Using enhanced builder with ML predictions and charts")
        else:
            builder = OptionChainMasterBuilder()

        # Load data
        df, excel_sheets = builder.load_existing_data()
        results["rows"] = len(df)
        results["columns"] = len(df.columns)

        # Add calculations
        df = builder.add_all_calculations(df)

        # Fill missing data
        df = builder.fill_missing_data(df)

        # Create Excel
        output_path = builder.create_excel_file(df, excel_sheets)

        results["build_status"] = "SUCCESS"
        print(f"  Excel file created: {output_path.name}")
    except Exception as e:
        results["build_status"] = f"ERROR: {str(e)}"
        print(f"  ERROR during build: {e}")
        import traceback

        traceback.print_exc()
        return results

    results["build_time"] = time.time() - build_start

    # Step 3: Verify
    print("\n" + "-" * 80)
    print("STEP 3: Verifying Excel File")
    print("-" * 80)

    verify_start = time.time()
    try:
        # Read file to get completeness
        xl = pd.ExcelFile(output_path)
        main_sheet = "CHAIN_RAW" if "CHAIN_RAW" in xl.sheet_names else "OptionChain_Data"
        if main_sheet not in xl.sheet_names:
            main_sheet = xl.sheet_names[0]

        df_check = pd.read_excel(xl, sheet_name=main_sheet)
        total_cells = len(df_check) * len(df_check.columns)
        filled_cells = df_check.notna().sum().sum()
        results["completeness"] = (filled_cells / total_cells) * 100

        # Run full verification
        verify_success = verify_excel_file()
        results["verify_status"] = "SUCCESS" if verify_success else "WARNINGS"
    except Exception as e:
        results["verify_status"] = f"ERROR: {str(e)}"
        print(f"  ERROR during verify: {e}")

    results["verify_time"] = time.time() - verify_start
    results["total_time"] = time.time() - start_time

    # Step 4: Performance Report
    print("\n" + "=" * 80)
    print("  PERFORMANCE REPORT")
    print("=" * 80)

    print(f"\nTiming:")
    print(f"  Fetch Time:    {results['fetch_time']:.2f} seconds")
    print(f"  Build Time:     {results['build_time']:.2f} seconds")
    print(f"  Verify Time:    {results['verify_time']:.2f} seconds")
    print(f"  Total Time:    {results['total_time']:.2f} seconds")

    print(f"\nData:")
    print(f"  Rows:          {results['rows']:,}")
    print(f"  Columns:       {results['columns']}")
    print(f"  Completeness:  {results['completeness']:.1f}%")

    print(f"\nStatus:")
    print(f"  Fetch:         {results['fetch_status']}")
    print(f"  Build:         {results['build_status']}")
    print(f"  Verify:        {results['verify_status']}")

    # Overall status
    if results["build_status"] == "SUCCESS" and results["verify_status"] in ["SUCCESS", "WARNINGS"]:
        print(f"\n" + "=" * 80)
        print("  STATUS: SUCCESS - Excel file updated and verified")
        print("=" * 80)
    else:
        print(f"\n" + "=" * 80)
        print("  STATUS: COMPLETED WITH ISSUES")
        print("=" * 80)

    print(f"\nFile Location: {output_path}")
    print(f"Update Time: {datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S IST')}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update OptionChain Master Excel file")
    parser.add_argument("--force-fetch", action="store_true", help="Force fresh data fetch even if CSV exists")

    args = parser.parse_args()

    results = update_optionchain_master(force_fetch=args.force_fetch)
    sys.exit(0 if results["build_status"] == "SUCCESS" else 1)
