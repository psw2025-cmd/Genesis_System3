"""
Data Provider — Dhan Only.
All market data comes from DhanHQ API.
NSE scraping, Yahoo Finance, bhavcopy — all removed.
Saves ~150MB RAM (no requests.Session pool).
"""
from __future__ import annotations
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]


def _get_dhan_client():
    """Get DhanHQ client with current credentials."""
    from dhanhq import DhanHQ
    client_id = os.environ.get("DHAN_CLIENT_ID", "")
    access_token = os.environ.get("DHAN_ACCESS_TOKEN", "")
    if not client_id or not access_token:
        raise ValueError("DHAN_CLIENT_ID / DHAN_ACCESS_TOKEN not set")
    return DhanHQ(client_id=client_id, access_token=access_token)


async def get_option_chain(symbol: str) -> Dict[str, Any]:
    """
    Get option chain from Dhan API.
    Falls back to cached file if Dhan unavailable.
    NO NSE scraping, NO Yahoo Finance, NO requests.Session.
    """
    sym = symbol.upper().strip()

    try:
        dhan = _get_dhan_client()
        # Dhan option chain API
        resp = dhan.get_option_chain(
            UnderlyingScrip=sym,
            UnderlyingSeg="IDX_I",
            Expiry=""
        )
        if resp and isinstance(resp, dict) and resp.get("status") == "success":
            from core.data.dhan_option_chain_parser import parse_chain
            return parse_chain(resp, sym)
    except Exception as e:
        logger.warning(f"Dhan option chain failed for {sym}: {e}")

    # Fallback: read from cached file (written by worker scheduler)
    return _read_cached_chain(sym)


def _read_cached_chain(sym: str) -> Dict[str, Any]:
    """Read cached chain data written by worker scheduler."""
    cache_file = ROOT / "state" / "chain_cache" / f"{sym}.json"
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text())
            data["cached"] = True
            return data
        except Exception:
            pass
    return {
        "underlying": sym, "spot": 0, "pcr": 0,
        "strikes": [], "error": "No data available",
        "source": "none", "cached": False,
    }


def get_spot_price(symbol: str) -> Optional[float]:
    """Get spot price from Dhan — synchronous version for workers."""
    try:
        dhan = _get_dhan_client()
        # Use Dhan LTP API
        resp = dhan.get_ltp_data(
            securities={"IDX_I": [symbol]}
        )
        if resp and isinstance(resp, dict):
            data = resp.get("data", {})
            if data:
                return float(list(data.values())[0].get("last_price", 0))
    except Exception as e:
        logger.warning(f"Dhan spot price failed for {symbol}: {e}")
    return None


# ── Backward compatibility aliases ───────────────────────────────────────
def fetch_option_chain(symbol: str, expiry: str = "") -> Dict[str, Any]:
    """Sync wrapper for backward compatibility."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Can't run async in sync context — return cached
            return _read_cached_chain(symbol)
        return loop.run_until_complete(get_option_chain(symbol))
    except Exception:
        return _read_cached_chain(symbol)


MARKET_CACHE_FILE = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
    "state",
    "market_cache.json",
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


def spot_price_from_chain(chain_json: Dict[str, Any]) -> float:
    """Extracts underlying spot price from option chain JSON."""
    try:
        if "spot" in chain_json:
            return float(chain_json["spot"])
        if "underlyingValue" in chain_json:
            return float(chain_json["underlyingValue"])
        if "records" in chain_json and "underlyingValue" in chain_json["records"]:
            return float(chain_json["records"]["underlyingValue"])
        return 0.0
    except Exception:
        return 0.0

