"""
Data Provider — Dhan Only.
All market data comes from DhanHQ API.
NSE scraping, Yahoo Finance, bhavcopy — all removed.
Saves ~150MB RAM (no requests.Session pool).

OI Cache helpers (load_oi_cache / save_oi_cache) are preserved so that
daily_gain_rank_and_validate.py and tests can compare prev-session OI.
"""
from __future__ import annotations
import json
import logging
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]

# ── OI cache ─────────────────────────────────────────────────────────────
MARKET_CACHE_FILE: str = str(ROOT / "state" / "market_cache.json")
_MAX_OI_CACHE_AGE_DAYS: int = 3


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


def is_expiry_day(dt: Optional[date] = None) -> bool:
    """Return True if *dt* (default today) is a weekly expiry day (Thursday)."""
    import datetime as _dt
    d = dt if dt is not None else _dt.date.today()
    return d.weekday() == 3  # 0=Mon … 3=Thu


def load_oi_cache() -> Dict[str, Any]:
    """
    Load previous-session OI from MARKET_CACHE_FILE.

    Returns {} when:
      - File missing or corrupt
      - Cache was written today (same-day guard — prev OI not meaningful yet)
      - Cache is older than _MAX_OI_CACHE_AGE_DAYS
      - cache_date field absent (backward-compat: return oi_data anyway)
    """
    path = Path(MARKET_CACHE_FILE)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}

    oi_data = data.get("oi_data", {})
    cache_date_str = data.get("cache_date")
    if not cache_date_str:
        # Backward compat: no date field — return as-is
        return oi_data

    try:
        cache_date = date.fromisoformat(cache_date_str)
    except ValueError:
        return oi_data

    today = date.today()
    age = (today - cache_date).days
    if age == 0:
        # Same-day cache: guard against morning re-run overwriting prev OI
        return {}
    if age > _MAX_OI_CACHE_AGE_DAYS:
        return {}

    return oi_data


def save_oi_cache(oi_data: Dict[str, Any]) -> None:
    """Persist current-session OI to MARKET_CACHE_FILE."""
    path = Path(MARKET_CACHE_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "cache_date": date.today().isoformat(),
                "oi_data": oi_data,
            },
            indent=2,
        )
    )


def spot_price_from_chain(chain_data: Dict[str, Any], symbol: str = "") -> float:
    """Extract spot price from a chain dict (Dhan / cached format)."""
    try:
        return float(chain_data.get("spot", 0) or chain_data.get("underlyingValue", 0) or 0)
    except Exception:
        return 0.0
