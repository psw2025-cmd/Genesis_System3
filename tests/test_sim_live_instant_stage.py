"""Existing Sim Live stage controls must select backend synthetic replay evidence instantly."""
from pathlib import Path
import pytest
from dashboard.backend.synthetic_paper_lifecycle import virtual_paper_lifecycle

ROOT=Path(__file__).resolve().parents[1]
UI=(ROOT/"dashboard/frontend/src/components/LiveSimulation.tsx").read_text()

@pytest.mark.parametrize("step,orders,fills,open_positions,closed",[
    (0,0,0,0,0),(5,1,1,1,0),(30,2,2,0,1)])
@pytest.mark.parametrize("scenario",["trend","range","volatile"])
def test_stage_evidence(scenario,step,orders,fills,open_positions,closed):
    result=virtual_paper_lifecycle(scenario,step)
    assert (result["order_count"],result["fill_count"],len(result["positions"]),len(result["closed_positions"]))==(orders,fills,open_positions,closed)
    assert result["broker_orders"] is False
    assert result["realized_net_pnl"] is None

def test_stage_controls_use_same_step_for_both_endpoints():
    assert "const [replayStep, setReplayStep] = useState(0)" in UI
    assert 'step=${replayStep}' in UI
    assert UI.count("}, [scenario, replayStep])")==2
    for step in (0,5,30):
        assert "step: "+str(step)+"," in UI
    assert "setLifecycle(null); setReplay(null)" in UI
    assert "never broker or persistent PAPER ledger" in UI
