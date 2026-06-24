"""
History Fetcher — Dhan Historical Candles (Data APIs ACTIVE 2026-06-23)
=======================================================================
Uses Dhan /v2/charts/historical endpoint for NSE index options OHLCV data.
Falls back to yfinance for spot price history if Dhan fails.

Supported symbols: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX
Supported intervals: 1, 5, 15, 25, 60 (minutes), D (daily)
History: up to 5 years (Dhan Data APIs plan)
"""

import logging
import os
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("history_fetcher")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Dhan security IDs for indices
_DHAN_SECURITY_IDS = {
    "NIFTY":      "13",
    "BANKNIFTY":  "25",
    "FINNIFTY":   "27",
    "MIDCPNIFTY": "442",
    "SENSEX":     "51",
}

_DHAN_EXCHANGE = "IDX_I"


def _load_dhan():
    """Load Dhan client from env."""
    try:
        import dotenv
        from dhanhq import dhanhq
        dotenv.load_dotenv(ROOT_DIR / ".secrets" / "dhan.env")
        token = os.environ.get("DHAN_ACCESS_TOKEN", "")
        client_id = os.environ.get("DHAN_CLIENT_ID", "")
        if not token or not client_id:
            return None
        return dhanhq(client_id, token)
    except Exception as e:
        logger.warning(f"Dhan init failed: {e}")
        return None


def get_history(
    symbol: str = "NIFTY",
    interval: str = "D",
    days: int = 365,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> Optional[List[dict]]:
    """
    Fetch OHLCV candles for an NSE index.

    Args:
        symbol:    NIFTY / BANKNIFTY / FINNIFTY / MIDCPNIFTY / SENSEX
        interval:  "1", "5", "15", "25", "60" (minutes) or "D" (daily)
        days:      number of calendar days of history (ignored if from_date set)
        from_date: YYYY-MM-DD override
        to_date:   YYYY-MM-DD override (defaults to today)

    Returns:
        List of dicts: {timestamp, open, high, low, close, volume}
        None on failure.
    """
    today = date.today()
    to_d = to_date or today.strftime("%Y-%m-%d")
    from_d = from_date or (today - timedelta(days=days)).strftime("%Y-%m-%d")

    sec_id = _DHAN_SECURITY_IDS.get(symbol.upper())
    if not sec_id:
        logger.warning(f"Unknown symbol {symbol} — defaulting to NIFTY")
        sec_id = "13"

    # --- Try Dhan historical candles (P0) ---
    dhan = _load_dhan()
    if dhan:
        try:
            chart_type = "D" if interval in ("D", "day", "daily") else interval
            resp = dhan.historical_daily_data(
                security_id=sec_id,
                exchange_segment=_DHAN_EXCHANGE,
                instrument_type="INDEX",
                expiry_code=0,
                from_date=from_d,
                to_date=to_d,
            ) if chart_type == "D" else dhan.intraday_minute_data(
                security_id=sec_id,
                exchange_segment=_DHAN_EXCHANGE,
                instrument_type="INDEX",
                interval=int(chart_type),
                from_date=from_d,
                to_date=to_d,
            )
            if resp and resp.get("status") == "success":
                candles = []
                data = resp.get("data", {})
                timestamps = data.get("timestamp", [])
                opens  = data.get("open", [])
                highs  = data.get("high", [])
                lows   = data.get("low", [])
                closes = data.get("close", [])
                volumes = data.get("volume", [])
                for i, ts in enumerate(timestamps):
                    candles.append({
                        "timestamp": ts,
                        "open":   float(opens[i])  if i < len(opens)   else 0.0,
                        "high":   float(highs[i])  if i < len(highs)   else 0.0,
                        "low":    float(lows[i])   if i < len(lows)    else 0.0,
                        "close":  float(closes[i]) if i < len(closes)  else 0.0,
                        "volume": float(volumes[i]) if i < len(volumes) else 0.0,
                        "source": "dhan",
                    })
                if candles:
                    logger.info(f"[Dhan] {symbol} historical: {len(candles)} candles ({from_d}→{to_d})")
                    return candles
        except Exception as e:
            logger.warning(f"[Dhan] historical fetch failed for {symbol}: {e}")

    # --- Fallback: yfinance spot price ---
    try:
        import yfinance as yf
        yf_map = {
            "NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK",
            "FINNIFTY": "NIFTY_FIN_SERVICE.NS", "SENSEX": "^BSESN",
        }
        ticker = yf_map.get(symbol.upper(), "^NSEI")
        df = yf.download(ticker, start=from_d, end=to_d, progress=False, auto_adjust=True)
        if df is not None and not df.empty:
            candles = []
            for ts, row in df.iterrows():
                candles.append({
                    "timestamp": int(ts.timestamp()),
                    "open":   float(row["Open"]),
                    "high":   float(row["High"]),
                    "low":    float(row["Low"]),
                    "close":  float(row["Close"]),
                    "volume": float(row.get("Volume", 0)),
                    "source": "yfinance",
                })
            logger.info(f"[yfinance] {symbol} fallback: {len(candles)} candles")
            return candles
    except Exception as e:
        logger.warning(f"[yfinance] fallback failed for {symbol}: {e}")

    logger.error(f"All history sources failed for {symbol}")
    return None
