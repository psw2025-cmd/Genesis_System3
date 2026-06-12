"""
Verify All Columns Fetched - Check real market data for all columns
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.broker import AngelOneBroker


def verify_all_columns():
    """Verify all columns are being fetched from real market."""
    print("=" * 80)
    print("  VERIFYING ALL COLUMNS FROM REAL MARKET DATA")
    print("=" * 80)

    # Initialize broker
    print("\n[STEP 1] Connecting to Broker...")
    try:
        broker = AngelOneBroker(allow_data_only=True)
        print("  [OK] Connected")
    except Exception as e:
        print(f"  [ERROR] Connection failed: {e}")
        return False

    # Fetch data for NIFTY
    print("\n[STEP 2] Fetching Real Market Data (NIFTY)...")
    try:
        chain_data = broker.get_option_chain_by_underlying("NIFTY", exchange="NFO")

        if not chain_data or len(chain_data) == 0:
            print("  [ERROR] No data returned")
            return False

        print(f"  [OK] Fetched {len(chain_data)} contracts")

        # Convert to DataFrame
        df = pd.DataFrame(chain_data)

        # Add timestamps if missing
        ist = pytz.timezone("Asia/Kolkata")
        now_ist = datetime.now(ist)
        if "timestamp_ist" not in df.columns:
            df["timestamp_ist"] = now_ist.strftime("%Y-%m-%d %H:%M:%S IST")
        if "timestamp_epoch" not in df.columns:
            df["timestamp_epoch"] = now_ist.timestamp()

        # Expected columns
        expected_columns = [
            "underlying",
            "exchange",
            "token",
            "symbol",
            "strike",
            "option_type",
            "expiry",
            "spot_price",
            "ltp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "oi",
            "bidPrice",
            "bidQty",
            "offerPrice",
            "offerQty",
            "delta",
            "gamma",
            "theta",
            "vega",
            "rho",
            "iv",
            "change",
            "pChange",
            "timestamp_ist",
            "timestamp_epoch",
        ]

        print("\n[STEP 3] Column Verification:")
        print(f"  Total columns in data: {len(df.columns)}")
        print(f"  Expected columns: {len(expected_columns)}")

        # Check each expected column
        print("\n  Column Status:")
        all_ok = True
        for col in expected_columns:
            if col in df.columns:
                # Check if has data
                has_data = df[col].notna().any()
                data_count = df[col].notna().sum()
                status = "OK" if has_data else "EMPTY"
                print(f"    {col:20s} [{status:5s}] ({data_count}/{len(df)} rows)")
                if not has_data:
                    all_ok = False
            else:
                print(f"    {col:20s} [MISSING]")
                all_ok = False

        # Show sample row
        print("\n[STEP 4] Sample Data (First Row):")
        if len(df) > 0:
            sample = df.iloc[0]
            for col in [
                "symbol",
                "strike",
                "option_type",
                "ltp",
                "volume",
                "oi",
                "bidPrice",
                "offerPrice",
                "delta",
                "iv",
                "spot_price",
            ]:
                if col in sample.index:
                    val = sample[col]
                    print(f"  {col:15s}: {val}")

        # Save updated data
        output_path = ROOT_DIR / "outputs" / "chain_raw_live.csv"
        df.to_csv(output_path, index=False)
        print(f"\n[STEP 5] Data saved to: {output_path}")

        if all_ok:
            print("\n[RESULT] ALL COLUMNS VERIFIED - DATA COMPLETE")
        else:
            print("\n[RESULT] SOME COLUMNS MISSING OR EMPTY")
            print("  Note: Some columns may be empty if market is closed")
            print("  All columns will be populated during market hours")

        return all_ok

    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    verify_all_columns()
