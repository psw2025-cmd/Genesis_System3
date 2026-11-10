"""Multibagger research must never claim a live Dhan-wide verified scan."""
from pathlib import Path
from dashboard.backend.multibagger_service import get_multibagger_research_data

def test_static_research_is_not_verified_or_full_dhan_scan():
    data=get_multibagger_research_data()
    assert data["status"]=="STATIC_RESEARCH_ONLY_NOT_VERIFIED"
    assert data["dhan_equity_universe_screened"] is False
    assert data["screened_equity_count"]==0
    assert data["prediction_accuracy_verified"] is False
    assert data["live_market_data_verified"] is False
    assert data["candidate_source"]=="STATIC_RESEARCH_UNIVERSE_HARDCODED"
    assert data["total_candidates"]==len(data["candidates"])
    assert all(v!="VERIFIED" for v in data["sections"].values())
    assert data["governance"]["order_placement_allowed"] is False

def test_ui_does_not_claim_all_equity_continuous_screening():
    src=(Path(__file__).resolve().parents[1]/"dashboard/frontend/src/components/workspaces/MultibaggerResearch.tsx").read_text()
    assert "full Dhan equity universe not screened" in src
    assert "Continuously screened via Stan Weinstein" not in src
