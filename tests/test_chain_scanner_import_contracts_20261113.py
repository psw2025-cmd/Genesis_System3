"""Regression proofs for chain snapshot and Moneycontrol OPTSTK contract."""
from __future__ import annotations

import copy
import math

import pytest

from dashboard.backend.chain_adapter import normalize_index_chain_exchange
from dashboard.backend.contract_gain_scanner import equity_gainer_seed_symbols


def test_closed_dhan_snapshot_does_not_become_live_or_fresh():
    raw = {
        "underlying": "NIFTY", "contracts": [{"strike": 23000, "option_type": "CE"}],
        "spot": 23100, "status": "MARKET_CLOSED_DHAN_SNAPSHOT",
        "data_source": "dhan", "stale": False, "live": True,
        "fetched_at_utc": "2026-11-12T09:59:00Z",
    }
    before = copy.deepcopy(raw)
    actual = normalize_index_chain_exchange(raw, "nifty")
    assert raw == before
    assert actual["underlying"] == "NIFTY"
    assert actual["total_contracts"] == 1
    assert actual["live"] is False
    assert actual["stale"] is True
    assert actual["verification_status"] == "DHAN_EOD_SNAPSHOT"
    assert actual["fetched_at_utc"] == before["fetched_at_utc"]
    assert actual.get("freshness_seconds") is None


@pytest.mark.parametrize("invalid", [None, [], "invalid", 123])
def test_invalid_payload_is_non_live_and_unverified(invalid):
    result = normalize_index_chain_exchange(invalid, "BANKNIFTY")
    assert result["total_contracts"] == 0
    assert result["spot"] == 0
    assert result["live"] is False
    assert result["verification_status"] == "NOT_VERIFIED"


@pytest.mark.parametrize("source", ["mock", "yahoo", "csv_fallback", "unknown"])
def test_non_broker_sources_never_upgrade_to_verified(source):
    result = normalize_index_chain_exchange({
        "contracts": [{"option_type": "PE"}], "spot": 500,
        "data_source": source, "live": True
    }, "SENSEX")
    assert result["verification_status"] == "NOT_VERIFIED"
    assert result["stale"] is True
    assert result["live"] is False


def test_empty_chain_does_not_manufacture_rows_or_spot():
    result = normalize_index_chain_exchange({
        "total_contracts": 219, "contracts": [],
        "spot": float("nan"), "data_source": "dhan"
    }, "NIFTY")
    assert result["total_contracts"] == 0
    assert result["spot"] == 0
    assert result["live"] is False


def test_open_market_dhan_source_preserves_producer_freshness():
    result = normalize_index_chain_exchange({
        "contracts": [{"option_type": "CE"}], "spot": 23000,
        "data_source": "dhan", "status": "MARKET_OPEN",
        "live": True, "stale": False,
        "snapshot_age_seconds": 11.0,
    }, "NIFTY")
    assert result["live"] is True
    assert result["stale"] is False
    assert result["snapshot_age_seconds"] == 11.0


def _mock_master(monkeypatch, payload):
    from core.brokers.dhan import equity_fo_universe
    monkeypatch.setattr(equity_fo_universe, "load_equity_fo_universe", lambda: payload)


def test_equity_moneycontrol_hints_must_be_verified_fo(monkeypatch):
    _mock_master(monkeypatch, {
        "implemented": True,
        "underlyings": ["RELIANCE", "INFY", "TCS"],
        "priority_underlyings": ["TCS", "INFY", "RELIANCE"],
    })
    result = equity_gainer_seed_symbols([
        {"symbol": "CASH_ONLY"}, {"underlying": "reliance"},
        {"ticker": "INFY"}, {"underlying": "RELIANCE"},
    ], limit=3)
    assert result == ["RELIANCE", "INFY", "TCS"]


def test_no_fo_master_does_not_claim_coverage(monkeypatch):
    _mock_master(monkeypatch, {
        "implemented": False, "underlyings": [],
        "priority_underlyings": ["RELIANCE"],
    })
    assert equity_gainer_seed_symbols([{"symbol": "RELIANCE"}], limit=8) == []


def test_malformed_market_data_is_ignored_without_crashing(monkeypatch):
    _mock_master(monkeypatch, {
        "implemented": True, "underlyings": ["TCS"],
        "priority_underlyings": ["TCS"],
    })
    assert equity_gainer_seed_symbols([None, 100, {"symbol": None}], limit=8) == ["TCS"]


def test_import_contract_is_present_without_network_call():
    from dashboard.backend.chain_adapter import normalize_index_chain_exchange as normalizer
    from dashboard.backend.contract_gain_scanner import equity_gainer_seed_symbols as selector
    assert callable(normalizer)
    assert callable(selector)
