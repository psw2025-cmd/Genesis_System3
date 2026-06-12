"""
Auto-fetch option chain for all indices every hour during market hours.

This script:
- Auto-detects market hours (9:15 AM - 3:30 PM IST, Mon-Fri)
- Fetches all indices every hour
- Adds timestamp to each row
- Appends to same CSV file (storage/live/option_chain_ALL_INDICES.csv)
- Can be scheduled to run every hour via Windows Task Scheduler
"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
import pytz

ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.broker import AngelOneBroker
from core.utils.logger import logger
from core.utils.option_chain_calculations import add_calculated_columns


def is_market_open():
    """
    Check if Indian stock market is currently open or should fetch data.

    Market hours: 9:15 AM - 3:30 PM IST, Monday to Friday
    Also fetches if within 15 minutes before market opens (pre-market data)
    Excludes market holidays (basic check - can be enhanced)

    Returns:
        bool: True if market is open or should fetch, False otherwise
    """
    # IST timezone
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    # Check if weekend (Saturday=5, Sunday=6)
    if now.weekday() >= 5:
        return False

    # Market hours: 9:15 AM - 3:30 PM IST
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)

    # Pre-market: Start fetching 15 minutes before market opens (9:00 AM)
    pre_market_start = now.replace(hour=9, minute=0, second=0, microsecond=0)

    # Check if current time is within market hours OR pre-market window
    is_open = pre_market_start <= now <= market_close

    return is_open


def get_market_status():
    """
    Get detailed market status information.

    Returns:
        dict with market status details
    """
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    status = {
        "is_open": is_market_open(),
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S IST"),
        "day_of_week": now.strftime("%A"),
        "is_weekend": now.weekday() >= 5,
    }

    if status["is_open"]:
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        time_until_close = market_close - now
        time_str = str(time_until_close).split(".")[0]
        status["time_until_close"] = time_str
    else:
        if now.weekday() >= 5:
            status["reason"] = "Weekend"
        elif now < now.replace(hour=9, minute=0, second=0, microsecond=0):
            market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
            time_until_open = market_open - now
            time_str = str(time_until_open).split(".")[0]
            status["reason"] = f"Pre-market (starts fetching at 9:00 AM, opens in {time_str})"
        elif now < now.replace(hour=9, minute=15, second=0, microsecond=0):
            market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
            time_until_open = market_open - now
            time_str = str(time_until_open).split(".")[0]
            status["reason"] = f"Pre-market window (9:00-9:15 AM) - fetching pre-market data"
        else:
            status["reason"] = "Post-market"

    return status


def fetch_and_append_option_chain(include_all_strikes: bool = False, output_file: str = None, force: bool = False):
    """
    Fetch option chain for all indices and append to CSV with timestamp.

    Args:
        include_all_strikes: If True, fetch all strikes. If False, only ATM strikes.
        output_file: Output CSV file path. Default: storage/live/option_chain_ALL_INDICES.csv
    """
    if output_file is None:
        output_file = ROOT_DIR / "storage" / "live" / "option_chain_ALL_INDICES.csv"
    else:
        output_file = Path(output_file)

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Check market status
    market_status = get_market_status()

    print("=" * 80)
    print("AUTO-FETCH OPTION CHAIN (HOURLY)")
    print("=" * 80)
    print(f"Current time: {market_status['current_time']}")
    print(f"Day: {market_status['day_of_week']}")
    print(f"Market status: {'OPEN' if market_status['is_open'] else 'CLOSED'}")
    if not market_status["is_open"]:
        print(f"Reason: {market_status.get('reason', 'Unknown')}")
    else:
        print(f"Time until close: {market_status.get('time_until_close', 'N/A')}")
    print()

    # Check if market is open (unless forced)
    if not force and not market_status["is_open"]:
        print("[SKIP] Market is closed. Skipping fetch.")
        print("       Will fetch automatically when market opens.")
        print("       Use --force flag to fetch anyway (for testing).")
        return False

    if force and not market_status["is_open"]:
        print("[FORCE] Market is closed, but forcing fetch anyway...")
        print()

    # Available indices
    AVAILABLE_INDICES = [
        {"name": "NIFTY", "exchange": "NFO"},
        {"name": "BANKNIFTY", "exchange": "NFO"},
        {"name": "FINNIFTY", "exchange": "NFO"},
        {"name": "MIDCPNIFTY", "exchange": "NFO"},
        {"name": "SENSEX", "exchange": "BFO"},
    ]

    print(f"Fetching option chain for: {', '.join([idx['name'] for idx in AVAILABLE_INDICES])}")
    print(f"Include all strikes: {include_all_strikes}")
    print(f"Output file: {output_file}")
    print()

    # Initialize broker
    print("Initializing AngelOne broker...")
    try:
        broker = AngelOneBroker(allow_data_only=True)
        print("[OK] Broker initialized\n")
    except Exception as e:
        print(f"[ERROR] Failed to initialize broker: {e}")
        logger.error(f"Broker initialization failed: {e}", exc_info=True)
        return False

    # Get current timestamp
    ist = pytz.timezone("Asia/Kolkata")
    fetch_timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")
    fetch_timestamp_iso = datetime.now(ist).isoformat()

    print(f"Fetch timestamp: {fetch_timestamp}")
    print()

    # Collect all option chains
    all_option_chains = []
    fetch_stats = {}

    for idx_info in AVAILABLE_INDICES:
        underlying_name = idx_info["name"]
        exchange = idx_info["exchange"]

        print(f"Fetching: {underlying_name} ({exchange})...", end=" ")

        try:
            option_chain = broker.get_option_chain_by_underlying(
                underlying_name=underlying_name,
                exchange=exchange,
                include_all_strikes=include_all_strikes,
            )

            if option_chain and len(option_chain) > 0:
                # Add timestamp to each option
                for opt in option_chain:
                    opt["fetch_timestamp"] = fetch_timestamp
                    opt["fetch_timestamp_iso"] = fetch_timestamp_iso
                    opt["fetch_date"] = datetime.now(ist).strftime("%Y-%m-%d")
                    opt["fetch_time"] = datetime.now(ist).strftime("%H:%M:%S")

                all_option_chains.extend(option_chain)
                fetch_stats[underlying_name] = {
                    "status": "SUCCESS",
                    "count": len(option_chain),
                }
                print(f"[OK] {len(option_chain)} options")
            else:
                fetch_stats[underlying_name] = {"status": "FAILED", "count": 0, "error": "No data returned"}
                print(f"[FAIL] No data")

        except Exception as e:
            fetch_stats[underlying_name] = {"status": "ERROR", "count": 0, "error": str(e)}
            print(f"[ERROR] {str(e)[:50]}")
            logger.error(f"Failed to fetch {underlying_name}: {e}", exc_info=True)

    print()

    if len(all_option_chains) == 0:
        print("[ERROR] No options fetched. Cannot append to CSV.")
        return False

    # Create DataFrame
    df_new = pd.DataFrame(all_option_chains)

    # Add calculated columns
    print("Adding calculated columns...")
    try:
        fetch_timestamp = all_option_chains[0].get("fetch_timestamp") if all_option_chains else None
        df_new = add_calculated_columns(df_new, fetch_timestamp=fetch_timestamp)
        print(f"[OK] Added calculated columns")
    except Exception as e:
        print(f"[WARNING] Failed to add calculated columns: {e}")
        logger.warning(f"Failed to add calculated columns: {e}", exc_info=True)

    # Ensure consistent column order (includes timestamps and calculated columns)
    preferred_order = [
        "fetch_timestamp",
        "fetch_timestamp_iso",
        "fetch_date",
        "fetch_time",
        "underlying",
        "exchange",
        "tradingSymbol",
        "symbol",
        "name",
        "token",
        "expiry",
        "expiry_date",
        "strike",
        "option_type",
        "instrumentType",
        "lotSize",
        "tickSize",
        "spot_price",
        "moneyness",
        "ltp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "oi",
        "change",
        "pChange",
        "bidPrice",
        "bidQty",
        "offerPrice",
        "offerQty",
        "intrinsic_value",
        "extrinsic_value",
        "intrinsic_pct",
        "atm_distance",
        "atm_distance_pct",
        "bid_ask_spread",
        "mid_price",
        "bid_ask_spread_pct",
        "volume_oi_ratio",
        "premium_pct_of_strike",
        "premium_pct_of_spot",
        "days_to_expiry",
        "time_to_expiry",
        "delta",
        "gamma",
        "theta",
        "vega",
        "rho",
        "iv",
        "delta_gamma_ratio",
        "theta_per_day",
        "pTime",
        "pOI",
        "pVolume",
    ]

    # Reorder columns
    existing_cols = df_new.columns.tolist()
    ordered_cols = [col for col in preferred_order if col in existing_cols]
    remaining_cols = [col for col in existing_cols if col not in preferred_order]
    df_new = df_new[ordered_cols + remaining_cols]

    # Append to CSV
    file_exists = output_file.exists()

    if file_exists:
        # Read existing file to check structure
        try:
            df_existing = pd.read_csv(output_file)
            print(f"Existing file found: {len(df_existing)} rows")

            # Remove duplicate columns from existing file if present
            cols_to_remove = ["strikePrice", "optionType", "impliedVolatility"]
            for col in cols_to_remove:
                if col in df_existing.columns and col not in df_new.columns:
                    df_existing = df_existing.drop(columns=[col])
                    print(f"Removed duplicate column '{col}' from existing data")

            # Ensure timestamp columns are strings in existing data
            timestamp_cols = ["fetch_timestamp", "fetch_timestamp_iso", "fetch_date", "fetch_time"]
            for col in timestamp_cols:
                if col in df_existing.columns:
                    df_existing[col] = df_existing[col].astype(str).replace("nan", "")

            # Add calculated columns to existing data if missing
            calc_cols = [
                "intrinsic_value",
                "extrinsic_value",
                "intrinsic_pct",
                "atm_distance",
                "atm_distance_pct",
                "bid_ask_spread",
                "mid_price",
                "bid_ask_spread_pct",
                "volume_oi_ratio",
                "premium_pct_of_strike",
                "premium_pct_of_spot",
                "days_to_expiry",
                "time_to_expiry",
                "delta_gamma_ratio",
                "theta_per_day",
            ]
            missing_calc = [col for col in calc_cols if col not in df_existing.columns]
            if missing_calc:
                print(f"Adding calculated columns to existing data: {len(missing_calc)} columns")
                try:
                    # Get fetch_date from existing data if available
                    fetch_date_col = df_existing.get("fetch_date", pd.Series())
                    fetch_timestamp_for_calc = None
                    if not fetch_date_col.empty and fetch_date_col.notna().any():
                        fetch_timestamp_for_calc = fetch_date_col.iloc[0] if pd.notna(fetch_date_col.iloc[0]) else None
                    df_existing = add_calculated_columns(df_existing, fetch_timestamp=fetch_timestamp_for_calc)
                    print(f"[OK] Added calculated columns to existing data")
                except Exception as e:
                    print(f"[WARNING] Failed to add calculated columns to existing data: {e}")

            # Append new data
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            print(f"Combined data: {len(df_combined)} rows (added {len(df_new)} new rows)")

            # Save combined file
            df_combined.to_csv(output_file, index=False, mode="w")
            print(f"[OK] Data appended to: {output_file}")

        except Exception as e:
            print(f"[ERROR] Failed to read existing file: {e}")
            # Save new file anyway
            df_new.to_csv(output_file, index=False, mode="w")
            print(f"[OK] Created new file: {output_file}")
    else:
        # Create new file
        df_new.to_csv(output_file, index=False, mode="w")
        print(f"[OK] Created new file: {output_file}")

    print()
    print("=" * 80)
    print("FETCH SUMMARY")
    print("=" * 80)
    print(f"Timestamp: {fetch_timestamp}")
    print(f"Total options fetched: {len(df_new)}")
    print()

    for idx_name, stats in fetch_stats.items():
        status_icon = "[OK]" if stats["status"] == "SUCCESS" else "[FAIL]"
        print(f"{status_icon} {idx_name:15} {stats['count']:4} options")

    print()
    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Auto-fetch option chain for all indices (hourly during market hours)")
    parser.add_argument(
        "--all-strikes",
        action="store_true",
        help="Fetch all strikes (default: only ATM strikes within 5 percent of spot)",
    )
    parser.add_argument("-o", "--output", default=None, help="Output CSV file path")
    parser.add_argument("--force", action="store_true", help="Force fetch even if market is closed (for testing)")

    args = parser.parse_args()

    # Check market status
    market_status = get_market_status()

    if not args.force and not market_status["is_open"]:
        print("=" * 80)
        print("MARKET CLOSED")
        print("=" * 80)
        print(f"Current time: {market_status['current_time']}")
        print(f"Status: {market_status.get('reason', 'Market is closed')}")
        print()
        print("Use --force flag to fetch anyway (for testing)")
        return 1

    success = fetch_and_append_option_chain(
        include_all_strikes=args.all_strikes, output_file=args.output, force=args.force
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
