"""
Tests for DataSourceManager Dhan + cached-file fallback.
No network calls — DhanHQ SDK and file I/O patched throughout.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data.datasource_manager import DataSourceManager


def _make_strikes(n=3):
    return [
        {"strike": 23000 + i * 100, "option_type": "CE" if i % 2 == 0 else "PE", "oi": 10000}
        for i in range(n)
    ]


@pytest.fixture
def dsm():
    return DataSourceManager()


# ── TC-FB-1: Dhan returns success → (DataFrame, spot) ────────────────────
def test_dhan_success_returns_df(dsm):
    import pandas as _pd

    mock_client = MagicMock()
    mock_client.get_option_chain.return_value = {"status": "success"}
    dsm._client = mock_client

    fake_df = _pd.DataFrame(_make_strikes())
    with patch("core.data.dhan_option_chain_parser.parse_option_chain_to_df", return_value=(fake_df, 23500.0)):
        df, spot = dsm.fetch_option_chain("NIFTY")

    assert df is not None
    assert spot == 23500.0
    assert len(df) == 3


# ── TC-FB-2: Dhan raises Exception → falls back to cache file ─────────────
def test_dhan_exception_falls_to_cache(dsm, tmp_path, monkeypatch):
    import core.data.datasource_manager as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    cache_dir = tmp_path / "state" / "chain_cache"
    cache_dir.mkdir(parents=True)
    (cache_dir / "NIFTY.json").write_text(
        json.dumps({"spot": 23000.0, "strikes": _make_strikes(2)})
    )

    mock_client = MagicMock()
    mock_client.get_option_chain.side_effect = Exception("Dhan API error")
    dsm._client = mock_client

    df, spot = dsm.fetch_option_chain("NIFTY")
    assert df is not None
    assert len(df) == 2
    assert spot == 23000.0


# ── TC-FB-3: Dhan returns non-success status → cache fallback ─────────────
def test_dhan_non_success_falls_to_cache(dsm, tmp_path, monkeypatch):
    import core.data.datasource_manager as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    cache_dir = tmp_path / "state" / "chain_cache"
    cache_dir.mkdir(parents=True)
    (cache_dir / "BANKNIFTY.json").write_text(
        json.dumps({"spot": 54000.0, "strikes": _make_strikes(5)})
    )

    mock_client = MagicMock()
    mock_client.get_option_chain.return_value = {"status": "error", "remarks": "API error"}
    dsm._client = mock_client

    with patch("core.data.dhan_option_chain_parser.parse_option_chain_to_df", return_value=(None, 0.0)):
        df, spot = dsm.fetch_option_chain("BANKNIFTY")
    assert df is not None
    assert len(df) == 5
    assert spot == 54000.0


# ── TC-FB-4: No credentials, no cache → (None, 0.0) ──────────────────────
def test_no_credentials_no_cache_returns_none(dsm, tmp_path, monkeypatch):
    import core.data.datasource_manager as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.delenv("DHAN_CLIENT_ID", raising=False)
    monkeypatch.delenv("DHAN_ACCESS_TOKEN", raising=False)
    dsm._client = None

    result = dsm.fetch_option_chain("NIFTY")
    assert result == (None, 0.0)


# ── TC-FB-5: Cache file exists, no Dhan → returns cached data ─────────────
def test_cache_file_used_when_no_dhan(dsm, tmp_path, monkeypatch):
    import core.data.datasource_manager as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    cache_dir = tmp_path / "state" / "chain_cache"
    cache_dir.mkdir(parents=True)
    (cache_dir / "NIFTY.json").write_text(
        json.dumps({"spot": 23300.0, "strikes": _make_strikes(4)})
    )
    monkeypatch.delenv("DHAN_CLIENT_ID", raising=False)
    monkeypatch.delenv("DHAN_ACCESS_TOKEN", raising=False)
    dsm._client = None

    df, spot = dsm.fetch_option_chain("NIFTY")
    assert df is not None
    assert len(df) == 4
    assert spot == 23300.0


# ── TC-FB-6: Corrupt cache file → (None, 0.0) ────────────────────────────
def test_corrupt_cache_returns_none(dsm, tmp_path, monkeypatch):
    import core.data.datasource_manager as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    cache_dir = tmp_path / "state" / "chain_cache"
    cache_dir.mkdir(parents=True)
    (cache_dir / "NIFTY.json").write_text("NOT VALID JSON {{")
    dsm._client = None
    monkeypatch.delenv("DHAN_CLIENT_ID", raising=False)
    monkeypatch.delenv("DHAN_ACCESS_TOKEN", raising=False)

    result = dsm.fetch_option_chain("NIFTY")
    assert result == (None, 0.0)


# ── TC-FB-7: get_option_chain dict structure when no data ─────────────────
def test_get_option_chain_no_data_structure(dsm, monkeypatch):
    monkeypatch.delenv("DHAN_CLIENT_ID", raising=False)
    monkeypatch.delenv("DHAN_ACCESS_TOKEN", raising=False)
    dsm._client = None
    result = dsm.get_option_chain("NIFTY")
    assert isinstance(result, dict)
    assert result.get("underlying") == "NIFTY"
    assert "strikes" in result
    assert isinstance(result["strikes"], list)
