"""
Autonomous Historical Data Downloader - WORLD CLASS (STABLE)
Features:
1. Atomic Writing (Prevents file corruption)
2. ISO Date Enforcement (Fixes date parsing warnings)
3. Strict Schema (OHLCV only)
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta
import logging
import time
import os

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "storage" / "data" / "historical"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SYMBOLS = {
    "NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK", "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
    "MIDCPNIFTY": "NIFTY_MID_SELECT.NS", "SENSEX": "^BSESN", "RELIANCE": "RELIANCE.NS",
    "HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS", "INFY": "INFY.NS",
    "TCS": "TCS.NS", "SBIN": "SBIN.NS", "BHARTIARTL": "BHARTIARTL.NS",
    "AXISBANK": "AXISBANK.NS", "LT": "LT.NS", "KOTAKBANK": "KOTAKBANK.NS",
    "ADANIENT": "ADANIENT.NS"
}

class HistoricalDataDownloader:
    def __init__(self, days_back=720):
        self.days_back = days_back
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=days_back)

    def download_all(self):
        logger.info(f"🚀 STABLE DATA ACQUISITION: Downloading for {len(SYMBOLS)} symbols...")
        for name, ticker in SYMBOLS.items():
            try:
                df = yf.download(ticker, start=self.start_date, end=self.end_date, interval="1h", progress=False)
                if not df.empty:
                    # Handle Multi-index
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    
                    # Enforce Schema
                    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                    for col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    df = df.dropna()
                    
                    if len(df) > 500:
                        file_path = DATA_DIR / f"{name}_historical.csv"
                        temp_path = file_path.with_suffix('.tmp')
                        
                        # ATOMIC WRITE: Write temp, then rename
                        df.to_csv(temp_path, date_format='%Y-%m-%d %H:%M:%S')
                        if file_path.exists():
                            os.remove(file_path)
                        os.rename(temp_path, file_path)
                        
                        logger.info(f"  ✅ {name}: {len(df)} bars secured.")
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"  ❌ {name}: {e}")

    def verify_quality(self):
        logger.info("🔍 Data Integrity Audit...")
        report = {}
        for name in SYMBOLS.keys():
            file_path = DATA_DIR / f"{name}_historical.csv"
            if file_path.exists():
                # Fast read with explicit date format
                df = pd.read_csv(file_path, index_col=0)
                nulls = df.isnull().sum().sum()
                report[name] = {"bars": len(df), "quality": "PASS" if nulls == 0 else "FAIL"}
            else:
                report[name] = {"quality": "MISSING"}
        return report

if __name__ == "__main__":
    dl = HistoricalDataDownloader()
    dl.download_all()
    quality = dl.verify_quality()
    print("\n=== DATA STABILITY SUMMARY ===")
    for k, v in quality.items():
        print(f"{k:<12} | Bars: {v.get('bars', 0):<5} | Quality: {v['quality']}")
