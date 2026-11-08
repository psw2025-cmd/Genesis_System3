"""Autonomous PAPER lifecycle: deterministic, broker-free, fail-closed proofs."""
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from dashboard.backend.autonomous_paper_core import (
    MasterPaperLedger, PaperEvidenceError, detect_opening_gap,
    estimate_costed_paper_pnl,
)


IST = timezone(timedelta(hours=5, minutes=30))
T0 = datetime(2026, 11, 9, 9, 30, tzinfo=IST)


def stamp(minutes=0):
    return (T0 + timedelta(minutes=minutes)).isoformat()


def position(name="PAPER-1", entry=100.0, qty=25):
    return {
        "position_id": name, "underlying": "NIFTY", "strike": 25000,
        "option_type": "CE", "qty": qty, "entry_price": entry,
        "current_price": entry, "status": "OPEN", "timestamp": stamp(),
        "market_data_source": "SYNTHETIC_TEST",
    }


def closed_position(p, price=110.0, pnl=None):
    if pnl is None:
        pnl = estimate_costed_paper_pnl(p["entry_price"], price, p["qty"])
    return dict(p, status="CLOSED", exit_price=price,
                realized_pnl=pnl, exit_reason="TARGET")


@pytest.mark.parametrize("previous,opening,expected", [
    (100.0, 102.0, "GAP_UP"),
    (100.0, 97.0, "GAP_DOWN"),
    (100.0, 100.2, "FLAT"),
    (100.0, 100.5, "GAP_UP"),
])
def test_opening_gap(previous, opening, expected):
    r = detect_opening_gap(
        session="2026-11-09", previous_close=previous,
        opening_price=opening, opened_at=stamp(), source="EXCHANGE_SESSION_OPEN"
    )
    assert r["direction"] == expected
    assert r["verification_status"] == "SOURCE_REPORTED_NOT_INDEPENDENTLY_VERIFIED"


@pytest.mark.parametrize("prev,opener,source", [
    (0, 105, "EXCHANGE"), (100, -1, "EXCHANGE"),
    (float("nan"), 100, "EXCHANGE"), (100, float("inf"), "EXCHANGE"),
    (100, 105, "SYNTHETIC_REPLAY"),
])
def test_invalid_opening_gap_fails_closed(prev, opener, source):
    with pytest.raises(PaperEvidenceError):
        detect_opening_gap(session="2026-11-09", previous_close=prev,
                           opening_price=opener, opened_at=stamp(), source=source)


def test_open_mark_close_recover_across_instances(tmp_path):
    path = tmp_path / "master.db"
    master = MasterPaperLedger(path)
    p = position()
    assert master.record_open(p, stamp()) is True
    assert master.record_mark(dict(p, current_price=105.0, unrealized_pnl=85), stamp(5))
    assert master.reconcile([p])["status"] == "PASS"
    state = MasterPaperLedger(path).snapshot()
    assert len(state["open_positions"]) == 1
    assert state["open_positions"][0]["current_price"] == 105.0
    closed = closed_position(p)
    assert master.record_close(closed, stamp(12))
    recovered = MasterPaperLedger(path).snapshot()
    assert not recovered["open_positions"]
    assert len(recovered["closed_positions"]) == 1
    assert recovered["closed_positions"][0]["pnl_verification_status"] == "COSTED_SIMULATION_NOT_BROKER_VERIFIED"
    assert master.reconcile([])["status"] == "PASS"
    assert recovered["verified_hash_chain"] is True
    assert recovered["event_count"] == 6


def test_duplicate_retry_is_exactly_once(tmp_path):
    ledger = MasterPaperLedger(tmp_path / "master.db")
    p = position()
    assert ledger.record_open(p, stamp())
    assert not ledger.record_open(p, stamp())
    assert ledger.snapshot()["event_count"] == 3
    assert ledger.record_close(closed_position(p), stamp(12))
    assert not ledger.record_close(closed_position(p), stamp(12))
    assert ledger.snapshot()["event_count"] == 5


def test_tampered_ledger_blocks_all_new_events(tmp_path):
    path = tmp_path / "master.db"
    ledger = MasterPaperLedger(path)
    p = position()
    ledger.record_open(p, stamp())
    with sqlite3.connect(path) as db:
        db.execute("UPDATE events SET payload='{}' WHERE event_type='PAPER_POSITION_OPENED'")
    with pytest.raises(PaperEvidenceError, match="HASH_MISMATCH"):
        ledger.snapshot()
    with pytest.raises(PaperEvidenceError, match="HASH_MISMATCH"):
        ledger.record_open(position("PAPER-2"), stamp(1))


