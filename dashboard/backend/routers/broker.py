"""
Broker router — Dhan read-only API endpoints.
All endpoints use the analyzer-only adapter. No order placement endpoints here.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter(prefix="/api/broker", tags=["broker"])

# ── Shared state (injected at app startup) ─────────────────────────
_state_store = None
_token_manager = None


def init(state_store, token_manager=None):
    global _state_store, _token_manager
    _state_store = state_store
    _token_manager = token_manager


def _safe_error(exc: Exception, limit: int = 120) -> str:
    return str(exc)[:limit]


def _extract_payload(resp: Dict[str, Any], key: str) -> list | dict:
    """Normalize read-only adapter response payloads."""
    if not isinstance(resp, dict):
        return []
    data = resp.get("data")
    if isinstance(data, dict) and key in data:
        return data.get(key) or []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        nested = data.get("data")
        if isinstance(nested, list):
            return nested
    return []


@router.get("/dhan/status")
async def get_dhan_status():
    """Dhan broker connection status — analyzer/read-only."""
    try:
        from core.brokers.dhan.dhan_readonly import get_status

        status = get_status()
        return {
            "connected": bool(status.get("connected", False)),
            "broker": status.get("broker", "dhan"),
            "mode": status.get("mode", "ANALYZER"),
            "status": "connected" if status.get("connected") else "disconnected",
            "error": status.get("error"),
            "latency_ms": status.get("latency_ms"),
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "source": status.get("source", "dhan_readonly"),
        }
    except Exception as e:
        return {
            "connected": False,
            "broker": "dhan",
            "mode": "ANALYZER",
            "error": _safe_error(e),
            "live_trading_enabled": False,
            "order_placement_allowed": False,
        }


@router.get("/status")
async def get_broker_status():
    """Quick broker status for dashboard TopBar."""
    return await get_dhan_status()


@router.get("/holdings")
async def get_holdings():
    """Real Dhan equity holdings via read-only adapter."""
    try:
        from core.brokers.dhan.dhan_readonly import get_holdings as _get_holdings

        resp = _get_holdings()
        holdings = _extract_payload(resp, "holdings")
        return {
            "holdings": holdings if isinstance(holdings, list) else [],
            "count": len(holdings) if isinstance(holdings, list) else 0,
            "source": resp.get("source"),
            "error": None if resp.get("success") else resp.get("error"),
        }
    except Exception as e:
        return {"holdings": [], "count": 0, "error": _safe_error(e)}


@router.get("/funds")
async def get_funds():
    """Real Dhan account funds via read-only adapter."""
    try:
        from core.brokers.dhan.dhan_readonly import get_funds as _get_funds

        resp = _get_funds()
        data = resp.get("data") if isinstance(resp, dict) else {}
        if isinstance(data, dict) and isinstance(data.get("data"), dict):
            data = data.get("data")
        if not isinstance(data, dict):
            data = {}
        return {
            "available_balance": data.get("availabelBalance", data.get("availableBalance", 0)),
            "used_margin": data.get("utilizedAmount", 0),
            "total_balance": data.get("sodLimit", 0),
            "source": resp.get("source") if isinstance(resp, dict) else None,
            "error": None if isinstance(resp, dict) and resp.get("success") else (resp or {}).get("error"),
        }
    except Exception as e:
        return {"available_balance": 0, "used_margin": 0, "total_balance": 0, "error": _safe_error(e)}


@router.get("/positions/live")
async def get_live_positions():
    """Real Dhan live positions via read-only adapter."""
    try:
        from core.brokers.dhan.dhan_readonly import get_positions as _get_positions

        resp = _get_positions()
        positions = _extract_payload(resp, "positions")
        return {
            "positions": positions if isinstance(positions, list) else [],
            "count": len(positions) if isinstance(positions, list) else 0,
            "source": resp.get("source"),
            "error": None if resp.get("success") else resp.get("error"),
        }
    except Exception as e:
        return {"positions": [], "count": 0, "error": _safe_error(e)}


@router.get("/truth")
async def get_broker_truth():
    """Unified broker truth — all broker data in one call."""
    status = await get_dhan_status()
    funds = await get_funds()
    holdings = await get_holdings()
    positions = await get_live_positions()
    return {
        "status": status,
        "funds": funds,
        "holdings": holdings,
        "positions": positions,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
