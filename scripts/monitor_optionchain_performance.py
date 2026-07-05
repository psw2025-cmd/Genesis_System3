"""
Monitor OptionChain Master Performance
Tracks update frequency, data quality, and system health
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def monitor_performance():
    """Monitor and report on OptionChain Master performance."""
    print("=" * 80)
    print("  OPTIONCHAIN MASTER - PERFORMANCE MONITOR")
    print("=" * 80)

    excel_path = ROOT_DIR / "outputs" / "OptionChain_Master_v3_AI_FINAL.xlsx"
    csv_path = ROOT_DIR / "outputs" / "chain_raw_live.csv"

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    # Check file status
    print("\nFile Status:")
    print("-" * 80)

    excel_exists = excel_path.exists()
    csv_exists = csv_path.exists()

    print(f"Excel File: {'EXISTS' if excel_exists else 'MISSING'}")
    if excel_exists:
        excel_age = now.timestamp() - excel_path.stat().st_mtime
        excel_age_str = str(timedelta(seconds=int(excel_age)))
        print(f"  Location: {excel_path}")
        print(f"  Size: {excel_path.stat().st_size:,} bytes")
        print(
            f"  Last Modified: {datetime.fromtimestamp(excel_path.stat().st_mtime, ist).strftime('%Y-%m-%d %H:%M:%S IST')}"
        )
        print(f"  Age: {excel_age_str}")

        if excel_age < 300:
            print(f"  Status: FRESH (updated within last 5 minutes)")
        elif excel_age < 3600:
            print(f"  Status: RECENT (updated within last hour)")
        else:
            print(f"  Status: STALE (needs update)")

    print(f"\nCSV Source: {'EXISTS' if csv_exists else 'MISSING'}")
    if csv_exists:
        csv_age = now.timestamp() - csv_path.stat().st_mtime
        csv_age_str = str(timedelta(seconds=int(csv_age)))
        print(f"  Location: {csv_path}")
        print(f"  Size: {csv_path.stat().st_size:,} bytes")
        print(
            f"  Last Modified: {datetime.fromtimestamp(csv_path.stat().st_mtime, ist).strftime('%Y-%m-%d %H:%M:%S IST')}"
        )
        print(f"  Age: {csv_age_str}")

    # Analyze Excel file
    if excel_exists:
        print("\n" + "-" * 80)
        print("Excel File Analysis:")
        print("-" * 80)

        try:
            xl = pd.ExcelFile(excel_path)
            main_sheet = "CHAIN_RAW" if "CHAIN_RAW" in xl.sheet_names else "OptionChain_Data"
            if main_sheet not in xl.sheet_names:
                main_sheet = xl.sheet_names[0]

            df = pd.read_excel(xl, sheet_name=main_sheet)

            print(f"Sheets: {len(xl.sheet_names)}")
            print(f"  {', '.join(xl.sheet_names)}")

            print(f"\nMain Sheet ({main_sheet}):")
            print(f"  Rows: {len(df):,}")
            print(f"  Columns: {len(df.columns)}")

            # Data completeness
            total_cells = len(df) * len(df.columns)
            filled_cells = df.notna().sum().sum()
            completeness = (filled_cells / total_cells) * 100
            print(f"  Completeness: {completeness:.1f}%")

            # Column categories
            contract_cols = [c for c in ["underlying", "strike", "option_type", "expiry"] if c in df.columns]
            price_cols = [c for c in ["ltp", "spot_price", "mid_price"] if c in df.columns]
            greeks_cols = [c for c in ["delta", "gamma", "theta", "vega", "iv"] if c in df.columns]
            calc_cols = [c for c in df.columns if c not in contract_cols + price_cols + greeks_cols]

            if contract_cols:
                contract_comp = df[contract_cols].notna().sum().sum() / (len(df) * len(contract_cols)) * 100
                print(f"  Contract Info: {contract_comp:.1f}%")

            if price_cols:
                price_comp = df[price_cols].notna().sum().sum() / (len(df) * len(price_cols)) * 100
                print(f"  Price Data: {price_comp:.1f}%")

            if greeks_cols:
                greeks_comp = df[greeks_cols].notna().sum().sum() / (len(df) * len(greeks_cols)) * 100
                print(f"  Greeks: {greeks_comp:.1f}%")

            print(f"  Calculated Columns: {len(calc_cols)}")

            # Underlying coverage
            if "underlying" in df.columns:
                underlyings = df["underlying"].unique()
                print(f"\nUnderlying Coverage: {len(underlyings)}")
                for u in underlyings:
                    count = len(df[df["underlying"] == u])
                    print(f"  {u}: {count} contracts")

            # Critical checks
            print(f"\nCritical Checks:")
            critical_cols = ["underlying", "strike", "option_type", "ltp", "spot_price"]
            missing_critical = [c for c in critical_cols if c not in df.columns]
            if missing_critical:
                print(f"  ERROR: Missing critical columns: {missing_critical}")
            else:
                print(f"  All critical columns present: OK")

            calc_cols_check = ["intrinsic_value", "extrinsic_value", "mid_price", "expected_move"]
            present_calc = [c for c in calc_cols_check if c in df.columns]
            print(f"  Calculated columns: {len(present_calc)}/{len(calc_cols_check)} present")

        except Exception as e:
            print(f"  ERROR analyzing Excel: {e}")

    # Recommendations
    print("\n" + "-" * 80)
    print("Recommendations:")
    print("-" * 80)

    if not excel_exists:
        print("  - Run UPDATE_OPTIONCHAIN_MASTER.bat to create Excel file")
    elif excel_age > 3600:
        print("  - Excel file is stale - run UPDATE_OPTIONCHAIN_MASTER.bat to refresh")

    if not csv_exists:
        print("  - CSV source missing - check if live system is running")
    elif csv_age > 600:
        print("  - CSV source is stale - check live system status")

    if excel_exists and completeness < 70:
        print("  - Data completeness is low - check data sources")

    print("\n" + "=" * 80)
    print("  MONITORING COMPLETE")
    print("=" * 80)
    print(f"\nCurrent Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")


if __name__ == "__main__":
    monitor_performance()
