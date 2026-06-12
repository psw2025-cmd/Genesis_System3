"""
Start Real Live Trading - Fetches real data from live market
Verifies all columns and starts paper trading with real market data
"""

import sys
from pathlib import Path
from datetime import datetime
import pytz
import pandas as pd
import json

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.broker import AngelOneBroker
from src.utils.market_hours import is_market_open
from scripts.run_live_chain import LiveChainRunner
from core.utils.logger import logger


def verify_data_columns(df: pd.DataFrame) -> dict:
    """Verify all expected columns are present in the data."""
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

    result = {
        "total_columns": len(df.columns),
        "expected_columns": len(expected_columns),
        "missing_columns": [],
        "extra_columns": [],
        "columns_with_data": [],
        "columns_empty": [],
    }

    for col in expected_columns:
        if col in df.columns:
            result["columns_with_data"].append(col)
            # Check if column has data
            if df[col].notna().sum() == 0:
                result["columns_empty"].append(col)
        else:
            result["missing_columns"].append(col)

    # Find extra columns
    for col in df.columns:
        if col not in expected_columns:
            result["extra_columns"].append(col)

    return result


def test_real_data_fetch():
    """Test fetching real data from live market."""
    print("=" * 80)
    print("  REAL LIVE MARKET DATA FETCH TEST")
    print("=" * 80)

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    # Check market hours
    market_open, reason = is_market_open(now)
    print(f"\nCurrent Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"Market Status: {'OPEN' if market_open else 'CLOSED'}")
    print(f"Reason: {reason}")

    if not market_open:
        print("\n[WARNING] Market is closed. Will use last available data.")
        print("For real live data, run during market hours (09:15-15:30 IST)")

    # Initialize broker
    print("\n[STEP 1] Initializing Broker Connection...")
    try:
        broker = AngelOneBroker(allow_data_only=True)
        print("  [OK] Broker initialized")
    except Exception as e:
        print(f"  [ERROR] Broker initialization failed: {e}")
        return False

    # Test fetching option chain for NIFTY
    print("\n[STEP 2] Fetching Real Option Chain Data (NIFTY)...")
    try:
        chain_data = broker.get_option_chain_by_underlying("NIFTY", exchange="NFO")

        if chain_data is None or len(chain_data) == 0:
            print("  [WARNING] No data returned from API")
            return False

        print(f"  [OK] Fetched {len(chain_data)} contracts")

        # Convert to DataFrame for analysis
        df = pd.DataFrame(chain_data)

        # Verify columns
        print("\n[STEP 3] Verifying Data Columns...")
        verification = verify_data_columns(df)

        print(f"\n  Total Columns: {verification['total_columns']}")
        print(f"  Expected Columns: {verification['expected_columns']}")
        print(f"  Columns with Data: {len(verification['columns_with_data'])}")

        if verification["missing_columns"]:
            print(f"\n  [WARNING] Missing Columns ({len(verification['missing_columns'])}):")
            for col in verification["missing_columns"]:
                print(f"    - {col}")
        else:
            print("\n  [OK] All expected columns present")

        if verification["columns_empty"]:
            print(f"\n  [WARNING] Empty Columns ({len(verification['columns_empty'])}):")
            for col in verification["columns_empty"]:
                print(f"    - {col}")

        if verification["extra_columns"]:
            print(f"\n  [INFO] Extra Columns ({len(verification['extra_columns'])}):")
            for col in verification["extra_columns"][:10]:  # Show first 10
                print(f"    - {col}")

        # Show sample data
        print("\n[STEP 4] Sample Data (First Row):")
        if len(df) > 0:
            sample = df.iloc[0]
            print(f"  Symbol: {sample.get('symbol', 'N/A')}")
            print(f"  Strike: {sample.get('strike', 'N/A')}")
            print(f"  LTP: {sample.get('ltp', 'N/A')}")
            print(f"  Volume: {sample.get('volume', 'N/A')}")
            print(f"  OI: {sample.get('oi', 'N/A')}")
            print(f"  Delta: {sample.get('delta', 'N/A')}")
            print(f"  IV: {sample.get('iv', 'N/A')}")
            print(f"  Bid: {sample.get('bidPrice', 'N/A')}")
            print(f"  Ask: {sample.get('offerPrice', 'N/A')}")

        # Save to CSV for verification
        output_path = ROOT_DIR / "outputs" / "chain_raw_live.csv"
        df.to_csv(output_path, index=False)
        print(f"\n[STEP 5] Data Saved to: {output_path}")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")

        return True

    except Exception as e:
        print(f"  [ERROR] Failed to fetch data: {e}")
        import traceback

        traceback.print_exc()
        return False


def start_real_paper_trading():
    """Start real paper trading with live market data."""
    print("\n" + "=" * 80)
    print("  STARTING REAL PAPER TRADING WITH LIVE MARKET DATA")
    print("=" * 80)

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    # Check market hours
    market_open, reason = is_market_open(now)

    if not market_open:
        print(f"\n[WARNING] Market is currently CLOSED")
        print(f"Reason: {reason}")
        print("\nOptions:")
        print("  1. Wait for market to open (09:15 IST)")
        print("  2. Use --ignore-market-hours flag to test anyway")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != "y":
            return False

    # Initialize runner (NOT simulation mode)
    print("\n[INFO] Initializing Live Chain Runner (REAL MODE)...")
    runner = LiveChainRunner(
        refresh_interval=5,
        use_websocket=True,
        prefer_weekly=True,
        sim_mode=False,  # REAL MODE
        ignore_market_hours=not market_open,
    )

    print("\n[INFO] Starting live trading cycle...")
    print("  - Real market data: YES")
    print("  - Paper trading: YES")
    print("  - Auto-updates: Every 5 seconds")
    print("\nPress Ctrl+C to stop")
    print("=" * 80)

    try:
        runner.run()
    except KeyboardInterrupt:
        print("\n\n[INFO] Stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Error during trading: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def main():
    """Main function."""
    print("=" * 80)
    print("  REAL LIVE MARKET TRADING - DATA VERIFICATION & START")
    print("=" * 80)

    # Step 1: Test data fetch
    print("\n[PHASE 1] Testing Real Data Fetch...")
    data_ok = test_real_data_fetch()

    if not data_ok:
        print("\n[ERROR] Data fetch test failed. Cannot proceed.")
        return

    # Step 2: Start paper trading
    print("\n" + "=" * 80)
    print("[PHASE 2] Starting Real Paper Trading...")
    print("=" * 80)

    # Auto-start if market is open, otherwise show instructions
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    market_open, reason = is_market_open(now)

    if market_open:
        print("\n[INFO] Market is OPEN - Starting real paper trading automatically...")
        start_real_paper_trading()
    else:
        print("\n[INFO] Market is CLOSED - Cannot start real trading")
        print(f"Reason: {reason}")
        print("\nTo start real paper trading when market opens:")
        print("  1. Run: START_REAL_LIVE_TRADING.bat")
        print("  2. Or: python scripts/run_live_chain.py")
        print("\nMarket hours: 09:15 - 15:30 IST (Mon-Fri)")


if __name__ == "__main__":
    main()
