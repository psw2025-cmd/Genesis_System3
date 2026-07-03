"""
Memory-aware middleware for Genesis System3.
Tracks RAM usage per request and auto-runs GC when above threshold.
Zero quality impact — pure infrastructure layer.
"""
from __future__ import annotations
import gc
import os
import time
from typing import Callable

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


# Configuration
MEM_WARN_MB   = int(os.environ.get("MEM_WARN_MB",  "380"))  # warn at 380MB
MEM_GC_MB     = int(os.environ.get("MEM_GC_MB",    "420"))  # force GC at 420MB
MEM_LIMIT_MB  = int(os.environ.get("MEM_LIMIT_MB", "480"))  # 512MB Starter limit

# Expensive endpoints — skip GC overhead tracking for fast paths
_FAST_PATHS = {"/", "/api/health", "/api/state", "/static"}

_last_gc_time = 0.0
GC_COOLDOWN_S = 30.0  # Don't GC more than once per 30s


async def memory_guard_middleware(request, call_next: Callable):
    """
    Middleware that:
    1. Tracks RSS before/after each request
    2. Forces GC if memory exceeds threshold
    3. Logs warnings when memory is high
    4. Never blocks requests — only advisory
    """
    global _last_gc_time

    path = request.url.path
    if path in _FAST_PATHS:
        return await call_next(request)

    rss_before = _rss_mb()
    t0 = time.monotonic()

    response = await call_next(request)

    rss_after = _rss_mb()
    elapsed_ms = (time.monotonic() - t0) * 1000
    delta_mb = rss_after - rss_before

    # Force GC if memory is high and cooldown has passed
    if rss_after > MEM_GC_MB and (time.monotonic() - _last_gc_time) > GC_COOLDOWN_S:
        gc.collect()
        _last_gc_time = time.monotonic()
        rss_after_gc = _rss_mb()
        print(f"[MemGuard] GC triggered — {rss_after:.0f}MB → {rss_after_gc:.0f}MB "
              f"freed={rss_after - rss_after_gc:.0f}MB after {path}")

    elif rss_after > MEM_WARN_MB:
        print(f"[MemGuard] WARN {rss_after:.0f}MB/{MEM_LIMIT_MB}MB "
              f"+{delta_mb:+.0f}MB  {path}  {elapsed_ms:.0f}ms")

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
