"""
Verify All Data Completeness - Check all columns and data quality
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def verify_all_data():
    """Verify all data in chain_raw_live.csv."""
    csv_path = ROOT_DIR / "outputs" / "chain_raw_live.csv"

    if not csv_path.exists():
        print(f"[ERROR] File not found: {csv_path}")
        return

    print("=" * 80)
    print("  COMPREHENSIVE DATA VERIFICATION")
    print("=" * 80)

    df = pd.read_csv(csv_path)

    print(f"\nFile: {csv_path}")
    print(f"Total Rows: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")

    # Check all columns
    print("\n" + "=" * 80)
    print("  COLUMN DATA COMPLETENESS")
    print("=" * 80)

    critical_columns = {
        "Contract Info": ["underlying", "exchange", "symbol", "strike", "option_type", "expiry", "token"],
        "Price Data": ["ltp", "open", "high", "low", "close", "bidPrice", "offerPrice"],
        "Market Data": ["volume", "oi", "change", "pChange"],
        "Greeks": ["delta", "gamma", "theta", "vega", "rho", "iv"],
        "Premium Data": ["pTime", "pOI", "pVolume"],
        "Other": ["spot_price", "moneyness", "timestamp_ist", "timestamp_epoch"],
    }

    issues = []

    for category, cols in critical_columns.items():
        print(f"\n[{category}]")
        for col in cols:
            if col in df.columns:
                non_null = df[col].notna().sum()
                pct = (non_null / len(df) * 100) if len(df) > 0 else 0

                # Check for invalid values
                invalid_count = 0
                if col in ["ltp", "bidPrice", "offerPrice", "iv"]:
                    invalid_count = ((df[col] <= 0) & df[col].notna()).sum()
                elif col == "delta":
                    # Delta can be negative for PE options, so check range differently
                    invalid_count = 0
                    for idx, row in df.iterrows():
                        if pd.notna(row.get(col)):
                            delta_val = row[col]
                            opt_type = row.get("option_type", "")
                            if opt_type == "CE" and (delta_val < 0 or delta_val > 1):
                                invalid_count += 1
                            elif opt_type == "PE" and (delta_val > 0 or delta_val < -1):
                                invalid_count += 1

                status = "OK" if pct > 90 and invalid_count == 0 else "PARTIAL" if pct > 0 else "EMPTY"
                if invalid_count > 0:
                    status = "INVALID"

                print(f"  {col:20s}: {non_null:3d}/{len(df):3d} ({pct:5.1f}%) [{status}]", end="")
                if invalid_count > 0:
                    print(f" - {invalid_count} invalid values")
                else:
                    print()

                if pct < 50 and col in ["ltp", "delta", "iv", "oi"]:
                    issues.append(f"{col}: Only {pct:.1f}% populated")
            else:
                print(f"  {col:20s}: MISSING")
                issues.append(f"{col}: Column missing")

    # Check data quality
    print("\n" + "=" * 80)
    print("  DATA QUALITY CHECKS")
    print("=" * 80)

    # Check bid <= ask
    if "bidPrice" in df.columns and "offerPrice" in df.columns:
        invalid_spread = ((df["bidPrice"] > df["offerPrice"]) & df["bidPrice"].notna() & df["offerPrice"].notna()).sum()
        if invalid_spread > 0:
            print(f"  [WARNING] {invalid_spread} rows with bidPrice > offerPrice")
            issues.append(f"Spread: {invalid_spread} invalid bid/ask spreads")
        else:
            print(f"  [OK] All bid/ask spreads valid")

    # Check LTP within bid/ask range
    if all(col in df.columns for col in ["ltp", "bidPrice", "offerPrice"]):
        invalid_ltp = 0
        for idx, row in df.iterrows():
            if pd.notna(row["ltp"]) and pd.notna(row["bidPrice"]) and pd.notna(row["offerPrice"]):
                if row["ltp"] < row["bidPrice"] or row["ltp"] > row["offerPrice"]:
                    invalid_ltp += 1
        if invalid_ltp > 0:
            print(f"  [WARNING] {invalid_ltp} rows with LTP outside bid/ask range")
            issues.append(f"LTP: {invalid_ltp} LTP values outside bid/ask")
        else:
            print(f"  [OK] All LTP values within bid/ask range")

    # Check delta range (should be 0-1 for CE, -1-0 for PE)
    if "delta" in df.columns:
        invalid_delta = 0
        for idx, row in df.iterrows():
            if pd.notna(row["delta"]):
                if row["option_type"] == "CE" and (row["delta"] < 0 or row["delta"] > 1):
                    invalid_delta += 1
                elif row["option_type"] == "PE" and (row["delta"] > 0 or row["delta"] < -1):
                    invalid_delta += 1
        if invalid_delta > 0:
            print(f"  [WARNING] {invalid_delta} rows with invalid delta range")
            issues.append(f"Delta: {invalid_delta} invalid delta values")
        else:
            print(f"  [OK] All delta values in valid range")

    # Check IV range (should be > 0 and < 2.0 typically)
    if "iv" in df.columns:
        invalid_iv = ((df["iv"] <= 0) | (df["iv"] > 2.0) & df["iv"].notna()).sum()
        if invalid_iv > 0:
            print(f"  [WARNING] {invalid_iv} rows with invalid IV (<=0 or >200%)")
            issues.append(f"IV: {invalid_iv} invalid IV values")
        else:
            print(f"  [OK] All IV values in valid range (0-200%)")

    # Check pOI and pVolume
    print("\n" + "=" * 80)
    print("  PREMIUM DATA (pOI, pVolume, pTime)")
    print("=" * 80)

    pOI_count = df["pOI"].notna().sum() if "pOI" in df.columns else 0
    pVolume_count = df["pVolume"].notna().sum() if "pVolume" in df.columns else 0
    pTime_count = df["pTime"].notna().sum() if "pTime" in df.columns else 0

    print(f"  pOI populated: {pOI_count}/{len(df)} ({pOI_count/len(df)*100:.1f}%)")
    print(f"  pVolume populated: {pVolume_count}/{len(df)} ({pVolume_count/len(df)*100:.1f}%)")
    print(f"  pTime populated: {pTime_count}/{len(df)} ({pTime_count/len(df)*100:.1f}%)")

    print("\n  [NOTE] pOI and pVolume are premium-weighted OI and Volume.")
    print("         - pOI = OI * LTP (total premium value in open interest)")
    print("         - pVolume = Volume * LTP (total premium value in volume)")
    print("         These are calculated from market data when available.")
    print(f"         Current status: pOI ({pOI_count/len(df)*100:.1f}%), pVolume ({pVolume_count/len(df)*100:.1f}%)")

    # Summary
    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80)

    if issues:
        print(f"  [WARNINGS] {len(issues)} issues found:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("  [OK] All data quality checks passed")

    # Show sample row
    print("\n" + "=" * 80)
    print("  SAMPLE DATA (First Row with Complete Data)")
    print("=" * 80)

    # Find a row with most data
    complete_row = None
    max_score = 0
    for idx, row in df.iterrows():
        score = sum(1 for col in ["ltp", "delta", "iv", "oi", "bidPrice", "offerPrice"] if pd.notna(row.get(col)))
        if score > max_score:
            max_score = score
            complete_row = row

    if complete_row is not None:
        for col in [
            "symbol",
            "strike",
            "option_type",
            "ltp",
            "bidPrice",
            "offerPrice",
            "volume",
            "oi",
            "delta",
            "gamma",
            "theta",
            "vega",
            "iv",
            "pOI",
            "pVolume",
            "pTime",
            "spot_price",
        ]:
            if col in complete_row.index:
                val = complete_row[col]
                print(f"  {col:15s}: {val}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    verify_all_data()
