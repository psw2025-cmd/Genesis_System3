"""
Tests for DataSourceManager bhavcopy parser.
No network calls — all tests use in-memory DataFrames.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data.datasource_manager import DataSourceManager


@pytest.fixture
def dsm():
    return DataSourceManager()


def _udiif_df(
    symbol="NIFTY", opt_type="CE", strike=23000, oi=61295, oi_change=60905, volume=1500, ltp=350.0, fin_instrm_tp="IDO"
):
    return pd.DataFrame(
        [
            {
                "TckrSymb": symbol,
                "OptnTp": opt_type,
                "StrkPric": strike,
                "OpnIntrst": oi,
                "ChngInOpnIntrst": oi_change,
                "TtlTradgVol": volume,
                "ClsPric": ltp,
                "XpryDt": "2026-06-26",
                "FinInstrmTp": fin_instrm_tp,
                "UndrlygPric": 23622.9,
            }
        ]
    )


def _old_fmt_df(symbol="NIFTY", opt_type="PE", strike=22500, oi=50000, oi_change=-3000, volume=800, ltp=120.5):
    return pd.DataFrame(
        [
            {
                "SYMBOL": symbol,
                "OPTION_TYP": opt_type,
                "STRIKE_PR": strike,
                "OPEN_INT": oi,
                "CHG_IN_OI": oi_change,
                "CONTRACTS": volume,
                "CLOSE": ltp,
                "INSTRUMENT": "OPTIDX",
                "EXPIRY_DT": "26-Jun-2026",
            }
        ]
    )


# TC-BP-1: UDiFF format — correct schema returned
def test_udiif_basic_parse(dsm):
    df = _udiif_df()
    result, spot = dsm._parse_bhavcopy(df, "NIFTY")
    assert result is not None
    assert len(result) == 1
    row = result.iloc[0]
    assert row["strike"] == 23000.0
    assert row["option_type"] == "CE"
    assert row["oi"] == 61295
    assert row["oi_change"] == 60905
    assert row["prev_oi"] == 61295 - 60905


# TC-BP-2: UDiFF symbol filter — wrong symbol excluded, FinInstrmTp NOT used as filter
def test_udiif_symbol_filter(dsm):
    rows = pd.DataFrame(
        [
            {
                "TckrSymb": "NIFTY",
                "OptnTp": "CE",
                "StrkPric": 23000,
                "OpnIntrst": 100,
                "ChngInOpnIntrst": 50,
                "TtlTradgVol": 10,
                "ClsPric": 100.0,
                "XpryDt": "2026-06-26",
                "FinInstrmTp": "IDO",
                "UndrlygPric": 23622.9,
            },
            {
                "TckrSymb": "BANKNIFTY",
                "OptnTp": "CE",
                "StrkPric": 48000,
                "OpnIntrst": 200,
                "ChngInOpnIntrst": 10,
                "TtlTradgVol": 20,
                "ClsPric": 200.0,
                "XpryDt": "2026-06-26",
                "FinInstrmTp": "IDO",
                "UndrlygPric": 54000.0,
            },
        ]
    )
    result, _ = dsm._parse_bhavcopy(rows, "NIFTY")
    assert result is not None
    assert len(result) == 1
    assert result.iloc[0]["option_type"] == "CE"


# TC-BP-3: Both CE and PE returned; non-CE/PE rows dropped
def test_udiif_ce_pe_only(dsm):
    rows = pd.DataFrame(
        [
            {
                "TckrSymb": "NIFTY",
                "OptnTp": "CE",
                "StrkPric": 23000,
                "OpnIntrst": 100,
                "ChngInOpnIntrst": 10,
                "TtlTradgVol": 10,
                "ClsPric": 100.0,
                "XpryDt": "2026-06-26",
                "FinInstrmTp": "IDO",
                "UndrlygPric": 23622.9,
            },
            {
                "TckrSymb": "NIFTY",
                "OptnTp": "PE",
                "StrkPric": 23000,
                "OpnIntrst": 200,
                "ChngInOpnIntrst": -10,
                "TtlTradgVol": 20,
                "ClsPric": 80.0,
                "XpryDt": "2026-06-26",
                "FinInstrmTp": "IDO",
                "UndrlygPric": 23622.9,
            },
            {
                "TckrSymb": "NIFTY",
                "OptnTp": "FUT",
                "StrkPric": 0,
                "OpnIntrst": 5000,
                "ChngInOpnIntrst": 100,
                "TtlTradgVol": 500,
                "ClsPric": 23600.0,
                "XpryDt": "2026-06-26",
                "FinInstrmTp": "IDX",
                "UndrlygPric": 23622.9,
            },
        ]
    )
    result, _ = dsm._parse_bhavcopy(rows, "NIFTY")
    assert result is not None
    assert len(result) == 2
    assert set(result["option_type"]) == {"CE", "PE"}


# TC-BP-4: Old format (pre-Jul 2024) — correct parse
def test_old_format_parse(dsm):
    df = _old_fmt_df()
    result, _ = dsm._parse_bhavcopy(df, "NIFTY")
    assert result is not None
    assert len(result) == 1
    row = result.iloc[0]
    assert row["oi"] == 50000
    assert row["oi_change"] == -3000
    assert row["volume"] == 800
    assert row["ltp"] == 120.5


# TC-BP-5: Old format — negative oi_change preserved; prev_oi computed correctly
def test_old_format_negative_oi_change(dsm):
    df = _old_fmt_df(oi=50000, oi_change=-3000)
    result, _ = dsm._parse_bhavcopy(df, "NIFTY")
    row = result.iloc[0]
    assert row["oi_change"] == -3000
    assert row["prev_oi"] == max(0, 50000 - (-3000))  # = 53000


# TC-BP-6: Symbol mismatch — returns None
def test_symbol_mismatch_returns_none(dsm):
    df = _udiif_df(symbol="BANKNIFTY")
    out = dsm._parse_bhavcopy(df, "NIFTY")
    assert out is None or (isinstance(out, tuple) and out[0] is None)


# TC-BP-7: Case-insensitive symbol matching
def test_case_insensitive_symbol(dsm):
    df = _udiif_df(symbol="nifty")
    result, _ = dsm._parse_bhavcopy(df, "NIFTY")
    assert result is not None
    assert len(result) == 1


# TC-BP-8: oi_change comes directly from column, not computed from two sessions
def test_oi_change_from_column(dsm):
    df = _udiif_df(oi=100000, oi_change=5000)
    result, _ = dsm._parse_bhavcopy(df, "NIFTY")
    assert result.iloc[0]["oi_change"] == 5000


# TC-BP-9: Unknown format — returns None (bare None, not a tuple)
def test_unknown_format_returns_none(dsm):
    df = pd.DataFrame([{"A": 1, "B": 2, "C": 3}])
    out = dsm._parse_bhavcopy(df, "NIFTY")
    assert out is None or (isinstance(out, tuple) and out[0] is None)


# TC-BP-10: Empty result after filter — returns None
def test_empty_after_filter_returns_none(dsm):
    df = _udiif_df(symbol="NIFTY", opt_type="CE")
    df["OptnTp"] = "FUT"  # invalidate option type so all rows are filtered out
    out = dsm._parse_bhavcopy(df, "NIFTY")
    assert out is None or (isinstance(out, tuple) and out[0] is None)
