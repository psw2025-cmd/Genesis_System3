"""Sim Live trade audit cannot invent predictions, real-market gains or learning."""
from pathlib import Path
import pytest
from dashboard.backend.synthetic_paper_lifecycle import virtual_paper_lifecycle

UI=(Path(__file__).resolve().parents[1]/"dashboard/frontend/src/components/LiveSimulation.tsx").read_text()

def test_ui_audit_has_explicit_missing_evidence():
    for required in ("synthetic-trade-outcome-audit", "Predicted gain %: NOT AVAILABLE",
                     "Actual gross gain % (synthetic)", "Actual NSE/BSE top CE/PE gain: NOT VERIFIED",
                     "Gross vs market-top gap: NOT VERIFIED", "Auto-learning: NOT TRAINED",
                     "Ranking/score: NOT AVAILABLE", "Charges / net gain: NOT VERIFIED"):
        assert required in UI

@pytest.mark.parametrize("scenario",["trend","range","volatile"])
def test_closed_synthetic_gross_and_duration_are_fill_derived(scenario):
    record=virtual_paper_lifecycle(scenario,30)
    assert len(record["fills"])==2
    entry,exit_=record["fills"]
    assert entry["side"]=="BUY" and exit_["side"]=="SELL"
    assert record["closed_positions"][0]["gross_pnl"]==round((exit_["price"]-entry["price"])*entry["qty"],2)
    assert record["closed_positions"][0]["net_pnl"] is None
    assert record["net_pnl_verified"] is False
    assert record["trade_verification_status"]=="NOT_VERIFIED"
