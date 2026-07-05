"""
Broker router — Dhan API endpoints.
All broker data: status, holdings, funds, positions.
Lazy imports: dhanhq loaded only when needed.

All external Dhan calls are read-only and run in worker threads with hard
timeouts. This prevents slow broker/network calls from blocking the FastAPI
async event loop and causing Render 502s.
"""
from __future__ import annotations
import asyncio
import os
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter(prefix="/api/broker", tags=["broker"])

BROKER_API_TIMEOUT_S = float(os.environ.get("BROKER_API_TIMEOUT_S", "4.0"))

# ── Shared state (injected at app startup) ─────────────────────────
_state_store = None
_token_manager = None


def init(state_store, token_manager=None):
    global _state_store, _token_manager
    _state_store = state_store
    _token_manager = token_manager


async def _run_readonly_call(fn, *args, timeout: float = BROKER_API_TIMEOUT_S, **kwargs):
    """Run a synchronous read-only broker call outside the event loop."""
    return await asyncio.wait_for(asyncio.to_thread(fn, *args, **kwargs), timeout=timeout)


def _token_status() -> Dict[str, Any]:
    from core.brokers.dhan.dhan_readonly import get_status

    s = get_status()
    # Keep a stable shape for callers in this router.
    return {"valid": bool(s.get("connected", False)), **s}


def _get_dhan_client():
    from dhanhq import DhanHQ

    client_id = os.environ.get("DHAN_CLIENT_ID", "")
    access_token = os.environ.get("DHAN_ACCESS_TOKEN", "")
    return DhanHQ(client_id=client_id, access_token=access_token)


def _fetch_holdings_sync() -> Dict[str, Any]:
    dhan = _get_dhan_client()
    resp = dhan.get_holdings()
    holdings = resp.get("data", []) if isinstance(resp, dict) else []
    return {"holdings": holdings, "count": len(holdings), "source": "dhan_readonly"}


def _fetch_funds_sync() -> Dict[str, Any]:
    dhan = _get_dhan_client()
    resp = dhan.get_fund_limits()
    data = resp.get("data", {}) if isinstance(resp, dict) else {}
    return {
        "available_balance": data.get("availabelBalance", 0),
        "used_margin": data.get("utilizedAmount", 0),
        "total_balance": data.get("sodLimit", 0),
        "source": "dhan_readonly",
    }


def _fetch_positions_sync() -> Dict[str, Any]:
    dhan = _get_dhan_client()
    resp = dhan.get_positions()
    positions = resp.get("data", []) if isinstance(resp, dict) else []
    return {"positions": positions, "count": len(positions), "source": "dhan_readonly"}


@router.get("/dhan/status")
async def get_dhan_status():
    """Dhan broker connection status — token validity, mode, client ID."""
    try:
        status = await _run_readonly_call(_token_status, timeout=2.0)
        return {
            "connected": status.get("valid", False),
            "mode": "READ-ONLY (Analyzer)",
            "client_id": f"...{os.environ.get('DHAN_CLIENT_ID', '')[-4:]}",
            "token_status": "VALID" if status.get("valid") else "INVALID",
            "holdings_api": "VALID" if status.get("valid") else "INVALID",
            "funds_api": "VALID" if status.get("valid") else "INVALID",
            "live_trading": "DISABLED (hardcoded 0)",
            "live_trading_enabled": False,
            "order_placement_allowed": False,
        }
    except asyncio.TimeoutError:
        return {"connected": False, "error": "token_status_timeout", "live_trading_enabled": False}
    except Exception as e:
        return {"connected": False, "error": str(e)[:100], "live_trading_enabled": False}


@router.get("/status")
async def get_broker_status():
    """Quick broker status for TopBar."""
    try:
        s = await _run_readonly_call(_token_status, timeout=2.0)
        return {"connected": s.get("valid", False), "broker": "dhan", "live_trading_enabled": False}
    except asyncio.TimeoutError:
        return {"connected": False, "broker": "dhan", "error": "token_status_timeout"}
    except Exception as e:
        return {"connected": False, "broker": "dhan", "error": str(e)[:80]}


@router.get("/holdings")
async def get_holdings():
    """Real Dhan equity holdings. Read-only, timeout-safe."""
    try:
        if not (await _run_readonly_call(_token_status, timeout=2.0)).get("valid"):
            return {"holdings": [], "error": "Token invalid", "live_trading_enabled": False}
        result = await _run_readonly_call(_fetch_holdings_sync)
        return {**result, "live_trading_enabled": False, "order_placement_allowed": False}
    except asyncio.TimeoutError:
        return {"holdings": [], "error": "holdings_timeout", "live_trading_enabled": False}
    except Exception as e:
        return {"holdings": [], "error": str(e)[:100], "live_trading_enabled": False}


@router.get("/funds")
async def get_funds():
    """Real Dhan account funds. Read-only, timeout-safe."""
    try:
        if not (await _run_readonly_call(_token_status, timeout=2.0)).get("valid"):
            return {"available_balance": 0, "error": "Token invalid", "live_trading_enabled": False}
        result = await _run_readonly_call(_fetch_funds_sync)
        return {**result, "live_trading_enabled": False, "order_placement_allowed": False}
    except asyncio.TimeoutError:
        return {"available_balance": 0, "error": "funds_timeout", "live_trading_enabled": False}
    except Exception as e:
        return {"available_balance": 0, "error": str(e)[:100], "live_trading_enabled": False}


@router.get("/positions/live")
async def get_live_positions():
    """Real Dhan live positions. Read-only, timeout-safe."""
    try:
        if not (await _run_readonly_call(_token_status, timeout=2.0)).get("valid"):
            return {"positions": [], "error": "Token invalid", "live_trading_enabled": False}
        result = await _run_readonly_call(_fetch_positions_sync)
        return {**result, "live_trading_enabled": False, "order_placement_allowed": False}
    except asyncio.TimeoutError:
        return {"positions": [], "error": "positions_timeout", "live_trading_enabled": False}
    except Exception as e:
        return {"positions": [], "error": str(e)[:100], "live_trading_enabled": False}


@router.get("/truth")
async def get_broker_truth():
    """Unified broker truth — all broker data in one call, sequential to avoid API bursts."""
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
