"""
Chain router — NSE option chain data.
Lazy imports: pandas/numpy only when computing chain stats.
Caches results in memory for 10s to prevent duplicate API calls.
"""
from __future__ import annotations
import json
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter

router = APIRouter(tags=["chain"])

# ── Simple in-process cache (avoids recomputing on every poll) ─────
_chain_cache: Dict[str, tuple] = {}  # sym -> (data, timestamp)
CACHE_TTL_S = 10  # 10 second cache — enough to serve rapid UI polls

ROOT = Path(__file__).resolve().parents[2]


def _get_cached(sym: str):
    entry = _chain_cache.get(sym)
    if entry and (time.time() - entry[1]) < CACHE_TTL_S:
        return entry[0]
    return None


def _set_cache(sym: str, data: Any):
    _chain_cache[sym] = (data, time.time())


@router.get("/api/chain/{underlying}")
async def get_chain(underlying: str):
    """
    Live NSE option chain for a given underlying.
    Cached 10s — handles rapid UI polling (every 5s) without hammering NSE.
    Memory-safe: no pandas DataFrame stored in memory between requests.
    """
    sym = underlying.upper().strip()

    # Return cached if fresh
    cached = _get_cached(sym)
    if cached is not None:
        return cached

    try:
        from core.data.nse_provider import get_option_chain
        data = await get_option_chain(sym)
        result = {
            "underlying": sym,
            "spot": data.get("spot", 0),
            "pcr": data.get("pcr", 0),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "strikes": data.get("strikes", []),
            "expiries": data.get("expiries", []),
            "atm": data.get("atm", 0),
            "source": data.get("source", "nse"),
        }
        _set_cache(sym, result)
        return result
    except Exception as e:
        # Return stale cache if available rather than error
        stale = _chain_cache.get(sym)
        if stale:
            stale_data = dict(stale[0])
            stale_data["stale"] = True
            stale_data["error"] = str(e)[:80]
            return stale_data
        return {
            "underlying": sym, "spot": 0, "pcr": 0,
            "strikes": [], "error": str(e)[:100],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@router.get("/api/underlyings")
async def get_underlyings():
    """List of supported underlyings for option chain."""
    return {
        "underlyings": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"],
        "default": "NIFTY",
    }
