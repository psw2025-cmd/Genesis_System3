"""
DhanHQ option-chain response parser.

Maps official Dhan leg fields to a normalized row dict. Computes derived fields
change_in_oi and bid_ask_spread. Does not expect non-Dhan aliases (bid, ask,
oi_change, flat greeks on leg).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_dhan_leg(leg: Dict[str, Any], strike: float, option_type: str) -> Dict[str, Any]:
    """Parse one CE/PE leg using official DhanHQ field names."""
    greeks = leg.get("greeks") or {}
    if not isinstance(greeks, dict):
        greeks = {}

    oi = _safe_int(leg.get("oi"))
    previous_oi = _safe_int(leg.get("previous_oi"))
    top_bid = _safe_float(leg.get("top_bid_price"))
    top_ask = _safe_float(leg.get("top_ask_price"))

    return {
        "strike": strike,
        "option_type": option_type,
        "security_id": leg.get("security_id"),
        "oi": oi,
        "previous_oi": previous_oi,
        "change_in_oi": oi - previous_oi,
        "volume": _safe_int(leg.get("volume")),
        "previous_volume": _safe_int(leg.get("previous_volume")),
        "ltp": _safe_float(leg.get("last_price")),
        "average_price": _safe_float(leg.get("average_price")),
        "previous_close_price": _safe_float(leg.get("previous_close_price")),
        "top_bid_price": top_bid,
        "top_bid_quantity": _safe_int(leg.get("top_bid_quantity")),
        "top_ask_price": top_ask,
        "top_ask_quantity": _safe_int(leg.get("top_ask_quantity")),
        "bid_ask_spread": top_ask - top_bid,
        "iv": _safe_float(leg.get("implied_volatility")) / 100.0,
        "implied_volatility": _safe_float(leg.get("implied_volatility")),
        "delta": _safe_float(greeks.get("delta")),
        "gamma": _safe_float(greeks.get("gamma")),
        "theta": _safe_float(greeks.get("theta")),
        "vega": _safe_float(greeks.get("vega")),
        "source": "dhan",
    }


def _iter_official_oc_rows(data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], float]:
    """Parse official Dhan v2 response shape: data.oc.{strike}.{ce|pe}."""
    rows: List[Dict[str, Any]] = []
    spot = _safe_float(data.get("last_price"))
    oc = data.get("oc") or {}
    if not isinstance(oc, dict):
        return rows, spot

    for strike_key, strike_payload in oc.items():
        if not isinstance(strike_payload, dict):
            continue
        strike = _safe_float(strike_key, _safe_float(strike_payload.get("strike_price")))
        for opt_type, key in (("CE", "ce"), ("PE", "pe")):
            leg = strike_payload.get(key)
            if isinstance(leg, dict) and leg:
                rows.append(parse_dhan_leg(leg, strike, opt_type))
    return rows, spot


def _iter_list_rows(items: Any, initial_spot: float = 0.0) -> Tuple[List[Dict[str, Any]], float]:
    """Parse SDK/list style rows that contain strike_price and ce/pe objects."""
    rows: List[Dict[str, Any]] = []
    spot = initial_spot
    if not isinstance(items, list):
        return rows, spot
    for item in items:
        if not isinstance(item, dict):
            continue
        spot = _safe_float(item.get("last_price", spot), spot)
        strike = _safe_float(item.get("strike_price", item.get("strike", 0)))
        for opt_type, key in (("CE", "ce"), ("PE", "pe")):
            leg = item.get(key)
            if isinstance(leg, dict) and leg:
                rows.append(parse_dhan_leg(leg, strike, opt_type))
    return rows, spot


def parse_dhan_option_chain_payload(payload: Any) -> Tuple[pd.DataFrame, float]:
    """
    Parse Dhan option_chain API response.

    Official Dhan v2 shape is:
      {"status":"success", "data":{"last_price": ..., "oc": {"strike": {"ce":..., "pe":...}}}}

    Some SDK versions may return a list-like wrapper. Both shapes are accepted.
    Returns (DataFrame, spot_price). Empty result means no official Dhan chain rows
    were present; callers must not silently substitute CSV/synthetic data as live.
    """
    if isinstance(payload, dict):
        data = payload.get("data", payload)
        if isinstance(data, dict):
            official_rows, spot = _iter_official_oc_rows(data)
            if official_rows:
                return pd.DataFrame(official_rows), spot
            list_rows, spot = _iter_list_rows(data.get("data", []), spot)
            if list_rows:
                return pd.DataFrame(list_rows), spot
        elif isinstance(data, list):
            list_rows, spot = _iter_list_rows(data)
            if list_rows:
                return pd.DataFrame(list_rows), spot
    elif isinstance(payload, list):
        list_rows, spot = _iter_list_rows(payload)
        if list_rows:
            return pd.DataFrame(list_rows), spot

    return pd.DataFrame(), 0.0


def parse_option_chain_to_df(resp: Dict[str, Any], symbol: str) -> tuple:
    """
    Parse option-chain response into (DataFrame, spot_price) tuple.

    First tries the official Dhan v2 parser. The legacy flat-list parser remains
    only for old internal wrappers; it does not invent data.
    """
    try:
        df, spot = parse_dhan_option_chain_payload(resp)
        if df is not None and not df.empty:
            return df, spot

        data = resp.get("data", {}) if isinstance(resp, dict) else {}
        spot = float(data.get("last_price", 0) or data.get("spot_price", 0) or 0) if isinstance(data, dict) else 0.0
        options = data.get("options_chain", []) if isinstance(data, dict) else []
        if not isinstance(options, list):
            return pd.DataFrame(), spot

        rows = []
        for opt in options:
            if isinstance(opt, dict):
                rows.append({
                    "strike": opt.get("strike_price", opt.get("SP", 0)),
                    "option_type": opt.get("option_type", opt.get("OT", "")),
                    "oi": opt.get("oi", opt.get("OI", 0)),
                    "previous_oi": opt.get("previous_oi", opt.get("prev_oi", 0)),
                    "change_in_oi": opt.get("change_in_oi", opt.get("COI", 0)),
                    "volume": opt.get("volume", opt.get("VOL", 0)),
                    "ltp": opt.get("last_price", opt.get("LTP", 0)),
                    "top_bid_price": opt.get("top_bid_price", opt.get("bid_price", opt.get("BP", 0))),
                    "top_ask_price": opt.get("top_ask_price", opt.get("ask_price", opt.get("AP", 0))),
                    "iv": _safe_float(opt.get("implied_volatility", opt.get("IV", 0))) / 100.0,
                    "implied_volatility": opt.get("implied_volatility", opt.get("IV", 0)),
                    "underlying": symbol,
                    "source": "dhan",
                })

        df = pd.DataFrame(rows) if rows else pd.DataFrame()
        return df, spot
    except Exception:
        return pd.DataFrame(), 0.0
