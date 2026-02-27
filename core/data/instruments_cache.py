"""
Instruments Cache Singleton
Loads instruments JSON once and caches in memory for fast access
"""

import os
import sys
import json
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
import time

ROOT_DIR = Path(__file__).parent.parent.parent
INSTRUMENT_JSON = ROOT_DIR / "storage" / "instruments" / "OpenAPIScripMaster.json"

from core.utils.logger import logger


class InstrumentsCache:
    """Singleton cache for instruments data"""

    _instance = None
    _instruments_df: Optional[pd.DataFrame] = None
    _load_time: float = 0.0
    _load_duration: float = 0.0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InstrumentsCache, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._instruments_df is None:
            self._load_instruments()

    def _load_instruments(self):
        """Load instruments JSON once into memory"""
        if not INSTRUMENT_JSON.exists():
            logger.error(f"Instrument JSON not found: {INSTRUMENT_JSON}")
            self._instruments_df = pd.DataFrame()
            return

        start_time = time.time()
        try:
            with open(INSTRUMENT_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                logger.error("Instrument JSON is not a list.")
                self._instruments_df = pd.DataFrame()
                return

            self._instruments_df = pd.DataFrame(data)
            self._load_duration = time.time() - start_time
            self._load_time = time.time()

            logger.info(f"[CACHE] Loaded instruments: {len(self._instruments_df)} rows in {self._load_duration:.3f}s")
        except Exception as e:
            logger.error(f"[CACHE] Failed to load instruments: {e}")
            self._instruments_df = pd.DataFrame()
            self._load_duration = 0.0

    def get_instruments_df(self) -> pd.DataFrame:
        """Get cached instruments DataFrame"""
        if self._instruments_df is None or self._instruments_df.empty:
            self._load_instruments()
        return self._instruments_df.copy()

    def get_tokens_for_underlying_expiry(
        self, underlying: str, expiry: str, strike_band: Optional[float] = None, spot_price: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Get pre-filtered tokens for underlying and expiry.

        Args:
            underlying: Underlying name (e.g., "NIFTY")
            expiry: Expiry date string
            strike_band: Optional strike band (e.g., ±10 strikes or ±2% of spot)
            spot_price: Optional spot price for percentage-based band

        Returns:
            Filtered DataFrame with tokens
        """
        df = self.get_instruments_df()
        if df.empty:
            return pd.DataFrame()

        # Filter by underlying and expiry
        # Assuming columns: name, expiry, strike, token, symbol, etc.
        filtered = df.copy()

        # Filter by underlying name (case-insensitive)
        if "name" in df.columns:
            filtered = filtered[filtered["name"].str.upper() == underlying.upper()]
        elif "symbol" in df.columns:
            # Try to match from symbol
            filtered = filtered[filtered["symbol"].str.contains(underlying.upper(), case=False, na=False)]

        # Filter by expiry
        if "expiry" in df.columns:
            # Normalize expiry format
            expiry_str = str(expiry).replace("-", "").upper()
            filtered = filtered[filtered["expiry"].astype(str).str.replace("-", "").str.upper() == expiry_str]

        # Filter by strike band if provided
        if strike_band is not None and spot_price is not None and "strike" in filtered.columns:
            if isinstance(strike_band, float) and strike_band < 1.0:
                # Percentage-based band (e.g., 0.02 = ±2%)
                min_strike = spot_price * (1 - strike_band)
                max_strike = spot_price * (1 + strike_band)
            else:
                # Absolute strike count (e.g., 10 = ±10 strikes)
                strike_step = 50  # Default strike step (adjust per underlying)
                min_strike = spot_price - (strike_band * strike_step)
                max_strike = spot_price + (strike_band * strike_step)

            filtered = filtered[(filtered["strike"] >= min_strike) & (filtered["strike"] <= max_strike)]

        return filtered

    def get_load_metrics(self) -> Dict:
        """Get cache load metrics"""
        return {
            "instruments_count": len(self._instruments_df) if self._instruments_df is not None else 0,
            "load_duration_sec": self._load_duration,
            "load_time": self._load_time,
            "cached": self._instruments_df is not None and not self._instruments_df.empty,
        }


# Global singleton instance
_instruments_cache = None


def get_instruments_cache() -> InstrumentsCache:
    """Get singleton instruments cache instance"""
    global _instruments_cache
    if _instruments_cache is None:
        _instruments_cache = InstrumentsCache()
    return _instruments_cache


def get_instruments_df() -> pd.DataFrame:
    """Convenience function to get instruments DataFrame"""
    return get_instruments_cache().get_instruments_df()


def get_tokens_for_underlying_expiry(
    underlying: str, expiry: str, strike_band: Optional[float] = None, spot_price: Optional[float] = None
) -> pd.DataFrame:
    """Convenience function to get filtered tokens"""
    return get_instruments_cache().get_tokens_for_underlying_expiry(underlying, expiry, strike_band, spot_price)
