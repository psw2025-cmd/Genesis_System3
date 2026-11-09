"""Regression: cached market display is not permission for automatic paper fills."""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from dashboard.backend.paper_feed_admission import (
    admit_paper_chains, missing_open_position_quotes,
)


def chain(**overrides):
    base = {
        "underlying": "NIFTY",
        "spot": 25000.0,
        "live": True,
        "stale": False,
        "status": "MARKET_OPEN",
        "snapshot_age_seconds": 1.0,
        "data_source": "dhan",
        "source": "index_micro",
        "contracts": [{
            "option_type": "CE", "strike": 25000.0, "ltp": 100.0,
            "previous_close_price": 75.0, "volume": 300,
        }],
    }
    base.update(overrides)
    return base


def test_fresh_live_dhan_push_is_admitted_without_broker_calls():
    accepted, blocked = admit_paper_chains([chain()])
    assert len(accepted) == 1 and not blocked
    assert accepted[0]["contracts"][0]["ltp"] == 100.0
    assert len(accepted[0]["contracts"]) == 1


@pytest.mark.parametrize(("change", "expected"), [
    ({"stale": True}, "CHAIN_NOT_FRESH_LIVE"),
    ({"live": False}, "CHAIN_NOT_FRESH_LIVE"),
    ({"live": None}, "CHAIN_NOT_FRESH_LIVE"),
    ({"snapshot_age_seconds": None}, "MISSING_OR_STALE_TRANSPORT_TIMESTAMP"),
    ({"snapshot_age_seconds": -1}, "MISSING_OR_STALE_TRANSPORT_TIMESTAMP"),
    ({"snapshot_age_seconds": 90.01}, "MISSING_OR_STALE_TRANSPORT_TIMESTAMP"),
    ({"snapshot_age_seconds": float("inf")}, "MISSING_OR_STALE_TRANSPORT_TIMESTAMP"),
    ({"snapshot_age_seconds": float("nan")}, "MISSING_OR_STALE_TRANSPORT_TIMESTAMP"),
    ({"data_source": "DHAN_REPLAY_SYNTHETIC"}, "SOURCE_NOT_DHAN_LIVE"),
    ({"data_source": "CSV_FALLBACK"}, "SOURCE_NOT_DHAN_LIVE"),
    ({"data_source": "Moneycontrol"}, "SOURCE_NOT_DHAN_LIVE"),
    ({"data_source": "real_only_no_proof"}, "SOURCE_NOT_DHAN_LIVE"),
    ({"source": "Dhan_last_good_snapshot"}, "SOURCE_NOT_DHAN_LIVE"),
    ({"source": "synthetic_fixture"}, "SOURCE_NOT_DHAN_LIVE"),
    ({"status": "MARKET_CLOSED_DHAN_SNAPSHOT"}, "SOURCE_NOT_DHAN_LIVE"),
    ({"spot": 0}, "INVALID_SPOT"),
    ({"spot": float("nan")}, "INVALID_SPOT"),
    ({"contracts": []}, "NO_USABLE_OPTION_QUOTES"),
])
def test_paper_entry_rejects_untrusted_market_frames(change, expected):
    accepted, rejected = admit_paper_chains([chain(**change)])
    assert not accepted
    assert rejected[0]["reason"] == expected


@pytest.mark.parametrize("bad", [
    {"strike": 0},
    {"ltp": float("nan")},
    {"ltp": float("inf")},
    {"ltp": -3},
    {"ltp": "bad"},
    {"previous_close_price": "not-a-number"},
    {"gain_pct": "invalid"},
    {"oi_change": object()},
    {"volume": float("inf")},
    {"option_type": "FUTURE"},
])
def test_bad_quote_cannot_drive_a_paper_order(bad):
    invalid = chain()["contracts"][0].copy()
    invalid.update(bad)
    accepted, rejected = admit_paper_chains([chain(contracts=[invalid])])
    assert accepted == []
    assert rejected[0]["reason"] == "NO_USABLE_OPTION_QUOTES"


def test_bad_contract_removed_but_valid_contract_can_continue():
    bad = dict(chain()["contracts"][0], ltp=float("nan"))
    accepted, rejected = admit_paper_chains([
        chain(contracts=[bad, chain()["contracts"][0]]),
    ])
    assert not rejected and len(accepted[0]["contracts"]) == 1


def test_missing_open_quote_blocks_all_entries_marks_and_exits():
    valid = chain()
    accepted, _ = admit_paper_chains([valid])
    open_position = {"underlying": "BANKNIFTY", "strike": 51000,
                     "option_type": "PE", "position_id": "PRIVATE_ID"}
    problems = missing_open_position_quotes([open_position], accepted)
    assert problems == ["MISSING_CURRENT_QUOTE"]
    assert "PRIVATE_ID" not in str(problems)


def test_fresh_quote_for_all_existing_positions_allows_tick():
    accepted, _ = admit_paper_chains([chain()])
    positions = [{"underlying": "NIFTY", "strike": 25000, "option_type": "CE"}]
    assert missing_open_position_quotes(positions, accepted) == []


def test_no_fresh_feed_is_not_a_market_outcome():
    accepted, rejected = admit_paper_chains([chain(stale=True)])
    assert not accepted and rejected
    assert missing_open_position_quotes([
        {"underlying": "NIFTY", "strike": 25000, "option_type": "CE"},
    ], accepted)


def test_freshness_limit_cannot_be_relaxed_beyond_90_seconds():
    with pytest.raises(ValueError, match="PAPER_FEED_MAX_AGE_INVALID"):
        admit_paper_chains([chain()], max_age_seconds=300)


def test_both_automatic_and_api_tick_paths_use_gate():
    """Static integration wiring without importing a network-heavy FastAPI app."""
    app = (Path(__file__).resolve().parents[1] /
           "dashboard" / "backend" / "app.py").read_text(encoding="utf-8")
    loop = app.split("async def cloud_paper_trading_loop():", 1)[1]
    loop = loop.split("def _refresh_spot_prices_blocking()", 1)[0]
    endpoint = app.split('async def paper_engine_tick(', 1)[1]
    endpoint = endpoint.split('@app.get("/api/paper/positions")', 1)[0]
    for segment in (loop, endpoint):
        assert "admit_paper_chains(chains)" in segment
        assert "missing_open_position_quotes(" in segment
        assert "engine.step(fresh_chains," in segment
        assert "if not fresh_chains or uncovered:" in segment


def test_gate_has_no_order_placement_or_network_imports():
    source = (Path(__file__).resolve().parents[1] /
              "dashboard" / "backend" / "paper_feed_admission.py").read_text(
                  encoding="utf-8")
    assert "import requests" not in source
    assert "import dhanhq" not in source
    assert "urlopen(" not in source
    assert ("place_" + "order(") not in source
