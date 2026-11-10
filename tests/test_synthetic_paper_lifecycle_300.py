"""Virtual market end-to-end lifecycle, source isolation, and no fabricated net profit."""
import pytest
from pathlib import Path
from dashboard.backend.synthetic_paper_lifecycle import virtual_paper_lifecycle

@pytest.mark.parametrize("scenario",["trend","range","volatile"])
@pytest.mark.parametrize("step",range(100))
def test_virtual_lifecycle_300(scenario,step):
    x=virtual_paper_lifecycle(scenario,step)
    assert x["broker_orders"] is False
    assert x["realized_net_pnl"] is None
    assert x["net_pnl_verified"] is False
    assert x["order_count"]==len(x["orders"])
    assert x["fill_count"]==len(x["fills"])
    if step<5:
        assert not x["orders"] and not x["fills"] and not x["positions"]
    elif step<30:
        assert len(x["orders"])==1 and len(x["fills"])==1 and len(x["positions"])==1
    else:
        assert len(x["orders"])==2 and len(x["fills"])==2 and not x["positions"]
        assert len(x["closed_positions"])==1
        closed=x["closed_positions"][0]
        assert closed["gross_pnl"]==round((x["fills"][1]["price"]-x["fills"][0]["price"])*25,2)
        assert closed["net_pnl"] is None and closed["charges"] is None

@pytest.mark.parametrize("scenario,step",[(s,n) for s in ["bad","trend","range","volatile"] for n in [-1,3601]])
def test_invalid_replay_inputs(scenario,step):
    with pytest.raises(ValueError):
        virtual_paper_lifecycle(scenario,step)

def test_existing_ui_wiring():
    root=Path(__file__).resolve().parents[1]
    ui=(root/"dashboard/frontend/src/components/LiveSimulation.tsx").read_text()
    api=(root/"dashboard/backend/app.py").read_text()
    assert 'data-testid="synthetic-paper-lifecycle"' in ui
    assert "/api/simulation/replay/lifecycle" in ui
    assert '@app.get("/api/simulation/replay/lifecycle")' in api
