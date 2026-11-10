import pytest
from backend.simulation.market_replay_engine import (
    DeterministicMarketSimulator,
    TickEvent,
)


def test_e2e_open_session_market_and_limit_fills():
    sim = DeterministicMarketSimulator(stale_threshold_sec=15.0)
    tick1 = TickEvent(
        symbol="NIFTY26NOV24500CE",
        ltp=145.50,
        volume=12500,
        timestamp_ns=1730951700000000000,
        bid=145.25,
        ask=145.75,
        is_market_open=True,
    )
    sim.ingest_tick(tick1, current_clock_sec=1000.0)

    mkt_order = sim.place_order("NIFTY26NOV24500CE", "BUY", "MARKET", quantity=75, current_clock_sec=1001.0)
    assert mkt_order.status == "FILLED"
    assert mkt_order.filled_price == 145.75

    lim_order = sim.place_order("NIFTY26NOV24500CE", "BUY", "LIMIT", quantity=75, price=140.00, current_clock_sec=1002.0)
    assert lim_order.status == "PENDING"

    tick2 = TickEvent(
        symbol="NIFTY26NOV24500CE",
        ltp=139.80,
        volume=18900,
        timestamp_ns=1730951760000000000,
        bid=139.65,
        ask=139.90,
        is_market_open=True,
    )
    sim.ingest_tick(tick2, current_clock_sec=1005.0)
    assert lim_order.status == "FILLED"
    assert lim_order.filled_price == 139.90


def test_after_market_hours_shows_both_market_closed_and_authentic_ltp():
    sim = DeterministicMarketSimulator()
    closing_tick = TickEvent(
        symbol="BANKNIFTY26NOV52000PE",
        ltp=312.45,
        volume=450000,
        timestamp_ns=1730973600000000000,
        bid=312.10,
        ask=312.80,
        is_market_open=False,
    )
    snapshot = sim.ingest_tick(closing_tick, current_clock_sec=2000.0)
    assert snapshot["market_status"] == "CLOSED"
    assert snapshot["display_banner"] == "Market Closed"
    assert snapshot["ltp"] == 312.45


def test_fail_closed_gate_blocks_orders_on_stale_feed():
    sim = DeterministicMarketSimulator(stale_threshold_sec=10.0)
    tick = TickEvent(
        symbol="NIFTY26NOV24500CE",
        ltp=150.0,
        volume=1000,
        timestamp_ns=1730951700000000000,
        bid=149.8,
        ask=150.2,
        is_market_open=True,
    )
    sim.ingest_tick(tick, current_clock_sec=100.0)
    rejected = sim.place_order("NIFTY26NOV24500CE", "BUY", "MARKET", quantity=75, current_clock_sec=125.0)
    assert rejected.status == "REJECTED"
    assert rejected.rejection_reason == "FAIL_CLOSED_STALE_FEED"


def test_fail_closed_rejects_corrupted_or_zero_ltp():
    sim = DeterministicMarketSimulator()
    bad_tick = TickEvent(
        symbol="NIFTY26NOV24500CE",
        ltp=0.0,
        volume=100,
        timestamp_ns=1730951700000000000,
        bid=0.0,
        ask=0.0,
        is_market_open=True,
    )
    with pytest.raises(ValueError, match="FAIL_CLOSED_GATE_INVALID_LTP"):
        sim.ingest_tick(bad_tick)


def test_rate_limit_429_chaos_injection():
    sim = DeterministicMarketSimulator()
    tick = TickEvent(
        symbol="NIFTY26NOV24500CE",
        ltp=150.0,
        volume=1000,
        timestamp_ns=1730951700000000000,
        bid=149.8,
        ask=150.2,
        is_market_open=True,
    )
    sim.ingest_tick(tick, current_clock_sec=500.0)
    sim.force_rate_limit(True)
    order = sim.place_order("NIFTY26NOV24500CE", "BUY", "MARKET", quantity=75, current_clock_sec=501.0)
    assert order.status == "REJECTED"
    assert order.rejection_reason == "HTTP_429_RATE_LIMIT"