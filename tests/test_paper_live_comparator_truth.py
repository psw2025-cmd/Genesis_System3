from __future__ import annotations

from pathlib import Path

import pytest

from core.trading import system3_paper_live_comparator as mod


class _OneFeatureModel:
    n_features_in_ = 1

    def predict(self, rows):
        return [float(rows[0][0]) + 10.0]


class _TwoFeatureModel:
    n_features_in_ = 2

    def predict(self, rows):
        return [123.0]


def test_fetch_live_ltp_has_no_hardcoded_market_fallback(monkeypatch):
    monkeypatch.setattr(mod, "fetch_market_quotes", lambda _request: {})
    assert mod.fetch_live_ltp("NIFTY") is None


def test_fetch_live_ltp_returns_only_positive_broker_quote(monkeypatch):
    sec_id = str(mod.INDEX_SECURITY_IDS["NIFTY"])
    monkeypatch.setattr(
        mod,
        "fetch_market_quotes",
        lambda _request: {sec_id: {"ltp": 25001.25}},
    )
    assert mod.fetch_live_ltp("NIFTY") == 25001.25


def test_model_prediction_invokes_real_predict(monkeypatch, tmp_path: Path):
    model_path = tmp_path / "NIFTY_model.pkl"
    model_path.write_bytes(b"placeholder")
    monkeypatch.setattr(mod.joblib, "load", lambda _path: _OneFeatureModel())
    assert mod.load_prediction(model_path, 25000.0) == 25010.0


def test_model_prediction_fails_closed_on_unknown_feature_schema(monkeypatch, tmp_path: Path):
    model_path = tmp_path / "NIFTY_model.pkl"
    model_path.write_bytes(b"placeholder")
    monkeypatch.setattr(mod.joblib, "load", lambda _path: _TwoFeatureModel())
    with pytest.raises(mod.ModelNotReady, match="feature schema"):
        mod.load_prediction(model_path, 25000.0)


def test_model_discovery_never_falls_back_to_wrong_symbol(tmp_path: Path):
    engine = mod.System3PaperLiveComparator(output_dir=tmp_path / "out")
    engine.root = tmp_path
    wrong = tmp_path / "BANKNIFTY_model.pkl"
    wrong.write_bytes(b"x" * 2000)
    assert engine.discover_model_for_symbol("NIFTY") is None


def test_live_loop_records_no_trade_when_broker_data_missing(monkeypatch, tmp_path: Path):
    engine = mod.System3PaperLiveComparator(output_dir=tmp_path / "out")
    monkeypatch.setattr(mod, "fetch_live_ltp", lambda _symbol: None)
    monkeypatch.setattr(engine, "discover_model_for_symbol", lambda _symbol: None)
    monkeypatch.setattr(mod, "is_market_open_ist", lambda: True)

    result = engine.run_live_loop("NIFTY", iterations=1, delay_s=0)

    assert result["truth_contract"] == "REAL_ONLY_FAIL_CLOSED_V1"
    assert result["total_trades"] == 0
    assert result["trades"][0]["execution_status"] == "DATA_NOT_READY"
    assert result["trades"][0]["signal_action"] == "NO_TRADE"
    assert result["trades"][0]["live_ltp"] is None
    assert result["order_placement_allowed"] is False
