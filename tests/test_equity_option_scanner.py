"""Tests for equity F&O universe and scanner."""

import pandas as pd

from core.brokers.dhan.equity_fo_universe import load_equity_fo_universe
from core.brokers.dhan.nse_option_symbol import parse_trading_symbol
from dashboard.backend.equity_option_scanner import (
    _parse_equity_option_rows,
    build_equity_options_report,
    scan_equity_top_gainers,
)


def test_equity_fo_universe_loads():
    u = load_equity_fo_universe()
    assert u["implemented"] is True
    assert u["underlying_count"] > 50
    assert "RELIANCE" in u["underlyings"] or "TCS" in u["underlyings"]


def test_parse_stock_option_symbol():
    parsed = parse_trading_symbol("RELIANCE25JUN2500CE")
    assert parsed is not None
    assert parsed["underlying"] == "RELIANCE"
    assert parsed["instrument_type"] == "OPTSTK"
    assert parsed["strike"] == 2500.0


def test_parse_stock_decimal_strike():
    parsed = parse_trading_symbol("VEDL25APR24292.5CE")
    assert parsed is not None
    assert parsed["underlying"] == "VEDL"
    assert parsed["strike"] == 292.5


def test_bhavcopy_equity_rows_exclude_index():
    df = pd.DataFrame(
        [
            {
                "TckrSymb": "NIFTY",
                "OptnTp": "CE",
                "StrkPric": 24000,
                "OpnIntrst": 1000,
                "ChngInOpnIntrst": 100,
                "TtlTradgVol": 500,
                "ClsPric": 150,
                "XpryDt": "2026-06-26",
                "FinInstrmTp": "IDO",
            },
            {
                "TckrSymb": "RELIANCE",
                "OptnTp": "CE",
                "StrkPric": 2500,
                "OpnIntrst": 2000,
                "ChngInOpnIntrst": 400,
                "TtlTradgVol": 800,
                "ClsPric": 80,
                "XpryDt": "2026-06-26",
                "FinInstrmTp": "STO",
            },
            {
                "TckrSymb": "RELIANCE",
                "OptnTp": "PE",
                "StrkPric": 2480,
                "OpnIntrst": 1500,
                "ChngInOpnIntrst": 150,
                "TtlTradgVol": 300,
                "ClsPric": 60,
                "XpryDt": "2026-06-26",
                "FinInstrmTp": "STO",
            },
        ]
    )
    rows = _parse_equity_option_rows(df)
    assert len(rows) == 2
    assert all(r["underlying"] == "RELIANCE" for r in rows)


def test_scan_equity_top_gainers():
    rows = [
        {"underlying": "RELIANCE", "option_type": "CE", "strike": 2500, "gain_pct": 25.0, "ltp": 80},
        {"underlying": "RELIANCE", "option_type": "PE", "strike": 2480, "gain_pct": 10.0, "ltp": 60},
        {"underlying": "TCS", "option_type": "CE", "strike": 4000, "gain_pct": 30.0, "ltp": 50},
    ]
    scan = scan_equity_top_gainers(rows, top_n=5)
    assert scan["market_top_ce"]["underlying"] == "TCS"
    assert scan["market_top_pe"]["underlying"] == "RELIANCE"


def test_build_equity_report_structure():
    report = build_equity_options_report(top_n=5)
    assert "segments" in report
    assert report["segments"]["equity_options"]["instrument_type"] == "OPTSTK"
    assert report["segments"]["index_options"]["instrument_type"] == "OPTIDX"
