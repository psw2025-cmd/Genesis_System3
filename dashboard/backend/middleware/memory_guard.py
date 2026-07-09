"""
Memory-aware middleware for Genesis System3.
Tracks RAM usage per request and auto-runs GC when above threshold.
Also enforces Dhan-only truth for option-chain dashboard responses.
"""
from __future__ import annotations

import gc
import json
import os
import time
from typing import Callable

from starlette.responses import JSONResponse, Response

try:
    import resource

    def _rss_mb() -> float:
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
except ImportError:

    def _rss_mb() -> float:
        try:
            with open("/proc/self/status") as f:
                for line in f:
                    if "VmRSS" in line:
                        return int(line.split()[1]) / 1024
        except Exception:
            return 0.0
        return 0.0


MEM_WARN_MB = int(os.environ.get("MEM_WARN_MB", "380"))
MEM_GC_MB = int(os.environ.get("MEM_GC_MB", "420"))
MEM_LIMIT_MB = int(os.environ.get("MEM_LIMIT_MB", "480"))

_FAST_PATHS = {"/", "/api/health", "/api/state", "/static"}

_last_gc_time = 0.0
GC_COOLDOWN_S = 30.0

_CHAIN_ALLOWED_DATA_SOURCES = {"dhan", "dhan_option_chain_live"}
_CHAIN_ALLOWED_SOURCE_PREFIXES = ("dhan", "worker_push")
_BAD_CHAIN_MARKERS = ("csv", "fallback", "synthetic", "bhavcopy", "nse", "yahoo", "fake", "mock")


def _chain_has_contracts_and_spot(payload: dict) -> bool:
    contracts = payload.get("contracts") or []
    if not isinstance(contracts, list) or not contracts:
        return False
    try:
        if float(payload.get("spot") or 0) <= 0:
            return False
    except Exception:
        return False
    try:
        if int(payload.get("total_contracts") or len(contracts)) <= 0:
            return False
    except Exception:
        return False
    return True


def _chain_source_is_dhan(payload: dict) -> bool:
    data_source = str(payload.get("data_source") or payload.get("source") or "").lower()
    source_priority = str(payload.get("source_priority") or "").lower()
    source_text = f"{data_source} {source_priority}"
    if any(bad in source_text for bad in _BAD_CHAIN_MARKERS):
        return False
    if data_source not in _CHAIN_ALLOWED_DATA_SOURCES:
        return False
    if source_priority and source_priority != "--" and not source_priority.startswith(_CHAIN_ALLOWED_SOURCE_PREFIXES):
        return False
    return True


def _chain_response_is_dhan_only(payload: dict) -> bool:
    """True only when the response contains Dhan-derived option-chain rows.

    During market hours, rows must be current and not stale. When the market is
    closed, a verified Dhan last-session snapshot is allowed only when clearly
    labelled as a snapshot and not as live.
    """
    if not _chain_has_contracts_and_spot(payload):
        return False
    if not _chain_source_is_dhan(payload):
        return False

    status = str(payload.get("status") or "").upper()
    if "FALLBACK" in status or "SYNTHETIC" in status or "CSV" in status:
        return False

    market_closed_snapshot = status in {"MARKET_CLOSED", "EOD_SNAPSHOT", "VERIFIED_DHAN_SNAPSHOT", "MARKET_CLOSED_DHAN_SNAPSHOT"}
    if bool(payload.get("stale")) and not market_closed_snapshot:
        return False
    if "STALE" in status and not market_closed_snapshot:
        return False

    return True


def _normalize_verified_chain_payload(payload: dict) -> dict:
    data = dict(payload)
    status = str(data.get("status") or "").upper()
    market_closed_snapshot = status in {"MARKET_CLOSED", "EOD_SNAPSHOT", "VERIFIED_DHAN_SNAPSHOT", "MARKET_CLOSED_DHAN_SNAPSHOT"}
    if market_closed_snapshot:
        data["data_source"] = "dhan"
        data["source_priority"] = "dhan_last_verified_snapshot"
        data["status"] = "MARKET_CLOSED_DHAN_SNAPSHOT"
        data["stale"] = False
        data["live"] = False
        data["snapshot"] = True
        data["message"] = "Market closed — showing last verified Dhan option-chain snapshot, not live ticks."
    return data


