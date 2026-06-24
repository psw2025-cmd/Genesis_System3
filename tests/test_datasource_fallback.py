"""
Tests for DataSourceManager fallback chain.
No network calls — _try_* methods are mocked.
"""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data.datasource_manager import DataSourceManager


def _make_df(symbol="NIFTY", rows=5):
    return pd.DataFrame(
        [
            {
                "strike": 23000 + i * 100,
                "option_type": "CE" if i % 2 == 0 else "PE",
                "oi": 10000,
                "oi_change": 500,
                "prev_oi": 9500,
                "volume": 100,
                "ltp": 200.0,
                "iv": 15.0,
                "source": symbol.lower(),
            }
            for i in range(rows)
        ]
    )


@pytest.fixture
def dsm():
    m = DataSourceManager()
    m._cache = {}
    return m


# TC-FB-1: NSE success — returns NSE data; bhavcopy not called
def test_nse_success_returns_nse_data(dsm):
    nse_df = _make_df("nse")
    with (
        patch.object(dsm, "_try_dhan", return_value=(None, None)),
        patch.object(dsm, "_try_nse", return_value=(nse_df, 23000.0)),
        patch.object(dsm, "_try_bhavcopy", side_effect=AssertionError("should not be called")),
    ):
        chain_df, spot = dsm.fetch_option_chain("NIFTY")
    assert chain_df is not None
    assert spot == 23000.0
    assert len(chain_df) == 5


# TC-FB-2: NSE raises ConnectionError → bhavcopy (P3) is tried
def test_nse_connection_error_falls_through_to_bhavcopy(dsm):
    bhavcopy_df = _make_df("bhavcopy")
    bhavcopy_df["source"] = "bhavcopy"
    with (
        patch.object(dsm, "_try_dhan", return_value=(None, None)),
        patch.object(dsm, "_try_nse", side_effect=ConnectionError("NSE 404")),
        patch.object(dsm, "_try_nsepython", side_effect=ConnectionError("nsepython fail")),
        patch.object(dsm, "_try_bhavcopy", return_value=(bhavcopy_df, 0.0)),
        patch.object(dsm, "_try_jugaad", side_effect=AssertionError("should not reach jugaad")),
    ):
        chain_df, spot = dsm.fetch_option_chain("NIFTY")
    assert chain_df is not None
    assert chain_df.iloc[0]["source"] == "bhavcopy"


# TC-FB-3: NSE HTTP error → fallback to bhavcopy
def test_nse_http_error_falls_to_bhavcopy(dsm):
    import requests

    bhavcopy_df = _make_df("bhavcopy")
    with (
        patch.object(dsm, "_try_dhan", return_value=(None, None)),
        patch.object(dsm, "_try_nse", side_effect=requests.HTTPError("503")),
        patch.object(dsm, "_try_nsepython", return_value=(None, None)),
        patch.object(dsm, "_try_bhavcopy", return_value=(bhavcopy_df, 0.0)),
    ):
        chain_df, spot = dsm.fetch_option_chain("NIFTY")
    assert chain_df is not None
    assert len(chain_df) == 5


# TC-FB-4: All network sources fail → synthetic fallback
def test_all_fail_falls_to_synthetic(dsm):
    synthetic_df = _make_df("synthetic")
    synthetic_df["source"] = "synthetic"
    with (
        patch.object(dsm, "_try_dhan", return_value=(None, None)),
        patch.object(dsm, "_try_nse", return_value=(None, None)),
        patch.object(dsm, "_try_nsepython", return_value=(None, None)),
        patch.object(dsm, "_try_bhavcopy", return_value=(None, None)),
        patch.object(dsm, "_try_jugaad", return_value=(None, None)),
        patch.object(dsm, "_try_yfinance", return_value=(None, None)),
        patch.object(dsm, "_try_synthetic", return_value=(synthetic_df, 23000.0)),
    ):
        chain_df, spot = dsm.fetch_option_chain("NIFTY")
    assert chain_df is not None
    assert chain_df.iloc[0]["source"] == "synthetic"


# TC-FB-5: Synthetic result is NOT cached
def test_synthetic_not_cached(dsm):
    synthetic_df = _make_df("synthetic")
    synthetic_df["source"] = "synthetic"
    with (
        patch.object(dsm, "_try_dhan", return_value=(None, None)),
        patch.object(dsm, "_try_nse", return_value=(None, None)),
        patch.object(dsm, "_try_nsepython", return_value=(None, None)),
        patch.object(dsm, "_try_bhavcopy", return_value=(None, None)),
        patch.object(dsm, "_try_jugaad", return_value=(None, None)),
        patch.object(dsm, "_try_yfinance", return_value=(None, None)),
        patch.object(dsm, "_try_synthetic", return_value=(synthetic_df, 23000.0)),
    ):
        dsm.fetch_option_chain("NIFTY")
    assert "NIFTY" not in dsm._cache


# TC-FB-6: Empty DataFrame from NSE → continue to next source
def test_empty_df_from_nse_falls_through(dsm):
    empty_df = pd.DataFrame()
    bhavcopy_df = _make_df("bhavcopy")
    with (
        patch.object(dsm, "_try_dhan", return_value=(None, None)),
        patch.object(dsm, "_try_nse", return_value=(empty_df, 0.0)),
        patch.object(dsm, "_try_nsepython", return_value=(None, None)),
        patch.object(dsm, "_try_bhavcopy", return_value=(bhavcopy_df, 0.0)),
    ):
        chain_df, spot = dsm.fetch_option_chain("NIFTY")
    assert chain_df is not None
    assert len(chain_df) == 5


# TC-FB-7: Cache hit within TTL — source functions not called
def test_cache_hit_bypasses_sources(dsm):
    cached_df = _make_df("cached")
    dsm._cache["NIFTY"] = (time.time(), cached_df, 23000.0)
    with patch.object(dsm, "_try_nse", side_effect=AssertionError("should not call nse")):
        chain_df, spot = dsm.fetch_option_chain("NIFTY")
    assert chain_df is not None
    assert len(chain_df) == 5
