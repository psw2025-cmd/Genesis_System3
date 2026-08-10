"""Multibagger equity screener — REAL data only (Dhan /v2/charts/historical).

Universe: NSE F&O equity underlyings (from Dhan security master — real OPTSTK list).
Metrics: 1Y/6M/3M returns, 52-week-high distance, volume expansion, 200DMA trend,
max drawdown — composed into a momentum multibagger score (0-100).
NEVER fabricates data: returns status=NOT_READY with the exact reason when the
token or security master is unavailable.
"""
from __future__ import annotations

import csv
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
SECURITY_MASTER = ROOT / "security_id_list.csv"
STATE_FILE = ROOT / "state" / "multibagger_screen.json"
HIST_URL = "https://api.dhan.co/v2/charts/historical"

_LOCK = threading.Lock()
_CACHE: Dict[str, Any] = {"generated_at_epoch": 0.0, "result": None}
_CACHE_TTL_S = 6 * 3600
_EQ_ID_MAP: Optional[Dict[str, str]] = None

METHODOLOGY = {
    "universe": "NSE F&O equity underlyings (Dhan security master, OPTSTK)",
    "data": "Dhan /v2/charts/historical daily candles (~400 trading days)",
    "score_weights": {
        "return_1y": 0.25,
        "return_6m": 0.20,
        "return_3m": 0.15,
        "near_52w_high": 0.15,
        "volume_expansion": 0.15,
        "above_200dma": 0.10,
    },
    "note": "Momentum-based multibagger candidate ranking. Research only — not advice.",
}


def _load_eq_id_map() -> Dict[str, str]:
    global _EQ_ID_MAP
    if _EQ_ID_MAP is not None:
        return _EQ_ID_MAP
    mapping: Dict[str, str] = {}
    if SECURITY_MASTER.exists():
        with open(SECURITY_MASTER, newline="", encoding="utf-8", errors="replace") as f:
            for row in csv.DictReader(f):
                if (
                    (row.get("SEM_EXM_EXCH_ID") or "").strip().upper() == "NSE"
                    and (row.get("SEM_INSTRUMENT_NAME") or "").strip().upper() == "EQUITY"
                    and (row.get("SEM_SEGMENT") or "").strip().upper() == "E"
                ):
                    sym = (row.get("SEM_TRADING_SYMBOL") or "").strip().upper()
                    sid = (row.get("SEM_SMST_SECURITY_ID") or "").strip()
                    if sym and sid:
                        mapping.setdefault(sym, sid)
    _EQ_ID_MAP = mapping
    return mapping


def _fo_equity_universe() -> List[str]:
    from core.brokers.dhan.equity_fo_universe import load_equity_fo_universe

    data = load_equity_fo_universe()
    syms = [str(s).upper() for s in (data.get("underlyings") or []) if s]
    return sorted(set(syms))


def _access_headers() -> Optional[Dict[str, str]]:
    try:
        from core.brokers.dhan.cloud_token_provider import get_access_token

        token = get_access_token(reason="multibagger_screen")
    except Exception:
        import os

        token = os.environ.get("DHAN_ACCESS_TOKEN", "").strip()
    if not token:
        return None
    return {"access-token": token, "Content-Type": "application/json"}


