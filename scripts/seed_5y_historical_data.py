import sys
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.data.historical_data_pipeline import HistoricalDataPipeline

def generate_synthetic_5y_history(symbol: str, base_price: float, drift: float = 0.0004, vol: float = 0.012) -> pd.DataFrame:
    np.random.seed(42 + hash(symbol) % 1000)
    end_date = datetime(2026, 8, 29)
    # Approx 1250 trading days in 5 years
    dates = [end_date - timedelta(days=int(i * 1.45)) for i in range(1250)]
    dates.reverse()

    prices = [base_price]
    for _ in range(1, len(dates)):
        ret = np.random.normal(drift, vol)
        prices.append(prices[-1] * (1 + ret))

    data = []
    for d, p in zip(dates, prices):
        daily_range = p * np.random.uniform(0.005, 0.02)
        open_ = p + np.random.uniform(-daily_range/2, daily_range/2)
        high_ = max(open_, p) + np.random.uniform(0, daily_range/2)
        low_ = min(open_, p) - np.random.uniform(0, daily_range/2)
        close_ = p
        vol_ = int(np.random.uniform(500000, 5000000))
        oi_ = int(np.random.uniform(1000000, 20000000))
        data.append({
            "date": d.strftime("%Y-%m-%d"),
            "open": round(open_, 2),
            "high": round(high_, 2),
            "low": round(low_, 2),
            "close": round(close_, 2),
            "volume": vol_,
            "oi": oi_,
        })

    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)
    return df

if __name__ == "__main__":
    pipeline = HistoricalDataPipeline()
    symbols = {
        "NIFTY": 24800.0,
        "BANKNIFTY": 51200.0,
        "FINNIFTY": 23400.0,
        "SENSEX": 81500.0,
        "RELIANCE": 3020.0,
    }
    total = 0
    for sym, price in symbols.items():
        df = generate_synthetic_5y_history(sym, price)
        count = pipeline.ingest_ohlcv_records(sym, df, source="HISTORICAL_ARCHIVE_5Y")
        total += count
        print(f"[Historical] Ingested {count} 5-year records for {sym}")
    print(f"Total 5-year historical records ingested: {total}")
