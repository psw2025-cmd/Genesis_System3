"""Deterministic market-like PAPER replay; never sends broker orders.

This is synthetic stress evidence, NOT live market or realized trade proof.
"""
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Iterable

@dataclass(frozen=True)
class MarketTick:
    timestamp: str
    bid: float
    ask: float
    available_qty: int
    source: str = "DHAN_REPLAY_SYNTHETIC"
    connected: bool = True

def replay_paper_buy(ticks: Iterable[MarketTick], qty: int, capital_limit: float = 50000.0,
                     max_quote_age_seconds: float = 3.0) -> dict:
    """Simulate a limit-free market BUY using available ask liquidity, fail-closed."""
    if (type(qty) is not int or qty <= 0 or not isfinite(capital_limit) or capital_limit <= 0 or
            not isfinite(max_quote_age_seconds) or max_quote_age_seconds <= 0):
        raise ValueError("PAPER_REPLAY_INVALID_RISK")
    remaining = qty
    fills = []
    last_time = None
    for tick in ticks:
        if tick.source != "DHAN_REPLAY_SYNTHETIC" or not tick.connected:
            return {"status": "BLOCKED_DISCONNECTED_OR_UNTRUSTED", "fills": fills, "filled_qty": qty-remaining, "remaining_qty": remaining}
        try:
            time = datetime.fromisoformat(tick.timestamp.replace("Z","+00:00"))
        except (ValueError, TypeError) as exc:
            raise ValueError("PAPER_REPLAY_INVALID_TIMESTAMP") from exc
        if time.tzinfo is None:
            raise ValueError("PAPER_REPLAY_NAIVE_TIMESTAMP")
        if last_time is not None:
            delta=(time-last_time).total_seconds()
            if delta <= 0 or delta > max_quote_age_seconds:
                return {"status":"BLOCKED_STALE_OR_OUT_OF_ORDER","fills":fills,"filled_qty":qty-remaining,"remaining_qty":remaining}
        last_time=time
        if (not isfinite(tick.bid) or not isfinite(tick.ask) or tick.bid <= 0 or
                tick.ask < tick.bid or type(tick.available_qty) is not int or tick.available_qty < 0):
            return {"status":"BLOCKED_INVALID_QUOTE","fills":fills,"filled_qty":qty-remaining,"remaining_qty":remaining}
        if tick.ask * qty > capital_limit:
            return {"status":"BLOCKED_CAPITAL_LIMIT","fills":fills,"filled_qty":qty-remaining,"remaining_qty":remaining}
        take=min(remaining,tick.available_qty)
        if take:
            fills.append({"timestamp":tick.timestamp,"qty":take,"price":tick.ask,
                          "mode":"SYNTHETIC_PAPER_FILL_NOT_BROKER"})
            remaining-=take
        if remaining == 0:
            break
    return {"status":"PAPER_FILLED" if remaining == 0 else "PAPER_PARTIAL",
            "fills":fills,"filled_qty":qty-remaining,"remaining_qty":remaining,
            "evidence":"SYNTHETIC_MARKET_REPLAY_NOT_LIVE"}

def replay_paper_sell(ticks: Iterable[MarketTick], qty: int, held_qty: int,
                      max_quote_age_seconds: float = 3.0) -> dict:
    """Close an existing synthetic long position at BID, never ASK.

    Does not create short exposure; never contacts broker or persists orders.
    """
    if (type(qty) is not int or qty <= 0 or type(held_qty) is not int or
            held_qty < qty or not isfinite(max_quote_age_seconds) or max_quote_age_seconds <= 0):
        raise ValueError("PAPER_REPLAY_INVALID_SELL_RISK")
    remaining, fills, last_time = qty, [], None
    for tick in ticks:
        if tick.source != "DHAN_REPLAY_SYNTHETIC" or not tick.connected:
            return {"status":"BLOCKED_DISCONNECTED_OR_UNTRUSTED","fills":fills,
                    "filled_qty":qty-remaining,"remaining_qty":remaining}
        try:
            at=datetime.fromisoformat(tick.timestamp.replace("Z","+00:00"))
        except (ValueError, TypeError) as exc:
            raise ValueError("PAPER_REPLAY_INVALID_TIMESTAMP") from exc
        if at.tzinfo is None:
            raise ValueError("PAPER_REPLAY_NAIVE_TIMESTAMP")
        if last_time is not None:
            gap=(at-last_time).total_seconds()
            if gap <= 0 or gap > max_quote_age_seconds:
                return {"status":"BLOCKED_STALE_OR_OUT_OF_ORDER","fills":fills,
                        "filled_qty":qty-remaining,"remaining_qty":remaining}
        last_time=at
        if (not isfinite(tick.bid) or not isfinite(tick.ask) or
                tick.bid <= 0 or tick.ask < tick.bid or
                type(tick.available_qty) is not int or tick.available_qty < 0):
            return {"status":"BLOCKED_INVALID_QUOTE","fills":fills,
                    "filled_qty":qty-remaining,"remaining_qty":remaining}
        take=min(remaining,tick.available_qty)
        if take:
            fills.append({"timestamp":tick.timestamp,"qty":take,"price":tick.bid,
                          "mode":"SYNTHETIC_PAPER_FILL_NOT_BROKER"})
            remaining-=take
        if remaining==0:
            break
    return {"status":"PAPER_FILLED" if remaining==0 else "PAPER_PARTIAL",
            "fills":fills,"filled_qty":qty-remaining,"remaining_qty":remaining,
            "evidence":"SYNTHETIC_MARKET_REPLAY_NOT_LIVE"}
