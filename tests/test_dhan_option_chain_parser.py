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
