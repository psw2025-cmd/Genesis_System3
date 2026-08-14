"""Tests for Dhan marketfeed LTP helpers and position enrichment."""

from core.brokers.dhan.market_ltp import (
    INDEX_SECURITY_IDS,
    _parse_quote_blob,
    enrich_positions_with_market_ltp,
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
