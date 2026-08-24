"""Fail-closed contracts for Dhan NSE/BSE cash and stock-option coverage."""

from __future__ import annotations

from core.brokers.dhan.equity_fo_universe import (
    load_equity_fo_universe,
    load_equity_market_coverage,
)
from dashboard.backend import contract_gain_scanner


def test_official_synced_master_is_preferred_over_bundled_fallback(monkeypatch, tmp_path):
    import csv
    from core.brokers.dhan import equity_fo_universe as universe_mod

    path = tmp_path / "api-scrip-master.csv"
    fields = [
        "SEM_EXM_EXCH_ID", "SEM_SEGMENT", "SEM_SMST_SECURITY_ID",
        "SEM_INSTRUMENT_NAME", "SEM_TRADING_SYMBOL", "SEM_OPTION_TYPE",
    ]
    rows = [
        ["NSE", "E", "1", "EQUITY", "ALPHA", ""],
        ["BSE", "E", "2", "EQUITY", "ALPHA", ""],
        ["NSE", "D", "3", "OPTSTK", "ALPHA-Jun2026-100-CE", "CE"],
        ["NSE", "D", "4", "OPTSTK", "ALPHA-Jun2026-100-PE", "PE"],
        ["BSE", "D", "5", "OPTSTK", "ALPHA-Jun2026-100-CE", "CE"],
        ["BSE", "D", "6", "OPTSTK", "ALPHA-Jun2026-100-PE", "PE"],
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        writer.writerows(rows)

    monkeypatch.setattr(universe_mod, "resolve_master_csv", lambda: path)
    universe_mod.load_equity_market_coverage.cache_clear()
    universe_mod.load_equity_fo_universe.cache_clear()
    try:
        coverage = universe_mod.load_equity_market_coverage()
        universe = universe_mod.load_equity_fo_universe()
        assert coverage["source"] == "api-scrip-master.csv"
        assert coverage["source_mode"] == "OFFICIAL_SYNC"
        assert coverage["stock_options"]["union_underlying_count"] == 1
        assert universe["underlyings"] == ["ALPHA"]
    finally:
        universe_mod.load_equity_market_coverage.cache_clear()
        universe_mod.load_equity_fo_universe.cache_clear()


def test_security_master_accounts_for_nse_bse_cash_and_both_option_sides():
    coverage = load_equity_market_coverage()

    assert coverage["implemented"] is True
    assert coverage["source"] in {"security_id_list.csv", "api-scrip-master.csv", "api-scrip-master-detailed.csv"}
    assert coverage["source_mode"] in {"OFFICIAL_SYNC", "BUNDLED_FALLBACK"}
    assert coverage["reliance_only"] is False
    assert coverage["cash"]["NSE"]["instrument_count"] > 1_000
    assert coverage["cash"]["BSE"]["instrument_count"] > 1_000
    assert coverage["cash"]["NSE"]["symbol_count"] > 1_000
    assert coverage["cash"]["BSE"]["symbol_count"] > 1_000
    assert coverage["stock_options"]["NSE"]["underlying_count"] > 100
    assert coverage["stock_options"]["BSE"]["underlying_count"] > 100
    assert coverage["stock_options"]["NSE"]["ce_contracts"] > 0
    assert coverage["stock_options"]["NSE"]["pe_contracts"] > 0
    assert coverage["stock_options"]["BSE"]["ce_contracts"] > 0
    assert coverage["stock_options"]["BSE"]["pe_contracts"] > 0
    assert coverage["stock_options"]["union_underlying_count"] >= 200
    assert coverage["stock_options"]["underlyings_missing_ce_or_pe"] == []
    assert coverage["scan_plan"]["quote_batch_size"] == 1_000
    assert coverage["scan_plan"]["option_chain_min_gap_seconds"] == 3.0
    assert coverage["scan_plan"]["unbounded_simultaneous_chain_fetch"] is False


def test_existing_option_discovery_is_full_union_not_reliance_only():
    universe = load_equity_fo_universe()
    names = set(universe["underlyings"])
    assert universe["underlying_count"] >= 200
    assert {"RELIANCE", "TCS", "HDFCBANK"}.issubset(names)
    assert universe["exchange_coverage"] == ["BSE_FNO", "NSE_FNO"]


def test_rotating_shards_account_for_every_option_underlying(monkeypatch):
    names = [f"EQ{i:03d}" for i in range(211)]
    monkeypatch.setattr(
        "core.brokers.dhan.equity_fo_universe.load_equity_fo_universe",
        lambda: {"underlyings": names, "priority_underlyings": names[:8]},
    )
    monkeypatch.setattr(contract_gain_scanner, "_SHARD_STATE", contract_gain_scanner._new_shard_state())

    for _ in range(80):
        contract_gain_scanner._equity_scan_universe(limit=12, rotate=True)
        if contract_gain_scanner.equity_shard_coverage()["cycle_complete"]:
            break

    result = contract_gain_scanner.equity_shard_coverage()
    assert result["universe_count"] == 211
    assert result["visited_count"] == 211
    assert result["coverage_pct"] == 100.0
    assert result["cycle_complete"] is True
    assert result["missing_symbols"] == []
    assert result["reliance_only"] is False


def test_prediction_horizons_are_explicit_and_paper_only():
    coverage = load_equity_market_coverage()
    horizons = coverage["prediction_horizons"]
    assert [row["id"] for row in horizons] == [
        "1_week",
        "3_weeks",
        "1_month",
        "3_months",
        "6_months",
        "1_year",
        "2_years",
    ]
    assert all(row["mode"] == "PAPER_RESEARCH_ONLY" for row in horizons)
    assert all(row["outcome_required"] is True for row in horizons)
    assert coverage["learning_contract"]["in_place_champion_mutation"] is False
    assert coverage["learning_contract"]["automatic_live_promotion"] is False
