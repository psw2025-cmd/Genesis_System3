"""
DataSourceManager — Dhan Only.
All market data from DhanHQ API.
Previous multi-source fallback (NSE/Yahoo/bhavcopy) removed to save RAM.
"""
from __future__ import annotations
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]


class DataSourceManager:
    """
    Single-source data manager — DhanHQ only.
    No NSE scraping, no Yahoo Finance, no bhavcopy, no requests.Session.
    Estimated memory: ~5MB vs ~150MB for multi-source version.
    """

    def __init__(self):
        self._client = None
        self._last_chain: Dict[str, Any] = {}

    def _get_client(self):
        if self._client is None:
            from dhanhq import DhanHQ
            client_id = os.environ.get("DHAN_CLIENT_ID", "")
            token = os.environ.get("DHAN_ACCESS_TOKEN", "")
            if client_id and token:
                self._client = DhanHQ(client_id=client_id, access_token=token)
        return self._client

    def get_option_chain(self, symbol: str, expiry: str = "") -> Dict[str, Any]:
        """Get option chain from Dhan. Falls back to cached file."""
        sym = symbol.upper()
        try:
            dhan = self._get_client()
            if dhan is None:
                raise ValueError("Dhan credentials not set")
            resp = dhan.get_option_chain(
                UnderlyingScrip=sym,
                UnderlyingSeg="IDX_I",
                Expiry=expiry,
            )
            if resp and resp.get("status") == "success":
                from core.data.dhan_option_chain_parser import parse_chain
                result = parse_chain(resp, sym)
                self._last_chain[sym] = result
                return result
        except Exception as e:
            logger.warning(f"[DSM] Dhan chain failed for {sym}: {e}")

        # Fallback: cached file from worker
        cache = ROOT / "state" / "chain_cache" / f"{sym}.json"
        if cache.exists():
            try:
                data = json.loads(cache.read_text())
                data["source"] = "cache"
                return data
            except Exception:
                pass

        return {
            "underlying": sym, "spot": 0, "pcr": 0,
            "strikes": [], "source": "none",
            "error": "No data — Dhan unavailable and no cache",
        }

    def get_spot_price(self, symbol: str) -> float:
        """Get spot price from Dhan LTP API."""
        try:
            dhan = self._get_client()
            if dhan is None:
                return 0.0
            resp = dhan.get_ltp_data(securities={"IDX_I": [symbol]})
            if resp and isinstance(resp, dict):
                data = resp.get("data", {})
                if data:
                    return float(list(data.values())[0].get("last_price", 0))
        except Exception as e:
            logger.warning(f"[DSM] Dhan LTP failed for {symbol}: {e}")
        return 0.0

    def health_check(self) -> Dict[str, Any]:
        """Check Dhan connectivity."""
        try:
            dhan = self._get_client()
            if dhan is None:
                return {"status": "NO_CREDENTIALS", "source": "dhan"}
            # Try a quick holdings call to verify token
            resp = dhan.get_holdings()
            ok = isinstance(resp, dict) and "data" in resp
            return {
                "status": "OK" if ok else "ERROR",
                "source": "dhan",
                "mode": "Dhan-only",
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)[:100], "source": "dhan"}


# Module-level singleton
_dsm: Optional[DataSourceManager] = None

def get_datasource_manager() -> DataSourceManager:
    global _dsm
    if _dsm is None:
        _dsm = DataSourceManager()
    return _dsm
