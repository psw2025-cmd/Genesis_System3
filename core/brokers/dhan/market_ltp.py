"""
Dhan marketfeed LTP/OHLC helpers (read-only).

Used for Dhan-parity live index ribbon (Nifty/Bank/Fin/VIX) and
enriching open positions when /positions omits lastTradedPrice.
Never places orders.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

logger = logging.getLogger("dhan_market_ltp")

# Official IDX_I security IDs (DhanHQ docs / instrument master)
INDEX_SECURITY_IDS: Dict[str, str] = {
    "NIFTY": "13",
    "BANKNIFTY": "25",
    "INDIAVIX": "26",
    "FINNIFTY": "27",
    "MIDCPNIFTY": "442",
    "SENSEX": "51",
}

INDEX_LABELS: Dict[str, str] = {
    "NIFTY": "Nifty 50",
    "BANKNIFTY": "Nifty Bank",
    "INDIAVIX": "India VIX",
    "FINNIFTY": "Fin Nifty",
    "MIDCPNIFTY": "Midcap Nifty",
    "SENSEX": "Sensex",
}

DEFAULT_INDEX_BOARD: Tuple[str, ...] = (
    "NIFTY",
    "BANKNIFTY",
    "FINNIFTY",
    "INDIAVIX",
    "MIDCPNIFTY",
)


def _as_float(val: Any) -> Optional[float]:
    try:
        if val is None or val == "":
            return None
        return float(val)
    except (TypeError, ValueError):
        return None


def _unwrap_feed(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    return payload


def _parse_quote_blob(blob: Any) -> Dict[str, Any]:
    if not isinstance(blob, dict):
        return {}
    ltp = _as_float(
        blob.get("last_price")
        or blob.get("lastPrice")
        or blob.get("LTP")
        or blob.get("ltp")
    )
    ohlc = blob.get("ohlc") if isinstance(blob.get("ohlc"), dict) else {}
    open_p = _as_float(blob.get("open") or ohlc.get("open"))
    high_p = _as_float(blob.get("high") or ohlc.get("high"))
    low_p = _as_float(blob.get("low") or ohlc.get("low"))
    close_p = _as_float(blob.get("close") or ohlc.get("close") or blob.get("prev_close"))
    change = _as_float(blob.get("net_change") or blob.get("change"))
    if change is None and ltp is not None and close_p not in (None, 0):
        change = ltp - close_p
    change_pct = None
    if change is not None and close_p not in (None, 0):
        change_pct = (change / close_p) * 100.0
    elif ltp is not None and close_p not in (None, 0):
        change_pct = ((ltp - close_p) / close_p) * 100.0
    return {
        "ltp": ltp,
        "open": open_p,
        "high": high_p,
        "low": low_p,
        "close": close_p,
        "change": change,
        "change_pct": change_pct,
    }


def fetch_market_quotes(securities: Mapping[str, Sequence[Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Batch OHLC/quote via Dhan marketfeed.

    Returns map keyed by security_id string -> quote fields.
    """
    if not securities:
        return {}
    cleaned: Dict[str, List[str]] = {}
    for seg, ids in securities.items():
        bucket: List[str] = []
        for sid in ids or []:
            s = str(sid).strip()
            if s and s not in bucket:
                bucket.append(s)
        if bucket:
            cleaned[str(seg)] = bucket
    if not cleaned:
        return {}

    try:
        from core.brokers.dhan.dhan_readonly import create_dhan_client
    except Exception as exc:
        logger.warning("market_ltp: cannot import create_dhan_client: %s", exc)
        return {}

    client = create_dhan_client()
    if client is None:
        return {}

    payload = None
    for method_name in ("ohlc_data", "quote_data", "ticker_data"):
        method = getattr(client, method_name, None)
        if not callable(method):
            continue
        try:
            payload = method(cleaned)
            if payload:
                break
        except Exception as exc:
            logger.info("market_ltp.%s failed: %s", method_name, exc)
            payload = None

    out: Dict[str, Dict[str, Any]] = {}
    data = _unwrap_feed(payload)
    # Shape A: { "IDX_I": { "13": {...} } }
    # Shape B: { "13": {...} }
    for key, val in data.items():
        if isinstance(val, dict) and any(
            isinstance(v, dict) and ("last_price" in v or "ohlc" in v or "LTP" in v or "ltp" in v)
            for v in val.values()
        ):
            for sid, blob in val.items():
                parsed = _parse_quote_blob(blob)
                if parsed.get("ltp") is not None:
                    out[str(sid)] = parsed
        else:
            parsed = _parse_quote_blob(val)
            if parsed.get("ltp") is not None:
                out[str(key)] = parsed
    return out


