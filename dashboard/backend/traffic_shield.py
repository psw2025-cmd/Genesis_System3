"""Single-flight, stale-if-error load shield for public read-only API traffic.

This is intentionally NOT a generic rate limiter. The production failure mode is
many dashboard readers arriving at the same cold/cache-miss boundary and causing
identical expensive Dhan/Firestore work. The shield:
- coalesces identical GETs by normalized URL;
- caps simultaneous expensive public GET producers;
- serves a recent successful stale snapshot during transient 429/5xx pressure;
- emits Retry-After on locally rejected overload;
- never wraps mutation routes or WebSockets.

All state is per Cloud Run instance. Durable business truth remains Firestore/
broker data; this module is only a short-lived traffic protection layer.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl, urlencode

from fastapi import Request
from fastapi.responses import Response


@dataclass
class _CachedResponse:
    stored_at: float
    status_code: int
    body: bytes
    media_type: Optional[str]
    headers: Dict[str, str]


# External requests that may fan out into broker/Firestore/chain work.
# Static/UI/auth endpoints are deliberately excluded.
_SHIELDED_EXACT = {
    "/api/batch/market-data",
    "/api/batch/positions-holdings",
    "/api/batch/chains",
    "/api/market/live_board",
    "/api/scanner/top_contract_gainers",
    "/api/paper",
    "/api/state",
    "/api/health",
    "/api/gain_rank",
    "/api/auto_gates",
}
_SHIELDED_PREFIXES = (
    "/api/chain/",
    "/api/broker/",
)

_FRESH_TTL = float(os.environ.get("SYSTEM3_TRAFFIC_SHIELD_FRESH_S", "3") or 3)
_STALE_TTL = float(os.environ.get("SYSTEM3_TRAFFIC_SHIELD_STALE_S", "60") or 60)
_MAX_PRODUCERS = max(1, int(os.environ.get("SYSTEM3_TRAFFIC_SHIELD_MAX_PRODUCERS", "8") or 8))
_PRODUCER_WAIT_S = max(0.05, float(os.environ.get("SYSTEM3_TRAFFIC_SHIELD_WAIT_S", "1.5") or 1.5))
_RETRY_AFTER_S = max(1, int(os.environ.get("SYSTEM3_TRAFFIC_SHIELD_RETRY_AFTER_S", "3") or 3))

_cache: Dict[str, _CachedResponse] = {}
_locks: Dict[str, asyncio.Lock] = {}
_locks_guard = asyncio.Lock()
_producer_slots = asyncio.Semaphore(_MAX_PRODUCERS)
_stats = Counter()
_stats_lock = asyncio.Lock()


def retire_legacy_delay_middleware(app: Any, dispatch_fn: Any) -> int:
    """Remove the old fixed-delay pseudo-rate-limiter before the app serves.

    The legacy middleware merely slept 50 ms on broker/chain requests. It did
    not cap concurrency, honor Retry-After, or coalesce duplicate work, and it
    could increase queued request pressure. The real traffic shield replaces it.
    """
    if app is None or dispatch_fn is None:
        return 0
    rows = list(getattr(app, "user_middleware", []) or [])
    kept = []
    removed = 0
    for row in rows:
        kwargs = getattr(row, "kwargs", {}) or {}
        if kwargs.get("dispatch") is dispatch_fn:
            removed += 1
            continue
        kept.append(row)
    if removed:
        app.user_middleware[:] = kept
        # Starlette builds this lazily; clear defensively if already materialized.
        if hasattr(app, "middleware_stack"):
            app.middleware_stack = None
    return removed


def _is_shielded(path: str) -> bool:
    return path in _SHIELDED_EXACT or any(path.startswith(prefix) for prefix in _SHIELDED_PREFIXES)


def _key(request: Request) -> str:
    # Cache-busters must not defeat coalescing. Preserve functional parameters.
    pairs = [(k, v) for k, v in parse_qsl(request.url.query, keep_blank_values=True) if k not in {"_ts", "t", "cacheBust"}]
    query = urlencode(sorted(pairs))
    return f"{request.url.path}?{query}" if query else request.url.path


async def _lock_for(key: str) -> asyncio.Lock:
    async with _locks_guard:
        return _locks.setdefault(key, asyncio.Lock())


async def _inc(name: str, value: int = 1) -> None:
    async with _stats_lock:
        _stats[name] += value


def _age(entry: _CachedResponse | None) -> float:
    return float("inf") if entry is None else max(0.0, time.monotonic() - entry.stored_at)


def _copy(entry: _CachedResponse, *, cache_state: str) -> Response:
    headers = dict(entry.headers)
    headers["X-System3-Traffic-Shield"] = cache_state
    headers["Age"] = str(int(_age(entry)))
    return Response(
        content=entry.body,
        status_code=entry.status_code,
        media_type=entry.media_type,
        headers=headers,
    )


def _stale_available(key: str) -> _CachedResponse | None:
    entry = _cache.get(key)
    return entry if entry and entry.status_code == 200 and _age(entry) <= _STALE_TTL else None


async def _materialize(response) -> _CachedResponse:
    body = getattr(response, "body", None)
    if body is None:
        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
        body = b"".join(chunks)
    if isinstance(body, str):
        body = body.encode("utf-8")
    safe_headers = {}
    for key, value in dict(response.headers).items():
        if key.lower() not in {"content-length", "transfer-encoding", "connection", "set-cookie"}:
            safe_headers[key] = value
    return _CachedResponse(
        stored_at=time.monotonic(),
        status_code=int(response.status_code),
        body=bytes(body or b""),
        media_type=getattr(response, "media_type", None) or response.headers.get("content-type"),
        headers=safe_headers,
    )


async def traffic_shield_middleware(request: Request, call_next):
    """ASGI/FastAPI middleware entrypoint."""
    if request.method.upper() != "GET" or not _is_shielded(request.url.path):
        return await call_next(request)

    key = _key(request)
    entry = _cache.get(key)
    if entry and entry.status_code == 200 and _age(entry) <= _FRESH_TTL:
        await _inc("fresh_hits")
        return _copy(entry, cache_state="fresh")

    lock = await _lock_for(key)
    if lock.locked():
        await _inc("coalesced_waiters")

    async with lock:
        # Another waiter may already have refreshed it.
        entry = _cache.get(key)
        if entry and entry.status_code == 200 and _age(entry) <= _FRESH_TTL:
            await _inc("joined_hits")
            return _copy(entry, cache_state="joined")

        acquired = False
        try:
            await asyncio.wait_for(_producer_slots.acquire(), timeout=_PRODUCER_WAIT_S)
            acquired = True
        except asyncio.TimeoutError:
            await _inc("local_overload_rejections")
            stale = _stale_available(key)
            if stale:
                await _inc("stale_overload_served")
                return _copy(stale, cache_state="stale-overload")
            payload = {
                "status": "BUSY",
                "reason": "SYSTEM3_TRAFFIC_SHIELD_SATURATED",
                "retry_after_s": _RETRY_AFTER_S,
                "live_trading_enabled": False,
            }
            print(json.dumps({"severity": "WARNING", "event": "SYSTEM3_TRAFFIC_SHIELD_429", "path": request.url.path, "retry_after_s": _RETRY_AFTER_S}, sort_keys=True))
            return Response(
                content=json.dumps(payload),
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(_RETRY_AFTER_S), "X-System3-Traffic-Shield": "rejected"},
            )

        try:
            await _inc("producer_calls")
            response = await call_next(request)
            materialized = await _materialize(response)
            transient = materialized.status_code == 429 or 500 <= materialized.status_code <= 599
            if transient:
                await _inc(f"upstream_status_{materialized.status_code}")
                stale = _stale_available(key)
                if stale:
                    await _inc("stale_transient_served")
                    print(json.dumps({"severity": "WARNING", "event": "SYSTEM3_TRAFFIC_STALE_FAILOVER", "path": request.url.path, "upstream_status": materialized.status_code}, sort_keys=True))
                    return _copy(stale, cache_state=f"stale-upstream-{materialized.status_code}")
                headers = dict(materialized.headers)
                if materialized.status_code == 429:
                    headers.setdefault("Retry-After", str(_RETRY_AFTER_S))
                headers["X-System3-Traffic-Shield"] = "upstream-transient"
                return Response(materialized.body, status_code=materialized.status_code, media_type=materialized.media_type, headers=headers)

            if materialized.status_code == 200:
                _cache[key] = materialized
            headers = dict(materialized.headers)
            headers["X-System3-Traffic-Shield"] = "producer"
            return Response(materialized.body, status_code=materialized.status_code, media_type=materialized.media_type, headers=headers)
        finally:
            if acquired:
                _producer_slots.release()


def traffic_shield_status() -> Dict[str, Any]:
    now = time.monotonic()
    cached_fresh = sum(1 for row in _cache.values() if row.status_code == 200 and now - row.stored_at <= _FRESH_TTL)
    cached_stale_usable = sum(1 for row in _cache.values() if row.status_code == 200 and now - row.stored_at <= _STALE_TTL)
    return {
        "status": "ENFORCED",
        "shielded_exact_count": len(_SHIELDED_EXACT),
        "shielded_prefix_count": len(_SHIELDED_PREFIXES),
        "max_concurrent_producers": _MAX_PRODUCERS,
        "producer_wait_s": _PRODUCER_WAIT_S,
        "fresh_ttl_s": _FRESH_TTL,
        "stale_ttl_s": _STALE_TTL,
        "retry_after_s": _RETRY_AFTER_S,
        "cache_entries": len(_cache),
        "fresh_entries": cached_fresh,
        "stale_usable_entries": cached_stale_usable,
        "stats": dict(_stats),
        "mutation_routes_shielded": False,
        "legacy_fixed_delay_middleware_required": False,
        "live_trading_enabled": False,
    }