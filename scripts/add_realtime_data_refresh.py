"""
Add Real-Time Data Refresh to Dashboard Backend
Ensures dashboard always shows fresh data from broker
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

import pytz
import requests

ROOT_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"


async def refresh_spot_prices():
    """Refresh spot prices from live sources"""
    symbols = {
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "FINNIFTY": "^NSEFINNIFTY",
        "MIDCPNIFTY": "^NSEMIDCP",
        "SENSEX": "^BSESN",
    }

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

    live_prices = {}
    for underlying, yahoo_symbol in symbols.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
            response = session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "chart" in data and "result" in data["chart"]:
                    result = data["chart"]["result"][0]
                    meta = result.get("meta", {})
                    ltp = meta.get("regularMarketPrice")
                    if ltp:
                        live_prices[underlying] = ltp
        except:
            pass

    return live_prices


async def update_chain_csv(underlying: str, spot_price: float):
    """Update chain CSV with fresh spot price"""
    try:
        import pandas as pd

        chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
        if chain_file.exists():
            df = pd.read_csv(chain_file)
            if "underlying" in df.columns and "spot_price" in df.columns:
                mask = df["underlying"].astype(str).str.upper() == underlying.upper()
                if mask.any():
                    df.loc[mask, "spot_price"] = spot_price
                    df.to_csv(chain_file, index=False)
                    return True
    except:
        pass
    return False


async def data_refresh_loop():
    """Main refresh loop - runs every 30 seconds"""
    while True:
        try:
            # Fetch live spot prices
            live_prices = await refresh_spot_prices()

            # Update CSV files
            for underlying, spot_price in live_prices.items():
                await update_chain_csv(underlying, spot_price)

            # Log refresh
            timestamp = datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()
            print(f"[{timestamp}] Data refreshed: {len(live_prices)} underlyings")

        except Exception as e:
            print(f"Error in data refresh: {e}")

        # Wait 30 seconds
        await asyncio.sleep(30)


if __name__ == "__main__":
    print("Starting real-time data refresh service...")
    asyncio.run(data_refresh_loop())
