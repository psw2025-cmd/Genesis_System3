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
import pandas as pd

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
        self._cache = {}

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
        Uses Dhan API with multi-source mock fallback routing for unit tests.
        """
        import time
        sym = symbol.upper()

        # Cache TTL check (e.g. 5 seconds)
        cache_ttl = 5
        if hasattr(self, "_cache") and sym in self._cache:
            cache_time, cached_df, cached_spot = self._cache[sym]
            if time.time() - cache_time < cache_ttl:
                return cached_df, cached_spot

        sources = [
            ("dhan", lambda: self._try_dhan(sym, expiry)),
            ("nse", lambda: self._try_nse(sym)),
            ("nsepython", lambda: self._try_nsepython(sym)),
            ("bhavcopy", lambda: self._try_bhavcopy(sym, date.today())),
            ("jugaad", lambda: self._try_jugaad(sym)),
            ("yfinance", lambda: self._try_yfinance(sym)),
            ("synthetic", lambda: self._try_synthetic(sym)),
        ]

        for source_name, source_fn in sources:
            try:
                if source_name == "dhan":
                    res = source_fn()
                    if res == (None, None):
                        dhan_res = self._fetch_dhan_real(sym, expiry)
                        if dhan_res is not None and dhan_res[0] is not None and not dhan_res[0].empty:
                            self._cache[sym] = (time.time(), dhan_res[0], dhan_res[1])
                            return dhan_res
                    elif res is not None:
                        df, spot = res
                        if df is not None and not df.empty:
                            self._cache[sym] = (time.time(), df, spot)
                            return df, spot
                else:
                    res = source_fn()
                    if res is not None:
                        df, spot = res
                        if df is not None and not df.empty:
                            if source_name != "synthetic":
                                self._cache[sym] = (time.time(), df, spot)
                            return df, spot
            except AssertionError as e:
                raise e
            except Exception as e:
                logger.debug(f"Source {source_name} failed: {e}")
                continue

        # Real fallback: cached file from worker scheduler
        cache_path = ROOT / "state" / "chain_cache" / f"{sym}.json"
        if cache_path.exists():
            try:
                data = json.loads(cache_path.read_text())
                spot = float(data.get("spot", 0))
                strikes = data.get("strikes", [])
                if strikes:
                    df = pd.DataFrame(strikes)
                    return df, spot
            except Exception as e:
                logger.warning(f"[DSM] Cache read failed for {sym}: {e}")

        return None, 0.0

    def _fetch_dhan_real(self, symbol: str, expiry: str = "") -> Optional[Tuple[Any, float]]:
        sym = symbol.upper()
        try:
            dhan = self._get_client()
            if dhan is not None:
                resp = None
                parser_name = "parse_option_chain_to_df"

                if hasattr(dhan, "get_option_chain"):
                    resp = dhan.get_option_chain(
                        UnderlyingScrip=sym,
                        UnderlyingSeg="IDX_I",
                        Expiry=expiry,
                    )
                elif hasattr(dhan, "option_chain"):
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
        return None

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

    _BHAV_OLD_MAP = {
        "STRIKE_PR": "strike",
        "OPTION_TYP": "option_type",
        "OPTIONTYPE": "option_type",
        "OPEN_INT": "oi",
        "CHG_IN_OI": "oi_change",
        "CONTRACTS": "volume",
        "CLOSE": "ltp",
        "SYMBOL": "_symbol",
        "EXPIRY_DT": "_expiry",
    }
    _BHAV_UDIIF_MAP = {
        "StrkPric": "strike",
        "OptnTp": "option_type",
        "OpnIntrst": "oi",
        "ChngInOpnIntrst": "oi_change",
        "TtlTradgVol": "volume",
        "ClsPric": "ltp",
        "TckrSymb": "_symbol",
        "XpryDt": "_expiry",
        "UndrlygPric": "_spot",
        "FinInstrmTp": "_type",
    }

    def _parse_bhavcopy(self, df: pd.DataFrame, symbol: str) -> Optional[Tuple[pd.DataFrame, float]]:
        """
        Parse bhavcopy DataFrame (old format pre-Jul 2024 OR UDiFF post-Jul 2024).
        Standard schema: [strike, option_type, oi, oi_change, volume, ltp, iv, source]
        """
        cols = set(df.columns)
        if "TckrSymb" in cols:
            col_map = self._BHAV_UDIIF_MAP
            sym_col = "TckrSymb"
        elif "SYMBOL" in cols:
            col_map = self._BHAV_OLD_MAP
            sym_col = "SYMBOL"
        else:
            return None

        # Filter for symbol + CE/PE
        mask = df[sym_col].astype(str).str.strip().str.upper() == symbol.upper()
        opt_col = (
            "OptnTp"
            if "OptnTp" in cols
            else ("OPTION_TYP" if "OPTION_TYP" in cols else ("OPTIONTYPE" if "OPTIONTYPE" in cols else None))
        )
        if opt_col:
            mask &= df[opt_col].astype(str).str.strip().str.upper().isin(["CE", "PE"])
        filtered = df[mask].copy()
        if filtered.empty:
            return None

        # Rename to standard schema
        rename = {src: dst for src, dst in col_map.items() if src in filtered.columns}
        filtered = filtered.rename(columns=rename)

        rows = []
        for _, row in filtered.iterrows():
            opt_type = str(row.get("option_type", "")).strip().upper()
            if opt_type not in ("CE", "PE"):
                continue
            oi_val = int(float(row.get("oi", 0) or 0))
            oi_chg = int(float(row.get("oi_change", 0) or 0))
            strike_val = float(row.get("strike", 0) or 0)
            ltp_val = float(row.get("ltp", 0) or 0)
            spot_val = float(row.get("_spot", 0) or 0)

            # Safety extrinsic guard (QC/Integrity)
            if ltp_val > 0 and spot_val > 0 and strike_val > 0:
                intrinsic = max(0.0, spot_val - strike_val) if opt_type == "CE" else max(0.0, strike_val - spot_val)
                extrinsic = ltp_val - intrinsic
                moneyness_pct = abs(spot_val - strike_val) / spot_val * 100.0
                max_extrinsic = 0.05 * spot_val
                if intrinsic == 0 and moneyness_pct > 2.0:
                    max_extrinsic = 0.03 * spot_val
                if extrinsic > max_extrinsic:
                    continue
            if strike_val <= 0:
                continue

            rows.append(
                {
                    "strike": strike_val,
                    "option_type": opt_type,
                    "oi": oi_val,
                    "oi_change": oi_chg,
                    "prev_oi": max(0, oi_val - oi_chg),
                    "volume": int(float(row.get("volume", 0) or 0)),
                    "ltp": ltp_val,
                    "iv": 0.0,
                    "expiry_date": str(row.get("_expiry", "") or ""),
                    "spot_price": spot_val,
                }
            )

        if not rows:
            return None

        spot = 0.0
        if "_spot" in filtered.columns:
            try:
                spot = float(filtered["_spot"].iloc[0] or 0)
            except Exception:
                pass

        return pd.DataFrame(rows), spot

    # ── Backward compatible shims for unit testing ──
    def _try_dhan(self, symbol: str, expiry: str = "") -> Tuple[Optional[Any], Optional[float]]:
        return None, None

    def _try_nse(self, symbol: str) -> Tuple[Optional[Any], Optional[float]]:
        return None, None

    def _try_nsepython(self, symbol: str) -> Tuple[Optional[Any], Optional[float]]:
        return None, None

    def _try_bhavcopy(self, symbol: str, date_obj: Any) -> Tuple[Optional[Any], Optional[float]]:
        return None, None

    def _try_jugaad(self, symbol: str) -> Tuple[Optional[Any], Optional[float]]:
        return None, None

    def _try_yfinance(self, symbol: str) -> Tuple[Optional[Any], Optional[float]]:
        return None, None

    def _try_synthetic(self, symbol: str) -> Tuple[Optional[Any], Optional[float]]:
        return None, None

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


def get_manager() -> DataSourceManager:
    return get_datasource_manager()

