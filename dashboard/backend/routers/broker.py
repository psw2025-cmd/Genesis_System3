"""
Broker router — Dhan API endpoints.
All broker data: status, holdings, funds, positions.
Lazy imports: dhanhq loaded only when needed.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
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


@router.get("/dhan/status")
async def get_dhan_status():
    """Dhan broker connection status — token validity, mode, client ID."""
    try:
        from core.brokers.dhan.token_manager import get_token_status
        status = get_token_status()
        return {
            "connected": status.get("valid", False),
            "mode": "READ-ONLY (Analyzer)",
            "client_id": f"...{os.environ.get('DHAN_CLIENT_ID', '')[-4:]}",
            "token_status": "VALID" if status.get("valid") else "INVALID",
            "holdings_api": "VALID" if status.get("valid") else "INVALID",
            "funds_api": "VALID" if status.get("valid") else "INVALID",
            "live_trading": "DISABLED (hardcoded 0)",
        }
    except Exception as e:
        return {"connected": False, "error": str(e)[:100]}


@router.get("/status")
async def get_broker_status():
    """Quick broker status for TopBar."""
    try:
        from core.brokers.dhan.token_manager import get_token_status
        s = get_token_status()
        return {"connected": s.get("valid", False), "broker": "dhan"}
    except Exception as e:
        return {"connected": False, "error": str(e)[:80]}


@router.get("/holdings")
async def get_holdings():
    """Real Dhan equity holdings."""
    try:
        from core.brokers.dhan.token_manager import get_token_status
        if not get_token_status().get("valid"):
            return {"holdings": [], "error": "Token invalid"}
        from dhanhq import DhanHQ
        client_id = os.environ.get("DHAN_CLIENT_ID", "")
        access_token = os.environ.get("DHAN_ACCESS_TOKEN", "")
        dhan = DhanHQ(client_id=client_id, access_token=access_token)
        resp = dhan.get_holdings()
        holdings = resp.get("data", []) if isinstance(resp, dict) else []
        return {"holdings": holdings, "count": len(holdings)}
    except Exception as e:
        return {"holdings": [], "error": str(e)[:100]}


@router.get("/funds")
async def get_funds():
    """Real Dhan account funds."""
    try:
        from core.brokers.dhan.token_manager import get_token_status
        if not get_token_status().get("valid"):
            return {"available_balance": 0, "error": "Token invalid"}
        from dhanhq import DhanHQ
        client_id = os.environ.get("DHAN_CLIENT_ID", "")
        access_token = os.environ.get("DHAN_ACCESS_TOKEN", "")
        dhan = DhanHQ(client_id=client_id, access_token=access_token)
        resp = dhan.get_fund_limits()
        data = resp.get("data", {}) if isinstance(resp, dict) else {}
        return {
            "available_balance": data.get("availabelBalance", 0),
            "used_margin": data.get("utilizedAmount", 0),
            "total_balance": data.get("sodLimit", 0),
        }
    except Exception as e:
        return {"available_balance": 0, "error": str(e)[:100]}


@router.get("/positions/live")
async def get_live_positions():
    """Real Dhan live positions."""
    try:
        from core.brokers.dhan.token_manager import get_token_status
        if not get_token_status().get("valid"):
            return {"positions": [], "error": "Token invalid"}
        from dhanhq import DhanHQ
        client_id = os.environ.get("DHAN_CLIENT_ID", "")
        access_token = os.environ.get("DHAN_ACCESS_TOKEN", "")
        dhan = DhanHQ(client_id=client_id, access_token=access_token)
        resp = dhan.get_positions()
        positions = resp.get("data", []) if isinstance(resp, dict) else []
        return {"positions": positions, "count": len(positions)}
    except Exception as e:
        return {"positions": [], "error": str(e)[:100]}


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
    }
