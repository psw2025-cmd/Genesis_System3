"""
Test script for Angel One Option Chain fetching.

Usage:
    python -m core.engine.test_angelone_option_chain [underlying] [--all-strikes]

Examples:
    python -m core.engine.test_angelone_option_chain NIFTY
    python -m core.engine.test_angelone_option_chain BANKNIFTY --all-strikes
    python -m core.engine.test_angelone_option_chain FINNIFTY
"""

import os
import sys
import argparse
import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.brokers.angel_one.broker import AngelOneBroker
from core.utils.logger import logger


def format_option_chain(option_chain, underlying_name):
    """Format option chain data for display with all available columns."""
    if not option_chain:
        print(f"\nNo option chain data available for {underlying_name}")
        return

    df = pd.DataFrame(option_chain)

    print(f"\n{'='*100}")
    print(f"OPTION CHAIN: {underlying_name} - COMPREHENSIVE DATA")
    print(f"{'='*100}")

    if "spot_price" in df.columns:
        spot = df["spot_price"].iloc[0]
        print(f"Spot Price: {spot:.2f}")

    if "expiry" in df.columns:
        expiry = df["expiry"].iloc[0]
        print(f"Expiry: {expiry}")

    print(f"Total Options: {len(df)}")

    # Check which columns are available
    has_greeks = any(df[col].notna().any() for col in ["delta", "gamma", "theta", "vega", "iv"] if col in df.columns)
    has_quote = any(df[col].notna().any() for col in ["open", "high", "low", "volume", "oi"] if col in df.columns)
    has_bidask = any(df[col].notna().any() for col in ["bidPrice", "offerPrice"] if col in df.columns)

    # Display basic info table
    print(f"\n{'='*100}")
    print("BASIC OPTION DATA")
    print(f"{'='*100}")
    print(f"{'Strike':<10} {'Type':<5} {'LTP':<10} {'Volume':<10} {'OI':<12} {'Moneyness':<10} {'Symbol':<30}")
    print("-" * 100)

    for opt in option_chain[:20]:  # Show first 20 for readability
        strike = opt.get("strike", 0)
        opt_type = opt.get("option_type", "")
        ltp = opt.get("ltp", None)
        volume = opt.get("volume", None)
        oi = opt.get("oi", None)
        moneyness = opt.get("moneyness", "")
        symbol = opt.get("symbol", "")

        ltp_str = f"{ltp:.2f}" if ltp is not None else "N/A"
        vol_str = f"{volume:,}" if volume is not None else "N/A"
        oi_str = f"{oi:,}" if oi is not None else "N/A"
        print(f"{strike:<10.2f} {opt_type:<5} {ltp_str:<10} {vol_str:<10} {oi_str:<12} {moneyness:<10} {symbol:<30}")

    if len(option_chain) > 20:
        print(f"... ({len(option_chain) - 20} more options)")

    # Display Greeks if available
    if has_greeks:
        print(f"\n{'='*100}")
        print("OPTION GREEKS")
        print(f"{'='*100}")
        print(f"{'Strike':<10} {'Type':<5} {'Delta':<10} {'Gamma':<10} {'Theta':<10} {'Vega':<10} {'IV':<10}")
        print("-" * 100)

        for opt in option_chain[:20]:
            strike = opt.get("strike", 0)
            opt_type = opt.get("option_type", "")
            delta = opt.get("delta", None)
            gamma = opt.get("gamma", None)
            theta = opt.get("theta", None)
            vega = opt.get("vega", None)
            iv = opt.get("iv", None)

            delta_str = f"{delta:.4f}" if delta is not None else "N/A"
            gamma_str = f"{gamma:.4f}" if gamma is not None else "N/A"
            theta_str = f"{theta:.2f}" if theta is not None else "N/A"
            vega_str = f"{vega:.2f}" if vega is not None else "N/A"
            iv_str = f"{iv:.2%}" if iv is not None else "N/A"
            print(
                f"{strike:<10.2f} {opt_type:<5} {delta_str:<10} {gamma_str:<10} {theta_str:<10} {vega_str:<10} {iv_str:<10}"
            )

    # Display bid/ask if available
    if has_bidask:
        print(f"\n{'='*100}")
        print("BID/ASK DATA")
        print(f"{'='*100}")
        print(f"{'Strike':<10} {'Type':<5} {'Bid':<10} {'BidQty':<10} {'Ask':<10} {'AskQty':<10} {'Spread':<10}")
        print("-" * 100)

        for opt in option_chain[:20]:
            strike = opt.get("strike", 0)
            opt_type = opt.get("option_type", "")
            bid = opt.get("bidPrice", None)
            bid_qty = opt.get("bidQty", None)
            ask = opt.get("offerPrice", None)
            ask_qty = opt.get("offerQty", None)

            bid_str = f"{bid:.2f}" if bid is not None else "N/A"
            bid_qty_str = f"{bid_qty:,}" if bid_qty is not None else "N/A"
            ask_str = f"{ask:.2f}" if ask is not None else "N/A"
            ask_qty_str = f"{ask_qty:,}" if ask_qty is not None else "N/A"

            spread = (ask - bid) if (ask is not None and bid is not None) else None
            spread_str = f"{spread:.2f}" if spread is not None else "N/A"

            print(
                f"{strike:<10.2f} {opt_type:<5} {bid_str:<10} {bid_qty_str:<10} {ask_str:<10} {ask_qty_str:<10} {spread_str:<10}"
            )

    # Summary statistics
    ce_options = [opt for opt in option_chain if opt.get("option_type") == "CE"]
    pe_options = [opt for opt in option_chain if opt.get("option_type") == "PE"]

    print(f"\n{'='*100}")
    print("SUMMARY STATISTICS")
    print(f"{'='*100}")
    print(f"  CE Options: {len(ce_options)}")
    print(f"  PE Options: {len(pe_options)}")

    if ce_options:
        ce_with_ltp = [opt for opt in ce_options if opt.get("ltp") is not None]
        if ce_with_ltp:
            ce_ltps = [opt["ltp"] for opt in ce_with_ltp]
            print(f"  CE LTP Range: {min(ce_ltps):.2f} - {max(ce_ltps):.2f}")

        ce_with_oi = [opt for opt in ce_options if opt.get("oi") is not None]
        if ce_with_oi:
            total_oi = sum(opt["oi"] for opt in ce_with_oi)
            print(f"  CE Total OI: {total_oi:,}")

    if pe_options:
        pe_with_ltp = [opt for opt in pe_options if opt.get("ltp") is not None]
        if pe_with_ltp:
            pe_ltps = [opt["ltp"] for opt in pe_with_ltp]
            print(f"  PE LTP Range: {min(pe_ltps):.2f} - {max(pe_ltps):.2f}")

        pe_with_oi = [opt for opt in pe_options if opt.get("oi") is not None]
        if pe_with_oi:
            total_oi = sum(opt["oi"] for opt in pe_with_oi)
            print(f"  PE Total OI: {total_oi:,}")

    # Column availability summary
    print(f"\n{'='*100}")
    print("DATA AVAILABILITY")
    print(f"{'='*100}")
    available_cols = []
    for col in [
        "ltp",
        "open",
        "high",
        "low",
        "volume",
        "oi",
        "bidPrice",
        "offerPrice",
        "delta",
        "gamma",
        "theta",
        "vega",
        "iv",
        "lotSize",
        "tickSize",
    ]:
        if col in df.columns and df[col].notna().any():
            available_cols.append(col)
    print(f"Available columns: {', '.join(available_cols)}")

    missing_cols = []
    for col in ["ltp", "volume", "oi", "delta", "gamma", "theta", "vega", "iv"]:
        if col not in df.columns or not df[col].notna().any():
            missing_cols.append(col)
    if missing_cols:
        print(f"Missing/empty columns: {', '.join(missing_cols)}")
        print("(Some data may not be available via API or market may be closed)")


