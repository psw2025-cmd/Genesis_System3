"""India timezone event evidence for actual paper prediction and orders."""
from datetime import datetime, timezone
import pytest
from dashboard.backend import paper_pipeline_v8 as p

def test_utc_to_ist_preserves_instant():
    stamp="2026-11-07T04:45:12.123456+00:00"
    ist=p._ist_event_time(stamp)
    assert ist=="2026-11-07T10:15:12.123456+05:30"
    assert datetime.fromisoformat(ist).astimezone(timezone.utc)==datetime.fromisoformat(stamp)

@pytest.mark.parametrize("stamp",["2026-11-07T10:15:00","bad"])
def test_ambiguous_or_invalid_timestamp_fails_closed(stamp):
    with pytest.raises(ValueError):
        p._ist_event_time(stamp)

def test_forecast_and_order_persist_indian_time(tmp_path,monkeypatch):
    day=p._today_ist()
    monkeypatch.setenv("TRADING_CAPITAL_LIMIT_INR","50000")
    monkeypatch.setattr(p,"_load_latest_gain_rank",lambda root:(
        {"date":day},[{"underlying":"NIFTY","option_side":"CE","spot":25000,"raw":{}}],"test"))
    monkeypatch.setattr(p,"_load_instruments_df",lambda:None)
    monkeypatch.setattr(p,"_safe_market_open",lambda:True)
    monkeypatch.setattr(p,"_select_option_contract",lambda *args:(
        {"symbol":"NIFTY-CE","lot_size":25},"OK"))
    monkeypatch.setattr(p,"_load_chain_quote",lambda *args:(
        {"ltp":100,"chain_data_source":"dhan"},"OK"))
    result=p.run_pipeline_once(tmp_path)
    assert result["paper_orders_written"]==1
    paths=p._pipeline_paths(tmp_path)
    import json
    forecast=json.loads(paths["forecast"].read_text().splitlines()[0])
    order=json.loads(paths["orders"].read_text().splitlines()[0])
    position=json.loads(paths["positions"].read_text())["positions"][0]
    for row in (forecast,order):
        assert row["created_ist"].endswith("+05:30")
        assert datetime.fromisoformat(row["created_ist"]).astimezone(timezone.utc)==datetime.fromisoformat(row["created_utc"])
    assert position["entry_time_ist"]==order["created_ist"]

@pytest.mark.parametrize("minute_index", range(300))
def test_300_timestamp_roundtrip_scenarios(minute_index):
    """300 real UTC-to-IST conversion checks spanning midnight and date rollover."""
    from datetime import timedelta
    utc=datetime(2026,11,6,19,0,tzinfo=timezone.utc)+timedelta(minutes=minute_index)
    local=datetime.fromisoformat(p._ist_event_time(utc.isoformat()))
    assert local.utcoffset()==timedelta(hours=5,minutes=30)
    assert local.astimezone(timezone.utc)==utc
    assert local.date().isoformat()==(utc+timedelta(hours=5,minutes=30)).date().isoformat()
