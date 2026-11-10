"""Existing 23-tab Sim Live wiring contract and replay safety."""
from pathlib import Path
import ast
import pytest
from dashboard.backend.paper_market_replay import MarketTick, replay_paper_buy

ROOT=Path(__file__).resolve().parents[1]

def test_existing_sim_live_wired_without_new_tab():
    sidebar=(ROOT/"dashboard/frontend/src/components/Sidebar.tsx").read_text()
    app=(ROOT/"dashboard/frontend/src/App.tsx").read_text()
    component=(ROOT/"dashboard/frontend/src/components/LiveSimulation.tsx").read_text()
    backend=(ROOT/"dashboard/backend/app.py").read_text()
    assert "id: 'sim-live'" in sidebar
    assert "case 'sim-live':     return <LiveSimulation />" in app
    assert "/api/simulation/replay/state" in component
    assert 'data-testid="synthetic-market-replay"' in component
    assert '@app.get("/api/simulation/replay/state")' in backend
    assert "SYNTHETIC TEST DATA" in component
    assert "real_broker_routes_called" in backend

@pytest.mark.parametrize("scenario,step",[(s,i) for s in ("trend","range","volatile") for i in range(100)])
def test_market_scenario_quote_invariants(scenario,step):
    drift={"trend":.4,"range":0.0,"volatile":-.2}[scenario]
    wiggle=((step%11)-5)*{"trend":.2,"range":.8,"volatile":2.0}[scenario]
    ask=round(max(1.0,100+drift*step+wiggle),2)
    bid=round(max(.01,ask-.5),2)
    quote=MarketTick("2026-11-09T03:45:00+00:00",bid,ask,25)
    result=replay_paper_buy([quote],25)
    assert result["status"]=="PAPER_FILLED"
    assert result["filled_qty"]==25
    assert result["fills"][0]["mode"]=="SYNTHETIC_PAPER_FILL_NOT_BROKER"

def test_backend_module_parses():
    ast.parse((ROOT/"dashboard/backend/app.py").read_text())
