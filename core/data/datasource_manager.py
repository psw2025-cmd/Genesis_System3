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
import time
from datetime import date, datetime, timezone
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
        # SENSEX is a BSE index. Keep the security id configurable because
        # Dhan instrument master can change. Current default follows the
        # existing repo mapping; the segment fix below is the important part.
        "SENSEX": "51",
    }

    # Official Dhan option-chain request uses UnderlyingScrip, UnderlyingSeg, Expiry.
    # Dhan annexure exposes BSE_FNO, not IDX_B. Using IDX_B produced no rows for SENSEX.
    _DHAN_SEGMENTS = {
        "NIFTY": "IDX_I",
        "BANKNIFTY": "IDX_I",
        "FINNIFTY": "IDX_I",
        "MIDCPNIFTY": "IDX_I",
        "SENSEX": "BSE_FNO",
    }

    # Fallback segments are attempted only when the primary segment returns no
    # official expiry/chain rows. No non-Dhan fallback is ever used.
    _DHAN_SEGMENT_FALLBACKS = {
        "SENSEX": ["IDX_I"],
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
    def _market_closed_now() -> bool:
        try:
            from utils.market_hours import is_market_open

            open_now, _reason = is_market_open()
            return not bool(open_now)
        except Exception:
            return False

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

    def _dhan_headers(self) -> Optional[Dict[str, str]]:
        client_id = os.environ.get("DHAN_CLIENT_ID", "").strip()
        token = os.environ.get("DHAN_ACCESS_TOKEN", "").strip()
        if not client_id or not token:
            self._last_error = "DHAN_CREDENTIALS_MISSING"
            return None
        return {
            "Content-Type": "application/json",
            "access-token": token,
            "client-id": client_id,
        }

    def _fetch_dhan_expiry_list_raw(self, sec_id: str, segment: str) -> List[str]:
        """Fetch official Dhan expiry list for an underlying."""
        headers = self._dhan_headers()
        if not headers:
            self._last_error = "DHAN_CREDENTIALS_MISSING_FOR_EXPIRY_LIST"
            return []
        try:
            import requests

            resp = requests.post(
                "https://api.dhan.co/v2/optionchain/expirylist",
                headers=headers,
                json={"UnderlyingScrip": int(sec_id), "UnderlyingSeg": segment},
                timeout=10,
            )
            try:
                payload = resp.json()
            except Exception:
                payload = {"raw": resp.text[:500]}
            if resp.status_code >= 400:
                self._last_error = f"DHAN_EXPIRY_LIST_HTTP_{resp.status_code}:{sec_id}:{segment}"
                logger.warning(f"[DSM] Dhan expiry-list HTTP {resp.status_code}: {payload}")
                return []
            if not isinstance(payload, dict) or payload.get("status") != "success":
                self._last_error = f"DHAN_EXPIRY_LIST_STATUS_{payload.get('status') if isinstance(payload, dict) else 'BAD_PAYLOAD'}:{sec_id}:{segment}"
                return []
            dates = payload.get("data") or []
            if not isinstance(dates, list):
                self._last_error = "DHAN_EXPIRY_LIST_BAD_DATA_SHAPE"
                return []
            return [str(x)[:10] for x in dates if str(x).strip()]
        except Exception as exc:
            self._last_error = f"DHAN_EXPIRY_LIST_ERROR: {exc}"
            logger.warning(f"[DSM] Dhan expiry-list fetch failed: {exc}")
            return []

    def _fetch_dhan_option_chain_raw(self, sec_id: str, segment: str, expiry: str) -> Optional[Dict[str, Any]]:
        """Fetch official Dhan v2 option-chain payload. No non-Dhan fallback."""
        headers = self._dhan_headers()
        if not headers:
            self._last_error = "DHAN_CREDENTIALS_MISSING_FOR_OPTION_CHAIN"
            return None
        try:
            import requests

            resp = requests.post(
                "https://api.dhan.co/v2/optionchain",
                headers=headers,
                json={"UnderlyingScrip": int(sec_id), "UnderlyingSeg": segment, "Expiry": expiry},
                timeout=15,
            )
            try:
                payload = resp.json()
            except Exception:
                payload = {"raw": resp.text[:500]}
            if resp.status_code >= 400:
                self._last_error = f"DHAN_OPTION_CHAIN_HTTP_{resp.status_code}:{sec_id}:{segment}:{expiry}"
                logger.warning(f"[DSM] Dhan option-chain HTTP {resp.status_code}: {payload}")
                return None
            if not isinstance(payload, dict) or payload.get("status") != "success":
                self._last_error = f"DHAN_OPTION_CHAIN_STATUS_{payload.get('status') if isinstance(payload, dict) else 'BAD_PAYLOAD'}:{sec_id}:{segment}:{expiry}"
                return None
            return payload
        except Exception as exc:
            self._last_error = f"DHAN_OPTION_CHAIN_ERROR: {exc}"
            logger.warning(f"[DSM] Dhan option-chain fetch failed: {exc}")
            return None

    def _official_expiry_list(self, sym: str, sec_id: str, segment: str) -> List[str]:
        key = f"{sym}:{sec_id}:{segment}"
        cache = self._load_expiry_cache()
        now_ts = datetime.now(timezone.utc).timestamp()
        item = cache.get(key) if isinstance(cache, dict) else None
        if isinstance(item, dict):
            age = now_ts - float(item.get("fetched_ts", 0) or 0)
            dates = item.get("dates") or []
            if age <= _EXPIRY_CACHE_TTL_S and isinstance(dates, list) and dates:
                return [str(x)[:10] for x in dates]

        dates = self._fetch_dhan_expiry_list_raw(sec_id, segment)
        if dates:
            cache[key] = {"dates": dates, "fetched_ts": now_ts}
            self._save_expiry_cache(cache)
        return dates

    def _pick_active_expiry(self, dates: List[str]) -> str:
        today = date.today()
        skip_today = self._market_closed_now()
        parsed: List[Tuple[date, str]] = []
        for raw in dates:
            try:
                d = datetime.strptime(str(raw)[:10], "%Y-%m-%d").date()
                parsed.append((d, str(raw)[:10]))
            except Exception:
                continue
        if skip_today:
            future = sorted((d, s) for d, s in parsed if d > today)
        else:
            future = sorted((d, s) for d, s in parsed if d >= today)
        if future:
            return future[0][1]
        if parsed and not skip_today:
            return sorted(parsed)[-1][1]
        return ""

    def _option_chain_expiry(self, sym: str, sec_id: str, segment: str, expiry: str = "") -> str:
        """Resolve option-chain expiry using Dhan's official expiry list only."""
        manual = (
            (expiry or "").strip()
            or os.environ.get(f"DHAN_OPTION_CHAIN_EXPIRY_{sym.upper()}", "").strip()
            or os.environ.get("DHAN_OPTION_CHAIN_EXPIRY", "").strip()
        )
        if manual:
            return manual[:10]
        dates = self._official_expiry_list(sym.upper(), sec_id, segment)
        picked = self._pick_active_expiry(dates)
        if picked:
            return picked
        self._last_error = self._last_error or "DHAN_EXPIRY_LIST_EMPTY_NO_OFFICIAL_EXPIRY"
        return ""

    def _candidate_underlying_pairs(self, sym: str, sec_id: str, segment: str) -> List[Tuple[str, str]]:
        pairs: List[Tuple[str, str]] = []
        def add(a: str, b: str) -> None:
            if a and b and (a, b) not in pairs:
                pairs.append((a, b))
        add(sec_id, segment)
        env_extra = os.environ.get(f"DHAN_OPTION_CHAIN_SEGMENT_FALLBACKS_{sym}", "").strip()
        extra_segments = [x.strip() for x in env_extra.split(",") if x.strip()] if env_extra else self._DHAN_SEGMENT_FALLBACKS.get(sym, [])
        for seg in extra_segments:
            add(sec_id, seg)
        return pairs

    def fetch_option_chain(self, symbol: str, expiry: str = "") -> Optional[Tuple[Any, float]]:
        """
        Fetch option chain from official Dhan REST only.

        Return:
          (DataFrame, spot_price) when official Dhan chain rows are available.
          (None, 0.0) when Dhan is unavailable/empty/error.
        """
        sym = symbol.upper()
        self._last_error = None

        try:
            sec_id = os.environ.get(f"DHAN_OPTION_CHAIN_SECURITY_ID_{sym}", "").strip() or self._DHAN_SECURITY_IDS.get(sym)
            segment = os.environ.get(
                f"DHAN_OPTION_CHAIN_SEGMENT_{sym}",
                self._DHAN_SEGMENTS.get(sym, "IDX_I"),
            ).strip() or "IDX_I"

            if not sec_id:
                self._last_error = f"DHAN_SECURITY_ID_MISSING:{sym}"
                logger.warning(f"[DSM] No Dhan security id configured for {sym}")
                return None, 0.0

            attempts = []
            pairs = self._candidate_underlying_pairs(sym, str(sec_id), segment)
            for idx, (candidate_sec_id, candidate_segment) in enumerate(pairs):
                if idx > 0:
                    time.sleep(float(os.environ.get("DHAN_OPTION_CHAIN_FALLBACK_SPACING_S", "3.25")))
                resolved_expiry = self._option_chain_expiry(sym, candidate_sec_id, candidate_segment, expiry)
                if not resolved_expiry:
                    attempts.append(f"{candidate_sec_id}:{candidate_segment}:NO_OFFICIAL_EXPIRY:{self.last_error}")
                    continue

                logger.info(
                    f"[DSM] Dhan REST option-chain fetch: {sym} sec_id={candidate_sec_id} segment={candidate_segment} expiry={resolved_expiry}"
                )
                resp = self._fetch_dhan_option_chain_raw(candidate_sec_id, candidate_segment, resolved_expiry)
                if not (resp and isinstance(resp, dict)):
                    attempts.append(f"{candidate_sec_id}:{candidate_segment}:{resolved_expiry}:{self.last_error or 'DHAN_EMPTY_RESPONSE'}")
                    continue

                from core.data import dhan_option_chain_parser as parser

                df, spot = parser.parse_dhan_option_chain_payload(resp)
                if df is not None and not df.empty:
                    try:
                        if "expiry" not in df.columns:
                            df["expiry"] = resolved_expiry
                        if "underlying" not in df.columns:
                            df["underlying"] = sym
                        if "dhan_underlying_segment" not in df.columns:
                            df["dhan_underlying_segment"] = candidate_segment
                        if "dhan_underlying_security_id" not in df.columns:
                            df["dhan_underlying_security_id"] = candidate_sec_id
                    except Exception:
                        pass
                    return df, spot
                attempts.append(f"{candidate_sec_id}:{candidate_segment}:{resolved_expiry}:EMPTY_ROWS")

            self._last_error = f"DHAN_EMPTY_OPTION_CHAIN_ROWS:{sym}:attempts={'|'.join(attempts[-4:])}"
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
            sec_id = os.environ.get(f"DHAN_OPTION_CHAIN_SECURITY_ID_{symbol.upper()}", "").strip() or self._DHAN_SECURITY_IDS.get(symbol.upper(), symbol)
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
