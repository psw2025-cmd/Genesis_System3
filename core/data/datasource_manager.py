"""
DataSourceManager — Dhan Only (backward-compatible API).
All market data from DhanHQ API.
NSE scraping, Yahoo Finance, bhavcopy removed to save RAM.
fetch_option_chain() preserved for chain_adapter.py compatibility.
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]

# --- GLOBAL STATE FOR CACHE & THROTTLING ---
_LAST_CHAIN_FETCH = 0.0
_EXPIRY_CACHE: Dict[int, Dict[str, Any]] = {}


class DataSourceManager:
    """
    Dhan-only data manager.
    Saves ~200MB vs multi-source version (no requests.Session pools).
    Backward-compatible: fetch_option_chain() returns (DataFrame, spot_price).
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from dhanhq import dhanhq
                from dhanhq.dhan_context import DhanContext

                client_id = os.environ.get("DHAN_CLIENT_ID", "")
                token = os.environ.get("DHAN_ACCESS_TOKEN", "")
                if client_id and token:
                    ctx = DhanContext(client_id, token)
                    self._client = dhanhq(ctx)
            except Exception as e:
                logger.warning(f"[DSM] Dhan client init failed: {e}")
        return self._client

    def _throttle(self):
        """Ensures a strict 3.2-second gap between heavy Dhan API calls."""
        global _LAST_CHAIN_FETCH
        elapsed = time.time() - _LAST_CHAIN_FETCH
        if elapsed < 3.2:
            time.sleep(3.2 - elapsed)
        _LAST_CHAIN_FETCH = time.time()

    def fetch_option_chain(self, symbol: str, expiry: str = "") -> Optional[Tuple[Any, float]]:
        """
        Fetch option chain — backward-compatible return: (DataFrame, spot_price).
        Uses Dhan API. Falls back to cached JSON file written by worker.

        For indices, Dhan requires numeric UnderlyingScrip (security_id).
        """
        import pandas as pd
        global _EXPIRY_CACHE

        sym = symbol.upper()

        # Security ID map for index option chains
        index_security_map = {
            "NIFTY": 13,
            "BANKNIFTY": 25,
            "FINNIFTY": 27,
            "MIDCPNIFTY": 442,
            "SENSEX": 51,
        }

        try:
            dhan = self._get_client()
            if dhan is not None:
                security_id = index_security_map.get(sym)
                if security_id is None:
                    logger.warning(f"[DSM] No security_id mapping for {sym}; falling back to cached chain")
                    raise ValueError(f"Unknown underlying for option_chain: {sym}")

                # 1. Resolve Expiry (Fetch if blank, use 1-hour cache)
                target_expiry = expiry
                if not target_expiry:
                    now = datetime.now()
                    cache_entry = _EXPIRY_CACHE.get(security_id)

                    if cache_entry and cache_entry["expires_at"] > now and cache_entry["expiries"]:
                        target_expiry = cache_entry["expiries"][0]
                    else:
                        self._throttle()
                        try:
                            # Fetch new expiry list from Dhan
                            exp_resp = dhan.get_expiry_list(UnderlyingScrip=str(security_id), UnderlyingSeg="IDX_I")
                            if exp_resp and isinstance(exp_resp, dict) and exp_resp.get("status") == "success":
                                data = exp_resp.get("data", [])
                                if data and isinstance(data, list):
                                    target_expiry = data[0]
                                    _EXPIRY_CACHE[security_id] = {
                                        "expiries": data,
                                        "expires_at": now + timedelta(hours=1)
                                    }
                        except AttributeError:
                            logger.warning(f"[DSM] get_expiry_list not available on this dhanhq version.")
                        except Exception as e:
                            logger.warning(f"[DSM] Expiry fetch error for {sym}: {e}")

                    if not target_expiry:
                        raise ValueError(f"No valid expiry resolved for {sym}. Cannot fetch chain.")

                # 2. Throttle and Fetch Chain
                self._throttle()
                resp = dhan.get_option_chain(
                    UnderlyingScrip=str(security_id),
                    UnderlyingSeg="IDX_I",
                    Expiry=target_expiry,
                )
                
                if resp and isinstance(resp, dict) and resp.get("status") == "success":
                    from core.data.dhan_option_chain_parser import parse_option_chain_to_df
                    df, spot = parse_option_chain_to_df(resp, sym)
                    if df is not None and not df.empty:
                        return df, spot
        except Exception as e:
            logger.warning(f"[DSM] Dhan fetch_option_chain failed for {sym}: {e}")

        # Fallback: cached file from worker scheduler
        cache = ROOT / "state" / "chain_cache" / f"{sym}.json"
        if cache.exists():
            try:
                import pandas as pd

                data = json.loads(cache.read_text())
                spot = float(data.get("spot", 0))
                strikes = data.get("strikes", [])
                if strikes:
                    df = pd.DataFrame(strikes)
                    return df, spot
            except Exception as e:
                logger.warning(f"[DSM] Cache read failed for {sym}: {e}")

        return None, 0.0

    def get_option_chain(self, symbol: str, expiry: str = "") -> Dict[str, Any]:
        """New-style API — returns dict directly."""
        result = self.fetch_option_chain(symbol, expiry)
        if result is None or result[0] is None:
            return {
                "underlying": symbol,
                "spot": 0,
                "pcr": 0,
                "strikes": [],
                "error": "No data available",
            }
        df, spot = result
        return {
            "underlying": symbol,
            "spot": spot,
            "strikes": df.to_dict("records") if hasattr(df, "to_dict") else [],
            "source": "dhan",
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
            logger.warning(f"[DSM] LTP failed for {symbol}: {e}")
        return 0.0

    def health_check(self) -> Dict[str, Any]:
        """Dhan connectivity check."""
        try:
            dhan = self._get_client()
            if dhan is None:
                return {"status": "NO_CREDENTIALS", "source": "dhan"}
            resp = dhan.get_holdings()
            ok = isinstance(resp, dict) and "data" in resp
            return {"status": "OK" if ok else "ERROR", "source": "dhan"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)[:100], "source": "dhan"}


def get_datasource_manager() -> DataSourceManager:
    return DataSourceManager()