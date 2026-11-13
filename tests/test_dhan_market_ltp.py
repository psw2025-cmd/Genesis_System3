"""Tests for Dhan marketfeed LTP helpers and position enrichment."""

import threading
import ast
import inspect
import asyncio
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

import pytest

import core.brokers.dhan.market_ltp as market_ltp
from core.brokers.dhan.market_ltp import (
    INDEX_SECURITY_IDS,
    _parse_quote_blob,
    _reset_marketfeed_coordination_for_tests,
    _rest_marketfeed,
    enrich_positions_with_market_ltp,
    fetch_market_quotes,
)


def test_parse_quote_blob_change_pct():
    parsed = _parse_quote_blob({"last_price": 24320.0, "ohlc": {"close": 24395.85}})
    assert parsed["ltp"] == 24320.0
    assert abs(parsed["change"] - (24320.0 - 24395.85)) < 1e-6
    assert parsed["change_pct"] is not None
    assert parsed["change_pct"] < 0


def test_india_vix_security_id():
    assert INDEX_SECURITY_IDS["INDIAVIX"] == "26"
    assert INDEX_SECURITY_IDS["NIFTY"] == "13"
    assert INDEX_SECURITY_IDS["BANKNIFTY"] == "25"
    assert INDEX_SECURITY_IDS["FINNIFTY"] == "27"


def test_enrich_positions_derives_ltp_from_unrealized(monkeypatch):
    monkeypatch.setattr(
        "core.brokers.dhan.market_ltp.fetch_market_quotes",
        lambda securities: {},
    )
    rows = enrich_positions_with_market_ltp(
        [
            {
                "symbol": "POWERGRID-Aug2026-280-CE",
                "net_qty": 3800.0,
                "avg_price": 1.54545,
                "ltp": 0.0,
                "unrealized_pnl": -3022.71,
                "raw": {"securityId": "138976", "exchangeSegment": "NSE_FNO"},
            }
        ]
    )
    assert len(rows) == 1
    assert rows[0]["ltp_source"] == "derived_from_unrealized"
    assert abs(rows[0]["ltp"] - 0.75) < 0.01


def test_enrich_positions_prefers_marketfeed(monkeypatch):
    monkeypatch.setattr(
        "core.brokers.dhan.market_ltp.fetch_market_quotes",
        lambda securities: {"138976": {"ltp": 0.70, "change_pct": -10.0}},
    )
    rows = enrich_positions_with_market_ltp(
        [
            {
                "symbol": "POWERGRID-Aug2026-280-CE",
                "net_qty": 3800.0,
                "avg_price": 1.54545,
                "ltp": 0.0,
                "unrealized_pnl": -3022.71,
                "raw": {"securityId": "138976", "exchangeSegment": "NSE_FNO"},
            }
        ]
    )
    assert rows[0]["ltp"] == 0.70
    assert rows[0]["ltp_source"] == "dhan_marketfeed"


def test_build_index_board_uses_fallback(monkeypatch):
    monkeypatch.setattr(
        "core.brokers.dhan.market_ltp.fetch_market_quotes",
        lambda securities: {},
    )
    from core.brokers.dhan.market_ltp import build_index_board

    board = build_index_board(
        symbols=["NIFTY", "INDIAVIX"],
        fallback_spots={"NIFTY": {"spot": 24320.55, "change_pct": -0.31, "source": "paced_chain_cache"}},
    )
    assert board["success"] is False
    nifty = next(r for r in board["indices"] if r["symbol"] == "NIFTY")
    assert nifty["ltp"] == 24320.55
    assert nifty["source"] == "paced_chain_cache"
    assert nifty["live"] is False
    assert nifty["change_pct"] is None
    assert nifty["data_status"] == "CACHED_UNVERIFIED"


def test_cached_video_spot_cannot_borrow_september_daily_percentage(monkeypatch):
    def forbidden_fetch(_):
        raise AssertionError("prefetched source miss must not refetch")

    monkeypatch.setattr(market_ltp, "fetch_market_quotes", forbidden_fetch)
    video_spot, september_close = 25225.80, 23398.10
    old_pct = (video_spot - september_close) / september_close * 100
    assert round(old_pct, 2) == 7.81
    board = market_ltp.build_index_board(
        symbols=["NIFTY"], prefetched_quotes={},
        fallback_spots={"NIFTY": {"spot": video_spot, "prev_close": september_close,
                                   "change_pct": old_pct, "source": "paced_chain_cache"}},
    )
    row = board["indices"][0]
    assert row["ltp"] == video_spot
    assert row["live"] is False
    assert row["close"] is None
    assert row["change"] is None
    assert row["change_pct"] is None
    assert board["live_count"] == 0


