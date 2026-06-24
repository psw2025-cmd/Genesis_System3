"""
DataSourceManager — Multi-Source Market Data with Auto-Fallback
===============================================================
Production-grade data resilience for Genesis System3.
Never lets the system fail due to a single data source going down.

Priority chain (verified by Gemini + Codex cross-audit 2026-06-13):
  P0: Dhan Data API     — GUARDED: real-time when subscribed; silently skipped on Error 806
  P1: NSE Live API      — public session (anti-bot in cloud, works in production)
  P2: nsepythonserver   — cloud-friendly wrapper with proxy rotation (same NSE backend)
  P3: NSE Bhavcopy      — EOD archive, auto-downloaded at 18:30 IST daily
                          KEY: contains CHG_IN_OI directly — no two-session comparison needed
  P4: jugaad-data       — alternative bhavcopy downloader (bhavcopy_fo_save)
  P5: yfinance          — SPOT PRICE ONLY (no Indian options OI/IV available)
  P6: Synthetic         — flat fallback, NEVER saved to OI cache

Bhavcopy advantage: `CHG_IN_OI` column gives OI change directly from yesterday.
                    No need to store prev_oi separately — bhavcopy IS the source of truth.

Optional (requires free account setup by user):
  Shoonya/Finvasia API  — real-time, free broker API, best live fallback
  Breeze Connect (ICICI) — real-time + 10 years historical options data

Auto-download: `scripts/bhavcopy_downloader.py` runs at 18:30 IST, stores
               to `storage/bhavcopy/YYYYMMDD_fo_bhavcopy.csv`

Health check: `scripts/datasource_health_check.py` runs at 08:00 IST,
              saves results to `state/datasource_health.json`

Standard output DataFrame schema:
  strike       float   — strike price
  option_type  str     — "CE" or "PE"
  oi           int     — open interest (contracts)
  volume       int     — total traded volume
  ltp          float   — last traded price
  iv           float   — implied volatility as decimal (0.18 = 18%)
  source       str     — which data source provided this row

Standard spot_price: float (underlying spot price)
"""

import io
import json
import logging
import os
import sys
import time
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests

ROOT_DIR = Path(__file__).parent.parent.parent
BHAVCOPY_DIR = ROOT_DIR / "storage" / "bhavcopy"
HEALTH_FILE = ROOT_DIR / "state" / "datasource_health.json"
HEALTH_CACHE_MINUTES = 5   # Cache successful fetches for 5 min

logger = logging.getLogger("datasource_manager")

# --------------------------------------------------------------------------- #
#  Standard column mapping from each source to the common schema               #
# --------------------------------------------------------------------------- #

STANDARD_COLS = ["strike", "option_type", "oi", "volume", "ltp", "iv", "source"]

# NSE bhavcopy column names — handles both old (pre-Jul 2024) and UDiFF (post-Jul 2024) formats
# UDiFF = Unified Data Interchange Format, NSE adopted it July 2024
# KEY: CHG_IN_OI / ChngInOpnIntrst gives OI change DIRECTLY from single day's file
_BHAV_OLD_MAP = {
    "STRIKE_PR": "strike",   "OPTION_TYP": "option_type",   "OPTIONTYPE": "option_type",
    "OPEN_INT": "oi",        "CHG_IN_OI": "oi_change",
    "CONTRACTS": "volume",   "CLOSE": "ltp",
    "SYMBOL": "_symbol",     "EXPIRY_DT": "_expiry",
}
_BHAV_UDIIF_MAP = {   # Post-July 2024 UDiFF format
    "StrkPric": "strike",          "OptnTp": "option_type",
    "OpnIntrst": "oi",             "ChngInOpnIntrst": "oi_change",
    "TtlTradgVol": "volume",       "ClsPric": "ltp",
    "TckrSymb": "_symbol",         "XpryDt": "_expiry",
    "UndrlygPric": "_spot",        "FinInstrmTp": "_type",
}

