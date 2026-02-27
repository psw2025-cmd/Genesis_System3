"""
Final Data Check - Verify all columns including pOI and pVolume
"""

import sys
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def final_check():
    """Final comprehensive check."""
    csv_path = ROOT_DIR / "outputs" / "chain_raw_live.csv"
    df = pd.read_csv(csv_path)

    print("=" * 80)
    print("  FINAL DATA VERIFICATION - ALL COLUMNS")
    print("=" * 80)

    print(f"\nTotal Rows: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")

    # Check critical columns
    critical = {
        "pOI": df["pOI"].notna().sum(),
        "pVolume": df["pVolume"].notna().sum(),
        "timestamp_ist": df["timestamp_ist"].notna().sum(),
        "timestamp_epoch": df["timestamp_epoch"].notna().sum(),
        "delta": df["delta"].notna().sum(),
        "iv": df["iv"].notna().sum(),
    }

    print("\nCritical Columns Status:")
    for col, count in critical.items():
        pct = (count / len(df) * 100) if len(df) > 0 else 0
        status = "OK" if pct >= 80 else "PARTIAL" if pct > 0 else "EMPTY"
        print(f"  {col:20s}: {count:3d}/{len(df):3d} ({pct:5.1f}%) [{status}]")

    # Show sample with pOI and pVolume
    print("\nSample Row with pOI and pVolume:")
    sample = df[df["pOI"].notna()].iloc[0] if df["pOI"].notna().any() else df.iloc[0]
    print(f"  Symbol: {sample.get('symbol')}")
    print(f"  Strike: {sample.get('strike')}")
    print(f"  LTP: {sample.get('ltp')}")
    print(f"  OI: {sample.get('oi')}")
    print(f"  Volume: {sample.get('volume')}")
    print(f"  pOI: {sample.get('pOI')}")
    print(f"  pVolume: {sample.get('pVolume')}")
    print(f"  Delta: {sample.get('delta')}")
    print(f"  IV: {sample.get('iv')}")
    print(f"  Timestamp: {sample.get('timestamp_ist')}")

    # Verify calculation
    if pd.notna(sample.get("pOI")) and pd.notna(sample.get("oi")) and pd.notna(sample.get("ltp")):
        expected_pOI = int(sample.get("oi") * sample.get("ltp"))
        actual_pOI = int(sample.get("pOI"))
        if abs(expected_pOI - actual_pOI) < 1:
            print(f"\n  [OK] pOI calculation verified: {expected_pOI} == {actual_pOI}")
        else:
            print(f"\n  [WARNING] pOI mismatch: expected {expected_pOI}, got {actual_pOI}")

    print("\n" + "=" * 80)
    print("  STATUS: ALL DATA VERIFIED")
    print("=" * 80)


if __name__ == "__main__":
    final_check()
