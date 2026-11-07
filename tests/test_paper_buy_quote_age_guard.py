"""Fail-closed BUY replay age-threshold regression; synthetic only."""
import pytest
from dashboard.backend.paper_market_replay import replay_paper_buy

@pytest.mark.parametrize("age", [0, -1, float("nan"), float("inf"), -float("inf")])
def test_buy_rejects_invalid_quote_age(age):
    with pytest.raises(ValueError, match="PAPER_REPLAY_INVALID_RISK"):
        replay_paper_buy([], 1, max_quote_age_seconds=age)