def main():
    parser = argparse.ArgumentParser(description="Test Angel One Option Chain fetching")
    parser.add_argument(
        "underlying",
        nargs="?",
        default="NIFTY",
        help="Underlying name (default: NIFTY). Options: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX",
    )
    parser.add_argument(
        "--all-strikes",
        action="store_true",
        help="Fetch all strikes (default: only ATM strikes)",
    )
    parser.add_argument(
        "--exchange",
        default=None,
        help="Exchange code (NFO for NSE, BFO for BSE). Auto-detected if not specified.",
    )

    args = parser.parse_args()

    underlying_name = args.underlying.upper()

    # Determine exchange
    if args.exchange:
        exchange = args.exchange.upper()
    else:
        # Auto-detect based on underlying
        if underlying_name == "SENSEX":
            exchange = "BFO"
        else:
            exchange = "NFO"

    logger.info(f"=== Angel One Option Chain Test: {underlying_name} ===")
    print(f"Fetching option chain for {underlying_name} on {exchange}...")
    print(f"All strikes: {args.all_strikes}")

    try:
        # Initialize broker (allow_data_only=True for data fetching without live trading permission)
        print("\nInitializing AngelOne broker...")
        broker = AngelOneBroker(allow_data_only=True)
        print("Login successful.\n")

        # Fetch option chain
        print(f"Fetching option chain data...")
        option_chain = broker.get_option_chain_by_underlying(
            underlying_name=underlying_name,
            exchange=exchange,
            include_all_strikes=args.all_strikes,
        )

        if option_chain:
            format_option_chain(option_chain, underlying_name)

            # Save to CSV (OVERWRITE to avoid duplicate headers)
            output_file = f"storage/live/option_chain_{underlying_name}_{exchange}.csv"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            df = pd.DataFrame(option_chain)

            # Remove existing file if it exists to avoid any append/duplicate header issues
            if os.path.exists(output_file):
                os.remove(output_file)

            # Write CSV with index=False (no row numbers) and mode='w' (overwrite, not append)
            df.to_csv(output_file, index=False, mode="w")
            print(f"\nOption chain saved to: {output_file}")
            print(f"  Total rows: {len(df)}")
            print(f"  Total columns: {len(df.columns)}")
        else:
            print(f"\nFailed to fetch option chain for {underlying_name}")
            logger.error(f"Option chain fetch returned None for {underlying_name}")

    except Exception as e:
        print(f"\n[ERROR] Failed to fetch option chain: {e}")
        logger.error(f"Option chain test failed: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return 1

    logger.info("=== Angel One Option Chain Test Completed ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
