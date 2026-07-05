"""
Tests for DataSourceManager (Dhan-only, post-simplification).
Covers: no-credentials fallback, cached-file fallback, API helpers.
No network calls — Dhan client patched throughout.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data.datasource_manager import DataSourceManager


@pytest.fixture
def dsm():
    return DataSourceManager()


@pytest.fixture
def chain_cache_dir(tmp_path):
    """Return a tmp chain_cache directory whose path is monkey-patched into DataSourceManager."""
    return tmp_path / "chain_cache"


# ── TC-DM-1: No credentials → (None, 0.0) ────────────────────────────────
def test_no_credentials_returns_none(dsm, monkeypatch):
    monkeypatch.delenv("DHAN_CLIENT_ID", raising=False)
    monkeypatch.delenv("DHAN_ACCESS_TOKEN", raising=False)
    dsm._client = None
    result = dsm.fetch_option_chain("NIFTY")
    assert result == (None, 0.0)


# ── TC-DM-2: Dhan SDK success → (DataFrame, spot) ───────────────────────
def test_dhan_success_returns_df(dsm):
    import pandas as pd

    mock_client = MagicMock()
    mock_client.get_option_chain.return_value = {"status": "success", "data": {}}
    dsm._client = mock_client

    fake_df = pd.DataFrame([{"strike": 23000, "option_type": "CE", "oi": 5000}])
    with patch("core.data.dhan_option_chain_parser.parse_option_chain_to_df", return_value=(fake_df, 23500.0)):
        df, spot = dsm.fetch_option_chain("NIFTY")

    assert df is not None
    assert len(df) == 1
    assert spot == 23500.0


# ── TC-DM-3: Dhan SDK error → cached JSON fallback ───────────────────────
def test_dhan_error_falls_to_cache(dsm, tmp_path, monkeypatch):
    cache_dir = tmp_path / "state" / "chain_cache"
    cache_dir.mkdir(parents=True)
    (cache_dir / "NIFTY.json").write_text(
        json.dumps(
            {
                "spot": 23400.0,
                "strikes": [{"strike": 23000, "option_type": "CE", "oi": 100}],
            }
        )
    )

    mock_client = MagicMock()
    mock_client.get_option_chain.side_effect = Exception("API error")
    dsm._client = mock_client

    import core.data.datasource_manager as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)

    df, spot = dsm.fetch_option_chain("NIFTY")
    assert df is not None
    assert len(df) == 1
    assert spot == 23400.0


# ── TC-DM-4: Cache file present, no Dhan client → cache used ─────────────
def test_no_client_uses_cache(dsm, tmp_path, monkeypatch):
    cache_dir = tmp_path / "state" / "chain_cache"
    cache_dir.mkdir(parents=True)
    (cache_dir / "BANKNIFTY.json").write_text(
        json.dumps(
            {
                "spot": 54000.0,
                "strikes": [
                    {"strike": 53000, "option_type": "PE", "oi": 200},
                    {"strike": 55000, "option_type": "CE", "oi": 300},
                ],
            }
        )
    )

    dsm._client = None
    monkeypatch.delenv("DHAN_CLIENT_ID", raising=False)
    monkeypatch.delenv("DHAN_ACCESS_TOKEN", raising=False)

    import core.data.datasource_manager as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)

    df, spot = dsm.fetch_option_chain("BANKNIFTY")
    assert df is not None
    assert len(df) == 2
    assert spot == 54000.0


# ── TC-DM-5: get_option_chain returns dict with required keys ─────────────
def test_get_option_chain_returns_dict(dsm, monkeypatch):
    monkeypatch.delenv("DHAN_CLIENT_ID", raising=False)
    monkeypatch.delenv("DHAN_ACCESS_TOKEN", raising=False)
    dsm._client = None
    result = dsm.get_option_chain("NIFTY")
    assert isinstance(result, dict)
    assert "underlying" in result
    assert "spot" in result
    assert "strikes" in result


# ── TC-DM-6: get_option_chain underlying is uppercased ───────────────────
def test_get_option_chain_uppercase_symbol(dsm, monkeypatch):
    monkeypatch.delenv("DHAN_CLIENT_ID", raising=False)
    monkeypatch.delenv("DHAN_ACCESS_TOKEN", raising=False)
    dsm._client = None
    result = dsm.get_option_chain("nifty")
    assert result["underlying"] == "NIFTY"


# ── TC-DM-7: get_spot_price returns 0.0 without credentials ──────────────
def test_get_spot_price_no_credentials(dsm, monkeypatch):
    monkeypatch.delenv("DHAN_CLIENT_ID", raising=False)
    monkeypatch.delenv("DHAN_ACCESS_TOKEN", raising=False)
    dsm._client = None
    price = dsm.get_spot_price("NIFTY")
    assert price == 0.0


# ── TC-DM-8: health_check returns dict with status key ───────────────────
def test_health_check_returns_status(dsm, monkeypatch):
    monkeypatch.delenv("DHAN_CLIENT_ID", raising=False)
    monkeypatch.delenv("DHAN_ACCESS_TOKEN", raising=False)
    dsm._client = None
    result = dsm.health_check()
    assert isinstance(result, dict)
    assert "status" in result
    assert result["status"] in ("OK", "ERROR", "NO_CREDENTIALS")


# ── TC-DM-9: health_check returns NO_CREDENTIALS without env vars ─────────
def test_health_check_no_credentials(dsm, monkeypatch):
    monkeypatch.delenv("DHAN_CLIENT_ID", raising=False)
    monkeypatch.delenv("DHAN_ACCESS_TOKEN", raising=False)
    dsm._client = None
    result = dsm.health_check()
    assert result["status"] == "NO_CREDENTIALS"


# ── TC-DM-10: get_datasource_manager returns DataSourceManager instance ───
def test_get_datasource_manager():
    from core.data.datasource_manager import get_datasource_manager
    mgr = get_datasource_manager()
    assert isinstance(mgr, DataSourceManager)
