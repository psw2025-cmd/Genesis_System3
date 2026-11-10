"""
DataSourceManager — Dhan Only (backward-compatible API).
All market data from DhanHQ API.
NSE scraping, Yahoo Finance, bhavcopy removed to save RAM.
fetch_option_chain() preserved for chain_adapter.py compatibility.
"""
from __future__ import annotations
import csv
import json
import logging
import os
import threading
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]

# Dhan option-chain hard limit is ~1 request / 3s across the whole process.
# Without a process-wide gate, Market Top + WS + UI polls stampede Dhan during
# market hours and every consumer sees empty/NO_DHAN_DATA while "WS LIVE" lies.
_DHAN_OC_LOCK = threading.Lock()
_DHAN_OC_LAST_TS = 0.0
_DHAN_OC_MIN_GAP_S = float(os.environ.get("DHAN_OC_MIN_GAP_S", "3.4"))
_DHAN_OC_TERMINAL_CODES = {429, 805, 808, 906}


def _pace_dhan_option_chain_call() -> None:
    """Block until the global Dhan OC gap has elapsed (must hold _DHAN_OC_LOCK)."""
    global _DHAN_OC_LAST_TS
    wait = _DHAN_OC_MIN_GAP_S - (time.time() - _DHAN_OC_LAST_TS)
    if wait > 0:
        time.sleep(wait)
    _DHAN_OC_LAST_TS = time.time()


