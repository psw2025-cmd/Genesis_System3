"""
Instruments Cache Singleton — production-grade Dhan master resolution.

Load order:
  1. OpenAPIScripMaster.json (runtime cache from daily sync)
  2. api-scrip-master-detailed.csv (official Dhan CDN sync)
  3. security_id_list.csv (bundled emergency fallback)

Never spam ERROR logs — sync runs at 08:35 IST via scripts/sync_dhan_instruments_master.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from core.data.instruments_master import (
    BUNDLED_CSV,
    RUNTIME_JSON,
    SYNCED_DETAILED,
    dataframe_from_dhan_csv,
    resolve_master_csv,
)
from core.utils.logger import logger

ROOT_DIR = Path(__file__).parent.parent.parent
INSTRUMENT_JSON = RUNTIME_JSON


def _load_from_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    return dataframe_from_dhan_csv(df)


def _persist_json(df: pd.DataFrame) -> None:
    if df.empty:
        return
    try:
        INSTRUMENT_JSON.parent.mkdir(parents=True, exist_ok=True)
        INSTRUMENT_JSON.write_text(
            json.dumps(df.to_dict(orient="records")),
            encoding="utf-8",
        )
        logger.info(f"[CACHE] Wrote runtime instruments JSON: {len(df)} rows")
    except Exception as exc:
        logger.warning(f"[CACHE] Could not persist runtime JSON: {exc}")


class InstrumentsCache:
    _instance = None
    _instruments_df: Optional[pd.DataFrame] = None
    _load_time: float = 0.0
    _load_duration: float = 0.0
    _load_failed: bool = False
    _status_logged: bool = False
    _source: str = "none"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InstrumentsCache, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._instruments_df is None and not self._load_failed:
            self._load_instruments()

    def _log_status_once(self, level: str, message: str) -> None:
        if self._status_logged:
            return
        self._status_logged = True
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)

    def _load_instruments(self) -> None:
        if self._load_failed:
            return

        start_time = time.time()

        if INSTRUMENT_JSON.exists():
            try:
                data = json.loads(INSTRUMENT_JSON.read_text(encoding="utf-8"))
                if isinstance(data, list) and data:
                    self._instruments_df = pd.DataFrame(data)
                    self._source = "runtime_json"
                    self._load_duration = time.time() - start_time
                    self._load_time = time.time()
                    self._log_status_once(
                        "info",
                        f"[CACHE] Instruments loaded from runtime JSON: {len(self._instruments_df)} rows",
                    )
                    return
            except Exception as exc:
                self._log_status_once("warning", f"[CACHE] Runtime JSON invalid, trying CSV: {exc}")

        csv_path = resolve_master_csv()
        if csv_path is None:
            self._instruments_df = pd.DataFrame()
            self._load_failed = True
            self._log_status_once(
                "error",
                "[CACHE] No instrument master — run scripts/sync_dhan_instruments_master.py",
            )
            return

        try:
            df = _load_from_csv(csv_path)
            if df.empty:
                raise RuntimeError(f"CSV normalized to empty dataframe: {csv_path}")
            self._instruments_df = df
            if csv_path == SYNCED_DETAILED:
                self._source = "dhan_official_sync"
            elif csv_path == BUNDLED_CSV:
                self._source = "bundled_fallback"
                self._log_status_once(
                    "warning",
                    f"[CACHE] Using bundled {BUNDLED_CSV.name} — schedule daily Dhan sync",
                )
            else:
                self._source = csv_path.name
            self._load_duration = time.time() - start_time
            self._load_time = time.time()
            logger.info(
                f"[CACHE] Instruments loaded from {csv_path.name}: {len(df)} rows "
                f"in {self._load_duration:.3f}s"
            )
            _persist_json(df)
        except Exception as exc:
            self._instruments_df = pd.DataFrame()
            self._load_failed = True
            self._log_status_once("error", f"[CACHE] Instrument master load failed: {exc}")

    def get_instruments_df(self) -> pd.DataFrame:
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
        csv_path = resolve_master_csv()
        return {
            "instruments_count": len(self._instruments_df) if self._instruments_df is not None else 0,
            "load_duration_sec": self._load_duration,
            "load_time": self._load_time,
            "cached": self._instruments_df is not None and not self._instruments_df.empty,
            "source": self._source,
            "runtime_json": str(INSTRUMENT_JSON),
            "synced_csv": str(SYNCED_DETAILED) if SYNCED_DETAILED.exists() else None,
            "csv_resolved": str(csv_path) if csv_path else None,
        }


_instruments_cache = None


def get_instruments_cache() -> InstrumentsCache:
    global _instruments_cache
    if _instruments_cache is None:
        _instruments_cache = InstrumentsCache()
    return _instruments_cache


def ensure_instruments_loaded() -> Dict:
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
