from datetime import date
import json

import pytest

from scripts.cepe_event_liquidity_candidate import (
    FEATURE_WEIGHTS,
    _percentile_ranks,
    evaluate,
    rank,
)


HEADER = (
    "BizDt,Sgmt,Src,FinInstrmTp,FinInstrmId,SsnId,TradDt,TckrSymb,XpryDt,"
    "StrkPric,OptnTp,OpnPric,HghPric,LwPric,ClsPric,"
    "PrvsClsgPric,UndrlygPric,OpnIntrst,ChngInOpnIntrst,TtlTradgVol,TtlTrfVal,"
    "TtlNbOfTxsExctd,NewBrdLotQty\n"
)


def snapshot(day: str, *, following: bool = False, missing_previous_close: bool = False) -> bytes:
    rows = []
    for index in range(20):
        opening = 60 if following and index in {18, 19} else (20 if following else 10)
        close = 15 + index / 10
        previous_close = "" if missing_previous_close and index == 0 else str(10 + index / 20)
        high = max(25, opening)
        rows.append(
            f"{day},FO,NSE,STO,{index + 1},F1,{day},A{index:02d},"
            f"2026-01-29,100,CE,{opening},{high},5,{close},"
            f"{previous_close},100,2000,{index - 5},2000,{200000 + index},"
            f"{100 + index},50\n"
        )
    return (HEADER + "".join(rows)).encode()


def calendar(before: date, after: date) -> bytes:
    return json.dumps(
        {
            "schema": "nse-session-calendar-v2",
            "segment": "FO",
            "start": before.isoformat(),
            "end": after.isoformat(),
            "available_at": "2026-09-27T00:00:00Z",
            "sources": [
                {
                    "circular": "NSE/FAOP/71777",
                    "url": "https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf",
                    "sha256": "a" * 64,
                }
            ],
            "days": {
                before.isoformat(): f"{before.isoformat()}T09:15:00+05:30",
                after.isoformat(): f"{after.isoformat()}T09:15:00+05:30",
            },
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()


def test_preregistered_weights_and_average_tie_percentiles_are_fixed():
    assert sum(FEATURE_WEIGHTS.values()) == pytest.approx(1)
    assert _percentile_ranks([1, 1, 3, 2]) == [0.375, 0.375, 1.0, 0.75]


def test_rank_uses_prior_fields_and_selects_exact_top_decile():
    result = rank(snapshot("2026-01-05"), date(2026, 1, 5), date(2026, 1, 6))
    assert len(result["eligible"]) == 20
    assert len(result["selected"]) == 2
    assert [item["symbol"] for item in result["selected"]] == ["A19", "A18"]
    assert result["expected_range"] is None
    assert result["forward_issued"] is False
    assert result["orders_allowed"] is False


def test_following_snapshot_changes_outcomes_without_changing_selection():
    before_day, after_day = date(2026, 1, 5), date(2026, 1, 6)
    prior = snapshot(before_day.isoformat())
    ordinary = evaluate(
        prior,
        snapshot(after_day.isoformat(), following=False),
        before_day,
        after_day,
        session_calendar=calendar(before_day, after_day),
    )
    jumps = evaluate(
        prior,
        snapshot(after_day.isoformat(), following=True),
        before_day,
        after_day,
        session_calendar=calendar(before_day, after_day),
    )
    assert ordinary["variant"]["selected"] == jumps["variant"]["selected"] == 2
    assert ordinary["variant"]["hits"] == 0
    assert jumps["variant"]["hits"] == 2
    assert jumps["variant"]["threshold_counts"]["3"] == 2
    assert jumps["same_universe_raw_momentum"]["selected"] == 2
    assert jumps["cost_and_fill_proof"] == "NOT_PROVEN"
    assert jumps["orders_allowed"] is False


def test_missing_required_feature_is_excluded_without_imputation():
    result = rank(
        snapshot("2026-01-05", missing_previous_close=True),
        date(2026, 1, 5),
        date(2026, 1, 6),
    )
    assert len(result["eligible"]) == 19
    assert result["rejected"]["MISSING_OR_INVALID_FEATURE"] == 1
    assert result["feature_availability"]["implied_volatility"] == "NOT_AVAILABLE_ZERO_COVERAGE"
