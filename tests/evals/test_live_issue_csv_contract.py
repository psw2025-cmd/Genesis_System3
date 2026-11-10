import csv
from pathlib import Path

import pytest

from scripts import system3_live_issue_ledger as ledger


def _event(message="Chrome error", **overrides):
    row = {
        "severity": "MEDIUM",
        "category": "BROWSER_TOOLING",
        "keyword": "ERROR",
        "status": "OPEN",
        "source_type": "TERMINAL",
        "source_path": "terminal.log",
        "message": message,
        "impact": "Browser proof may be incomplete",
        "next_action": "Classify and retry",
        "owner": "SYSTEM3_CONTINUOUS_CLOSURE",
    }
    row.update(overrides)
    return row


def test_csv_is_excel_readable_upserts_history_and_redacts_secrets(tmp_path):
    target = tmp_path / "issues.csv"
    assert ledger.write_events(target, [_event("ERROR access_token=do-not-store")]) == "CSV_UPDATED"
    assert ledger.write_events(target, [_event("ERROR access_token=do-not-store", status="RESOLVED", resolution_evidence="driver restored")]) == "CSV_UPDATED"
    with target.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["status"] == "RESOLVED"
    assert rows[0]["occurrence_count"] == "2"
    assert rows[0]["resolution_evidence"] == "driver restored"
    assert "do-not-store" not in target.read_text(encoding="utf-8-sig")
    assert "[REDACTED]" in rows[0]["message"]
    assert b"\r\n" not in target.read_bytes()


def test_excel_lock_spools_and_flushes_without_losing_event(tmp_path, monkeypatch):
    target = tmp_path / "issues.csv"
    real_replace = ledger.os.replace
    monkeypatch.setattr(ledger.os, "replace", lambda *_: (_ for _ in ()).throw(PermissionError("locked")))
    assert ledger.write_events(target, [_event()]) == "SPOOLED_FILE_LOCKED"
    assert target.with_suffix(".csv.pending.jsonl").exists()
    monkeypatch.setattr(ledger.os, "replace", real_replace)
    assert ledger.write_events(target, []) == "CSV_UPDATED"
    assert target.exists()
    assert not target.with_suffix(".csv.pending.jsonl").exists()


def test_user_question_required_for_human_input():
    with pytest.raises(ValueError, match="user_input_question"):
        ledger.normalize(_event(user_input_required="YES"))


def test_scanner_records_keyword_with_context_but_does_not_claim_root_cause(tmp_path):
    source = tmp_path / "terminal.log"
    source.write_text("ok\nPHONE_REGISTRATION_ERROR from chrome background service\n", encoding="utf-8")
    events = ledger.scan_files([source])
    assert len(events) == 1
    assert events[0]["keyword"] == "PHONE_REGISTRATION_ERROR"
    assert "not proof" in events[0]["impact"]


def test_default_csv_path_is_canonical_audit_location():
    assert ledger.DEFAULT_CSV == ledger.ROOT / "audit" / "live_agent_issue_ledger" / "SYSTEM3_LIVE_UNRESOLVED_ISSUES.csv"