def _blocked_chain_payload(original: dict) -> dict:
    """Return explicit blocked state instead of unusable market data."""
    return {
        "underlying": str(original.get("underlying") or "").upper(),
        "contracts": [],
        "spot": 0,
        "pcr": 0,
        "total_contracts": 0,
        "data_source": "dhan",
        "source_priority": "dhan_only_no_rows",
        "status": "NO_DHAN_DATA",
        "stale": False,
        "blocked": True,
        "blocked_reason": "NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS",
        "suppressed_source": original.get("data_source"),
        "suppressed_source_priority": original.get("source_priority"),
        "suppressed_status": original.get("status"),
        "message": "No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.",
    }


async def _enforce_dhan_only_chain_response(request, response):
    """Rewrite non-Dhan /api/chain responses to explicit NO_DHAN_DATA."""
    if request.method.upper() != "GET" or not request.url.path.startswith("/api/chain/"):
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    headers = dict(response.headers)
    headers.pop("content-length", None)

    if response.status_code != 200:
        return Response(
            content=body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
            background=response.background,
        )

    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return Response(
            content=body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
            background=response.background,
        )

    if isinstance(payload, dict) and _chain_response_is_dhan_only(payload):
        return JSONResponse(_normalize_verified_chain_payload(payload), status_code=200)
    if isinstance(payload, dict):
        return JSONResponse(_blocked_chain_payload(payload), status_code=200)

    return Response(
        content=body,
        status_code=response.status_code,
        headers=headers,
        media_type=response.media_type,
        background=response.background,
    )


async def memory_guard_middleware(request, call_next: Callable):
    """
    Middleware that:
    1. Tracks RSS before/after each request
    2. Forces GC if memory exceeds threshold
    3. Logs warnings when memory is high
    4. Enforces Dhan-only chain truth so old local rows cannot be shown as live
    """
    global _last_gc_time

    path = request.url.path
    if path in _FAST_PATHS:
        return await call_next(request)

    rss_before = _rss_mb()
    t0 = time.monotonic()

    response = await call_next(request)
    response = await _enforce_dhan_only_chain_response(request, response)

    rss_after = _rss_mb()
    elapsed_ms = (time.monotonic() - t0) * 1000
    delta_mb = rss_after - rss_before

    if rss_after > MEM_GC_MB and (time.monotonic() - _last_gc_time) > GC_COOLDOWN_S:
        gc.collect()
        _last_gc_time = time.monotonic()
        rss_after_gc = _rss_mb()
        print(
            f"[MemGuard] GC triggered — {rss_after:.0f}MB → {rss_after_gc:.0f}MB "
            f"freed={rss_after - rss_after_gc:.0f}MB after {path}"
        )

    elif rss_after > MEM_WARN_MB:
        print(f"[MemGuard] WARN {rss_after:.0f}MB/{MEM_LIMIT_MB}MB +{delta_mb:+.0f}MB  {path}  {elapsed_ms:.0f}ms")

    return response


def get_memory_stats() -> dict:
    """Return current memory stats for /api/health endpoint."""
    rss = _rss_mb()
    return {
        "rss_mb": round(rss, 1),
        "limit_mb": MEM_LIMIT_MB,
        "pct_used": round(rss / MEM_LIMIT_MB * 100, 1),
        "warn_threshold_mb": MEM_WARN_MB,
        "gc_threshold_mb": MEM_GC_MB,
        "status": "OK" if rss < MEM_WARN_MB else "WARN" if rss < MEM_GC_MB else "HIGH",
    }