def test_prefetched_quote_uses_its_own_denominator_and_never_refetches(monkeypatch):
    monkeypatch.setattr(market_ltp, "fetch_market_quotes", lambda _: pytest.fail("duplicate fetch"))
    board = market_ltp.build_index_board(
        symbols=["NIFTY"],
        prefetched_quotes={"13": {"ltp": 25225.80, "close": 25255.05,
                                  "change": 1827.70, "change_pct": 7.81}},
        fallback_spots={"NIFTY": {"spot": 23118.60, "change_pct": -1.19}},
    )
    row = board["indices"][0]
    assert row["change"] == pytest.approx(25225.80 - 25255.05)
    assert row["change_pct"] == pytest.approx((25225.80 - 25255.05) / 25255.05 * 100)
    assert row["change_pct"] < 0
    assert row["change_provenance"] == "SAME_QUOTE_CLOSE"
    assert row["freshness"] == "UNVERIFIED"


def test_real_zero_percent_not_overridden_by_old_fallback():
    row = market_ltp.build_index_board(
        symbols=["NIFTY"],
        prefetched_quotes={"13": {"ltp": 25225.80, "close": 25225.80, "change": 0, "change_pct": 0}},
        fallback_spots={"NIFTY": {"spot": 25225.80, "prev_close": 23398.10, "change_pct": 7.81}},
    )["indices"][0]
    assert row["change"] == 0
    assert row["change_pct"] == 0


@pytest.mark.parametrize("close", [None, 0, -1, float("nan"), float("inf"), "invalid", True, 1e-320])
def test_unverified_denominator_never_publishes_daily_percentage(close):
    row = market_ltp.build_index_board(
        symbols=["NIFTY"],
        prefetched_quotes={"13": {"ltp": 25225.80, "close": close, "change_pct": 7.81}},
    )["indices"][0]
    assert row["change_pct"] is None
    assert row["change_provenance"] == "UNVERIFIED"
    parsed = _parse_quote_blob({"last_price": 25225.80, "ohlc": {"close": close}})
    assert parsed["change_pct"] is None


