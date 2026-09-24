"""A fixed ranking must be computed from the previous snapshot only."""
from datetime import date
import pytest
from scripts.cepe_walkforward_baseline import run

HEADER = b"TckrSymb,XpryDt,OptnTp,StrkPric,OpnPric,ClsPric,TradDt,TtlTradgVol\n"


def snapshot(day: str, a_open: int, a_close: int, b_open: int, b_close: int):
    return (HEADER +
            (f"A,2026-09-29,CE,100,{a_open},{a_close},{day},200\n"
             f"B,2026-09-29,PE,200,{b_open},{b_close},{day},200\n").encode())


def test_preceding_session_rank_and_holdout_accounting():
    first = (date(2026, 9, 16), snapshot("2026-09-16", 5, 10, 10, 10))
    second = (date(2026, 9, 17), snapshot("2026-09-17", 40, 10, 10, 10))
    third = (date(2026, 9, 18), snapshot("2026-09-18", 10, 10, 40, 10))
    result = run([first, second, third], top_k=1)
    assert result["train_pairs"][0]["hits"] == 1
    assert result["holdout_pair"]["hits"] == 0
    assert result["holdout_pair"]["missed_winners"] == 1
    assert result["forward_issued_predictions"] == 0


def test_discontinuous_history_rejected():
    first = (date(2026, 9, 1), snapshot("2026-09-01", 5, 10, 10, 10))
    second = (date(2026, 9, 18), snapshot("2026-09-18", 40, 10, 10, 10))
    with pytest.raises(ValueError, match="Gap"):
        run([first, second])


def test_next_day_prices_cannot_change_previous_day_picks():
    first = (date(2026, 9, 17), snapshot("2026-09-17", 5, 10, 10, 10))
    following = (date(2026, 9, 18), snapshot("2026-09-18", 40, 10, 10, 10))
    changed_following = (date(2026, 9, 18),
                         snapshot("2026-09-18", 10, 10, 40, 10))
    original = run([first, following], top_k=1)["holdout_pair"]
    modified = run([first, changed_following], top_k=1)["holdout_pair"]
    assert original["selected_keys_sha256"] == modified["selected_keys_sha256"]
    assert original["hits"] != modified["hits"]
