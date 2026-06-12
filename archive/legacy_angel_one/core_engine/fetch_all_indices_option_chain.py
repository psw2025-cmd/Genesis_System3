"""
Fetch option chain for ALL available indices from Angel One.

This script fetches options for:
- NIFTY (NFO)
- BANKNIFTY (NFO)
- FINNIFTY (NFO)
- MIDCPNIFTY (NFO)
- SENSEX (BFO)

And saves to a single combined CSV file without duplicate headers.
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


# All available indices
AVAILABLE_INDICES = [
    {"name": "NIFTY", "exchange": "NFO"},
    {"name": "BANKNIFTY", "exchange": "NFO"},
    {"name": "FINNIFTY", "exchange": "NFO"},
    {"name": "MIDCPNIFTY", "exchange": "NFO"},
    {"name": "SENSEX", "exchange": "BFO"},
]


def fetch_all_indices_option_chain(include_all_strikes: bool = False, output_file: str = None):
    """
    Fetch option chain for all available indices and save to CSV.

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

    print("=" * 80)
    print("FETCHING OPTION CHAIN FOR ALL INDICES")
    print("=" * 80)
    print(f"Indices to fetch: {', '.join([idx['name'] for idx in AVAILABLE_INDICES])}")
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
        return False

    # Collect all option chains
    all_option_chains = []
    fetch_stats = {}

    for idx_info in AVAILABLE_INDICES:
        underlying_name = idx_info["name"]
        exchange = idx_info["exchange"]

        print(f"{'='*80}")
        print(f"Fetching: {underlying_name} ({exchange})")
        print(f"{'='*80}")

        try:
            option_chain = broker.get_option_chain_by_underlying(
                underlying_name=underlying_name,
                exchange=exchange,
                include_all_strikes=include_all_strikes,
            )

            if option_chain and len(option_chain) > 0:
                # Add timestamps to each option
                ist = pytz.timezone("Asia/Kolkata")
                fetch_timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")
                fetch_timestamp_iso = datetime.now(ist).isoformat()
                fetch_date = datetime.now(ist).strftime("%Y-%m-%d")
                fetch_time = datetime.now(ist).strftime("%H:%M:%S")

                for opt in option_chain:
                    opt["fetch_timestamp"] = fetch_timestamp
                    opt["fetch_timestamp_iso"] = fetch_timestamp_iso
                    opt["fetch_date"] = fetch_date
                    opt["fetch_time"] = fetch_time

                all_option_chains.extend(option_chain)
                fetch_stats[underlying_name] = {
                    "status": "SUCCESS",
                    "count": len(option_chain),
                    "ce_count": len([opt for opt in option_chain if opt.get("option_type") == "CE"]),
                    "pe_count": len([opt for opt in option_chain if opt.get("option_type") == "PE"]),
                }
                print(
                    f"[OK] Fetched {len(option_chain)} options ({fetch_stats[underlying_name]['ce_count']} CE, {fetch_stats[underlying_name]['pe_count']} PE)"
                )
            else:
                fetch_stats[underlying_name] = {"status": "FAILED", "count": 0, "error": "No data returned"}
                print(f"[WARNING] No data returned for {underlying_name}")

        except Exception as e:
            fetch_stats[underlying_name] = {"status": "ERROR", "count": 0, "error": str(e)}
            print(f"[ERROR] Failed to fetch {underlying_name}: {e}")
            logger.error(f"Failed to fetch {underlying_name}: {e}", exc_info=True)

        print()

    # Summary
    print("=" * 80)
    print("FETCH SUMMARY")
    print("=" * 80)
    total_options = len(all_option_chains)
    print(f"Total options fetched: {total_options}")
    print()

    for idx_name, stats in fetch_stats.items():
        status_icon = "[OK]" if stats["status"] == "SUCCESS" else "[FAIL]"
        print(f"{status_icon} {idx_name:15} {stats['count']:4} options", end="")
        if stats["status"] == "SUCCESS":
            print(f" ({stats['ce_count']} CE, {stats['pe_count']} PE)")
        else:
            print(f" - {stats.get('error', 'Unknown error')}")

    print()

    if total_options == 0:
        print("[ERROR] No options fetched. Cannot create CSV.")
        return False

    # Create DataFrame
    print("Creating DataFrame...")
    df = pd.DataFrame(all_option_chains)

    # Add calculated columns
    print("Adding calculated columns...")
    try:
        fetch_timestamp = all_option_chains[0].get("fetch_timestamp") if all_option_chains else None
        df = add_calculated_columns(df, fetch_timestamp=fetch_timestamp)
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

    # Reorder columns (keep existing order for columns not in preferred_order)
    existing_cols = df.columns.tolist()
    ordered_cols = [col for col in preferred_order if col in existing_cols]
    remaining_cols = [col for col in existing_cols if col not in preferred_order]
    df = df[ordered_cols + remaining_cols]

    # Save to CSV (OVERWRITE, not append - to avoid duplicate headers)
    print(f"Saving to CSV: {output_file}")
    print(f"  Total rows: {len(df)}")
    print(f"  Total columns: {len(df.columns)}")
    print(
        f"  Indices included: {', '.join([idx for idx, stats in fetch_stats.items() if stats['status'] == 'SUCCESS'])}"
    )

    # Remove existing file if it exists to avoid any append issues
    if output_file.exists():
        output_file.unlink()
        print(f"  Removed existing file to avoid duplicate headers")

    # Write CSV with index=False to avoid row numbers
    df.to_csv(output_file, index=False, mode="w")

    print(f"\n[SUCCESS] Option chain saved to: {output_file}")
    print()

    # Show data completeness
    print("=" * 80)
    print("DATA COMPLETENESS")
    print("=" * 80)
    critical_cols = ["ltp", "oi", "volume", "bidPrice", "offerPrice", "delta"]
    for col in critical_cols:
        if col in df.columns:
            non_null = df[col].notna().sum()
            pct = (non_null / len(df)) * 100
            status = "[OK]" if pct >= 50 else "[LOW]"
            print(f"{status} {col:15} {non_null:4}/{len(df):4} ({pct:5.1f}%)")

    print()

    # Show breakdown by underlying
    print("=" * 80)
    print("BREAKDOWN BY UNDERLYING")
    print("=" * 80)
    if "underlying" in df.columns:
        breakdown = df.groupby("underlying").size().sort_values(ascending=False)
        for underlying, count in breakdown.items():
            print(f"  {underlying:15} {count:4} options")

    print()
    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fetch option chain for ALL available indices from Angel One")
    parser.add_argument(
        "--all-strikes",
        action="store_true",
        help="Fetch all strikes (default: only ATM strikes within 5 percent of spot)",
    )
    parser.add_argument("-o", "--output", default=None, help="Output CSV file path")

    args = parser.parse_args()

    success = fetch_all_indices_option_chain(include_all_strikes=args.all_strikes, output_file=args.output)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
