"""
Genesis System3 cloud startup compatibility hooks.

Why this exists:
- Render imports dashboard.backend.app through uvicorn.
- Current app startup still calls background_data_refresh(), but that legacy
  coroutine is absent in app.py.
- Python automatically imports sitecustomize from PYTHONPATH (/app in the
  Render Docker image), so this file provides a safe fallback through builtins
  before dashboard.backend.app is imported.

Safety:
- Analyzer/read-only only.
- No broker order placement, modification, cancellation, or live trading.
- No secrets are read or printed.
"""

from __future__ import annotations

import asyncio
import builtins
import os


async def _system3_background_data_refresh_fallback() -> None:
    """Non-fatal no-op background refresh loop for cloud startup stability.

    The frontend/API already read live chain/state through request handlers and
    worker-produced files. This fallback only prevents FastAPI startup from
    crashing when the legacy background_data_refresh symbol is missing.
    """
    interval_s = int(os.getenv("BACKGROUND_DATA_REFRESH_INTERVAL_S", "300") or "300")
    print("[startup-compat] background_data_refresh fallback active (no-op)")
    while True:
        await asyncio.sleep(max(60, interval_s))


if not hasattr(builtins, "background_data_refresh"):
    builtins.background_data_refresh = _system3_background_data_refresh_fallback