def _fetch_daily(security_id: str, headers: Dict[str, str], days: int = 430) -> Optional[Dict[str, list]]:
    import requests

    to_d = datetime.now(timezone.utc).date()
    from_d = to_d - timedelta(days=days)
    body = {
        "securityId": str(security_id),
        "exchangeSegment": "NSE_EQ",
        "instrument": "EQUITY",
        "expiryCode": 0,
        "oi": False,
        "fromDate": from_d.isoformat(),
        "toDate": to_d.isoformat(),
    }
    resp = requests.post(HIST_URL, json=body, headers=headers, timeout=12)
    if resp.status_code != 200:
        return None
    data = resp.json()
    closes = data.get("close") or []
    if len(closes) < 120:
        return None
    return data


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _score_symbol(symbol: str, candles: Dict[str, list]) -> Dict[str, Any]:
    closes = [float(c) for c in candles["close"]]
    volumes = [float(v) for v in (candles.get("volume") or [0] * len(closes))]
    n = len(closes)
    last = closes[-1]

    def ret(days: int) -> Optional[float]:
        idx = n - 1 - days
        if idx < 0 or closes[idx] <= 0:
            return None
        return (last / closes[idx] - 1.0) * 100.0

    ret_1y = ret(min(250, n - 1))
    ret_6m = ret(125)
    ret_3m = ret(63)
    high_52w = max(closes[-min(250, n):])
    pct_from_52w_high = (last / high_52w - 1.0) * 100.0 if high_52w > 0 else None
    vol_recent = sum(volumes[-20:]) / 20.0 if len(volumes) >= 20 else 0.0
    vol_base = sum(volumes[-200:-20]) / max(1, len(volumes[-200:-20])) if len(volumes) >= 60 else 0.0
    vol_expansion = (vol_recent / vol_base) if vol_base > 0 else None
    dma_200 = sum(closes[-min(200, n):]) / min(200, n)
    above_200dma = last > dma_200
    peak = closes[0]
    max_dd = 0.0
    for c in closes[-min(250, n):]:
        peak = max(peak, c)
        if peak > 0:
            max_dd = min(max_dd, (c / peak - 1.0) * 100.0)

    s = (
        0.25 * _clamp01(((ret_1y or 0.0) + 20.0) / 120.0)
        + 0.20 * _clamp01(((ret_6m or 0.0) + 10.0) / 70.0)
        + 0.15 * _clamp01(((ret_3m or 0.0) + 10.0) / 50.0)
        + 0.15 * _clamp01(1.0 + (pct_from_52w_high or -100.0) / 25.0)
        + 0.15 * _clamp01(((vol_expansion or 0.0) - 0.5) / 2.0)
        + 0.10 * (1.0 if above_200dma else 0.0)
    )
    return {
        "symbol": symbol,
        "score": round(s * 100.0, 1),
        "close": round(last, 2),
        "return_1y_pct": round(ret_1y, 1) if ret_1y is not None else None,
        "return_6m_pct": round(ret_6m, 1) if ret_6m is not None else None,
        "return_3m_pct": round(ret_3m, 1) if ret_3m is not None else None,
        "pct_from_52w_high": round(pct_from_52w_high, 1) if pct_from_52w_high is not None else None,
        "volume_expansion_x": round(vol_expansion, 2) if vol_expansion is not None else None,
        "above_200dma": above_200dma,
        "max_drawdown_1y_pct": round(max_dd, 1),
        "candles_used": n,
    }


def run_screen(scan_limit: int = 60, top: int = 25, force_refresh: bool = False) -> Dict[str, Any]:
    now = time.time()
    with _LOCK:
        cached = _CACHE.get("result")
        if (
            cached
            and not force_refresh
            and now - float(_CACHE.get("generated_at_epoch") or 0) < _CACHE_TTL_S
        ):
            out = dict(cached)
            out["cache_hit"] = True
            out["rows"] = out.get("rows", [])[:top]
            return out

    headers = _access_headers()
    if not headers:
        return {
            "status": "NOT_READY",
            "reason": "DHAN_ACCESS_TOKEN unavailable — screener needs live broker data (no fake data will be shown)",
            "rows": [],
            "data_source": "dhan_charts_historical",
            "methodology": METHODOLOGY,
        }
    id_map = _load_eq_id_map()
    if not id_map:
        return {
            "status": "NOT_READY",
            "reason": "security_id_list.csv missing — cannot map symbols to NSE_EQ security IDs",
            "rows": [],
            "data_source": "dhan_charts_historical",
            "methodology": METHODOLOGY,
        }

    universe = _fo_equity_universe()
    scan = [s for s in universe if s in id_map][: max(10, min(scan_limit, 150))]

    rows: List[Dict[str, Any]] = []
    errors = 0

    def _work(sym: str) -> Optional[Dict[str, Any]]:
        try:
            candles = _fetch_daily(id_map[sym], headers)
            if not candles:
                return None
            return _score_symbol(sym, candles)
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_work, sym): sym for sym in scan}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                rows.append(r)
            else:
                errors += 1

    rows.sort(key=lambda r: r["score"], reverse=True)
    for i, r in enumerate(rows, 1):
        r["rank"] = i

    try:
        from fo_eligibility_filter import FOEligibilityFilter
    except ImportError:
        from dashboard.backend.fo_eligibility_filter import FOEligibilityFilter
    filt = FOEligibilityFilter()
    try:
        filt.bootstrap_universe()
    except Exception:
        pass
    for r in rows:
        ok, reason = filt.is_eligible(r["symbol"])
        r["fo_eligible"] = ok
        r["fo_reason"] = reason

    result = {
        "status": "OK" if rows else "NO_DATA",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "universe_size": len(universe),
        "scanned": len(scan),
        "succeeded": len(rows),
        "errors": errors,
        "rows": rows,
        "data_source": "dhan_charts_historical",
        "cache_hit": False,
        "cache_ttl_s": _CACHE_TTL_S,
        "methodology": METHODOLOGY,
        "live_trading_enabled": False,
    }
    if rows:
        with _LOCK:
            _CACHE["result"] = result
            _CACHE["generated_at_epoch"] = now
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            STATE_FILE.write_text(json.dumps(result, default=str))
        except OSError:
            pass
    out = dict(result)
    out["rows"] = rows[:top]
    return out