def test_reconciliation_rejects_missing_projection(tmp_path):
    ledger = MasterPaperLedger(tmp_path / "master.db")
    ledger.record_open(position(), stamp())
    assert ledger.reconcile([])["status"] == "BLOCKED"
    assert ledger.reconcile([position("OTHER")])["status"] == "BLOCKED"


def test_outcome_never_fabricates_exchange_truth(tmp_path):
    ledger = MasterPaperLedger(tmp_path / "master.db")
    p = position()
    ledger.record_open(p, stamp())
    with pytest.raises(PaperEvidenceError, match="CLOSED_POSITION"):
        ledger.record_outcome("PAPER-1", reference_price=110, at=stamp(15),
                              source="PAPER_SIMULATION")
    ledger.record_close(closed_position(p), stamp(12))
    observation = ledger.record_outcome("PAPER-1", reference_price=110,
                                        at=stamp(15), source="PAPER_SIMULATION")
    assert observation["validation_status"] == "NOT_VERIFIED"
    assert ledger.learning_proposal(stamp(20))["status"] == "NOT_VERIFIED"
    assert not ledger.learning_proposal(stamp(20))["model_promoted"]


def test_learning_is_shadow_only_with_chronological_holdout(tmp_path):
    ledger = MasterPaperLedger(tmp_path / "master.db")
    for i in range(10):
        p = position(f"PAPER-{i}")
        p["timestamp"] = stamp(i)
        ledger.record_open(p, stamp(i))
        ledger.record_close(closed_position(p), stamp(i + 20))
        row = ledger.record_outcome(
            p["position_id"], reference_price=110, at=stamp(i + 30),
            source="INDEPENDENT_EXCHANGE_SNAPSHOT", reference_id=f"source-{i}")
        assert row["validation_status"] == "SOURCE_ATTESTED"
    proposal = ledger.learning_proposal(stamp(100))
    assert proposal["status"] == "SHADOW_ONLY"
    assert proposal["train_count"] == 8
    assert proposal["holdout_count"] == 2
    assert proposal["model_promoted"] is False


def test_legacy_positions_are_preserved_but_not_verified(tmp_path):
    path = tmp_path / "master.db"
    ledger = MasterPaperLedger(path)
    p = position()
    ledger.import_legacy_once([p], [], stamp())
    state = MasterPaperLedger(path).snapshot()
    assert len(state["open_positions"]) == 1
    assert state["legacy_unverified"] is True
    with pytest.raises(PaperEvidenceError, match="LEGACY_RECONCILIATION_REQUIRED"):
        ledger.record_open(position("PAPER-2"), stamp(1))
    assert ledger.record_close(closed_position(p), stamp(12))
    assert not ledger.snapshot()["open_positions"]


def test_gap_record_is_idempotent_and_tamper_evident(tmp_path):
    ledger = MasterPaperLedger(tmp_path / "master.db")
    gap = detect_opening_gap(session="2026-11-09", previous_close=100,
                             opening_price=97, opened_at=stamp(), source="SESSION_OPEN")
    assert ledger.record_gap("NIFTY", gap)
    assert not ledger.record_gap("NIFTY", gap)
    state = ledger.snapshot()
    assert state["gaps"]["NIFTY"]["direction"] == "GAP_DOWN"
    assert state["event_count"] == 1


def test_invalid_datetime_rejected(tmp_path):
    ledger = MasterPaperLedger(tmp_path / "master.db")
    with pytest.raises(PaperEvidenceError, match="TIMEZONE"):
        ledger.record_open(position(), "2026-11-09T09:15:00")


def test_capital_guard_counts_all_open_positions(tmp_path):
    ledger = MasterPaperLedger(tmp_path / "master.db")
    p = position("A", entry=100.0, qty=300)
    ledger.record_open(p, stamp())
    with pytest.raises(PaperEvidenceError, match="CUMULATIVE_CAPITAL_LIMIT"):
        ledger.record_open(position("B", entry=100.0, qty=250), stamp(1))
    assert len(ledger.snapshot()["open_positions"]) == 1


def test_net_pnl_reconciliation_blocks_fake_profit(tmp_path):
    ledger = MasterPaperLedger(tmp_path / "master.db")
    p = position()
    ledger.record_open(p, stamp())
    bad = closed_position(p)
    bad["realized_pnl"] += 10000
    with pytest.raises(PaperEvidenceError, match="NET_PNL_RECONCILIATION"):
        ledger.record_close(bad, stamp(12))
    assert len(ledger.snapshot()["open_positions"]) == 1
    assert not ledger.snapshot()["closed_positions"]
