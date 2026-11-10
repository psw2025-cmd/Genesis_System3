"""No PAPER fills from stale forecasts or a closed exchange."""
from dashboard.backend import paper_pipeline_v8 as p


def _run(tmp_path, monkeypatch, *, fresh, market_open):
    day = p._today_ist()
    forecast_date = day if fresh else "2020-01-01"
    monkeypatch.setattr(p, "_load_latest_gain_rank", lambda root: (
        {"date": forecast_date},
        [{"underlying": "NIFTY", "option_side": "CE",
          "confidence": 0.8, "spot": 25000, "raw": {}}],
        "test_forecast",
    ))
    monkeypatch.setattr(p, "_load_instruments_df", lambda: None)
    monkeypatch.setattr(p, "_safe_market_open", lambda: market_open)
    monkeypatch.setattr(p, "_select_option_contract", lambda *args: (
        {"symbol": "NIFTY-CE", "lot_size": 25}, "OK"
    ))
    monkeypatch.setattr(p, "_load_chain_quote", lambda *args: (
        {"ltp": 100, "chain_data_source": "dhan"}, "OK"
    ))
    return p.run_pipeline_once(tmp_path)


def test_closed_market_cannot_create_paper_order(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, fresh=True, market_open=False)
    assert result["paper_orders_written"] == 0
    assert result["forecasts_written"] == 1
    assert any(b["reason"] == "MARKET_CLOSED_PAPER_ENTRY" for b in result["blockers"])
    assert not p._pipeline_paths(tmp_path)["orders"].exists()


def test_stale_prediction_cannot_create_paper_order(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, fresh=False, market_open=True)
    assert result["paper_orders_written"] == 0
    assert result["forecasts_written"] == 1
    assert any(b["reason"] == p.BLOCK_STALE_FORECAST for b in result["blockers"])
    assert not p._pipeline_paths(tmp_path)["orders"].exists()


def test_stale_and_closed_both_block(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, fresh=False, market_open=False)
    assert result["paper_orders_written"] == 0
    assert result["blocked_written"] == 1
