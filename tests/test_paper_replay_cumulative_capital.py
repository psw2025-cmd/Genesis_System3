"""Aggregate synthetic fill cost must never exceed the PAPER capital ceiling."""
from datetime import datetime, timedelta, timezone

from dashboard.backend.paper_market_replay import MarketTick, replay_paper_buy


def test_rising_ask_blocks_second_partial_fill_without_erasing_first():
    t = datetime(2026, 11, 7, 9, 15, tzinfo=timezone.utc)
    ticks = [
        MarketTick(t.isoformat(), 90.0, 100.0, 1),
        MarketTick((t + timedelta(seconds=1)).isoformat(), 110.0, 120.0, 1),
    ]
    result = replay_paper_buy(ticks, qty=2, capital_limit=210.0)
    assert result["status"] == "BLOCKED_CAPITAL_LIMIT"
    assert result["filled_qty"] == 1
    assert result["remaining_qty"] == 1
    assert result["fills"][0]["price"] == 100.0
    assert result["fills"][0]["mode"] == "SYNTHETIC_PAPER_FILL_NOT_BROKER"


def test_aggregate_cap_allows_fills_within_conservative_ceiling():
    t = datetime(2026, 11, 7, 9, 15, tzinfo=timezone.utc)
    ticks = [
        MarketTick(t.isoformat(), 90.0, 100.0, 1),
        MarketTick((t + timedelta(seconds=1)).isoformat(), 110.0, 120.0, 1),
    ]
    result = replay_paper_buy(ticks, qty=2, capital_limit=240.0)
    assert result["status"] == "PAPER_FILLED"
    assert result["filled_qty"] == 2
    assert sum(f["qty"] * f["price"] for f in result["fills"]) == 220.0
