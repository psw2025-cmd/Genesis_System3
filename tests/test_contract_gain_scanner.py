"""Tests for live CE/PE contract gain scanner."""

import pytest

from dashboard.backend.contract_gain_scanner import (
    INDEX_SEGMENTS,
    compute_contract_gain_pct,
    scan_all_segments_from_chains,
    scan_segment_contracts,
)


def test_compute_gain_from_ltp_and_prev_close():
    c = {"ltp": 110.0, "previous_close_price": 100.0, "option_type": "CE"}
    assert compute_contract_gain_pct(c) == pytest.approx(10.0)


def test_compute_gain_from_change_percent():
    c = {"change_percent": 15.5, "ltp": 50, "option_type": "PE"}
    assert compute_contract_gain_pct(c) == pytest.approx(15.5)


def test_scan_segment_finds_top_ce_and_pe():
    contracts = [
        {
            "option_type": "CE",
            "strike": 24000,
            "ltp": 120,
            "previous_close_price": 100,
            "trading_symbol": "NIFTY05FEB2624000CE",
        },
        {
            "option_type": "CE",
            "strike": 24100,
            "ltp": 55,
            "previous_close_price": 50,
            "trading_symbol": "NIFTY05FEB2624100CE",
        },
        {
            "option_type": "PE",
            "strike": 23900,
            "ltp": 88,
            "previous_close_price": 80,
            "trading_symbol": "NIFTY05FEB2623900PE",
        },
        {
            "option_type": "PE",
            "strike": 23800,
            "ltp": 30,
            "previous_close_price": 25,
            "trading_symbol": "NIFTY05FEB2623800PE",
        },
    ]
    result = scan_segment_contracts(contracts, "NIFTY")
    assert result["top_ce"]["gain_pct"] == pytest.approx(20.0)
    assert result["top_pe"]["gain_pct"] == pytest.approx(20.0)
    assert result["top_ce"]["strike"] == 24000
    assert len(result["top_ce_list"]) >= 2


def test_scan_all_segments_implementation_matrix():
    chains = {
        "NIFTY": {
            "contracts": [
                {"option_type": "CE", "strike": 24000, "ltp": 110, "previous_close_price": 100},
                {"option_type": "PE", "strike": 23900, "ltp": 90, "previous_close_price": 80},
            ],
            "status": "MARKET_OPEN",
            "data_source": "dhan",
            "spot": 24050,
        },
        "BANKNIFTY": {"contracts": [], "status": "NO_DATA"},
        "FINNIFTY": {
            "contracts": [
                {"option_type": "CE", "strike": 23000, "ltp": 50, "previous_close_price": 40},
                {"option_type": "PE", "strike": 22900, "ltp": 44, "previous_close_price": 40},
            ],
            "data_source": "dhan",
        },
        "MIDCPNIFTY": {
            "contracts": [
                {"option_type": "CE", "strike": 11000, "ltp": 22, "previous_close_price": 20},
                {"option_type": "PE", "strike": 10900, "ltp": 18, "previous_close_price": 16},
            ],
        },
    }
    report = scan_all_segments_from_chains(chains)
    assert report["segments_total"] == 4
    assert report["segments_implemented"] == 3
    assert "BANKNIFTY" in report["missing_segments"]
    assert report["market_wide"]["top_ce"]["underlying"] == "FINNIFTY"
    assert len(INDEX_SEGMENTS) == 4
