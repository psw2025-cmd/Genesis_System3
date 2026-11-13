"""Dhan-only, read-only index quote adapter used by the legacy route."""

from datetime import datetime, timezone
from typing import Any, Dict


def get_live_price(symbol="NIFTY") -> Dict[str, Any]:
    """Return an index quote without inventing a source timestamp or freshness."""
    from core.brokers.dhan.market_ltp import (
        INDEX_SECURITY_IDS,
        classify_quote_freshness,
        fetch_market_quotes,
    )

    normalized = str(symbol or "").strip().upper()
    security_id = INDEX_SECURITY_IDS.get(normalized)
    retrieval_time = datetime.now(timezone.utc).isoformat()
    if not security_id:
        return {
            "symbol": normalized,
            "spot": 0.0,
            "ltp": 0.0,
            "source": "NONE",
            "status": "UNSUPPORTED_SYMBOL",
            "freshness": "UNVERIFIED",
            "timestamp": retrieval_time,
            "retrieved_at_utc": retrieval_time,
        }

    quotes = fetch_market_quotes({"IDX_I": [security_id]})
    quote = quotes.get(security_id) or {}
    try:
        ltp = float(quote.get("ltp") or 0.0)
    except (TypeError, ValueError):
        ltp = 0.0
    source_timestamp = quote.get("source_timestamp")
    freshness = classify_quote_freshness(source_timestamp)
    return {
        "symbol": normalized,
        "spot": ltp,
        "ltp": ltp,
        "change": quote.get("change"),
        "change_pct": quote.get("change_pct"),
        "source": "DHAN_MARKETFEED" if ltp > 0 else "DHAN_UNAVAILABLE",
        "status": freshness["status"] if ltp > 0 else "UNAVAILABLE",
        "freshness": freshness["status"],
        "source_timestamp": source_timestamp,
        "age_seconds": freshness["age_seconds"],
        "timestamp": retrieval_time,
        "retrieved_at_utc": retrieval_time,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
