"""
Analyze chain_raw_live.csv - Show all columns and data availability
"""

import sys
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def analyze_csv():
    """Analyze the chain_raw_live.csv file."""
    csv_path = ROOT_DIR / "outputs" / "chain_raw_live.csv"

    if not csv_path.exists():
        print(f"[ERROR] File not found: {csv_path}")
        return

    print("=" * 80)
    print("  CHAIN_RAW_LIVE.CSV ANALYSIS")
    print("=" * 80)

    df = pd.read_csv(csv_path)

    print(f"\nFile: {csv_path}")
    print(f"Total Rows: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")

    print("\n" + "=" * 80)
    print("  COLUMN DATA AVAILABILITY")
    print("=" * 80)

    # Categorize columns
    contract_cols = ["underlying", "exchange", "symbol", "strike", "option_type", "expiry", "token"]
    price_cols = ["ltp", "open", "high", "low", "close", "bidPrice", "offerPrice"]
    market_cols = ["volume", "oi", "change", "pChange"]
    greeks_cols = ["delta", "gamma", "theta", "vega", "rho", "iv"]
    other_cols = ["spot_price", "moneyness", "timestamp_ist", "timestamp_epoch"]

    categories = {
        "Contract Info": contract_cols,
        "Price Data": price_cols,
        "Market Data": market_cols,
        "Greeks": greeks_cols,
        "Other": other_cols,
    }

    for category, cols in categories.items():
        print(f"\n[{category}]")
        for col in cols:
            if col in df.columns:
                non_null = df[col].notna().sum()
                pct = (non_null / len(df) * 100) if len(df) > 0 else 0
                status = "OK" if pct > 90 else "PARTIAL" if pct > 0 else "EMPTY"
                print(f"  {col:20s}: {non_null:3d}/{len(df):3d} ({pct:5.1f}%) [{status}]")
            else:
                print(f"  {col:20s}: MISSING")

    # Show missing columns
    all_expected = contract_cols + price_cols + market_cols + greeks_cols + other_cols
    missing = [col for col in all_expected if col not in df.columns]
    if missing:
        print(f"\n[MISSING COLUMNS]")
        for col in missing:
            print(f"  - {col}")

    # Show sample data
    print("\n" + "=" * 80)
    print("  SAMPLE DATA (First Row)")
    print("=" * 80)
    if len(df) > 0:
        sample = df.iloc[0]
        print(f"  Symbol: {sample.get('symbol', 'N/A')}")
        print(f"  Strike: {sample.get('strike', 'N/A')}")
        print(f"  Option Type: {sample.get('option_type', 'N/A')}")
        print(f"  Spot Price: {sample.get('spot_price', 'N/A')}")
        print(f"  LTP: {sample.get('ltp', 'N/A')}")
        print(f"  Bid: {sample.get('bidPrice', 'N/A')} | Ask: {sample.get('offerPrice', 'N/A')}")
        print(f"  Volume: {sample.get('volume', 'N/A')}")
        print(f"  OI: {sample.get('oi', 'N/A')}")
        print(f"  Delta: {sample.get('delta', 'N/A')}")
        print(f"  IV: {sample.get('iv', 'N/A')}")
        print(f"  Timestamp: {sample.get('timestamp_ist', 'N/A')}")

    # Summary
    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80)

    total_cols = len(df.columns)
    populated_cols = sum(1 for col in df.columns if df[col].notna().any())
    empty_cols = [col for col in df.columns if not df[col].notna().any()]

    print(f"  Total Columns: {total_cols}")
    print(f"  Columns with Data: {populated_cols}")
    print(f"  Empty Columns: {len(empty_cols)}")

    if empty_cols:
        print(f"\n  Empty Columns List:")
        for col in empty_cols:
            print(f"    - {col}")

    # Note about Greeks
    greeks_empty = all(not df[col].notna().any() for col in greeks_cols if col in df.columns)
    if greeks_empty:
        print("\n  [NOTE] Greeks columns (delta, gamma, theta, vega, rho, iv) are empty.")
        print("         This is normal when market is closed.")
        print("         Greeks data will be available during market hours (09:15-15:30 IST).")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    analyze_csv()
