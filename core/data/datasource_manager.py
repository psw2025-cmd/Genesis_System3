"""
DataSourceManager — Dhan Only (backward-compatible API).
All market data from DhanHQ API.

If Dhan does not return valid option-chain rows, callers receive NO_DHAN_DATA
and must display a blocked state instead of stale prices.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]
_STATE_DIR = ROOT / "state"
_EXPIRY_CACHE = _STATE_DIR / "dhan_option_expiry_cache.json"
_EXPIRY_CACHE_TTL_S = int(os.environ.get("DHAN_EXPIRY_CACHE_TTL_S", "21600"))


class DataSourceManager:
    """
    Dhan-only data manager.
    Backward-compatible: fetch_option_chain() returns (DataFrame, spot_price).
    """

    _DHAN_SECURITY_IDS = {
        "NIFTY": "13",
        "BANKNIFTY": "25",
        "FINNIFTY": "27",
        "MIDCPNIFTY": "442",
        "SENSEX": "51",
    }

    # Official Dhan option-chain request uses UnderlyingScrip, UnderlyingSeg, Expiry.
    _DHAN_SEGMENTS = {
        "NIFTY": "IDX_I",
        "BANKNIFTY": "IDX_I",
        "FINNIFTY": "IDX_I",
        "MIDCPNIFTY": "IDX_I",
        "SENSEX": "IDX_B",
    }

    def __init__(self):
        self._client = None
        self._last_error: Optional[str] = None

    @property
    def last_error(self) -> Optional[str]:
        return self._last_error

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
                else:
                    self._last_error = "DHAN_CREDENTIALS_MISSING"
            except Exception as e:
                self._last_error = f"DHAN_CLIENT_INIT_FAILED: {e}"
                logger.warning(f"[DSM] Dhan client init failed: {e}")
        return self._client

    @staticmethod
    def _nearest_expiry() -> str:
        """Last-resort fallback only; official expiry-list is preferred."""
        today = date.today()
        days_ahead = (3 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    def _load_expiry_cache(self) -> Dict[str, Any]:
        try:
            if not _EXPIRY_CACHE.exists():
                return {}
            return json.loads(_EXPIRY_CACHE.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_expiry_cache(self, cache: Dict[str, Any]) -> None:
        try:
            _STATE_DIR.mkdir(parents=True, exist_ok=True)
            tmp = _EXPIRY_CACHE.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")
            os.replace(tmp, _EXPIRY_CACHE)
        except Exception as exc:
            logger.warning(f"[DSM] Could not save Dhan expiry cache: {exc}")

    def _fetch_dhan_expiry_list_raw(self, sec_id: str, segment: str) -> List[str]:
        """Fetch official Dhan expiry list for an underlying.

        This uses the documented REST endpoint directly instead of relying on a
        particular SDK method name. It avoids the old nearest-Thursday guess.
        """
        client_id = os.environ.get("DHAN_CLIENT_ID", "").strip()
        token = os.environ.get("DHAN_ACCESS_TOKEN", "").strip()
        if not client_id or not token:
            self._last_error = "DHAN_CREDENTIALS_MISSING_FOR_EXPIRY_LIST"
            return []
        try:
            import requests

            resp = requests.post(
                "https://api.dhan.co/v2/optionchain/expirylist",
                headers={
                    "Content-Type": "application/json",
                    "access-token": token,
                    "client-id": client_id,
                },
                json={"UnderlyingScrip": int(sec_id), "UnderlyingSeg": segment},
                timeout=10,
            )
            try:
                payload = resp.json()
            except Exception:
                payload = {"raw": resp.text[:500]}
            if resp.status_code >= 400:
                self._last_error = f"DHAN_EXPIRY_LIST_HTTP_{resp.status_code}"
                logger.warning(f"[DSM] Dhan expiry-list HTTP {resp.status_code}: {payload}")
                return []
            if not isinstance(payload, dict) or payload.get("status") != "success":
                self._last_error = f"DHAN_EXPIRY_LIST_STATUS_{payload.get('status') if isinstance(payload, dict) else 'BAD_PAYLOAD'}"
                return []
            dates = payload.get("data") or []
            if not isinstance(dates, list):
                return []
            return [str(x) for x in dates if str(x).strip()]
        except Exception as exc:
            self._last_error = f"DHAN_EXPIRY_LIST_ERROR: {exc}"
            logger.warning(f"[DSM] Dhan expiry-list fetch failed: {exc}")
            return []

    def _official_expiry_list(self, sym: str, sec_id: str, segment: str) -> List[str]:
        key = f"{sym}:{sec_id}:{segment}"
        cache = self._load_expiry_cache()
        now_ts = datetime.now(timezone.utc).timestamp()
        item = cache.get(key) if isinstance(cache, dict) else None
        if isinstance(item, dict):
            age = now_ts - float(item.get("fetched_ts", 0) or 0)
            dates = item.get("dates") or []
            if age <= _EXPIRY_CACHE_TTL_S and isinstance(dates, list) and dates:
                return [str(x) for x in dates]

        dates = self._fetch_dhan_expiry_list_raw(sec_id, segment)
        if dates:
            cache[key] = {"dates": dates, "fetched_ts": now_ts}
            self._save_expiry_cache(cache)
        return dates

    @staticmethod
    def _pick_active_expiry(dates: List[str]) -> str:
        today = date.today()
        parsed: List[Tuple[date, str]] = []
        for raw in dates:
            try:
                d = datetime.strptime(str(raw)[:10], "%Y-%m-%d").date()
                parsed.append((d, str(raw)[:10]))
            except Exception:
                continue
        future = sorted((d, s) for d, s in parsed if d >= today)
        if future:
            return future[0][1]
        if parsed:
            return sorted(parsed)[-1][1]
        return ""

    def _option_chain_expiry(self, sym: str, sec_id: str, segment: str, expiry: str = "") -> str:
        """Resolve option-chain expiry using Dhan's official expiry list.

        Explicit env/request override is still honored for emergency operator
        control, but automatic operation uses /optionchain/expirylist.
        """
        manual = (
            (expiry or "").strip()
            or os.environ.get(f"DHAN_OPTION_CHAIN_EXPIRY_{sym.upper()}", "").strip()
            or os.environ.get("DHAN_OPTION_CHAIN_EXPIRY", "").strip()
        )
        if manual:
            return manual
        dates = self._official_expiry_list(sym.upper(), sec_id, segment)
        picked = self._pick_active_expiry(dates)
        if picked:
            return picked
        fallback = self._nearest_expiry()
        self._last_error = self._last_error or "DHAN_EXPIRY_LIST_EMPTY_USING_LAST_RESORT_DATE_GUESS"
        return fallback

    def fetch_option_chain(self, symbol: str, expiry: str = "") -> Optional[Tuple[Any, float]]:
        """
        Fetch option chain from Dhan only.

        Return:
          (DataFrame, spot_price) when official Dhan chain rows are available.
          (None, 0.0) when Dhan is unavailable/empty/error.
        """
        sym = symbol.upper()
        self._last_error = None

        try:
            dhan = self._get_client()
            if dhan is None:
                self._last_error = self._last_error or "DHAN_CLIENT_UNAVAILABLE"
                return None, 0.0

            resp = None
            parser_name = "parse_option_chain_to_df"
            sec_id = self._DHAN_SECURITY_IDS.get(sym)
            segment = os.environ.get(
                f"DHAN_OPTION_CHAIN_SEGMENT_{sym}",
                self._DHAN_SEGMENTS.get(sym, "IDX_I"),
            ).strip() or "IDX_I"

            if not sec_id:
                self._last_error = f"DHAN_SECURITY_ID_MISSING:{sym}"
                logger.warning(f"[DSM] No Dhan security id configured for {sym}")
                return None, 0.0

            resolved_expiry = self._option_chain_expiry(sym, sec_id, segment, expiry)

            if hasattr(dhan, "get_option_chain"):
                logger.info(f"[DSM] Dhan get_option_chain fetch: {sym} sec_id={sec_id} segment={segment} expiry={resolved_expiry}")
                resp = dhan.get_option_chain(
                    UnderlyingScrip=int(sec_id),
                    UnderlyingSeg=segment,
                    Expiry=resolved_expiry,
                )
            elif hasattr(dhan, "option_chain"):
                logger.info(f"[DSM] Dhan option_chain fetch: {sym} sec_id={sec_id} segment={segment} expiry={resolved_expiry}")
                resp = dhan.option_chain(
                    under_security_id=sec_id,
                    under_exchange_segment=segment,
                    expiry=resolved_expiry,
                )
                parser_name = "parse_dhan_option_chain_payload"
            else:
                self._last_error = "DHAN_OPTION_CHAIN_METHOD_MISSING"
                logger.warning("[DSM] Dhan client has no option-chain method")

            if not (resp and isinstance(resp, dict)):
                self._last_error = self._last_error or "DHAN_EMPTY_RESPONSE"
                return None, 0.0
            if resp.get("status") != "success":
                self._last_error = f"DHAN_STATUS_{resp.get('status') or 'UNKNOWN'}"
                return None, 0.0

            from core.data import dhan_option_chain_parser as parser

            if parser_name == "parse_dhan_option_chain_payload":
                df, spot = parser.parse_dhan_option_chain_payload(resp)
            else:
                df, spot = parser.parse_option_chain_to_df(resp, sym)
            if df is not None and not df.empty:
                return df, spot
            self._last_error = f"DHAN_EMPTY_OPTION_CHAIN_ROWS:{sym}:{resolved_expiry}"
            return None, 0.0
        except Exception as e:
            self._last_error = f"DHAN_FETCH_ERROR: {e}"
            logger.warning(f"[DSM] Dhan fetch_option_chain failed for {sym}: {e}")
            return None, 0.0

    def get_option_chain(self, symbol: str, expiry: str = "") -> Dict[str, Any]:
        """New-style API — returns dict directly. Dhan-only."""
        result = self.fetch_option_chain(symbol, expiry)
        if result is None or result[0] is None:
            return {
                "underlying": symbol.upper(),
                "spot": 0,
                "pcr": 0,
                "strikes": [],
                "status": "NO_DHAN_DATA",
                "source": "dhan",
                "error": self.last_error or "No Dhan option-chain data available",
            }
        df, spot = result
        return {
            "underlying": symbol.upper(),
            "spot": spot,
            "strikes": df.to_dict("records") if hasattr(df, "to_dict") else [],
            "source": "dhan",
            "status": "OK",
        }

    def get_spot_price(self, symbol: str) -> float:
        """Get spot price from Dhan LTP API where available."""
        try:
            dhan = self._get_client()
            if dhan is None:
                return 0.0
            sec_id = self._DHAN_SECURITY_IDS.get(symbol.upper(), symbol)
            segment = os.environ.get(
                f"DHAN_OPTION_CHAIN_SEGMENT_{symbol.upper()}",
                self._DHAN_SEGMENTS.get(symbol.upper(), "IDX_I"),
            ).strip() or "IDX_I"
            resp = dhan.get_ltp_data(securities={segment: [int(sec_id) if str(sec_id).isdigit() else sec_id]})
            if resp and isinstance(resp, dict):
                data = resp.get("data", {})
                if data:
                    first = list(data.values())[0]
                    if isinstance(first, dict):
                        return float(first.get("last_price", 0) or 0)
        except Exception as e:
            logger.warning(f"[DSM] LTP failed for {symbol}: {e}")
        return 0.0

    def health_check(self) -> Dict[str, Any]:
        """Dhan connectivity check."""
        try:
            dhan = self._get_client()
            if dhan is None:
                return {"status": "NO_CREDENTIALS", "source": "dhan", "error": self.last_error}
            resp = dhan.get_holdings()
            ok = isinstance(resp, dict) and "data" in resp
            return {"status": "OK" if ok else "ERROR", "source": "dhan"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)[:100], "source": "dhan"}


def get_datasource_manager() -> DataSourceManager:
    return DataSourceManager()
