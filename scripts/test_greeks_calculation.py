"""
Test Greeks Calculation - Verify Black-Scholes fallback works
"""

import sys
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.broker import AngelOneBroker


def test_greeks():
    """Test Greeks calculation."""
    print("=" * 80)
    print("  TESTING GREEKS CALCULATION (WITH BLACK-SCHOLES FALLBACK)")
    print("=" * 80)

    # Initialize broker
    print("\n[STEP 1] Initializing Broker...")
    try:
        broker = AngelOneBroker(allow_data_only=True)
        print("  [OK] Broker initialized")
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        return False

    # Fetch option chain
    print("\n[STEP 2] Fetching Option Chain...")
    try:
        chain_data = broker.get_option_chain_by_underlying("NIFTY", exchange="NFO")

        if not chain_data or len(chain_data) == 0:
            print("  [ERROR] No data")
            return False

        print(f"  [OK] Fetched {len(chain_data)} contracts")

        # Convert to DataFrame
        df = pd.DataFrame(chain_data)

        # Check Greeks
        print("\n[STEP 3] Checking Greeks Data...")
        delta_count = df["delta"].notna().sum()
        gamma_count = df["gamma"].notna().sum()
        theta_count = df["theta"].notna().sum()
        vega_count = df["vega"].notna().sum()
        iv_count = df["iv"].notna().sum()

        print(f"  Delta populated: {delta_count}/{len(df)} ({delta_count/len(df)*100:.1f}%)")
        print(f"  Gamma populated: {gamma_count}/{len(df)} ({gamma_count/len(df)*100:.1f}%)")
        print(f"  Theta populated: {theta_count}/{len(df)} ({theta_count/len(df)*100:.1f}%)")
        print(f"  Vega populated: {vega_count}/{len(df)} ({vega_count/len(df)*100:.1f}%)")
        print(f"  IV populated: {iv_count}/{len(df)} ({iv_count/len(df)*100:.1f}%)")

        # Show sample
        if delta_count > 0:
            sample = df[df["delta"].notna()].iloc[0]
            print("\n[STEP 4] Sample Option with Greeks:")
            print(f"  Symbol: {sample.get('symbol')}")
            print(f"  Strike: {sample.get('strike')}")
            print(f"  LTP: {sample.get('ltp')}")
            print(f"  Delta: {sample.get('delta')}")
            print(f"  Gamma: {sample.get('gamma')}")
            print(f"  Theta: {sample.get('theta')}")
            print(f"  Vega: {sample.get('vega')}")
            print(f"  IV: {sample.get('iv')}")

        # Save updated CSV
        output_path = ROOT_DIR / "outputs" / "chain_raw_live.csv"
        df.to_csv(output_path, index=False)
        print(f"\n[STEP 5] Updated CSV saved to: {output_path}")

        if delta_count > 0:
            print("\n[RESULT] SUCCESS - Greeks are being calculated!")
        else:
            print("\n[RESULT] WARNING - Greeks still empty (may need market to be open)")

        return delta_count > 0

    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_greeks()
