"""Offline deterministic proof for 200+ stock-option paced scanner coverage."""
from pathlib import Path

import pytest

from dashboard.backend.equity_rotation_policy import choose_equity_gainer_symbol as choose


def test_all_219_symbols_eventually_visited_without_dhan_calls():
    universe = [f"STOCK{i:03d}" for i in range(219)]
    priority = universe[:12]
    series = [choose(i, universe, priority) for i in range(4 * 219)]
    assert set(universe).issubset(series)
    assert len(series) == 4 * 219


def test_missing_first_priority_cannot_starve_subsequent_equities():
    universe = ["LUPIN", "RELIANCE", "INFY", "HDFCBANK", "TCS"]
    selected = [choose(i, universe, ["LUPIN", "RELIANCE"]) for i in range(40)]
    assert set(selected) == set(universe)
    assert selected.count("LUPIN") < len(selected)


def test_priority_every_fourth_turn_full_universe_advances():
    universe = ["AAA", "BBB", "CCC", "DDD"]
    priority = ["AAA"]
    assert [choose(i, universe, priority) for i in range(8)] == [
        "AAA", "AAA", "BBB", "CCC", "AAA", "DDD", "AAA", "BBB"
    ]


def test_priorities_not_in_master_are_not_scanned_if_master_available():
    universe = ["NIFTYCO", "RELIANCE"]
    selected = [choose(i, universe, ["DELISTED", "RELIANCE"]) for i in range(20)]
    assert "DELISTED" not in selected
    assert set(selected) == set(universe)


def test_no_master_degrades_to_priority_round_robin_without_coverage_claim():
    assert [choose(i, [], ["LUPIN", "INFY"]) for i in range(5)] == [
        "LUPIN", "INFY", "LUPIN", "INFY", "LUPIN"
    ]
    assert choose(0, [], []) is None


def test_symbol_normalization_does_not_duplicate_or_mutate_input():
    u = [" reliance ", "RELIANCE", "tcs"]
    p = [" TCS ", "TCS"]
    assert set(choose(i, u, p) for i in range(20)) == {"RELIANCE", "TCS"}
    assert u == [" reliance ", "RELIANCE", "tcs"]


@pytest.mark.parametrize("cursor", [-1, 1.5, "1", None])
def test_invalid_cursor_fails_closed(cursor):
    with pytest.raises(ValueError):
        choose(cursor, ["RELIANCE"], [])


def test_app_wiring_stays_cache_only_and_paced():
    app = (Path(__file__).resolve().parents[1] /
           "dashboard" / "backend" / "app.py").read_text(encoding="utf-8")
    block = app.split("def _next_equity_gainer_symbol()", 1)[1].split(
        "def _build_market_top_from_chain_cache", 1
    )[0]
    assert "choose_equity_gainer_symbol" in block
    assert "_cached_equity_fo_underlyings()" in block
    assert "return symbol" in block
    assert "_get_chain_uncached" not in block
    assert "_warm_one_index_chain" not in block
    report_block = app.split("def _build_market_top_from_chain_cache(", 1)[1].split(
        "def _cached_equity_paper_seed_chains", 1
    )[0]
    assert "warmed_symbols = list(_PUSHED_CHAIN_CACHE)" in report_block
    assert "_usable_chain_snapshot(chain)" in report_block
    assert "_get_chain_uncached" not in report_block
    assert "await " not in report_block
