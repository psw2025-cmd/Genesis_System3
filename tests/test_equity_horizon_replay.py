"""Date-frozen equity decisions and distinct horizon observations."""
from datetime import date
from scripts.equity_horizon_replay import replay

HEADER = b"TradDt,ISIN,TckrSymb,SctySrs,ClsPric,TtlTradgVol\n"


def market(day, first, second):
    return (HEADER + (f"{day},IN0000000001,A,EQ,{first},20000\n"
                      f"{day},IN0000000002,B,EQ,{second},10000\n").encode())


def test_future_price_changes_outcome_but_cannot_change_picks():
    first = (date(2026, 9, 11), market("2026-09-11", 10, 10))
    last = (date(2026, 9, 18), market("2026-09-18", 25, 10))
    changed = (date(2026, 9, 18), market("2026-09-18", 5, 10))
    a = replay([first, last], top_k=1)["decisions"][0]
    b = replay([first, changed], top_k=1)["decisions"][0]
    assert a["selected_keys_sha256"] == b["selected_keys_sha256"]
    assert a["horizons"]["7"]["at_least_2x"] == 1
    assert b["horizons"]["7"]["at_least_2x"] == 0
    assert a["horizons"]["14"]["status"] == "MISSING_TARGET_SESSION"
    assert a["horizons"]["365"]["status"] == "MISSING_TARGET_SESSION"


def test_report_never_calls_raw_prices_adjusted_performance():
    first = (date(2026, 9, 11), market("2026-09-11", 10, 10))
    last = (date(2026, 9, 18), market("2026-09-18", 25, 10))
    result = replay([first, last], top_k=1)
    assert result["adjusted_return_proven"] is False
    assert result["forecast_accuracy_proven"] is False
    assert result["company_equity_classification_proven"] is False
    assert result["instrument_scope"] == "NSE_EQ_SERIES_MIXED_INSTRUMENTS"
    assert result["decisions"][0]["horizons"]["7"]["status"] == "UNADJUSTED_RESEARCH_ONLY"
