"""Fully offline receipts; no market feed or broker credentials."""
import csv
import hashlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from dashboard.backend.autonomous_paper_core import (
    MasterPaperLedger, PaperEvidenceError, estimate_costed_paper_pnl,
)
from scripts.paper_ledger_reconciliation_export import generate_receipt, publish, main

IST = timezone(timedelta(hours=5, minutes=30))
T0 = datetime(2026, 11, 9, 10, 0, tzinfo=IST)
def at(minutes=0):
    return (T0 + timedelta(minutes=minutes)).isoformat()


def position(name="PAPER-REPORT-1"):
    return {"position_id": name, "underlying": "NIFTY", "option_type": "CE",
            "strike": 25000, "qty": 25, "entry_price": 100.0,
            "current_price": 100.0, "timestamp": at(), "status": "OPEN",
            "market_data_source": "SYNTHETIC_REPLAY_TEST"}


def test_closed_trade_export_hash_chain_and_readback(tmp_path):
    db = tmp_path / "ledger.db"
    master = MasterPaperLedger(db)
    p = position()
    assert master.record_open(p, at())
    net = estimate_costed_paper_pnl(100.0, 110.0, 25)
    assert master.record_close(dict(p, exit_price=110.0, realized_pnl=net), at(12))
    receipt = publish(db, tmp_path / "receipt")
    assert receipt["status"] == "PASS_HASH_VERIFIED_PAPER_SIMULATION_ONLY"
    assert receipt["ledger_hash_chain_verified"] is True
    assert receipt["ledger_event_count"] == 6
    assert receipt["closed_positions"] == 1
    assert receipt["real_broker_orders_count_verified"] is False
    assert receipt["independent_market_outcome_count"] == 0
    folder = tmp_path / "receipt"
    rows = list(csv.DictReader((folder / "paper_trades.csv").open()))
    daily = list(csv.DictReader((folder / "paper_daily.csv").open()))
    assert len(rows) == len(daily) == 1
    assert rows[0]["outcome_validation_status"] == "NOT_VERIFIED"
    assert rows[0]["paper_fill_mode"] == "SIMULATED_PAPER_FILL_NOT_BROKER"
    assert float(rows[0]["estimated_net_pnl_inr"]) == net
    assert daily[0]["exit_day_utc"] == "2026-11-09"
    assert float(daily[0]["simulated_net_pnl_inr"]) == net
    assert json.loads((folder / "paper_receipt.json").read_text()) == receipt
    assert hashlib.sha256((folder / "paper_trades.csv").read_bytes()).hexdigest() == receipt["trades_csv_sha256"]


def test_open_only_report_never_fabricates_realized_pnl(tmp_path):
    db = tmp_path / "open.db"
    MasterPaperLedger(db).record_open(position(), at())
    manifest, trades, daily = generate_receipt(db)
    assert manifest["open_positions"] == 1
    assert manifest["closed_positions"] == 0
    assert manifest["independent_market_outcome_count"] == 0
    assert list(csv.DictReader(trades.splitlines()))[0]["estimated_net_pnl_inr"] == ""
    assert list(csv.DictReader(daily.splitlines())) == []


def test_missing_or_corrupt_master_ledger_fail_closed_without_artifact(tmp_path):
    missing = tmp_path / "missing.db"
    output = tmp_path / "reports"
    with pytest.raises(PaperEvidenceError, match="MISSING"):
        publish(missing, output)
    assert not missing.exists() and not output.exists()
    db = tmp_path / "ledger.db"
    master = MasterPaperLedger(db)
    master.record_open(position(), at())
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE events SET payload='{}' WHERE event_type='PAPER_POSITION_OPENED'")
    with pytest.raises(PaperEvidenceError, match="HASH_MISMATCH"):
        publish(db, output)
    assert not output.exists()


def test_legacy_snapshot_export_is_blocked_not_upgraded(tmp_path):
    db = tmp_path / "legacy.db"
    master = MasterPaperLedger(db)
    master.import_legacy_once([], [{"position_id": "LEGACY-1", "status": "CLOSED",
                                   "realized_pnl": 60000.0}], at())
    receipt, trades, daily = generate_receipt(db)
    assert receipt["status"] == "BLOCKED_LEGACY_NOT_VERIFIED"
    assert receipt["legacy_unverified"] is True
    assert receipt["closed_positions"] == 1
    assert list(csv.DictReader(trades.splitlines()))[0]["estimated_net_pnl_inr"] == ""
    assert list(csv.DictReader(daily.splitlines())) == []


def test_broker_api_not_imported_and_manifest_is_provenance_only():
    from pathlib import Path
    script = Path(__file__).resolve().parents[1] / "scripts/paper_ledger_reconciliation_export.py"
    source = script.read_text()
    for forbidden in ("requests.post", "dhan.place_order", "DhanLogin", "broker_order_count: 0"):
        assert forbidden not in source

def test_untrusted_position_id_cannot_inject_spreadsheet_formula(tmp_path):
    db = tmp_path / "spreadsheet_safe.db"
    master = MasterPaperLedger(db)
    assert master.record_open(position(name="=1+1"), at())
    receipt, trades, _ = generate_receipt(db)
    row = list(csv.DictReader(trades.splitlines()))[0]
    assert row["position_id"] == "'=1+1"
    assert receipt["real_broker_orders_count_verified"] is False
