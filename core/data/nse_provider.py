"""
Shared NSE public API provider for option chain data.
Used by both the gain ranking pipeline (morning) and market validation (evening).

v2: Now backed by DataSourceManager — tries NSE live API first, then falls
    back through nsepython → bhavcopy archive → jugaad-data → yfinance → synthetic.
    Direct NSE fetch functions preserved for backward compatibility.
"""
import json
import logging
import os
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)

_NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

_OPTION_CHAIN_URL = "https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        s = requests.Session()
        s.headers.update(_NSE_HEADERS)
        try:
            s.get("https://www.nseindia.com", timeout=8)
        except Exception as e:
            logger.warning(f"NSE homepage warm-up failed: {e}")
        _session = s
    return _session


def reset_session() -> None:
    global _session
    _session = None


def fetch_option_chain(symbol: str) -> Optional[Dict]:
    """
    Returns raw NSE option chain JSON for the given index symbol (e.g. 'NIFTY').
    Returns None on failure. Caller should handle None gracefully.
    This is the DIRECT NSE path — used internally and by legacy callers.
    For the smart multi-source path, use fetch_option_chain_smart() below.
    """
    url = _OPTION_CHAIN_URL.format(symbol=symbol)
    try:
        resp = _get_session().get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"NSE option chain fetch failed [{symbol}]: {e}")
        reset_session()
        return None


def fetch_option_chain_smart(symbol: str):
    """
    Smart multi-source fetch with auto-fallback.
    Returns (chain_df: pd.DataFrame | None, spot_price: float).
    chain_df uses standard schema: [strike, option_type, oi, volume, ltp, iv, source]
    Falls back through: NSE → nsepython → bhavcopy → jugaad → yfinance → synthetic.
    """
    from core.data.datasource_manager import fetch_option_chain_smart as _smart_fetch
    return _smart_fetch(symbol)


def total_oi_from_chain(chain_json: Dict) -> int:
    """
    Sums total open interest (calls + puts) across all strikes from NSE JSON.
    Returns 0 if data is malformed.
    """
    try:
        records = chain_json["records"]["data"]
        total = 0
        for row in records:
            total += row.get("CE", {}).get("openInterest", 0)
            total += row.get("PE", {}).get("openInterest", 0)
        return total
    except Exception:
        return 0


def spot_price_from_chain(chain_json: Dict) -> float:
    """Extracts underlying spot price from NSE option chain JSON."""
    try:
        return float(chain_json["records"]["underlyingValue"])
    except Exception:
        return 0.0


MARKET_CACHE_FILE = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
    "state", "market_cache.json",
)


MAX_OI_CACHE_AGE_DAYS = 3  # Stale after 3 calendar days (handles long weekends)


def load_oi_cache() -> Dict[str, int]:
    """
    Loads previous session OI totals from state/market_cache.json.

    Safety rules (Codex audit 2026-06-13):
    - Stale after MAX_OI_CACHE_AGE_DAYS (avoids holiday/weekend stale data)
    - Returns {} if cache date == today (guards against same-day overwrite)
    - Returns {} if file missing/corrupt
    """
    from datetime import date, datetime
    try:
        with open(MARKET_CACHE_FILE) as f:
            data = json.load(f)

        cache_date_str = data.get("cache_date")
        if cache_date_str:
            cache_date = datetime.strptime(cache_date_str, "%Y-%m-%d").date()
            today = date.today()
            age_days = (today - cache_date).days

            if age_days == 0:
                # Same day — don't use as prev_oi (morning run guard)
                logger.info("OI cache is from today — skipping as prev_oi (same-day guard)")
                return {}
            if age_days > MAX_OI_CACHE_AGE_DAYS:
                logger.warning(f"OI cache is {age_days} days old — treating as stale (holiday guard)")
                return {}

        return data.get("oi_data", {})
    except Exception:
        return {}


def load_oi_cache_raw() -> Dict:
    """Returns the full cache dict including metadata. Used by dashboard."""
    try:
        with open(MARKET_CACHE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_oi_cache(oi_data: Dict[str, int]) -> None:
    """
    Saves current OI totals to state/market_cache.json for next session's prev_oi.
    Stores cache_date so staleness can be detected on next read.
    """
    from datetime import date, datetime
    os.makedirs(os.path.dirname(MARKET_CACHE_FILE), exist_ok=True)
    payload = {
        "last_updated": datetime.now().isoformat(timespec="seconds"),
        "cache_date": date.today().isoformat(),
        "oi_data": oi_data,
    }
    with open(MARKET_CACHE_FILE, "w") as f:
        json.dump(payload, f, indent=2)
    logger.info(f"OI cache saved for {payload['cache_date']}: {list(oi_data.keys())}")


def is_expiry_day() -> bool:
    """
    Returns True if today is a Thursday (weekly NSE expiry day).
    On expiry day, OI change scores should be disabled to avoid rollover distortion.
    """
    from datetime import date
    return date.today().weekday() == 3  # Thursday = 3
