"""Real paper pipeline cumulative exposure and corrupted position tests."""
import json
import pytest
from dashboard.backend import paper_pipeline_v8 as p

@pytest.mark.parametrize("existing_qty,existing_price,corrupt,allowed,reason",[
    (0,100,False,True,None),
    (250,100,False,True,None),
    (251,100,False,False,"PAPER_CAPITAL_LIMIT_BLOCK"),
    (400,100,False,False,"PAPER_CAPITAL_LIMIT_BLOCK"),
    (1,100,True,False,"PAPER_EXPOSURE_UNVERIFIED"),
    (1,-100,False,False,"PAPER_EXPOSURE_UNVERIFIED"),
    (1,float("nan"),False,False,"PAPER_EXPOSURE_UNVERIFIED"),
])
def test_cumulative_exposure(tmp_path,monkeypatch,existing_qty,existing_price,corrupt,allowed,reason):
    day=p._today_ist()
    monkeypatch.setenv("TRADING_CAPITAL_LIMIT_INR","50000")
    monkeypatch.setattr(p,"_load_latest_gain_rank",lambda root:(
        {"date":day},[{"underlying":"NIFTY","option_side":"CE","spot":25000,"raw":{}}],"test"))
    monkeypatch.setattr(p,"_load_instruments_df",lambda:None)
    monkeypatch.setattr(p,"_safe_market_open",lambda:True)
    monkeypatch.setattr(p,"_select_option_contract",lambda *args:(
        {"symbol":"NIFTY-CE","lot_size":250},"OK"))
    monkeypatch.setattr(p,"_load_chain_quote",lambda *args:(
        {"ltp":100,"chain_data_source":"dhan"},"OK"))
    path=p._pipeline_paths(tmp_path)["positions"]
    if corrupt:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text("{corrupted")
    elif existing_qty:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({"positions":[{"position_id":"old","status":"PAPER_OPEN",
                     "qty":existing_qty,"entry_price":existing_price}]}))
    result=p.run_pipeline_once(tmp_path)
    assert result["paper_orders_written"]==int(allowed)
    if not allowed:
        assert any(x["reason"]==reason for x in result["blockers"])
