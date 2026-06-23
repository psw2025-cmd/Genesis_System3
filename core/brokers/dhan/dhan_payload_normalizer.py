"""Normalize Dhan API payloads to consistent list/dict shapes for dashboard truth."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union


def _as_list(raw: Any, keys: tuple[str, ...]) -> List[Dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if isinstance(raw, dict):
        for key in keys:
            val = raw.get(key)
            if isinstance(val, list):
                return [x for x in val if isinstance(x, dict)]
        if all(isinstance(v, dict) for v in raw.values()):
            return list(raw.values())
    return []


def normalize_holdings_payload(raw: Any) -> List[Dict[str, Any]]:
    return _as_list(raw, ("data", "holdings"))


def normalize_positions_payload(raw: Any) -> List[Dict[str, Any]]:
    return _as_list(raw, ("data", "positions"))


def normalize_funds_payload(raw: Any) -> Dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        if "data" in raw and isinstance(raw["data"], dict):
            return raw["data"]
        if "data" in raw and isinstance(raw["data"], list) and raw["data"]:
            first = raw["data"][0]
            return first if isinstance(first, dict) else {}
        return raw
    if isinstance(raw, list) and raw and isinstance(raw[0], dict):
        return raw[0]
    return {}


def normalize_holding_row(item: Dict[str, Any]) -> Dict[str, Any]:
    qty = item.get("totalQty") or item.get("quantity") or item.get("availableQty") or 0
    avg = item.get("avgCostPrice") or item.get("averagePrice") or item.get("costPrice") or 0
    ltp = item.get("lastTradedPrice") or item.get("ltp") or item.get("lastPrice") or 0
    try:
        qty_f = float(qty)
        avg_f = float(avg)
        ltp_f = float(ltp)
    except (TypeError, ValueError):
        qty_f, avg_f, ltp_f = 0.0, 0.0, 0.0
    pnl = (ltp_f - avg_f) * qty_f if qty_f else 0.0
    return {
        "symbol": item.get("tradingSymbol") or item.get("symbol") or item.get("securityId") or "UNKNOWN",
        "quantity": qty_f,
        "avg_price": avg_f,
        "ltp": ltp_f,
        "current_value": ltp_f * qty_f,
        "pnl": pnl,
        "pnl_pct": ((ltp_f - avg_f) / avg_f * 100) if avg_f else None,
        "raw": item,
    }


def normalize_position_row(item: Dict[str, Any]) -> Dict[str, Any]:
    qty = item.get("netQty") or item.get("netQuantity") or item.get("quantity") or 0
    try:
        qty_f = float(qty)
    except (TypeError, ValueError):
        qty_f = 0.0
    return {
        "symbol": item.get("tradingSymbol") or item.get("symbol") or "UNKNOWN",
        "product": item.get("productType") or item.get("product") or "--",
        "net_qty": qty_f,
        "avg_price": float(item.get("buyAvg") or item.get("averagePrice") or item.get("costPrice") or 0),
        "ltp": float(item.get("lastTradedPrice") or item.get("ltp") or 0),
        "unrealized_pnl": float(item.get("unrealizedProfit") or item.get("unrealized_pnl") or 0),
        "realized_pnl": float(item.get("realizedProfit") or item.get("realized_pnl") or 0),
        "raw": item,
    }


def normalize_funds_row(item: Dict[str, Any]) -> Dict[str, Any]:
    avail = item.get("availabelBalance")
    if avail is None:
        avail = item.get("availableBalance") or item.get("available_balance")
    utilized = item.get("utilizedAmount") or item.get("utilized_amount") or item.get("utilisedAmount")
    total = item.get("sodLimit") or item.get("totalLimit") or item.get("collateralAmount")
    try:
        avail_f = float(avail) if avail is not None else None
        utilized_f = float(utilized) if utilized is not None else None
        total_f = float(total) if total is not None else None
    except (TypeError, ValueError):
        avail_f = utilized_f = total_f = None
    return {
        "available_balance": avail_f,
        "utilized_amount": utilized_f,
        "total_limit": total_f,
        "raw": item,
    }
