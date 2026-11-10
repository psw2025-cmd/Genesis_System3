"""Repeated market tick timestamps must never mint duplicate synthetic liquidity."""
from datetime import datetime, timezone
import pytest
from dashboard.backend.paper_market_replay import MarketTick, replay_paper_buy, replay_paper_sell

T = datetime(2026, 11, 7, 9, 15, tzinfo=timezone.utc).isoformat()

@pytest.mark.parametrize("side", ["BUY", "SELL"])
def test_duplicate_timestamp_fails_closed_without_double_filling(side):
    ticks = [MarketTick(T, 99.0, 100.0, 1), MarketTick(T, 99.0, 100.0, 1)]
    result = (replay_paper_buy(ticks, 2) if side == "BUY"
              else replay_paper_sell(ticks, 2, held_qty=2))
    assert result["status"] == "BLOCKED_STALE_OR_OUT_OF_ORDER"
    assert result["filled_qty"] == 1
    assert result["remaining_qty"] == 1
    assert len(result["fills"]) == 1
    assert result["fills"][0]["mode"] == "SYNTHETIC_PAPER_FILL_NOT_BROKER"
