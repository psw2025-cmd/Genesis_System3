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


def _chain_response_is_dhan_only(payload: dict) -> bool:
    """True only when the response contains current Dhan-derived option-chain rows."""
    contracts = payload.get("contracts") or []
    if not isinstance(contracts, list) or not contracts:
        return False

    if bool(payload.get("stale")):
        return False

    status = str(payload.get("status") or "").upper()
    if "STALE" in status or "FALLBACK" in status or "SYNTHETIC" in status or "CSV" in status:
        return False

    data_source = str(payload.get("data_source") or "").lower()
    source_priority = str(payload.get("source_priority") or "").lower()
    source_text = f"{data_source} {source_priority}"
    if any(bad in source_text for bad in ("csv", "fallback", "synthetic", "bhavcopy", "nse", "yahoo")):
        return False

    if data_source not in _CHAIN_ALLOWED_DATA_SOURCES:
        return False

    if source_priority and source_priority != "--" and not source_priority.startswith(_CHAIN_ALLOWED_SOURCE_PREFIXES):
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
        "blocked_reason": "NO_CURRENT_DHAN_OPTION_CHAIN_ROWS",
        "suppressed_source": original.get("data_source"),
        "suppressed_source_priority": original.get("source_priority"),
        "suppressed_status": original.get("status"),
        "message": "No current Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.",
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

    if isinstance(payload, dict) and not _chain_response_is_dhan_only(payload):
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