def _dhan_non_success_codes(resp: Any) -> set[int]:
    """Extract only known Dhan/HTTP failure codes from a non-success response.

    SDK versions have emitted codes under several nested key names (for example
    ``errorCode``, ``error_code``, ``code`` and HTTP status fields).  Keep this
    intentionally narrow so arbitrary numeric market values cannot suppress the
    existing bounded retry for unknown transient failures.
    """
    codes: set[int] = set()
    code_keys = {
        "code",
        "errorcode",
        "error_code",
        "error-code",
        "httpstatus",
        "http_status",
        "statuscode",
        "status_code",
    }

    def _walk(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                _walk(child_value, str(child_key).strip().lower())
            return
        if isinstance(value, (list, tuple)):
            for child in value:
                _walk(child, key)
            return
        if key not in code_keys:
            return
        text = str(value or "").strip().upper()
        for prefix in ("DH-", "DH_", "HTTP_", "HTTP-", "HTTP "):
            if text.startswith(prefix):
                text = text[len(prefix):]
                break
        try:
            code = int(text)
        except (TypeError, ValueError):
            return
        if code in _DHAN_OC_TERMINAL_CODES:
            codes.add(code)

    _walk(resp)
    # Some SDKs place only prose in remarks for rate limiting.  Recognize this
    # one provider-defined condition without treating arbitrary numbers as codes.
    try:
        rendered = json.dumps(resp, sort_keys=True, default=str).lower()
    except Exception:
        rendered = str(resp).lower()
    if "too many requests" in rendered or "http_429" in rendered or "http 429" in rendered:
        codes.update({429, 805})
    return codes


def _is_terminal_dhan_non_success(resp: Any) -> bool:
    """True when retrying this Dhan response would amplify auth/rate-limit failure."""
    return bool(_dhan_non_success_codes(resp))


class DataSourceManager:
    """
    Dhan-only data manager.
    Saves ~200MB vs multi-source version (no requests.Session pools).
    Backward-compatible: fetch_option_chain() returns (DataFrame, spot_price).
    """

    # Dhan optionchain APIs require INTEGER under_security_id (string IDs fail silently).
    _DHAN_SECURITY_IDS = {
        "NIFTY": 13,
        "BANKNIFTY": 25,
        "FINNIFTY": 27,
        "MIDCPNIFTY": 442,
        "SENSEX": 51,
        "BANKEX": 12,
    }

    # Dhan option-chain UnderlyingSeg for index underlyings (NSE + BSE Sensex)
    # is IDX_I. IDX_B fails silently on expiry_list/optionchain for SENSEX=51.
    # Env override still available: DHAN_OPTION_CHAIN_SEGMENT_SENSEX=<value>
    _DHAN_SEGMENTS = {
        "NIFTY": "IDX_I",
        "BANKNIFTY": "IDX_I",
        "FINNIFTY": "IDX_I",
        "MIDCPNIFTY": "IDX_I",
        "SENSEX": "IDX_I",
        "BANKEX": "BSE_FNO",
    }

    def __init__(self):
        self._client = None
        self._cache = {}
        self._equity_sec_ids: Dict[str, int] = {}

    def _get_client(self):
        from core.utils.env_loader import get_dhan_credentials
        creds = get_dhan_credentials()
        client_id = creds.get("client_id", "").strip().lstrip("\ufeff")
        token = creds.get("access_token", "").strip().lstrip("\ufeff")
        if hasattr(self, "_cached_token") and self._cached_token != token:
            self._client = None
        self._cached_token = token
        if self._client is None and client_id and token:
            try:
                from dhanhq import dhanhq
                from dhanhq.dhan_context import DhanContext
                ctx = DhanContext(client_id, token)
                self._client = dhanhq(ctx)
            except Exception as e:
                logger.warning(f"[DSM] Dhan client init failed: {e}")
        return self._client

    @staticmethod
    def _as_int_security_id(value: Any) -> Optional[int]:
        try:
            if value is None or value == "":
                return None
            return int(str(value).strip())
        except Exception:
            return None

    def _resolve_underlying(self, sym: str) -> Tuple[Optional[int], str]:
        """Return (security_id:int, exchange_segment) for index or equity FO."""
        sym_u = sym.upper()
        env_id = self._as_int_security_id(os.environ.get(f"DHAN_SECURITY_ID_{sym_u}", ""))
        env_seg = (os.environ.get(f"DHAN_OPTION_CHAIN_SEGMENT_{sym_u}", "") or "").strip()
        if env_id is not None:
            return env_id, env_seg or self._DHAN_SEGMENTS.get(sym_u, "IDX_I")

        if sym_u in self._DHAN_SECURITY_IDS:
            return (
                int(self._DHAN_SECURITY_IDS[sym_u]),
                env_seg or self._DHAN_SEGMENTS.get(sym_u, "IDX_I"),
            )

        if sym_u in self._equity_sec_ids:
            return self._equity_sec_ids[sym_u], env_seg or "NSE_EQ"

        # Institutional Indian Equity Security IDs
        INSTITUTIONAL_EQUITY_IDS = {
            "RELIANCE": 2885,
            "TCS": 11536,
            "INFY": 1594,
            "HDFCBANK": 1333,
            "ICICIBANK": 4963,
            "SBIN": 3045,
            "TATAMOTORS": 3456,
            "BHARTIARTL": 10604,
            "ITC": 1660,
            "LT": 11483,
        }
        if sym_u in INSTITUTIONAL_EQUITY_IDS:
            return INSTITUTIONAL_EQUITY_IDS[sym_u], env_seg or "NSE_EQ"

        # In-memory SQLite Master Cache lookup (zero CSV dependency)
        try:
            from core.data.dhan_master_cache import get_master_cache

            sec_id, seg, exch = get_master_cache().resolve_underlying_security(sym_u)
            if sec_id:
                return sec_id, env_seg or seg
        except Exception:
            pass

        # Resolve NSE equity underlying id from security master (OPTSTK parents).
        try:
            from core.brokers.dhan.equity_fo_universe import is_equity_fo_symbol

            if not is_equity_fo_symbol(sym_u):
                return None, ""
        except Exception:
            pass

        master = ROOT / "security_id_list.csv"
        if not master.exists():
            return None, ""
        try:
            df = pd.read_csv(master, low_memory=False)
            cols = {c.upper(): c for c in df.columns}
            exch_c = cols.get("SEM_EXM_EXCH_ID") or cols.get("EXCH_ID")
            inst_c = cols.get("SEM_INSTRUMENT_NAME") or cols.get("INSTRUMENT")
            seg_c = cols.get("SEM_SEGMENT") or cols.get("SEGMENT")
            sid_c = cols.get("SEM_SMST_SECURITY_ID") or cols.get("SECURITY_ID")
            name_c = cols.get("SM_SYMBOL_NAME") or cols.get("SYMBOL_NAME")
            tsym_c = cols.get("SEM_TRADING_SYMBOL") or cols.get("SEM_CUSTOM_SYMBOL")
            if not sid_c:
                return None, ""
            work = df
            if exch_c:
                work = work[work[exch_c].astype(str).str.upper() == "NSE"]
            # Prefer EQ cash underlying row; fall back to any OPTSTK row's underlying map via EQ.
            if inst_c and seg_c:
                eq = work[
                    (work[inst_c].astype(str).str.upper() == "EQUITY")
                    & (work[seg_c].astype(str).str.upper().isin(["E", "EQ", "CASH"]))
                ]
            else:
                eq = work
            if name_c is not None and not eq.empty:
                hit = eq[eq[name_c].astype(str).str.strip().str.upper() == sym_u]
            else:
                hit = eq.iloc[0:0]
            if hit.empty and tsym_c is not None and not eq.empty:
                hit = eq[eq[tsym_c].astype(str).str.strip().str.upper() == sym_u]
            if hit.empty:
                return None, ""
            sid = self._as_int_security_id(hit.iloc[0][sid_c])
            if sid is None:
                return None, ""
            self._equity_sec_ids[sym_u] = sid
            return sid, env_seg or "NSE_EQ"
        except Exception as exc:
            logger.warning(f"[DSM] equity security id resolve failed for {sym_u}: {exc}")
            return None, ""

    @staticmethod
    def _nearest_expiry() -> str:
        """Calendar fallback only — prefer broker expiry_list when available."""
        override = os.environ.get("DHAN_OPTION_CHAIN_EXPIRY", "").strip()
        if override:
            return override

        today = date.today()
        # NIFTY weekly is Monday; keep nearest Mon as last-resort fallback.
        days_ahead = (0 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    @staticmethod
    def _extract_expiry_list(resp: Any) -> list:
        if not isinstance(resp, dict) or resp.get("status") != "success":
            return []
        data = resp.get("data")
        # SDK nest: data.data = [dates...]; HTTP: data = [dates...]
        for _ in range(3):
            if isinstance(data, list):
                return [str(x) for x in data if x]
            if isinstance(data, dict):
                if isinstance(data.get("data"), list):
                    return [str(x) for x in data.get("data") if x]
                data = data.get("data")
                continue
            break
        return []

    @staticmethod
    def _nearest_master_expiry(sym: str) -> str:
        """Return the nearest non-expired option expiry from Dhan's master."""
        master = ROOT / "security_id_list.csv"
        if not master.exists():
            return ""
        wanted = sym.strip().upper()
        aliases = {"BSXOPT": "SENSEX", "BKXOPT": "BANKEX"}
        today = date.today().isoformat()
        found = set()
        try:
            with master.open(encoding="utf-8", errors="replace") as handle:
                for row in csv.DictReader(handle):
                    inst = str(row.get("SEM_INSTRUMENT_NAME") or row.get("INSTRUMENT") or "").upper()
                    if inst not in {"OPTIDX", "OPTSTK"}:
                        continue
                    trading = str(row.get("SEM_TRADING_SYMBOL") or "").strip().upper()
                    name = trading.split("-", 1)[0] if "-" in trading else str(
                        row.get("SM_SYMBOL_NAME") or row.get("SYMBOL_NAME") or ""
                    ).strip().upper()
                    name = aliases.get(name, name)
                    expiry_value = str(row.get("SEM_EXPIRY_DATE") or row.get("EXPIRY_DATE") or "").strip()[:10]
                    if name == wanted and len(expiry_value) == 10 and expiry_value >= today:
                        found.add(expiry_value)
        except (OSError, csv.Error):
            return ""
        return min(found) if found else ""

    def _option_chain_expiry(self, dhan: Any, sec_id: int, segment: str, sym: str, expiry: str = "") -> str:
        """Resolve expiry via env override, then Dhan expiry_list, then calendar fallback."""
        explicit = (
            (expiry or "").strip()
            or os.environ.get(f"DHAN_OPTION_CHAIN_EXPIRY_{sym.upper()}", "").strip()
            or os.environ.get("DHAN_OPTION_CHAIN_EXPIRY", "").strip()
        )
        if explicit:
            return explicit
        try:
            if hasattr(dhan, "expiry_list"):
                resp = dhan.expiry_list(
                    under_security_id=int(sec_id),
                    under_exchange_segment=segment,
                )
                dates = self._extract_expiry_list(resp)
                if dates:
                    return dates[0]
        except Exception as exc:
            logger.warning(f"[DSM] expiry_list failed for {sym}: {exc}")
        master_expiry = self._nearest_master_expiry(sym)
        if master_expiry:
            return master_expiry
        return self._nearest_expiry()

    def fetch_option_chain(self, symbol: str, expiry: str = "") -> Optional[Tuple[Any, float]]:
        """
        Fetch option chain — backward-compatible return: (DataFrame, spot_price).
        Uses Dhan API with multi-source mock fallback routing for unit tests.
        """
        import time
        sym = symbol.upper()
        cache_key = (sym, expiry or "")

        # Cache TTL check (e.g. 5 seconds)
        cache_ttl = 5
        if hasattr(self, "_cache") and cache_key in self._cache:
            cache_time, cached_df, cached_spot = self._cache[cache_key]
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
                res = source_fn()
                if res is not None and isinstance(res, tuple) and len(res) >= 2 and res[0] is not None:
                    df, spot = res[0], res[1]
                    if hasattr(df, "empty") and not df.empty:
                        if source_name != "synthetic":
                            self._cache[cache_key] = (time.time(), df, spot)
                        return df, float(spot or 0.0)
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
                strikes = data.get("strikes") or data.get("contracts") or []
                if strikes:
                    df = pd.DataFrame(strikes)
                    return df, spot
            except Exception as e:
                logger.warning(f"[DSM] Cache read failed for {sym}: {e}")

        return None, 0.0

    def _fetch_dhan_real(self, symbol: str, expiry: str = "") -> Optional[Tuple[Any, float]]:
        sym = symbol.upper()
        # Serialize ALL Dhan OC traffic (expiry_list + option_chain + retry).
        with _DHAN_OC_LOCK:
            try:
                dhan = self._get_client()
                if dhan is None:
                    return None

                resp = None
                parser_name = "parse_dhan_option_chain_payload"
                sec_id, segment = self._resolve_underlying(sym)
                if sec_id is None:
                    logger.warning(f"[DSM] No Dhan security id configured for {sym}")
                    return None

                _pace_dhan_option_chain_call()
                resolved_expiry = self._option_chain_expiry(dhan, sec_id, segment, sym, expiry)
                logger.info(
                    f"[DSM] Dhan option_chain fetch: {sym} sec_id={sec_id} seg={segment} expiry={resolved_expiry}"
                )

                _pace_dhan_option_chain_call()
                if hasattr(dhan, "option_chain"):
                    resp = dhan.option_chain(
                        under_security_id=int(sec_id),
                        under_exchange_segment=segment,
                        expiry=resolved_expiry,
                    )
                elif hasattr(dhan, "get_option_chain"):
                    resp = dhan.get_option_chain(
                        UnderlyingScrip=int(sec_id),
                        UnderlyingSeg=segment,
                        Expiry=resolved_expiry,
                    )
                    parser_name = "parse_option_chain_to_df"
                else:
                    logger.warning("[DSM] Dhan client has no option-chain method")
                    return None

                if resp and isinstance(resp, dict) and resp.get("status") == "success":
                    from core.data import dhan_option_chain_parser as parser

                    if parser_name == "parse_dhan_option_chain_payload":
                        df, spot = parser.parse_dhan_option_chain_payload(resp)
                    else:
                        df, spot = parser.parse_option_chain_to_df(resp, sym)
                    if df is not None and not df.empty:
                        # Dhan OC legs omit expiry; stamp the expiry we requested.
                        df = df.copy()
                        df["expiry_date"] = resolved_expiry
                        df["expiry"] = resolved_expiry
                        return df, spot
                else:
                    remarks = ""
                    if isinstance(resp, dict):
                        remarks = str(resp.get("remarks") or resp.get("error_message") or resp)[:180]
                    logger.warning(f"[DSM] Dhan option_chain non-success for {sym}: {remarks or resp}")
                    terminal_codes = _dhan_non_success_codes(resp)
                    if terminal_codes:
                        logger.warning(
                            f"[DSM] Dhan option_chain terminal non-success for {sym}; "
                            f"codes={sorted(terminal_codes)} immediate_retry=false"
                        )
                        return None
                    # Preserve one bounded retry only for unclassified transient failures.
                    _pace_dhan_option_chain_call()
                    if hasattr(dhan, "option_chain"):
                        resp = dhan.option_chain(
                            under_security_id=int(sec_id),
                            under_exchange_segment=segment,
                            expiry=resolved_expiry,
                        )
                    if resp and isinstance(resp, dict) and resp.get("status") == "success":
                        from core.data import dhan_option_chain_parser as parser

                        df, spot = parser.parse_dhan_option_chain_payload(resp)
                        if df is not None and not df.empty:
                            df = df.copy()
                            df["expiry_date"] = resolved_expiry
                            df["expiry"] = resolved_expiry
                            return df, spot
                    logger.warning(
                        f"[DSM] Dhan option_chain retry failed for {sym}: "
                        f"{str((resp or {}).get('remarks') if isinstance(resp, dict) else resp)[:160]}"
                    )
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

    def _try_dhan(self, symbol: str, expiry: str = "") -> Tuple[Optional[Any], Optional[float]]:
        res = self._fetch_dhan_real(symbol, expiry)
        return res if res is not None else (None, None)

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
