import pytest
from dashboard.backend.paper_prediction_outcome_audit import evaluate_paper_prediction

BASE = dict(trade_id="PAPER-001", predicted_gain_pct=20.0, entry_price=100.0, exit_price=110.0,
            entry_timestamp="2026-11-09T09:20:00+05:30", exit_timestamp="2026-11-09T09:35:00+05:30")

def test_prediction_error_and_hold_duration():
    result=evaluate_paper_prediction(**BASE)
    assert result["actual_gross_gain_pct"] == 10.0
    assert result["prediction_error_pct_points"] == -10.0
    assert result["holding_seconds"] == 900
    assert result["net_gain_pct"] is None
    assert result["learning_status"] == "NOT_TRAINED"
    assert result["training_eligible"] is False
    assert result["market_top_comparison_status"] == "NOT_VERIFIED"

def test_provisional_top_comparison_not_claimed_verified():
    result=evaluate_paper_prediction(**BASE, market_top_gain_pct=35,
        market_top_source="MARKET_SNAPSHOT", market_top_timestamp="2026-11-09T09:35:00+05:30",
        market_top_universe="NSE_EQUITY_FNO_CE_PE")
    assert result["market_top_gap_pct_points"] == -25
    assert result["market_top_comparison_status"] == "PROVISIONAL_SOURCE_REPORTED"
    assert result["real_market_outcome_verified"] is False

@pytest.mark.parametrize("changes",[
    {"entry_price":0}, {"exit_price":-1}, {"predicted_gain_pct":float("nan")},
    {"entry_timestamp":"2026-11-09T09:20:00"}, {"exit_timestamp":"2026-11-09T09:19:00+05:30"},
    {"market_top_gain_pct":30}, {"market_top_gain_pct":30,"market_top_source":"x",
      "market_top_timestamp":"2026-11-09T09:36:00+05:30","market_top_universe":"CE_PE"},
])
def test_invalid_or_incomparable_data_fails_closed(changes):
    with pytest.raises(ValueError):
        evaluate_paper_prediction(**(BASE|changes))

def test_timezone_equivalent_holding_duration():
    result=evaluate_paper_prediction(**(BASE|{"entry_timestamp":"2026-11-09T03:50:00Z"}))
    assert result["holding_seconds"] == 900
