"""
Test Excel with Virtual Live Data
Generates realistic virtual data and creates Excel to show it working
"""

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.enhance_optionchain_with_predictions import EnhancedOptionChainBuilder


def generate_virtual_live_data():
    """Generate realistic virtual live option chain data."""
    print("=" * 80)
    print("  GENERATING VIRTUAL LIVE DATA")
    print("=" * 80)

    virtual_data = []
    underlyings = {
        "NIFTY": {"spot": 29150, "strike_step": 50},
        "BANKNIFTY": {"spot": 48500, "strike_step": 100},
        "FINNIFTY": {"spot": 22100, "strike_step": 50},
        "MIDCPNIFTY": {"spot": 12500, "strike_step": 25},
    }

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    for underlying, config in underlyings.items():
        spot = config["spot"]
        strike_step = config["strike_step"]

        # Generate strikes around ATM (±5%)
        strikes = []
        for i in range(-10, 11):
            strike = round(spot + (i * strike_step))
            if strike > 0:
                strikes.append(strike)

        for strike in strikes:
            for opt_type in ["CE", "PE"]:
                # Realistic pricing
                moneyness = abs(spot - strike) / spot

                if opt_type == "CE":
                    intrinsic = max(0, spot - strike)
                else:
                    intrinsic = max(0, strike - spot)

                # Base premium calculation
                time_value = spot * 0.02 * (1 - moneyness)  # Time value
                iv_factor = np.random.uniform(0.15, 0.30)  # IV 15-30%
                premium = intrinsic + (time_value * iv_factor)

                # Add some randomness
                premium *= np.random.uniform(0.95, 1.05)
                premium = max(0.05, premium)  # Minimum premium

                # Volume and OI (higher near ATM)
                atm_distance = abs(strike - spot) / spot
                if atm_distance < 0.01:  # Very close to ATM
                    volume = np.random.randint(50000, 200000)
                    oi = np.random.randint(500000, 2000000)
                elif atm_distance < 0.02:  # Close to ATM
                    volume = np.random.randint(10000, 50000)
                    oi = np.random.randint(100000, 500000)
                else:
                    volume = np.random.randint(1000, 10000)
                    oi = np.random.randint(10000, 100000)

                # Greeks (simplified)
                if opt_type == "CE":
                    delta = min(0.99, max(0.01, 0.5 + (spot - strike) / (spot * 0.1)))
                else:
                    delta = max(-0.99, min(-0.01, -0.5 + (strike - spot) / (spot * 0.1)))

                gamma = np.random.uniform(0.00001, 0.0001)
                theta = np.random.uniform(-30, -5)
                vega = np.random.uniform(10, 50)
                iv = np.random.uniform(0.15, 0.30)

                # Bid/Ask
                spread_pct = np.random.uniform(0.3, 1.5)  # 0.3-1.5% spread
                mid_price = premium
                bid_price = mid_price * (1 - spread_pct / 200)
                ask_price = mid_price * (1 + spread_pct / 200)

                virtual_data.append(
                    {
                        "underlying": underlying,
                        "exchange": "NFO",
                        "token": f"{underlying}_{strike}_{opt_type}",
                        "symbol": f"{underlying}24FEB26{strike}{opt_type}",
                        "strike": strike,
                        "option_type": opt_type,
                        "expiry": "24FEB2026",
                        "spot_price": spot,
                        "ltp": premium,
                        "open": premium * np.random.uniform(0.98, 1.02),
                        "high": premium * np.random.uniform(1.00, 1.05),
                        "low": premium * np.random.uniform(0.95, 1.00),
                        "close": premium * np.random.uniform(0.98, 1.02),
                        "volume": volume,
                        "oi": oi,
                        "bidPrice": bid_price,
                        "bidQty": np.random.randint(100, 1000),
                        "offerPrice": ask_price,
                        "offerQty": np.random.randint(100, 1000),
                        "delta": delta,
                        "gamma": gamma,
                        "theta": theta,
                        "vega": vega,
                        "rho": np.random.uniform(-5, 5),
                        "iv": iv,
                        "change": premium * np.random.uniform(-0.05, 0.05),
                        "pChange": np.random.uniform(-5, 5),
                        "timestamp_ist": now.strftime("%Y-%m-%d %H:%M:%S IST"),
                        "timestamp_epoch": now.timestamp(),
                    }
                )

    df = pd.DataFrame(virtual_data)
    print(f"\nGenerated {len(df)} virtual contracts")
    print(f"Underlyings: {df['underlying'].unique()}")
    print(f"Total CE: {len(df[df['option_type'] == 'CE'])}")
    print(f"Total PE: {len(df[df['option_type'] == 'PE'])}")

    return df


def main():
    """Main execution."""
    print("\n" + "=" * 80)
    print("  EXCEL TEST WITH VIRTUAL LIVE DATA")
    print("=" * 80)

    # Generate virtual data
    virtual_df = generate_virtual_live_data()

    # Save to CSV first (simulate live data)
    csv_path = ROOT_DIR / "outputs" / "chain_raw_live.csv"
    virtual_df.to_csv(csv_path, index=False)
    print(f"\nSaved virtual data to: {csv_path}")

    # Build Excel with virtual data
    print("\n" + "=" * 80)
    print("  BUILDING EXCEL WITH VIRTUAL DATA")
    print("=" * 80)

    builder = EnhancedOptionChainBuilder()

    # Load virtual data
    df = virtual_df.copy()
    excel_sheets = {}

    # Add all calculations
    print("\nAdding calculations...")
    df = builder.add_all_calculations(df)

    # Add ML predictions
    print("Adding ML predictions...")
    df = builder.add_ml_predictions(df)

    # Add trade signals
    print("Adding trade signals...")
    df = builder.add_trade_signals(df)

    # Fill missing data
    df = builder.fill_missing_data(df)

    # Create Excel
    excel_path = ROOT_DIR / "outputs" / "OptionChain_Master_VIRTUAL_TEST.xlsx"
    builder.excel_path = excel_path

    output_path = builder.create_excel_file(df, excel_sheets)

    print("\n" + "=" * 80)
    print("  VIRTUAL DATA TEST COMPLETE")
    print("=" * 80)
    print(f"\nExcel file: {output_path}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # Show sample data
    print("\nSample Data (Top 5 by predicted profit):")
    if "predicted_profit" in df.columns:
        top = df.nlargest(5, "predicted_profit")[
            ["underlying", "strike", "option_type", "predicted_profit", "ml_confidence", "trade_signal"]
        ]
        print(top.to_string())

    print("\nStatus: SUCCESS")
    print("Open the Excel file to see virtual live data with all calculations!")


if __name__ == "__main__":
    main()