# Symbol→yfinance ticker for spot prices only
_YF_SPOT_MAP = {
    "NIFTY":      "^NSEI",
    "BANKNIFTY":  "^NSEBANK",
    "FINNIFTY":   "NIFTY_FIN_SERVICE.NS",
    "MIDCPNIFTY": "NIFTY_MIDCAP_50.NS",
    "SENSEX":     "^BSESN",
}


# --------------------------------------------------------------------------- #
#  DataSourceManager                                                            #
# --------------------------------------------------------------------------- #

class DataSourceManager:
    """
    Central manager for all market data fetching.
    Tries each source in priority order; first success wins.
    Results are cached for HEALTH_CACHE_MINUTES to avoid hammering sources.
    """

    def __init__(self):
        self._cache: Dict[str, Tuple[float, pd.DataFrame, float]] = {}
        # {symbol: (timestamp, chain_df, spot_price)}
        self._health: Dict[str, str] = {}  # source -> "OK"/"FAIL"/"SKIP"
        self._nse_session: Optional[requests.Session] = None
        self._source_stats: Dict[str, int] = {}  # source -> success count

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def fetch_option_chain(
        self, symbol: str, date_: Optional[date] = None
    ) -> Tuple[Optional[pd.DataFrame], float]:
        """
        Fetch option chain for `symbol`.
        Returns (chain_df, spot_price) using the first working source.
        chain_df has STANDARD_COLS schema; spot_price is float (0.0 if unknown).
        Returns (None, 0.0) only if ALL sources including synthetic fail.
        """
        if date_ is None:
            date_ = date.today()

        # Cache hit (live data only, not bhavcopy)
        cached = self._cache.get(symbol)
        if cached and (time.time() - cached[0]) < HEALTH_CACHE_MINUTES * 60:
            logger.debug(f"Cache hit for {symbol}")
            return cached[1], cached[2]

        # P0=Dhan (guarded), P1=NSE live, P2=nsepython(server), P3=bhavcopy, P4=jugaad, P5=yfinance(spot), P6=synthetic
        sources = [
            ("dhan",      self._try_dhan,      False),
            ("nse",       self._try_nse,       False),
            ("nsepython", self._try_nsepython, False),
            ("bhavcopy",  self._try_bhavcopy,  True),   # needs date_ arg
            ("jugaad",    self._try_jugaad,    True),   # needs date_ arg
            ("yfinance",  self._try_yfinance,  False),  # spot-only → synthetic chain
            ("synthetic", self._try_synthetic, False),
        ]

        for src_name, src_fn, needs_date in sources:
            try:
                if needs_date:
                    result = src_fn(symbol, date_)
                else:
                    result = src_fn(symbol)

                if result is None:
                    self._health[src_name] = "SKIP"
                    continue

                chain_df, spot = result
                if chain_df is None or chain_df.empty:
                    self._health[src_name] = "EMPTY"
                    continue

                chain_df = self._normalise(chain_df, src_name)
                self._health[src_name] = "OK"
                self._source_stats[src_name] = self._source_stats.get(src_name, 0) + 1

                # Only cache live (non-synthetic) data
                if src_name != "synthetic":
                    self._cache[symbol] = (time.time(), chain_df, spot)

                logger.info(f"{symbol}: data from [{src_name}] — {len(chain_df)} rows, spot={spot:.0f}")
                return chain_df, spot

            except Exception as e:
                logger.warning(f"{symbol}: [{src_name}] failed — {e}")
                self._health[src_name] = f"FAIL: {e}"

        return None, 0.0

    def fetch_spot_price(self, symbol: str) -> float:
        """
        Fetch spot price for `symbol` using available sources.
        Faster path — tries NSE first, then yfinance.
        """
        for src_fn in [self._try_nse_spot, self._try_yfinance_spot]:
            try:
                price = src_fn(symbol)
                if price and price > 0:
                    return price
            except Exception:
                pass
        return 0.0

    def health_check(self) -> Dict:
        """
        Probe all sources for NIFTY and return health status.
        Saves result to state/datasource_health.json.
        """
        status = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "sources": {}
        }
        test_symbol = "NIFTY"
        sources = [
            ("dhan",      self._try_dhan,      False),
            ("nse",       self._try_nse,       False),
            ("nsepython", self._try_nsepython, False),
            ("bhavcopy",  self._try_bhavcopy,  True),
            ("jugaad",    self._try_jugaad,    True),
            ("yfinance",  self._try_yfinance,  False),
        ]
        for src_name, src_fn, needs_date in sources:
            t0 = time.time()
            try:
                if needs_date:
                    result = src_fn(test_symbol, date.today() - timedelta(days=1))
                else:
                    result = src_fn(test_symbol)
                latency_ms = int((time.time() - t0) * 1000)
                if result and result[0] is not None and not result[0].empty:
                    status["sources"][src_name] = {"status": "OK", "latency_ms": latency_ms, "rows": len(result[0])}
                else:
                    status["sources"][src_name] = {"status": "EMPTY", "latency_ms": latency_ms}
            except Exception as e:
                latency_ms = int((time.time() - t0) * 1000)
                status["sources"][src_name] = {"status": "FAIL", "error": str(e)[:100], "latency_ms": latency_ms}

        # Determine overall resilience
        ok_count = sum(1 for s in status["sources"].values() if s["status"] == "OK")
        status["ok_sources"] = ok_count
        status["resilience"] = "HIGH" if ok_count >= 3 else "MEDIUM" if ok_count >= 2 else "LOW" if ok_count >= 1 else "CRITICAL"

        HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HEALTH_FILE, "w") as f:
            json.dump(status, f, indent=2)
        return status

    def get_last_health(self) -> Dict:
        if HEALTH_FILE.exists():
            with open(HEALTH_FILE) as f:
                return json.load(f)
        return {}

    def source_stats(self) -> Dict[str, int]:
        return dict(self._source_stats)

    # ------------------------------------------------------------------ #
    #  P0: Dhan Data API (PRIMARY — Data APIs ACTIVE 2026-06-23)            #
    # ------------------------------------------------------------------ #

    # Security IDs for Dhan option chain API
    _DHAN_SECURITY_IDS = {
        "NIFTY":      "13",
        "BANKNIFTY":  "25",
        "FINNIFTY":   "27",
        "MIDCPNIFTY": "442",
        "SENSEX":     "51",
    }

    @staticmethod
    def _nearest_expiry() -> str:
        """Return nearest Thursday (weekly NIFTY/BANKNIFTY expiry) as YYYY-MM-DD."""
        from datetime import date, timedelta
        today = date.today()
        # Thursday = weekday 3
        days_ahead = (3 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7  # already Thursday → use next week
        expiry = today + timedelta(days=days_ahead)
        return expiry.strftime("%Y-%m-%d")

    def _try_dhan(self, symbol: str) -> Optional[Tuple[pd.DataFrame, float]]:
        """Dhan option chain API — Data APIs subscription ACTIVE as of 2026-06-23."""
        try:
            import dotenv
            from dhanhq import dhanhq
            dotenv.load_dotenv(ROOT_DIR / ".secrets" / "dhan.env")
            token = os.environ.get("DHAN_ACCESS_TOKEN", "")
            client_id = os.environ.get("DHAN_CLIENT_ID", "")
            if not token or not client_id:
                return None
            dhan = dhanhq(client_id, token)
            sec_id = self._DHAN_SECURITY_IDS.get(symbol.upper(), "13")
            expiry = self._nearest_expiry()
            logger.info(f"[Dhan P0] Fetching option chain: {symbol} sec_id={sec_id} expiry={expiry}")
            resp = dhan.option_chain(under_security_id=sec_id, under_exchange_segment="IDX_I",
                                      expiry=expiry)
            if resp and resp.get("status") == "success":
                from core.data.dhan_option_chain_parser import (
                    parse_dhan_option_chain_payload,
                )
                df, spot = parse_dhan_option_chain_payload(resp)
                if not df.empty:
                    return df, spot
            return None
        except Exception:
            return None  # Silently fail — Error 806 is expected until subscribed

    # ------------------------------------------------------------------ #
    #  P2: NSE Live Public API                                             #
    # ------------------------------------------------------------------ #

    def _try_nse(self, symbol: str) -> Optional[Tuple[pd.DataFrame, float]]:
        """NSE public API — works in production, anti-bot in cloud/CI."""
        session = self._get_nse_session()
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        try:
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            records = data.get("records", {}).get("data", [])
            if not records:
                return None
            spot = float(data.get("records", {}).get("underlyingValue", 0))
            rows = []
            for entry in records:
                strike = float(entry.get("strikePrice", 0))
                for opt_type, key in [("CE", "CE"), ("PE", "PE")]:
                    leg = entry.get(key, {})
                    if not leg:
                        continue
                    rows.append({
                        "strike": strike,
                        "option_type": opt_type,
                        "oi": int(leg.get("openInterest", 0)),
                        "volume": int(leg.get("totalTradedVolume", 0)),
                        "ltp": float(leg.get("lastPrice", 0)),
                        "iv": float(leg.get("impliedVolatility", 0)) / 100.0,
                    })
            return (pd.DataFrame(rows), spot) if rows else None
        except Exception as e:
            self._nse_session = None  # Reset session on failure
            raise e

    def _try_nse_spot(self, symbol: str) -> float:
        """Quick spot price from NSE quote API."""
        session = self._get_nse_session()
        sym_map = {"NIFTY": "Nifty 50", "BANKNIFTY": "Nifty Bank",
                   "FINNIFTY": "Nifty Fin Service", "MIDCPNIFTY": "NIFTY MID SELECT"}
        idx_name = sym_map.get(symbol, symbol)
        url = f"https://www.nseindia.com/api/allIndices"
        try:
            resp = session.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("data", []):
                if item.get("index") == idx_name:
                    return float(item.get("last", 0))
        except Exception:
            pass
        return 0.0

    def _get_nse_session(self) -> requests.Session:
        if self._nse_session is None:
            s = requests.Session()
            s.headers.update({
                "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 Chrome/124.0 Safari/537.36"),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.nseindia.com/option-chain",
            })
            # Warm up session with homepage cookies
            try:
                s.get("https://www.nseindia.com", timeout=8)
            except Exception:
                pass
            self._nse_session = s
        return self._nse_session

    # ------------------------------------------------------------------ #
    #  P3: nsepython library                                               #
    # ------------------------------------------------------------------ #

    def _try_nsepython(self, symbol: str) -> Optional[Tuple[pd.DataFrame, float]]:
        """nsepython — server edition, no auth required. pip install nsepython"""
        try:
            from nsepython import nse_optionchain_scrapper  # type: ignore
        except ImportError:
            logger.debug("nsepython not installed — skipping")
            return None
        try:
            payload = nse_optionchain_scrapper(symbol)
            records = payload.get("records", {}).get("data", [])
            if not records:
                return None
            spot = float(payload.get("records", {}).get("underlyingValue", 0))
            rows = []
            for entry in records:
                strike = float(entry.get("strikePrice", 0))
                for opt_type in ("CE", "PE"):
                    leg = entry.get(opt_type, {})
                    if not leg:
                        continue
                    rows.append({
                        "strike": strike,
                        "option_type": opt_type,
                        "oi": int(leg.get("openInterest", 0)),
                        "volume": int(leg.get("totalTradedVolume", 0)),
                        "ltp": float(leg.get("lastPrice", 0)),
                        "iv": float(leg.get("impliedVolatility", 0)) / 100.0,
                    })
            return (pd.DataFrame(rows), spot) if rows else None
        except Exception as e:
            raise e

    # ------------------------------------------------------------------ #
    #  P4: NSE Bhavcopy Archive (EOD, auto-downloaded)                    #
    # ------------------------------------------------------------------ #

    def _try_bhavcopy(
        self, symbol: str, date_: Optional[date] = None
    ) -> Optional[Tuple[pd.DataFrame, float]]:
        """
        Read from locally cached bhavcopy CSV.
        Falls back to previous trading days (up to 5 days back) if today not yet available.
        """
        BHAVCOPY_DIR.mkdir(parents=True, exist_ok=True)
        search_date = date_ or date.today()

        for delta in range(6):  # today, yesterday, ..., 5 days back
            check_date = search_date - timedelta(days=delta)
            if check_date.weekday() >= 5:  # skip weekends
                continue
            date_str = check_date.strftime("%Y%m%d")
            csv_path = BHAVCOPY_DIR / f"{date_str}_fo_bhavcopy.csv"
            if csv_path.exists():
                try:
                    df = pd.read_csv(csv_path, low_memory=False)
                    result = self._parse_bhavcopy(df, symbol)
                    if result:
                        chain_df, spot = result
                        logger.info(f"  {symbol}: bhavcopy from {date_str} ({len(chain_df)} rows)")
                        return chain_df, spot
                except Exception as e:
                    logger.warning(f"Bhavcopy {date_str} parse error: {e}")

        # Not cached locally — try to download last trading day
        try:
            return self._download_and_parse_bhavcopy(symbol, search_date)
        except Exception as e:
            logger.warning(f"Bhavcopy download failed: {e}")
            return None

    def _download_and_parse_bhavcopy(
        self, symbol: str, ref_date: date
    ) -> Optional[Tuple[pd.DataFrame, float]]:
        """Download NSE FO bhavcopy from archives and parse it."""
        # Try last 5 trading days
        for delta in range(1, 6):
            check_date = ref_date - timedelta(days=delta)
            if check_date.weekday() >= 5:
                continue

            date_str = check_date.strftime("%Y%m%d")
            # New format (2022+)
            url_new = (f"https://nsearchives.nseindia.com/content/fo/"
                       f"BhavCopy_NSE_FO_0_0_0_{date_str}_F_0000.csv.zip")
            # Old format (pre-2022 fallback)
            old_dd = check_date.strftime("%d")
            old_mon = check_date.strftime("%b").upper()
            old_yyyy = check_date.strftime("%Y")
            url_old = (f"https://nsearchives.nseindia.com/content/historical/DERIVATIVES/"
                       f"{old_yyyy}/{old_mon}/fo{old_dd}{old_mon}{old_yyyy}bhav.csv.zip")

            for url in [url_new, url_old]:
                try:
                    session = self._get_nse_session()
                    resp = session.get(url, timeout=20)
                    if resp.status_code != 200:
                        continue
                    # Extract CSV from zip
                    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                        csv_name = next((n for n in zf.namelist() if n.endswith(".csv")), None)
                        if not csv_name:
                            continue
                        raw = zf.read(csv_name)

                    df = pd.read_csv(io.StringIO(raw.decode("utf-8", errors="replace")), low_memory=False)

                    # Cache it locally
                    BHAVCOPY_DIR.mkdir(parents=True, exist_ok=True)
                    local_path = BHAVCOPY_DIR / f"{date_str}_fo_bhavcopy.csv"
                    df.to_csv(local_path, index=False)
                    logger.info(f"Bhavcopy {date_str} downloaded and cached ({len(df)} rows)")

                    result = self._parse_bhavcopy(df, symbol)
                    if result:
                        return result
                except Exception:
                    continue
        return None

    def _parse_bhavcopy(
        self, df: pd.DataFrame, symbol: str
    ) -> Optional[Tuple[pd.DataFrame, float]]:
        """
        Parse bhavcopy DataFrame (old format pre-Jul 2024 OR UDiFF post-Jul 2024).

        KEY FEATURE: Bhavcopy contains CHG_IN_OI / ChngInOpnIntrst — the OI change
        from yesterday is directly available. We pass it as oi_change column so the
        caller can build oi_history without needing two separate sessions.

        Output: standard DataFrame with columns [strike, option_type, oi, oi_change, volume, ltp, iv, source]
        """
        cols = set(df.columns)

        # Detect format: UDiFF (post-Jul 2024) uses TckrSymb; old uses SYMBOL
        if "TckrSymb" in cols:
            col_map = _BHAV_UDIIF_MAP
            sym_col = "TckrSymb"
            type_col = "FinInstrmTp"
            type_val = "OPTIDX"
        elif "SYMBOL" in cols:
            col_map = _BHAV_OLD_MAP
            sym_col = "SYMBOL"
            type_col = "INSTRUMENT"
            type_val = "OPTIDX"
        else:
            logger.warning(f"Unknown bhavcopy format — columns: {list(cols)[:10]}")
            return None

        # Filter: options for this symbol.
        # Do NOT filter by FinInstrmTp/INSTRUMENT — UDiFF uses "IDO" for index options
        # (not "OPTIDX"). Instead, filter by symbol + has a valid OptnTp (CE/PE).
        mask = (df[sym_col].astype(str).str.strip().str.upper() == symbol.upper())
        opt_col = "OptnTp" if "OptnTp" in cols else ("OPTION_TYP" if "OPTION_TYP" in cols
                  else ("OPTIONTYPE" if "OPTIONTYPE" in cols else None))
        if opt_col:
            mask &= df[opt_col].astype(str).str.strip().str.upper().isin(["CE", "PE"])
        filtered = df[mask].copy()
        if filtered.empty:
            return None

        # Rename columns to standard schema
        rename = {src: dst for src, dst in col_map.items() if src in filtered.columns}
        filtered = filtered.rename(columns=rename)

        # Build standard rows — include oi_change directly from bhavcopy
        rows = []
        phantom_drops = 0
        phantom_samples: list[str] = []
        for _, row in filtered.iterrows():
            opt_type = str(row.get("option_type", "")).strip().upper()
            if opt_type not in ("CE", "PE"):
                continue
            oi_val = int(float(row.get("oi", 0) or 0))
            oi_chg = int(float(row.get("oi_change", 0) or 0))
            strike_val = float(row.get("strike", 0) or 0)
            ltp_val = float(row.get("ltp", 0) or 0)
            spot_val = float(row.get("_spot", 0) or 0)

            # ── B1 DATA-INTEGRITY GUARD (source-level, extrinsic-calibrated) ──
            # Reject phantom-priced rows BEFORE they enter the pipeline.
            # A bad bhavcopy row gave a BANKNIFTY 60000 CE an LTP of 4440 when
            # fair value was ~280 → single -1.25L backtest loss.
            # Logic: an option's EXTRINSIC value (ltp - intrinsic) cannot exceed
            # ~5% of spot for index options (ATM straddle is ~3-4% of spot).
            # For far-OTM (>2% away, zero intrinsic), tighten to 3% of spot.
            if ltp_val > 0 and spot_val > 0 and strike_val > 0:
                intrinsic = max(0.0, spot_val - strike_val) if opt_type == "CE" else max(0.0, strike_val - spot_val)
                extrinsic = ltp_val - intrinsic
                moneyness_pct = abs(spot_val - strike_val) / spot_val * 100.0
                max_extrinsic = 0.05 * spot_val
                if intrinsic == 0 and moneyness_pct > 2.0:
                    max_extrinsic = 0.03 * spot_val
                if extrinsic > max_extrinsic:
                    phantom_drops += 1
                    if len(phantom_samples) < 2:
                        phantom_samples.append(
                            f"{strike_val:.0f}{opt_type} ltp={ltp_val:.0f} extrinsic={extrinsic:.0f}"
                        )
                    continue
            if strike_val <= 0:
                continue

            rows.append({
                "strike": strike_val,
                "option_type": opt_type,
                "oi": oi_val,
                "oi_change": oi_chg,            # direct from bhavcopy!
                "prev_oi": max(0, oi_val - oi_chg),  # reconstructed
                "volume": int(float(row.get("volume", 0) or 0)),
                "ltp": ltp_val,
                "iv": 0.0,  # IV not in bhavcopy; ATM straddle proxy computed in gain_rank_engine
                "expiry_date": str(row.get("_expiry", "") or ""),
                "spot_price": spot_val,
            })

        if phantom_drops:
            sample = "; ".join(phantom_samples) if phantom_samples else ""
            logger.info(
                f"[bhavcopy] {symbol}: dropped {phantom_drops} phantom-priced rows (QC guard)"
                + (f" — e.g. {sample}" if sample else "")
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

    # ------------------------------------------------------------------ #
    #  P5: jugaad-data (historical F&O)                                   #
    # ------------------------------------------------------------------ #

    def _try_jugaad(
        self, symbol: str, date_: Optional[date] = None
    ) -> Optional[Tuple[pd.DataFrame, float]]:
        """jugaad-data — historical NSE F&O data. pip install jugaad-data"""
        try:
            from jugaad_data.nse.fno import FNO  # type: ignore
        except ImportError:
            logger.debug("jugaad-data not installed — skipping")
            return None
        try:
            fno = FNO()
            ref_date = date_ or date.today()
            # Use yesterday (jugaad doesn't have intraday live data)
            fetch_date = ref_date - timedelta(days=1)
            # Find nearest weekday
            while fetch_date.weekday() >= 5:
                fetch_date -= timedelta(days=1)

            # Get index option chain for the nearest expiry
            df_raw = fno.option_chain(symbol=symbol, date=fetch_date)
            if df_raw is None or df_raw.empty:
                return None

            # jugaad columns: SYMBOL, EXPIRY_DT, STRIKE_PR, OPTION_TYP, OPEN_INT, CONTRACTS, CLOSE
            rows = []
            for _, row in df_raw.iterrows():
                opt_type = str(row.get("OPTION_TYP", "")).strip().upper()
                if opt_type not in ("CE", "PE"):
                    continue
                rows.append({
                    "strike": float(row.get("STRIKE_PR", 0) or 0),
                    "option_type": opt_type,
                    "oi": int(float(row.get("OPEN_INT", 0) or 0)),
                    "volume": int(float(row.get("CONTRACTS", 0) or 0)),
                    "ltp": float(row.get("CLOSE", 0) or 0),
                    "iv": 0.0,
                })
            return (pd.DataFrame(rows), 0.0) if rows else None
        except Exception as e:
            raise e

    # ------------------------------------------------------------------ #
    #  P6: yfinance (spot prices only)                                    #
    # ------------------------------------------------------------------ #

    def _try_yfinance(self, symbol: str) -> Optional[Tuple[pd.DataFrame, float]]:
        """
        yfinance — spot price only (no options data for Indian markets).
        Returns synthetic chain (flat) with real spot price.
        """
        spot = self._try_yfinance_spot(symbol)
        if spot <= 0:
            return None
        return self._make_synthetic_chain(symbol, spot, source_tag="yfinance+synthetic"), spot

    def _try_yfinance_spot(self, symbol: str) -> float:
        try:
            import yfinance as yf  # type: ignore
        except ImportError:
            return 0.0
        ticker_sym = _YF_SPOT_MAP.get(symbol.upper())
        if not ticker_sym:
            return 0.0
        try:
            ticker = yf.Ticker(ticker_sym)
            info = ticker.fast_info
            price = float(getattr(info, "last_price", None) or getattr(info, "regularMarketPrice", None) or 0)
            return price
        except Exception:
            return 0.0

    # ------------------------------------------------------------------ #
    #  P7: Synthetic fallback                                              #
    # ------------------------------------------------------------------ #

    def _try_synthetic(self, symbol: str) -> Optional[Tuple[pd.DataFrame, float]]:
        """
        Last-resort flat synthetic data.
        OI is uniform (no change signal). Never saved to OI cache.
        """
        spot_defaults = {"NIFTY": 23000.0, "BANKNIFTY": 52000.0,
                         "FINNIFTY": 23500.0, "MIDCPNIFTY": 12000.0,
                         "SENSEX": 76000.0}
        spot = spot_defaults.get(symbol.upper(), 20000.0)
        chain = self._make_synthetic_chain(symbol, spot, source_tag="synthetic")
        logger.warning(f"{symbol}: SYNTHETIC FALLBACK — OI data will not be saved to cache")
        return chain, spot

    def _make_synthetic_chain(
        self, symbol: str, spot: float, source_tag: str = "synthetic"
    ) -> pd.DataFrame:
        """Create a flat synthetic option chain (zero OI change signal)."""
        step = 50 if "NIFTY" in symbol.upper() else 100
        atm = round(spot / step) * step
        strikes = [atm + i * step for i in range(-10, 11)]
        rows = []
        for s in strikes:
            for opt_type in ("CE", "PE"):
                rows.append({
                    "strike": float(s),
                    "option_type": opt_type,
                    "oi": 100000,  # flat — signals zero OI change
                    "volume": 10000,
                    "ltp": max(1.0, abs(spot - s) * 0.3),
                    "iv": 0.18,
                    "source": source_tag,
                })
        return pd.DataFrame(rows)

    # ------------------------------------------------------------------ #
    #  Utility                                                             #
    # ------------------------------------------------------------------ #

    def _normalise(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        """Ensure standard columns exist and are correctly typed."""
        if "source" not in df.columns:
            df = df.copy()
            df["source"] = source
        for col, dtype, default in [
            ("strike", float, 0.0), ("oi", int, 0),
            ("volume", int, 0),     ("ltp", float, 0.0),
            ("iv", float, 0.0),
        ]:
            if col not in df.columns:
                df[col] = default
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default).astype(dtype)
        if "option_type" not in df.columns:
            df["option_type"] = "CE"
        df["option_type"] = df["option_type"].astype(str).str.upper().str.strip()
        df = df[df["option_type"].isin(["CE", "PE"])]
        return df.reset_index(drop=True)

    def is_synthetic(self, chain_df: pd.DataFrame) -> bool:
        """Returns True if the chain data came from synthetic fallback."""
        if chain_df is None or chain_df.empty:
            return True
        if "source" in chain_df.columns:
            sources = chain_df["source"].unique()
            return all("synthetic" in str(s) for s in sources)
        return False


# --------------------------------------------------------------------------- #
#  Module-level singleton (used by nse_provider.py + daily runner)             #
# --------------------------------------------------------------------------- #

_manager: Optional[DataSourceManager] = None


def get_manager() -> DataSourceManager:
    global _manager
    if _manager is None:
        _manager = DataSourceManager()
    return _manager


def fetch_option_chain_smart(
    symbol: str, date_: Optional[date] = None
) -> Tuple[Optional[pd.DataFrame], float]:
    """
    Smart fetch with auto-fallback.
    Returns (chain_df, spot_price). chain_df may come from any source in the
    priority chain. spot_price is 0.0 if all sources failed.
    """
    return get_manager().fetch_option_chain(symbol, date_)


def run_health_check() -> Dict:
    """Run full health check on all data sources. Used by datasource_health_check.py."""
    return get_manager().health_check()

