"""Unit tests for DhanHQ option-chain parser."""

import json
from pathlib import Path

import pytest

from core.data.dhan_option_chain_parser import (
    parse_dhan_leg,
    parse_dhan_option_chain_payload,
)

FIXTURE = Path(__file__).parent / "fixtures" / "dhan_option_chain_sample.json"


@pytest.fixture
def sample_payload():
    with open(FIXTURE, encoding="utf-8") as f:
        return json.load(f)


def test_official_dhan_v2_oc_payload_parsed():
    payload = {
        "status": "success",
        "data": {
            "last_price": 25642.8,
            "oc": {
                "25650.000000": {
                    "ce": {
                        "average_price": 146.99,
                        "greeks": {"delta": 0.53871, "theta": -15.1539, "gamma": 0.00132, "vega": 12.18593},
                        "implied_volatility": 9.789193798280868,
                        "last_price": 134,
                        "oi": 3786445,
                        "previous_close_price": 244.85,
                        "previous_oi": 402220,
                        "previous_volume": 31931705,
                        "security_id": 42528,
                        "top_ask_price": 134,
                        "top_ask_quantity": 1365,
                        "top_bid_price": 133.55,
                        "top_bid_quantity": 1625,
                        "volume": 117567970,
                    },
                    "pe": {
                        "average_price": 134.62,
                        "greeks": {"delta": -0.46732, "theta": -10.61131, "gamma": 0.00109, "vega": 12.2025},
                        "implied_volatility": 11.939337251280934,
                        "last_price": 132.8,
                        "oi": 3096145,
                        "previous_close_price": 101.45,
                        "previous_oi": 2327260,
                        "previous_volume": 81224780,
                        "security_id": 42529,
                        "top_ask_price": 132.75,
                        "top_ask_quantity": 390,
                        "top_bid_price": 132.45,
                        "top_bid_quantity": 65,
                        "volume": 157009970,
                    },
                }
            },
        },
    }

    df, spot = parse_dhan_option_chain_payload(payload)

    assert spot == pytest.approx(25642.8)
    assert len(df) == 2
    assert set(df["option_type"]) == {"CE", "PE"}
    assert set(df["source"]) == {"dhan"}
    ce = df[df["option_type"] == "CE"].iloc[0]
    assert ce["strike"] == pytest.approx(25650.0)
    assert ce["ltp"] == pytest.approx(134)
    assert ce["oi"] == 3786445
    assert ce["previous_oi"] == 402220
    assert ce["change_in_oi"] == 3384225
    assert ce["top_bid_price"] == pytest.approx(133.55)
    assert ce["top_ask_price"] == pytest.approx(134)


def test_unknown_payload_returns_empty_df_without_fallback_rows():
    df, spot = parse_dhan_option_chain_payload({"status": "success", "data": {"last_price": 1, "oc": {}}})

    assert spot == 0.0
    assert df.empty


def test_ce_and_pe_parsed(sample_payload):
    df, spot = parse_dhan_option_chain_payload(sample_payload)
    assert spot == pytest.approx(24500.5)
    assert set(df["option_type"]) == {"CE", "PE"}
    strike_24400 = df[df["strike"] == 24400.0]
    assert len(strike_24400) == 2
    assert set(strike_24400["option_type"]) == {"CE", "PE"}


def test_greeks_from_nested_object(sample_payload):
    df, _ = parse_dhan_option_chain_payload(sample_payload)
    ce = df[df["option_type"] == "CE"].iloc[0]
    assert ce["delta"] == pytest.approx(0.62)
    assert ce["gamma"] == pytest.approx(0.0009)
    assert ce["theta"] == pytest.approx(-4.8)
    assert ce["vega"] == pytest.approx(11.5)


def test_change_in_oi_computed(sample_payload):
    df, _ = parse_dhan_option_chain_payload(sample_payload)
    ce = df[df["option_type"] == "CE"].iloc[0]
    pe = df[df["option_type"] == "PE"].iloc[0]
    assert ce["change_in_oi"] == 1000
    assert pe["change_in_oi"] == -500


def test_bid_ask_from_top_fields(sample_payload):
    df, _ = parse_dhan_option_chain_payload(sample_payload)
    ce = df[df["option_type"] == "CE"].iloc[0]
    assert ce["top_bid_price"] == pytest.approx(179.5)
    assert ce["top_ask_price"] == pytest.approx(181.0)
    assert ce["bid_ask_spread"] == pytest.approx(1.5)


def test_missing_null_values_safe(sample_payload):
    df, _ = parse_dhan_option_chain_payload(sample_payload)
    null_ce = df[df["security_id"] == "52177"].iloc[0]
    assert null_ce["ltp"] == 0.0
    assert null_ce["oi"] == 0
    assert null_ce["change_in_oi"] == 0
    assert null_ce["bid_ask_spread"] == 0.0
    assert null_ce["delta"] == 0.0


def test_parse_dhan_leg_does_not_use_wrong_aliases():
    leg = {
        "oi": 100,
        "previous_oi": 80,
        "top_bid_price": 10.0,
        "top_ask_price": 10.5,
        "greeks": {"delta": 0.5},
        "bid": 9.0,
        "ask": 11.0,
        "oi_change": 999,
        "delta": 0.99,
    }
    row = parse_dhan_leg(leg, 24000.0, "CE")
    assert row["change_in_oi"] == 20
    assert row["top_bid_price"] == 10.0
    assert row["delta"] == 0.5
