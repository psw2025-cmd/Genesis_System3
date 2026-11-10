"""Eval specs for autonomous-loop discovered defects (test-first)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dashboard" / "backend"))

from gain_rank_spot_enrichment import (  # noqa: E402
    enrich_gain_rank_rows_with_authenticated_spots,
    is_authenticated_spot_entry,
)


def test_rejects_synthetic_base_spot_lookup():
    assert not is_authenticated_spot_entry(
        {"spot": 24000.0, "source": "BASE_SPOT_PRICES", "status": "SYNTHETIC"}
    )
    assert not is_authenticated_spot_entry({"spot": 24000.0, "source": "synthetic"})


def test_accepts_market_closed_dhan_snapshot():
    assert is_authenticated_spot_entry(
        {
            "spot": 24366.0,
            "source": "dhan",
            "status": "MARKET_CLOSED_DHAN_SNAPSHOT",
        }
    )


def test_enrich_fills_missing_spot_from_authenticated_snapshot_only():
    rows = [
        {"underlying": "NIFTY", "gain_pct": 12.0},
        {"underlying": "FINNIFTY", "gain_pct": 8.0, "spot_price": 0},
        {"underlying": "BANKNIFTY", "gain_pct": 5.0, "spot_price": 52000.0},
    ]
    lookup = {
        "NIFTY": {"spot": 24366.0, "status": "MARKET_CLOSED_DHAN_SNAPSHOT", "source": "dhan"},
        "FINNIFTY": {"spot": 24100.0, "status": "MARKET_CLOSED_DHAN_SNAPSHOT", "source": "dhan"},
        "BANKNIFTY": {"spot": 1.0, "source": "synthetic", "status": "SYNTHETIC"},  # must not overwrite
    }
    out = enrich_gain_rank_rows_with_authenticated_spots(rows, lookup)
    by_u = {r["underlying"]: r for r in out}
    assert by_u["NIFTY"]["spot_price"] == 24366.0
    assert "SNAPSHOT" in by_u["NIFTY"]["spot_price_source"].upper() or by_u["NIFTY"]["spot_price_source"]
    assert by_u["FINNIFTY"]["spot_price"] == 24100.0
    # Existing positive spot preserved; synthetic lookup must not replace it
    assert by_u["BANKNIFTY"]["spot_price"] == 52000.0


def test_enrich_leaves_blank_when_no_authenticated_spot():
    rows = [{"underlying": "MIDCPNIFTY", "gain_pct": 1.0}]
    out = enrich_gain_rank_rows_with_authenticated_spots(rows, {})
    assert "spot_price" not in out[0] or not out[0].get("spot_price")
