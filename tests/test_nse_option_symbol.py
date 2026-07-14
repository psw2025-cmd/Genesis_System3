"""Tests for NSE/Dhan option trading symbol resolver."""

import json
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from core.brokers.dhan.nse_option_symbol import (
    build_trading_symbol,
    enrich_option_row,
    parse_trading_symbol,
    resolve_option_contract,
)

FIXTURE_INSTR = Path(__file__).parent / "fixtures" / "dhan_instruments_sample.json"
SESSION_EXPIRY = "2026-02-05"


def test_build_trading_symbol_dhan_format():
    sym = build_trading_symbol("NIFTY", date(2026, 2, 5), 23500, "CE")
    assert sym == "NIFTY05FEB2623500CE"


def test_parse_trading_symbol_roundtrip():
    sym = "NIFTY05FEB2623500CE"
    parsed = parse_trading_symbol(sym)
    assert parsed is not None
    assert parsed["underlying"] == "NIFTY"
    assert parsed["strike"] == 23500.0
    assert parsed["option_type"] == "CE"
    assert parsed["expiry_date"] == "2026-02-05"


def test_parse_banknifty_symbol():
    parsed = parse_trading_symbol("BANKNIFTY05FEB2648500PE")
    assert parsed["underlying"] == "BANKNIFTY"
    assert parsed["strike"] == 48500.0
    assert parsed["option_type"] == "PE"


def test_resolve_from_instrument_master():
    df = pd.DataFrame(json.loads(FIXTURE_INSTR.read_text(encoding="utf-8")))

    with patch("core.brokers.dhan.nse_option_symbol.get_instruments_df", return_value=df):
        resolved = resolve_option_contract("NIFTY", 23500, "CE", expiry_date=SESSION_EXPIRY)
    assert resolved["trading_symbol"] == "NIFTY05FEB2623500CE"
    assert resolved["security_id"] == "52175"
    assert resolved["lot_size"] == 50
    assert resolved["resolved_from"] == "instrument_master"


def test_enrich_replaces_index_with_trading_symbol():
    row = {
        "underlying": "NIFTY",
        "symbol": "NIFTY",
        "strike": 23500,
        "option_type": "CE",
        "expiry_date": SESSION_EXPIRY,
    }
    out = enrich_option_row(row)
    assert out["trading_symbol"] == "NIFTY05FEB2623500CE"
    assert out["symbol"] == "NIFTY05FEB2623500CE"
    assert out["underlying"] == "NIFTY"
    assert out["expiry_date"] == SESSION_EXPIRY


def test_enrich_fixture_trade_shape():
    trade = {
        "position_id": "POS_0001",
        "underlying": "NIFTY",
        "option_type": "CE",
        "strike": 23500,
        "expiry_date": SESSION_EXPIRY,
    }
    out = enrich_option_row(trade)
    assert out["trading_symbol"].endswith("CE")
    assert "23500" in out["trading_symbol"]
