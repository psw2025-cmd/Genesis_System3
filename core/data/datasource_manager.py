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
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]


class DataSourceManager:
    """
    Dhan-only data manager.
    Saves ~200MB vs multi-source version (no requests.Session pools).
    Backward-compatible: fetch_option_chain() returns (DataFrame, spot_price).
    """

    _DHAN_SECURITY_IDS = {
        "NIFTY": "13",
        "BANKNIFTY": "25",
        "FINNIFTY": "27",
        "MIDCPNIFTY": "442",
        "SENSEX": "51",
    }

    # Dhan option-chain segment is not identical for every index.
    # Keep env override so Render can correct a broker-side segment without code deploy:
    #   DHAN_OPTION_CHAIN_SEGMENT_SENSEX=<broker accepted value>
    _DHAN_SEGMENTS = {
        "NIFTY": "IDX_I",
        "BANKNIFTY": "IDX_I",
        "FINNIFTY": "IDX_I",
        "MIDCPNIFTY": "IDX_I",
        "SENSEX": "IDX_B",
    }

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

    @staticmethod
    def _nearest_expiry() -> str:
        """Return nearest Thursday as YYYY-MM-DD for Dhan option_chain fallback."""
        override = os.environ.get("DHAN_OPTION_CHAIN_EXPIRY", "").strip()
        if override:
            return override

        today = date.today()
        days_ahead = (3 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    def _option_chain_expiry(self, sym: str, expiry: str = "") -> str:
        """Resolve option-chain expiry without requiring a code deploy."""
        return (
            (expiry or "").strip()
            or os.environ.get(f"DHAN_OPTION_CHAIN_EXPIRY_{sym.upper()}", "").strip()
            or self._nearest_expiry()
        )

    def fetch_option_chain(self, symbol: str, expiry: str = "") -> Optional[Tuple[Any, float]]:
        """
        Fetch option chain — backward-compatible return: (DataFrame, spot_price).
        Uses Dhan API. Falls back to cached JSON file written by worker.
        """
        import pandas as pd
        sym = symbol.upper()

        try:
            dhan = self._get_client()
            if dhan is not None:
                resp = None
                parser_name = "parse_option_chain_to_df"

                if hasattr(dhan, "get_option_chain"):
                    # Older/internal wrappers exposed get_option_chain(...).
                    resp = dhan.get_option_chain(
                        UnderlyingScrip=sym,
                        UnderlyingSeg="IDX_I",
                        Expiry=expiry,
                    )
                elif hasattr(dhan, "option_chain"):
                    # DhanHQ SDK 2.2 exposes option_chain(...), not get_option_chain(...).
                    sec_id = self._DHAN_SECURITY_IDS.get(sym)
                    if sec_id:
                        resolved_expiry = self._option_chain_expiry(sym, expiry)
                        logger.info(
                            f"[DSM] Dhan option_chain fetch: {sym} sec_id={sec_id} expiry={resolved_expiry}"
                        )
                        segment = os.environ.get(
                            f"DHAN_OPTION_CHAIN_SEGMENT_{sym}",
                            self._DHAN_SEGMENTS.get(sym, "IDX_I"),
                        ).strip() or "IDX_I"
                        resp = dhan.option_chain(
                            under_security_id=sec_id,
                            under_exchange_segment=segment,
                            expiry=resolved_expiry,
                        )
                        parser_name = "parse_dhan_option_chain_payload"
                    else:
                        logger.warning(f"[DSM] No Dhan security id configured for {sym}")
                else:
                    logger.warning("[DSM] Dhan client has no option-chain method")

                if resp and isinstance(resp, dict) and resp.get("status") == "success":
                    from core.data import dhan_option_chain_parser as parser

                    if parser_name == "parse_dhan_option_chain_payload":
                        df, spot = parser.parse_dhan_option_chain_payload(resp)
                    else:
                        df, spot = parser.parse_option_chain_to_df(resp, sym)
                    if df is not None and not df.empty:
                        return df, spot
        except Exception as e:
            logger.warning(f"[DSM] Dhan fetch_option_chain failed for {sym}: {e}")

        # Fallback: cached file from worker scheduler
        cache = ROOT / "state" / "chain_cache" / f"{sym}.json"
        if cache.exists():
            try:
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
                "underlying": symbol, "spot": 0, "pcr": 0,
                "strikes": [], "error": "No data available",
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