def build_index_board(symbols: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """Live index ribbon matching Dhan web (LTP + change %)."""
    wanted = [str(s).upper() for s in (symbols or DEFAULT_INDEX_BOARD)]
    sec_ids = [INDEX_SECURITY_IDS[s] for s in wanted if s in INDEX_SECURITY_IDS]
    quotes = fetch_market_quotes({"IDX_I": sec_ids}) if sec_ids else {}
    rows: List[Dict[str, Any]] = []
    for sym in wanted:
        sid = INDEX_SECURITY_IDS.get(sym)
        q = quotes.get(str(sid), {}) if sid else {}
        rows.append(
            {
                "symbol": sym,
                "label": INDEX_LABELS.get(sym, sym),
                "security_id": sid,
                "exchange_segment": "IDX_I",
                "ltp": q.get("ltp"),
                "change": q.get("change"),
                "change_pct": q.get("change_pct"),
                "close": q.get("close"),
                "live": q.get("ltp") is not None,
            }
        )
    live_n = sum(1 for r in rows if r.get("live"))
    return {
        "success": live_n > 0,
        "source": "dhan_marketfeed_ohlc",
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "count": len(rows),
        "live_count": live_n,
        "indices": rows,
    }


def enrich_positions_with_market_ltp(rows: Sequence[MutableMapping[str, Any]]) -> List[Dict[str, Any]]:
    """Fill missing position LTP from marketfeed; else derive from unrealized P&L."""
    need: Dict[str, List[str]] = {}
    for row in rows:
        try:
            if float(row.get("ltp") or 0) > 0:
                continue
        except (TypeError, ValueError):
            pass
        raw = row.get("raw") if isinstance(row.get("raw"), dict) else {}
        sid = str(raw.get("securityId") or row.get("security_id") or "").strip()
        seg = str(
            raw.get("exchangeSegment")
            or row.get("exchange_segment")
            or "NSE_FNO"
        ).strip() or "NSE_FNO"
        if not sid:
            continue
        need.setdefault(seg, [])
        if sid not in need[seg]:
            need[seg].append(sid)

    quotes = fetch_market_quotes(need) if need else {}
    out: List[Dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        try:
            cur = float(item.get("ltp") or 0)
        except (TypeError, ValueError):
            cur = 0.0
        if cur > 0:
            item.setdefault("ltp_source", "broker_positions")
            out.append(item)
            continue

        raw = item.get("raw") if isinstance(item.get("raw"), dict) else {}
        sid = str(raw.get("securityId") or item.get("security_id") or "").strip()
        q = quotes.get(sid) if sid else None
        if q and q.get("ltp") is not None:
            item["ltp"] = float(q["ltp"])
            item["ltp_source"] = "dhan_marketfeed"
            out.append(item)
            continue

        # Derive LTP from MTM when marketfeed unavailable (Dhan positions often omit LTP).
        try:
            qty = float(item.get("net_qty") or 0)
            avg = float(item.get("avg_price") or 0)
            upnl = float(item.get("unrealized_pnl") or 0)
        except (TypeError, ValueError):
            qty = avg = upnl = 0.0
        if qty:
            item["ltp"] = avg + (upnl / qty)
            item["ltp_source"] = "derived_from_unrealized"
        else:
            item["ltp_source"] = "missing"
        out.append(item)
    return out
