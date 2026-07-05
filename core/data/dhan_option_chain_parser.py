"""
DhanHQ option-chain response parser.

Maps official Dhan leg fields to a normalized row dict. Computes derived fields
change_in_oi and bid_ask_spread. Does not expect non-Dhan aliases (bid, ask,
oi_change, flat greeks on leg).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

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


def parse_dhan_option_chain_payload(
    payload: Any,
) -> Tuple[pd.DataFrame, float]:
    """
    Parse Dhan option_chain API response.

    Accepts full response dict or bare list of strike rows.
    Returns (DataFrame, spot_price).
    """
    rows: List[Dict[str, Any]] = []
    spot = 0.0

    if isinstance(payload, dict):
        data = payload.get("data", payload)
        if isinstance(data, dict):
            items = data.get("data", [])
            spot = _safe_float(data.get("last_price", spot))
        else:
            items = data if isinstance(data, list) else []
    elif isinstance(payload, list):
        items = payload
    else:
        items = []

    for item in items:
        if not isinstance(item, dict):
            continue
        spot = _safe_float(item.get("last_price", spot))
        strike = _safe_float(item.get("strike_price", 0))
        for opt_type, key in [("CE", "ce"), ("PE", "pe")]:
            leg = item.get(key)
            if isinstance(leg, dict) and leg:
                rows.append(parse_dhan_leg(leg, strike, opt_type))

    return (pd.DataFrame(rows), spot) if rows else (pd.DataFrame(), spot)

def parse_option_chain_to_df(resp: Dict[str, Any], symbol: str) -> tuple:
    """
    Parse Dhan option chain response into (DataFrame, spot_price) tuple.
    Backward-compatible with chain_adapter.py which expects this format.
    """
    try:
        import pandas as pd
        data = resp.get("data", {})
        spot = float(data.get("last_price", 0) or data.get("spot_price", 0) or 0)
        options = data.get("oc", data.get("options_chain", []))
        
        if not options and isinstance(data, dict):
            # Try to find option data in nested structure
            for key in data:
                if isinstance(data[key], list) and len(data[key]) > 0:
                    options = data[key]
                    break
        
        if not options:
            return pd.DataFrame(), spot
        
        rows = []
        for opt in options:
            if isinstance(opt, dict):
                rows.append({
                    "strike": opt.get("strike_price", opt.get("SP", 0)),
                    "option_type": opt.get("option_type", opt.get("OT", "")),
                    "oi": opt.get("oi", opt.get("OI", 0)),
                    "volume": opt.get("volume", opt.get("VOL", 0)),
                    "ltp": opt.get("last_price", opt.get("LTP", 0)),
                    "bid": opt.get("bid_price", opt.get("BP", 0)),
                    "ask": opt.get("ask_price", opt.get("AP", 0)),
                    "iv": opt.get("implied_volatility", opt.get("IV", 0)),
                    "change_in_oi": opt.get("change_in_oi", opt.get("COI", 0)),
                    "underlying": symbol,
                })
        
        df = pd.DataFrame(rows) if rows else pd.DataFrame()
        return df, spot
    except Exception as e:
        import pandas as pd
        return pd.DataFrame(), 0.0
