"""
Instruments Cache Singleton
Loads instruments JSON once and caches in memory for fast access.
Falls back to security_id_list.csv when OpenAPIScripMaster.json is absent (Render deploy).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent.parent
INSTRUMENT_JSON = ROOT_DIR / "storage" / "instruments" / "OpenAPIScripMaster.json"
SECURITY_CSV = ROOT_DIR / "security_id_list.csv"

from core.utils.logger import logger


def _map_exchange(exch: str, segment: str) -> str:
    if exch == "NSE" and segment == "D":
        return "NFO"
    if exch == "BSE" and segment == "D":
        return "BFO"
    return exch or "NSE"


def _load_from_security_csv() -> pd.DataFrame:
    """Build instruments DataFrame from Dhan security_id_list.csv."""
    if not SECURITY_CSV.exists():
        return pd.DataFrame()

    usecols = [
        "SEM_EXM_EXCH_ID",
        "SEM_SEGMENT",
        "SEM_SMST_SECURITY_ID",
        "SEM_INSTRUMENT_NAME",
        "SEM_TRADING_SYMBOL",
        "SEM_LOT_UNITS",
        "SM_SYMBOL_NAME",
        "SEM_EXPIRY_DATE",
        "SEM_STRIKE_PRICE",
        "SEM_TICK_SIZE",
    ]
    df = pd.read_csv(SECURITY_CSV, usecols=usecols, low_memory=False)
    # NSE/BSE derivatives only — keeps memory reasonable (~90k rows vs 230k+)
    df = df[df["SEM_SEGMENT"].astype(str).str.upper() == "D"]
    if df.empty:
        return pd.DataFrame()

    symbols = df["SEM_TRADING_SYMBOL"].astype(str)
    underlying = symbols.str.split("-").str[0].str.upper()
    out = pd.DataFrame(
        {
            "token": df["SEM_SMST_SECURITY_ID"].astype(str),
            "symbol": symbols,
            "name": underlying,
            "description": df["SM_SYMBOL_NAME"].astype(str),
            "expiry": df["SEM_EXPIRY_DATE"].astype(str).str[:10],
            "strike": pd.to_numeric(df["SEM_STRIKE_PRICE"], errors="coerce").fillna(0),
            "lotsize": pd.to_numeric(df["SEM_LOT_UNITS"], errors="coerce").fillna(1),
            "instrumenttype": df["SEM_INSTRUMENT_NAME"].astype(str),
            "exch_seg": [
                _map_exchange(str(e), str(s))
                for e, s in zip(df["SEM_EXM_EXCH_ID"], df["SEM_SEGMENT"])
            ],
            "tick_size": pd.to_numeric(df["SEM_TICK_SIZE"], errors="coerce").fillna(0.05),
        }
    )
    return out


def _persist_json(df: pd.DataFrame) -> None:
    """Write compact JSON cache for faster reloads within the same deploy."""
    if df.empty:
        return
    try:
        INSTRUMENT_JSON.parent.mkdir(parents=True, exist_ok=True)
        records = df.to_dict(orient="records")
        INSTRUMENT_JSON.write_text(json.dumps(records), encoding="utf-8")
        logger.info(f"[CACHE] Wrote instruments JSON: {len(records)} rows -> {INSTRUMENT_JSON}")
    except Exception as exc:
        logger.warning(f"[CACHE] Could not persist instruments JSON: {exc}")


class InstrumentsCache:
    """Singleton cache for instruments data"""

    _instance = None
    _instruments_df: Optional[pd.DataFrame] = None
    _load_time: float = 0.0
    _load_duration: float = 0.0
    _load_failed: bool = False
    _missing_logged: bool = False
    _source: str = "none"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InstrumentsCache, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._instruments_df is None and not self._load_failed:
            self._load_instruments()

    def _log_missing_once(self, message: str) -> None:
        if not self._missing_logged:
            logger.warning(message)
            self._missing_logged = True

    def _load_instruments(self) -> None:
        """Load instruments JSON or CSV fallback once into memory."""
        if self._load_failed:
            return

        start_time = time.time()
        if INSTRUMENT_JSON.exists():
            try:
                with open(INSTRUMENT_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list) and data:
                    self._instruments_df = pd.DataFrame(data)
                    self._source = "json"
                    self._load_duration = time.time() - start_time
                    self._load_time = time.time()
                    logger.info(
                        f"[CACHE] Loaded instruments from JSON: {len(self._instruments_df)} rows "
                        f"in {self._load_duration:.3f}s"
                    )
                    return
            except Exception as exc:
                self._log_missing_once(f"[CACHE] JSON load failed, trying CSV fallback: {exc}")

        self._log_missing_once(
            f"Instrument JSON not found at {INSTRUMENT_JSON}; loading from {SECURITY_CSV.name}"
        )
        try:
            df = _load_from_security_csv()
            if df.empty:
                self._instruments_df = pd.DataFrame()
                self._load_failed = True
                logger.error("[CACHE] No instruments from JSON or security_id_list.csv")
                return
            self._instruments_df = df
            self._source = "security_id_list.csv"
            self._load_duration = time.time() - start_time
            self._load_time = time.time()
            logger.info(
                f"[CACHE] Loaded instruments from CSV: {len(self._instruments_df)} rows "
                f"in {self._load_duration:.3f}s"
            )
            _persist_json(df)
        except Exception as exc:
            self._instruments_df = pd.DataFrame()
            self._load_failed = True
            logger.error(f"[CACHE] Failed to load instruments from CSV: {exc}")

    def get_instruments_df(self) -> pd.DataFrame:
        """Get cached instruments DataFrame (empty if unavailable)."""
        if self._instruments_df is None and not self._load_failed:
            self._load_instruments()
        if self._instruments_df is None:
            return pd.DataFrame()
        return self._instruments_df.copy()

    def get_tokens_for_underlying_expiry(
        self, underlying: str, expiry: str, strike_band: Optional[float] = None, spot_price: Optional[float] = None
    ) -> pd.DataFrame:
        df = self.get_instruments_df()
        if df.empty:
            return pd.DataFrame()

        filtered = df.copy()
        if "name" in df.columns:
            filtered = filtered[filtered["name"].str.upper() == underlying.upper()]
        elif "symbol" in df.columns:
            filtered = filtered[filtered["symbol"].str.contains(underlying.upper(), case=False, na=False)]

        if "expiry" in df.columns:
            expiry_str = str(expiry).replace("-", "").upper()
            filtered = filtered[filtered["expiry"].astype(str).str.replace("-", "").str.upper() == expiry_str]

        if strike_band is not None and spot_price is not None and "strike" in filtered.columns:
            if isinstance(strike_band, float) and strike_band < 1.0:
                min_strike = spot_price * (1 - strike_band)
                max_strike = spot_price * (1 + strike_band)
            else:
                strike_step = 50
                min_strike = spot_price - (strike_band * strike_step)
                max_strike = spot_price + (strike_band * strike_step)
            filtered = filtered[(filtered["strike"] >= min_strike) & (filtered["strike"] <= max_strike)]

        return filtered

    def get_load_metrics(self) -> Dict:
        return {
            "instruments_count": len(self._instruments_df) if self._instruments_df is not None else 0,
            "load_duration_sec": self._load_duration,
            "load_time": self._load_time,
            "cached": self._instruments_df is not None and not self._instruments_df.empty,
            "source": self._source,
            "json_path": str(INSTRUMENT_JSON),
            "csv_fallback": str(SECURITY_CSV),
        }


_instruments_cache = None


def get_instruments_cache() -> InstrumentsCache:
    global _instruments_cache
    if _instruments_cache is None:
        _instruments_cache = InstrumentsCache()
    return _instruments_cache


def ensure_instruments_loaded() -> Dict:
    """Warm instruments cache at app startup; safe to call multiple times."""
    cache = get_instruments_cache()
    df = cache.get_instruments_df()
    metrics = cache.get_load_metrics()
    metrics["rows"] = len(df)
    return metrics


def get_instruments_df() -> pd.DataFrame:
    return get_instruments_cache().get_instruments_df()


def get_tokens_for_underlying_expiry(
    underlying: str, expiry: str, strike_band: Optional[float] = None, spot_price: Optional[float] = None
) -> pd.DataFrame:
    return get_instruments_cache().get_tokens_for_underlying_expiry(
        underlying, expiry, strike_band, spot_price
    )
