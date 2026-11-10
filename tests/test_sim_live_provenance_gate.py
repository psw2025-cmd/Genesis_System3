"""Reject stale, wrong-scenario and wrong-source virtual evidence at UI boundary."""
from pathlib import Path
from dashboard.backend.synthetic_paper_lifecycle import virtual_paper_lifecycle

UI=(Path(__file__).resolve().parents[1]/"dashboard/frontend/src/components/LiveSimulation.tsx").read_text()

def test_virtual_source_and_step_validation():
    for check in ("payload?.mode === 'SYNTHETIC_PAPER_ONLY'",
                  "payload?.source === 'DETERMINISTIC_SYNTHETIC_MARKET'",
                  "payload?.broker_orders === false",
                  "payload?.scenario === scenario",
                  "payload?.step === replayStep",
                  "LIFECYCLE_PROVENANCE_MISMATCH",
                  "REPLAY_PROVENANCE_MISMATCH"):
        assert check in UI

def test_fail_closed_visibility():
    assert 'role="alert"' in UI
    assert "Synthetic lifecycle blocked:" in UI
    assert "setLifecycle(valid ? payload : null)" in UI
    assert "setReplay(payload?.scenario === scenario && payload?.step === replayStep ? payload : null)" in UI

def test_backend_provenance_contract():
    for scenario in ("trend","range","volatile"):
        for step in (0,5,30,3600):
            result=virtual_paper_lifecycle(scenario,step)
            assert result["scenario"]==scenario
            assert result["step"]==step
            assert result["mode"]=="SYNTHETIC_PAPER_ONLY"
            assert result["source"]=="DETERMINISTIC_SYNTHETIC_MARKET"
            assert result["broker_orders"] is False
