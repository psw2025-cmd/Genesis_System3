"""Capital limits enforced in the actual PAPER entry path, without broker orders."""
import pytest
from dashboard.backend import paper_pipeline_v8 as p

@pytest.mark.parametrize("price,lot,limit,allowed", [
    (100,25,"50000",True),
    (2000,25,"50000",True),
    (2001,25,"50000",False),
    (100,1000,"50000",False),
    (100,25,"1000",False),
    (100,25,"bad",False),
    (100,25,"nan",False),
    (100,25,"-1",False),
    (100,25,"0",False),
    (100,25,"inf",False),
])
def test_actual_paper_pipeline_capital_guard(tmp_path,monkeypatch,price,lot,limit,allowed):
    day=p._today_ist()
    monkeypatch.setenv("TRADING_CAPITAL_LIMIT_INR",limit)
    monkeypatch.setattr(p,"_load_latest_gain_rank",lambda root:(
        {"date":day},[{"underlying":"NIFTY","option_side":"CE",
                        "confidence":0.8,"spot":25000,"raw":{}}],"test"))
    monkeypatch.setattr(p,"_load_instruments_df",lambda:None)
    monkeypatch.setattr(p,"_safe_market_open",lambda:True)
    monkeypatch.setattr(p,"_select_option_contract",lambda *args:(
        {"symbol":"NIFTY-CE","lot_size":lot},"OK"))
    monkeypatch.setattr(p,"_load_chain_quote",lambda *args:(
        {"ltp":price,"chain_data_source":"dhan"},"OK"))
    result=p.run_pipeline_once(tmp_path)
    assert result["paper_orders_written"] == int(allowed)
    if not allowed:
        assert any(b["reason"]=="PAPER_CAPITAL_LIMIT_BLOCK" for b in result["blockers"])
        assert not p._pipeline_paths(tmp_path)["orders"].exists()
    else:
        assert result["paper_orders"][0]["qty"]*result["paper_orders"][0]["entry_price"] <= float(limit)
