"""
Data Provider — Dhan Only.
All market data comes from DhanHQ API.
NSE scraping, Yahoo Finance, bhavcopy — all removed.
Saves ~150MB RAM (no requests.Session pool).
"""
from __future__ import annotations
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
DHAN_API_TIMEOUT_S = float(os.environ.get("DHAN_API_TIMEOUT_S", "4.0"))


def _get_dhan_client():
    """Get DhanHQ client with current credentials."""
    from dhanhq import DhanHQ
    client_id = os.environ.get("DHAN_CLIENT_ID", "")
    access_token = os.environ.get("DHAN_ACCESS_TOKEN", "")
    if not client_id or not access_token:
        raise ValueError("DHAN_CLIENT_ID / DHAN_ACCESS_TOKEN not set")
    return DhanHQ(client_id=client_id, access_token=access_token)


def _fetch_dhan_option_chain_sync(sym: str) -> Optional[Dict[str, Any]]:
    """Synchronous Dhan option-chain call. Must only run in a worker thread."""
    dhan = _get_dhan_client()
    resp = dhan.get_option_chain(
        UnderlyingScrip=sym,
        UnderlyingSeg="IDX_I",
        Expiry="",
    )
    if resp and isinstance(resp, dict) and resp.get("status") == "success":
        from core.data.dhan_option_chain_parser import parse_chain

        return parse_chain(resp, sym)
    return None


async def get_option_chain(symbol: str) -> Dict[str, Any]:
    """
    Get option chain from Dhan API with hard timeout.

    Dashboard/UI requests must never block the FastAPI event loop. DhanHQ calls
    are synchronous, so they run in a worker thread and fall back to cached data
    on timeout/error. This protects Render from request pile-ups and 502s while
    preserving real-data priority when Dhan responds quickly.
    """
    sym = symbol.upper().strip()

    try:
        parsed = await asyncio.wait_for(
            asyncio.to_thread(_fetch_dhan_option_chain_sync, sym),
            timeout=DHAN_API_TIMEOUT_S,
        )
        if parsed:
            return parsed
    except asyncio.TimeoutError:
        logger.warning("Dhan option chain timed out for %s after %.1fs", sym, DHAN_API_TIMEOUT_S)
    except Exception as e:
        logger.warning("Dhan option chain failed for %s: %s", sym, e)

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
        "underlying": sym,
        "spot": 0,
        "pcr": 0,
        "strikes": [],
        "error": "No data available",
        "source": "none",
        "cached": False,
    }


def get_spot_price(symbol: str) -> Optional[float]:
    """Get spot price from Dhan — synchronous version for workers."""
    try:
        dhan = _get_dhan_client()
        # Use Dhan LTP API
        resp = dhan.get_ltp_data(securities={"IDX_I": [symbol]})
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
    try:
        asyncio.get_running_loop()
        # Can't run async from a running loop — return cached immediately.
        return _read_cached_chain(symbol)
    except RuntimeError:
        pass

    try:
        return asyncio.run(get_option_chain(symbol))
    except Exception:
        return _read_cached_chain(symbol)
