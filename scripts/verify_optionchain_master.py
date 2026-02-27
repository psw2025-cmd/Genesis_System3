"""
Final Verification of OptionChain Master Excel File
Checks all sheets, columns, data quality, and calculations
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def verify_excel_file():
    """Comprehensive verification of Excel file."""
    excel_path = ROOT_DIR / "outputs" / "OptionChain_Master_v3_AI_FINAL.xlsx"

    print("=" * 80)
    print("  OPTIONCHAIN MASTER - FINAL VERIFICATION")
    print("=" * 80)

    if not excel_path.exists():
        print(f"ERROR: File not found: {excel_path}")
        return False

    try:
        xl = pd.ExcelFile(excel_path)

        print(f"\nFile: {excel_path.name}")
        print(f"Size: {excel_path.stat().st_size:,} bytes")
        print(f"Sheets: {len(xl.sheet_names)}")
        print(f"Sheet names: {xl.sheet_names}")

        # Verify main data sheet
        main_sheet = "CHAIN_RAW" if "CHAIN_RAW" in xl.sheet_names else "OptionChain_Data"
        if main_sheet not in xl.sheet_names:
            main_sheet = xl.sheet_names[0]

        print(f"\nMain Sheet: {main_sheet}")
        df = pd.read_excel(xl, sheet_name=main_sheet)

        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")

        # Check critical columns
        critical_cols = ["underlying", "strike", "option_type", "ltp", "spot_price"]
        missing_critical = [col for col in critical_cols if col not in df.columns]

        if missing_critical:
            print(f"  ERROR: Missing critical columns: {missing_critical}")
            return False
        else:
            print(f"  All critical columns present: OK")

        # Check calculated columns
        calc_cols = [
            "intrinsic_value",
            "extrinsic_value",
            "bid_ask_spread",
            "mid_price",
            "atm_distance",
            "atm_distance_pct",
            "expected_move",
            "gamma_exposure",
            "theta_exposure",
            "liquidity_score",
            "iv_rank",
            "breakeven_price",
            "theoretical_price",
            "moneyness",
        ]

        present_calc = [col for col in calc_cols if col in df.columns]
        missing_calc = [col for col in calc_cols if col not in df.columns]

        print(f"\nCalculated Columns:")
        print(f"  Present: {len(present_calc)}/{len(calc_cols)}")
        if present_calc:
            print(f"    {', '.join(present_calc[:5])}...")
        if missing_calc:
            print(f"  Missing: {', '.join(missing_calc)}")

        # Data completeness
        total_cells = len(df) * len(df.columns)
        filled_cells = df.notna().sum().sum()
        completeness = (filled_cells / total_cells) * 100

        print(f"\nData Completeness: {completeness:.1f}%")

        # Check data quality by column category
        print(f"\nData Quality by Category:")

        # Contract info
        contract_cols = ["underlying", "strike", "option_type", "expiry", "token"]
        contract_completeness = df[contract_cols].notna().sum().sum() / (len(df) * len(contract_cols)) * 100
        print(f"  Contract Info: {contract_completeness:.1f}%")

        # Price data
        price_cols = ["ltp", "spot_price", "mid_price", "bidPrice", "offerPrice"]
        price_cols = [c for c in price_cols if c in df.columns]
        if price_cols:
            price_completeness = df[price_cols].notna().sum().sum() / (len(df) * len(price_cols)) * 100
            print(f"  Price Data: {price_completeness:.1f}%")

        # Greeks
        greeks_cols = ["delta", "gamma", "theta", "vega", "iv"]
        greeks_cols = [c for c in greeks_cols if c in df.columns]
        if greeks_cols:
            greeks_completeness = df[greeks_cols].notna().sum().sum() / (len(df) * len(greeks_cols)) * 100
            print(f"  Greeks: {greeks_completeness:.1f}%")

        # Calculated columns
        if present_calc:
            calc_completeness = df[present_calc].notna().sum().sum() / (len(df) * len(present_calc)) * 100
            print(f"  Calculated: {calc_completeness:.1f}%")

        # Verify calculations are correct
        print(f"\nCalculation Verification:")

        # Intrinsic value check
        if "intrinsic_value" in df.columns and "spot_price" in df.columns and "strike" in df.columns:
            sample = df[df["intrinsic_value"].notna() & df["spot_price"].notna() & df["strike"].notna()].head(5)
            errors = 0
            for idx, row in sample.iterrows():
                spot = row["spot_price"]
                strike = row["strike"]
                opt_type = str(row["option_type"]).upper()
                intrinsic = row["intrinsic_value"]

                if opt_type == "CE":
                    expected = max(0, spot - strike)
                else:
                    expected = max(0, strike - spot)

                if abs(intrinsic - expected) > 0.01:
                    errors += 1

            if errors == 0:
                print(f"  Intrinsic Value: OK")
            else:
                print(f"  Intrinsic Value: {errors} errors found")

        # Mid price check
        if "mid_price" in df.columns and "bidPrice" in df.columns and "offerPrice" in df.columns:
            sample = df[df["mid_price"].notna() & df["bidPrice"].notna() & df["offerPrice"].notna()].head(5)
            errors = 0
            for idx, row in sample.iterrows():
                mid = row["mid_price"]
                expected = (row["bidPrice"] + row["offerPrice"]) / 2
                if abs(mid - expected) > 0.01:
                    errors += 1

            if errors == 0:
                print(f"  Mid Price: OK")
            else:
                print(f"  Mid Price: {errors} errors found")

        # Check all sheets
        print(f"\nSheet Verification:")
        for sheet_name in xl.sheet_names:
            try:
                sheet_df = pd.read_excel(xl, sheet_name=sheet_name, nrows=5)
                print(
                    f"  {sheet_name}: {len(pd.read_excel(xl, sheet_name=sheet_name))} rows, {len(sheet_df.columns)} columns - OK"
                )
            except Exception as e:
                print(f"  {sheet_name}: ERROR - {str(e)}")

        # Final status
        print(f"\n" + "=" * 80)
        if completeness > 75 and len(present_calc) >= 10:
            print("  STATUS: PRODUCTION READY")
        elif completeness > 60:
            print("  STATUS: GOOD (Minor improvements possible)")
        else:
            print("  STATUS: NEEDS IMPROVEMENT")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = verify_excel_file()
    sys.exit(0 if success else 1)
