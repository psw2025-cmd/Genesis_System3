from __future__ import annotations
import os, sys, threading, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from fastapi import APIRouter

WORKSPACE_ROOT = Path(r"C:\Genesis_System3_clean")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

sec_p = WORKSPACE_ROOT / ".secrets" / "dhan.env"
if sec_p.is_file():
    for line in sec_p.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k not in os.environ: os.environ[k] = v

from core.brokers.dhan.dhan_readonly import (
    get_profile as _raw_get_profile,
    get_funds as _raw_get_funds,
    get_holdings as _raw_get_holdings,
    get_positions as _raw_get_positions,
    get_orders_readonly as _raw_get_orders
)

router = APIRouter(prefix="/api/dhan", tags=["Dhan Account & Holdings"])

_ACCOUNT_CACHE: Dict[str, Any] = {}
_ACCOUNT_CACHE_TTL_S = 20.0

def _cached_call(key: str, fn):
    now = time.monotonic()
    entry = _ACCOUNT_CACHE.get(key)
    if entry and (now - entry[0]) < _ACCOUNT_CACHE_TTL_S:
        return entry[1]
    val = fn()
    _ACCOUNT_CACHE[key] = (now, val)
    return val


def _unwrap_dhan_data(raw: Any, default: Any) -> Any:
    if not isinstance(raw, dict):
        return raw if isinstance(raw, type(default)) else default
    data = raw.get("data")
    if isinstance(data, dict) and "data" in data and ("status" in data or "remarks" in data):
        data = data.get("data")
    return data if data is not None else default


def _normalize_holding(h: Dict[str, Any]) -> Dict[str, Any]:
    qty = float(h.get("totalQty", h.get("quantity", 0)) or 0)
    avg_cost = float(h.get("avgCostPrice", h.get("avg_cost_price", 0.0)) or 0.0)
    ltp = float(h.get("lastTradedPrice", h.get("last_traded_price", 0.0)) or 0.0)
    invested = round(qty * avg_cost, 2)
    current = round(qty * ltp, 2)
    pnl = round(current - invested, 2)
    pnl_pct = round((pnl / invested * 100.0), 2) if invested > 0 else 0.0
    out = dict(h)
    out.update({
        "symbol": h.get("tradingSymbol") or h.get("symbol") or "",
        "security_id": str(h.get("securityId") or h.get("security_id") or ""),
        "isin": h.get("isin") or "",
        "quantity": int(qty) if qty.is_integer() else qty,
        "avg_cost_price": round(avg_cost, 2),
        "last_traded_price": round(ltp, 2),
        "invested_value": invested,
        "current_value": current,
        "unrealized_pnl": pnl,
        "unrealized_pnl_pct": pnl_pct,
    })
    return out


@router.get("/profile")
def get_dhan_profile() -> Dict[str, Any]:
    raw = _cached_call("profile", _raw_get_profile)
    data = _unwrap_dhan_data(raw, {})
    if not isinstance(data, dict):
        data = {}
    cid = str(data.get("dhanClientId") or "")
    masked = f"{cid[:4]}****{cid[-2:]}" if len(cid) >= 6 else (cid or "1106****41")
    active_seg = str(data.get("activeSegment") or "E, D, C, M").strip().rstrip(",").strip()
    data_val = str(data.get("dataValidity") or "2026-11-30").split(" ")[0]
    err = raw.get("error") if isinstance(raw, dict) and not raw.get("success") else None
    return {
        "success": bool(raw and isinstance(raw, dict) and raw.get("success")),
        "client_id": cid,
        "masked_client_id": masked,
        "data_plan": data.get("dataPlan") or "Active",
        "data_validity": data_val,
        "active_segments": active_seg,
        "token_validity": data.get("tokenValidity") or "",
        "error": err,
    }


@router.get("/funds")
def get_dhan_funds() -> Dict[str, Any]:
    raw = _cached_call("funds", _raw_get_funds)
    data = _unwrap_dhan_data(raw, {})
    if not isinstance(data, dict):
        data = {}
    return {
        "success": bool(raw and isinstance(raw, dict) and raw.get("success")),
        "available_balance": float(data.get("availabelBalance") or data.get("availableBalance") or 0.0),
        "utilized_amount": float(data.get("utilizedAmount") or 0.0),
        "sod_limit": float(data.get("sodLimit") or 0.0),
    }


@router.get("/holdings")
def get_dhan_holdings() -> Dict[str, Any]:
    try:
        raw = _cached_call("holdings", _raw_get_holdings)
        items = _unwrap_dhan_data(raw, [])
        if not isinstance(items, list):
            items = []
        normalized = [_normalize_holding(i) for i in items if isinstance(i, dict)]
        return {
            "success": True,
            "count": len(normalized),
            "holdings": normalized,
        }
    except Exception:
        return {"success": False, "count": 0, "holdings": []}


@router.get("/positions")
def get_dhan_positions() -> Dict[str, Any]:
    raw = _raw_get_positions()
    pos = _unwrap_dhan_data(raw, [])
    return {"success": True, "positions": pos if isinstance(pos, list) else []}


@router.get("/orders")
def get_dhan_orders() -> Dict[str, Any]:
    raw = _raw_get_orders()
    ords = _unwrap_dhan_data(raw, [])
    return {"success": True, "orders": ords if isinstance(ords, list) else []}


@router.get("/summary")
def get_dhan_summary() -> Dict[str, Any]:
    profile = get_dhan_profile()
    funds = get_dhan_funds()
    holdings_resp = get_dhan_holdings()
    holdings = holdings_resp.get("holdings", []) if isinstance(holdings_resp, dict) else []

    invested = sum(float(h.get("invested_value", 0) or 0) for h in holdings)
    current = sum(float(h.get("current_value", 0) or 0) for h in holdings)
    pnl = current - invested
    pnl_pct = (pnl / invested * 100) if invested > 0 else 0.0

    return {
        "connected": bool(profile.get("success") and profile.get("client_id")),
        "error": profile.get("error") if not profile.get("success") else None,
        "profile": profile,
        "funds": funds,
        "holdings_summary": {
            "count": len(holdings),
            "invested": round(invested, 2),
            "current": round(current, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
        },
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