def test_live_board_route_matches_adapter_and_has_no_historical_baseline_calls():
    source = (Path(__file__).resolve().parents[1] / "dashboard/backend/app.py").read_text(encoding="utf-8-sig")
    route = next(n for n in ast.parse(source).body if isinstance(n, ast.AsyncFunctionDef) and n.name == "get_market_live_board")
    calls = [n for n in ast.walk(route) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    assert not {"get_previous_close", "get_index_baseline"}.intersection(n.func.id for n in calls)
    board_call = next(n for n in calls if n.func.id == "build_index_board")
    kwargs = {kw.arg: {} for kw in board_call.keywords}
    inspect.signature(market_ltp.build_index_board).bind(**kwargs)


@pytest.mark.parametrize("quote", [{}, {"13": {"ltp": 25225.80, "close": 25255.05}}])
def test_actual_route_build_reuses_single_batch_without_old_close(monkeypatch, quote):
    # Execute only this trusted route AST: importing the whole app starts unrelated
    # bootstrap paths. Every provider dependency below is a strict offline stub.
    source = (Path(__file__).resolve().parents[1] / "dashboard/backend/app.py").read_text(encoding="utf-8-sig")
    route = next(n for n in ast.parse(source).body if isinstance(n, ast.AsyncFunctionDef) and n.name == "get_market_live_board")
    route.decorator_list = []
    module = ast.fix_missing_locations(ast.Module(body=[route], type_ignores=[]))
    calls = []

    def fetch(securities):
        calls.append(securities)
        return quote

    monkeypatch.setattr(market_ltp, "fetch_market_quotes", fetch)
    monkeypatch.setitem(sys.modules, "core.brokers.dhan.dhan_readonly",
                        types.SimpleNamespace(get_holdings=lambda: {"data": []}))

    async def run_blocking(fn, timeout):
        return fn()

    namespace = {
        "_cache_get": lambda *args: None,
        "_cache_set": lambda key, value: value,
        "_run_blocking": run_blocking,
        "_TTL_CHAIN": 120,
        "_PUSHED_CHAIN_CACHE": {"NIFTY": {"data": {"spot": 25225.80, "change_pct": 7.81}}},
        "datetime": datetime, "IST": timezone.utc, "asyncio": asyncio,
    }
    exec(compile(module, "isolated_live_board_route", "exec"), namespace)
    result = asyncio.run(namespace["get_market_live_board"]())
    assert len(calls) == 1
    assert "error" not in result
    nifty = next(r for r in result["indices"] if r["symbol"] == "NIFTY")
    assert nifty["ltp"] == 25225.80
    if quote:
        assert nifty["change_pct"] < 0
        assert nifty["prev_close"] == 25255.05
    else:
        assert nifty["live"] is False
        assert nifty["change_pct"] is None
        assert nifty["prev_close"] is None


def test_rest_marketfeed_does_not_retry_alternate_body_after_429(monkeypatch):
    calls = []

    class Response:
        status_code = 429
        text = '{"data":{"805":"Too many requests. Further requests may result in the user being blocked."}}'

        def json(self):
            return {}

    def fake_post(url, headers, json, timeout):
        calls.append((url, json))
        return Response()

    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.setattr(
        "core.brokers.dhan.dhan_readonly.get_dhan_credentials",
        lambda: {"client_id": "masked-test-client", "access_token": "masked-test-token"},
    )

    payload, error = _rest_marketfeed(
        "https://api.dhan.co/v2/marketfeed/ohlc",
        {"IDX_I": ["13", "25"]},
    )
    assert payload is None
    assert error is not None and "HTTP_429" in error
    assert len(calls) == 1


def test_fetch_market_quotes_stops_endpoint_and_sdk_fallbacks_after_429(monkeypatch):
    _reset_marketfeed_coordination_for_tests()
    calls = []

    def fake_rest(url, securities):
        calls.append(url)
        return None, 'HTTP_429:{"data":{"805":"Too many requests"}}'

    monkeypatch.setattr(market_ltp, "_rest_marketfeed", fake_rest)
    result = fetch_market_quotes({"IDX_I": ["13", "25"]})

    assert result == {}
    assert len(calls) == 1
    assert calls[0].endswith("/marketfeed/ohlc")
    assert any("HTTP_429" in error for error in fetch_market_quotes.last_errors)
    assert fetch_market_quotes.last_meta["rate_limited"] is True
    assert fetch_market_quotes.last_meta["cooldown_remaining_s"] > 0


def test_fetch_market_quotes_positive_cache_avoids_repeat_provider_call(monkeypatch):
    _reset_marketfeed_coordination_for_tests()
    calls = []

    def fake_uncached(cleaned):
        calls.append(cleaned)
        return {"13": {"ltp": 24500.0}}, [], False

    monkeypatch.setattr(market_ltp, "_fetch_market_quotes_uncached", fake_uncached)

    first = fetch_market_quotes({"IDX_I": ["13"]})
    second = fetch_market_quotes({"IDX_I": ["13"]})

    assert first == second == {"13": {"ltp": 24500.0}}
    assert len(calls) == 1
    assert fetch_market_quotes.last_meta["cache_hit"] is True


def test_fetch_market_quotes_concurrent_same_key_singleflights(monkeypatch):
    _reset_marketfeed_coordination_for_tests()
    calls = []
    entered = threading.Event()
    release = threading.Event()
    results = []

    def fake_uncached(cleaned):
        calls.append(cleaned)
        entered.set()
        assert release.wait(timeout=3.0)
        return {"13": {"ltp": 24501.0}}, [], False

    monkeypatch.setattr(market_ltp, "_fetch_market_quotes_uncached", fake_uncached)

    t1 = threading.Thread(target=lambda: results.append(fetch_market_quotes({"IDX_I": ["13"]})))
    t2 = threading.Thread(target=lambda: results.append(fetch_market_quotes({"IDX_I": ["13"]})))
    t1.start()
    assert entered.wait(timeout=1.0)
    t2.start()
    release.set()
    t1.join(timeout=3.0)
    t2.join(timeout=3.0)

    assert not t1.is_alive() and not t2.is_alive()
    assert len(calls) == 1
    assert len(results) == 2
    assert all(row == {"13": {"ltp": 24501.0}} for row in results)


def test_fetch_market_quotes_rate_limit_cooldown_suppresses_next_key(monkeypatch):
    _reset_marketfeed_coordination_for_tests()
    calls = []

    def fake_uncached(cleaned):
        calls.append(cleaned)
        return {}, ['ohlc:HTTP_429:{"805":"Too many requests"}'], True

    monkeypatch.setattr(market_ltp, "_fetch_market_quotes_uncached", fake_uncached)

    first = fetch_market_quotes({"IDX_I": ["13"]})
    second = fetch_market_quotes({"NSE_EQ": ["1333"]})

    assert first == {}
    assert second == {}
    assert len(calls) == 1
    assert fetch_market_quotes.last_errors == ["marketfeed:RATE_LIMIT_COOLDOWN"]
    assert fetch_market_quotes.last_meta["rate_limited"] is True
    assert fetch_market_quotes.last_meta["cooldown_remaining_s"] > 0


def test_build_index_board_exposes_safe_coordination_metadata(monkeypatch):
    _reset_marketfeed_coordination_for_tests()

    def fake_uncached(cleaned):
        return {"13": {"ltp": 24502.0, "close": 24400.0, "change": 102.0, "change_pct": 0.4}}, [], False

    monkeypatch.setattr(market_ltp, "_fetch_market_quotes_uncached", fake_uncached)
    board = market_ltp.build_index_board(symbols=["NIFTY"])

    assert board["success"] is True
    assert board["live_trading_enabled"] is False
    assert board["order_placement_allowed"] is False
    assert board["feed_coordination"]["coordination_scope"] == "process"
    assert "cache_ttl_s" in board["feed_coordination"]
    assert "rate_limit_cooldown_s" in board["feed_coordination"]
