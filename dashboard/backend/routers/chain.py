"""
Chain router — lightweight discovery endpoints only.

Important:
- The authoritative /api/chain/{underlying} endpoint lives in dashboard.backend.app.
- It serves worker-pushed option-chain snapshots from the web process cache and
  avoids expensive inline chain fetching on the 512MB Render web service.
- Do not re-register /api/chain/{underlying} here; route order would shadow the
  optimized app-level endpoint and can reintroduce 503/OOM risk.
"""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["chain"])


@router.get("/api/underlyings")
async def get_underlyings():
    """List of supported underlyings for option chain."""
    return {
        "underlyings": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"],
        "default": "NIFTY",
        "chain_endpoint": "/api/chain/{underlying}",
        "chain_source": "app_worker_pushed_cache",
    }
