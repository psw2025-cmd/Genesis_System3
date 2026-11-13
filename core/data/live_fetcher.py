"""
live_fetcher.py — Authoritative DhanHQ Live Price Fetcher.
Replaces legacy crypto/Binance stub with real Dhan marketfeed & option-chain spot lookup.
Paper-mode safe: read-only quote retrieval only; never places orders.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Dict

IST = timezone(timedelta(hours=5, minutes=30))


def get_live_price(symbol: str = "NIFTY") -> Dict[str, Any]:
    """Return authoritative Dhan live spot quote for an index or F&O equity symbol."""
    sym = str(symbol or "NIFTY").strip().upper()
    if sym in ("BTCUSDT", "BTC-USD", "CRYPTO"):
        sym = "NIFTY"

    now_ist = datetime.now(IST).isoformat()
    last_err = ""

    # 1. Primary path: Dhan marketfeed index board
    try:
        from core.brokers.dhan.market_ltp import INDEX_SECURITY_IDS, build_index_board

        if sym in INDEX_SECURITY_IDS:
            board = build_index_board(symbols=[sym])
            for row in board.get("indices") or []:
                if str(row.get("symbol") or "").upper() == sym and row.get("ltp") is not None:
                    ltp_val = float(row["ltp"])
                    return {
                        "symbol": sym,
                        "spot": ltp_val,
                        "ltp": ltp_val,
                        "change": float(row.get("change") or 0.0),
                        "change_pct": float(row.get("change_pct") or 0.0),
                        "source": "DHAN_LIVE",
                        "timestamp": board.get("generated_at") or now_ist,
                        "status": "SUCCESS",
                    }
    except Exception as exc:
        last_err = str(exc)

    # 2. Secondary path: Read-only option chain snapshot spot
    try:
        from core.brokers.dhan.option_chain import fetch_option_chain_snapshot

        snap = fetch_option_chain_snapshot(sym)
        if isinstance(snap, dict) and snap.get("spot"):
            spot_val = float(snap["spot"])
            return {
                "symbol": sym,
                "spot": spot_val,
                "ltp": spot_val,
                "change": float(snap.get("change") or 0.0),
                "change_pct": float(snap.get("change_pct") or 0.0),
                "source": "DHAN_CHAIN_SNAPSHOT",
                "timestamp": snap.get("timestamp") or now_ist,
                "status": "SUCCESS",
            }
    except Exception as exc:
        if not last_err:
            last_err = str(exc)

    return {
        "symbol": sym,
        "spot": 0.0,
        "ltp": 0.0,
        "change": 0.0,
        "change_pct": 0.0,
        "source": "DHAN_UNAVAILABLE",
        "timestamp": now_ist,
        "status": "ERROR",
        "error": last_err or f"No live Dhan quote available for {sym}",
    }
