"""
<<<<<<< HEAD
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
=======
Broker router — Dhan read-only API endpoints.
All endpoints use the analyzer-only adapter. No order placement endpoints here.
"""
from __future__ import annotations

>>>>>>> origin/main
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter(prefix="/api/broker", tags=["broker"])

<<<<<<< HEAD
BROKER_API_TIMEOUT_S = float(os.environ.get("BROKER_API_TIMEOUT_S", "4.0"))

=======
>>>>>>> origin/main
# ── Shared state (injected at app startup) ─────────────────────────
_state_store = None
_token_manager = None


def init(state_store, token_manager=None):
    global _state_store, _token_manager
    _state_store = state_store
    _token_manager = token_manager


<<<<<<< HEAD
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
=======
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
>>>>>>> origin/main


@router.get("/dhan/status")
async def get_dhan_status():
<<<<<<< HEAD
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
=======
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
>>>>>>> origin/main


@router.get("/status")
async def get_broker_status():
<<<<<<< HEAD
    """Quick broker status for TopBar."""
    try:
        s = await _run_readonly_call(_token_status, timeout=2.0)
        return {"connected": s.get("valid", False), "broker": "dhan", "live_trading_enabled": False}
    except asyncio.TimeoutError:
        return {"connected": False, "broker": "dhan", "error": "token_status_timeout"}
    except Exception as e:
        return {"connected": False, "broker": "dhan", "error": str(e)[:80]}
=======
    """Quick broker status for dashboard TopBar."""
    return await get_dhan_status()
>>>>>>> origin/main


@router.get("/holdings")
async def get_holdings():
<<<<<<< HEAD
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
=======
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
>>>>>>> origin/main


@router.get("/funds")
async def get_funds():
<<<<<<< HEAD
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
=======
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
>>>>>>> origin/main


@router.get("/positions/live")
async def get_live_positions():
<<<<<<< HEAD
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
=======
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
>>>>>>> origin/main


@router.get("/truth")
async def get_broker_truth():
<<<<<<< HEAD
    """Unified broker truth — all broker data in one call, sequential to avoid API bursts."""
=======
    """Unified broker truth — all broker data in one call."""
>>>>>>> origin/main
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
