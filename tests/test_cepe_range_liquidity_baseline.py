from datetime import date

from scripts.cepe_range_liquidity_baseline import rank, evaluate

HEADER = "TradDt,TckrSymb,XpryDt,StrkPric,OptnTp,OpnPric,ClsPric,HghPric,LwPric,TtlTradgVol,OpnIntrst\n"


def snapshot(day, *, future_open=20, missing_oi=False):
    rows = []
    for i in range(20):
        opening = 10 if day == "2026-01-05" else future_open
        # A00 has raw momentum 2x but very wide range. Other rows have
        # less raw momentum but stronger range-normalized progress.
        close = 20 if i == 0 else 15
        high = 100 if i == 0 else max(20, opening)
        oi = "" if missing_oi and i == 0 else "2000"
        rows.append(f"{day},A{i:02d},2026-01-29,100,CE,{opening},{close},{high},5,1000,{oi}\n")
    return (HEADER + "".join(rows)).encode()


def test_range_normalization_and_tie_break_are_prior_only():
    result = rank(snapshot("2026-01-05"), date(2026,1,5), date(2026,1,6))
    assert [r["symbol"] for r in result["selected"]] == ["A01", "A02"]
    assert len(result["eligible"]) == 20
    assert result["expected_range"] is None and result["forward_issued"] is False


def test_outcome_changes_score_but_cannot_change_selection():
    before = snapshot("2026-01-05")
    first = evaluate(before, snapshot("2026-01-06",future_open=20),date(2026,1,5),date(2026,1,6))
    second = evaluate(before, snapshot("2026-01-06",future_open=60),date(2026,1,5),date(2026,1,6))
    assert first["variant"]["selected"] == second["variant"]["selected"] == 2
    assert first["variant"]["hits"] == 0 and second["variant"]["hits"] == 2
    assert second["same_universe_momentum"]["selected"] == 2
    assert second["variant"]["assumed_cost_stress_mean_return_pct"]["100"] == 299
    assert second["orders_allowed"] is False and second["cost_and_fill_proof"] == "NOT_PROVEN"


def test_missing_open_interest_is_counted_and_never_imputed():
    result = rank(snapshot("2026-01-05",missing_oi=True),date(2026,1,5),date(2026,1,6))
    assert len(result["eligible"]) == 19 and len(result["selected"]) == 1
    assert result["rejected"]["MISSING_OR_INVALID_FEATURE"] == 1
