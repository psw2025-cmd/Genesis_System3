"""The public price route must not turn a cached chain snapshot into a live tick."""

import asyncio
from datetime import datetime, timedelta, timezone

import dashboard.backend.app as app_module
from dashboard.backend.app import _live_price_truth


def test_cached_chain_price_is_not_live():
    result = _live_price_truth(
        "NIFTY",
        {"ltp": 25044.65, "source": "paced_chain_cache", "live": False,
         "data_status": "CACHED_UNVERIFIED", "freshness": "UNVERIFIED"},
        datetime.now(timezone.utc).isoformat(),
    )
    assert result["status"] == "UNVERIFIED"
    assert result["ltp"] is None
    assert result["last_known_ltp"] == 25044.65
    assert result["source"] == "paced_chain_cache"


def test_recent_exchange_tick_can_be_live():
    exchange_time = datetime.now(timezone.utc).isoformat()
    result = _live_price_truth(
        "NIFTY",
        {"ltp": 25100.25, "source": "dhan_marketfeed", "live": True,
         "data_status": "BROKER_QUOTE", "exchange_timestamp": exchange_time},
    )
    assert result["status"] == "SUCCESS"
    assert result["ltp"] == 25100.25
    assert result["source"] == "DHAN_LIVE"
    assert result["tick_age_sec"] <= 60


def test_old_exchange_tick_is_stale():
    exchange_time = (datetime.now(timezone.utc) - timedelta(seconds=90)).isoformat()
    result = _live_price_truth(
        "NIFTY",
        {"ltp": 25100.25, "source": "dhan_marketfeed", "live": True,
         "data_status": "BROKER_QUOTE", "exchange_timestamp": exchange_time},
    )
    assert result["status"] == "STALE"
    assert result["ltp"] is None
    assert result["last_known_ltp"] == 25100.25


def test_fetch_time_is_not_exchange_time():
    result = _live_price_truth(
        "NIFTY",
        {"ltp": 25100.25, "source": "DHAN_CHAIN_SNAPSHOT",
         "timestamp": datetime.now(timezone.utc).isoformat(), "status": "SUCCESS"},
    )
    assert result["status"] == "UNVERIFIED"
    assert result["ltp"] is None


def test_public_route_does_not_upgrade_cached_chain_price(monkeypatch):
    cached = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "indices": [{"symbol": "NIFTY", "ltp": 25044.65,
                     "source": "paced_chain_cache", "live": False,
                     "data_status": "CACHED_UNVERIFIED"}],
        "equities": [],
    }
    monkeypatch.setattr(app_module, "_cache_get", lambda key, ttl: cached)
    result = asyncio.run(app_module.get_live_price_endpoint("NIFTY"))
    assert result["status"] == "UNVERIFIED"
    assert result["ltp"] is None
    assert result["last_known_ltp"] == 25044.65
