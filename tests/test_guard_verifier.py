from pathlib import Path

from scripts.guard_verifier import (
    api_ui_truth,
    latest_firestore_proof,
    reconciliation_negative_control,
    unconditional_gate_passes,
)


def test_api_not_ready_requires_visible_live_off_and_never_live_on():
    safe_ui = "PAPER MODE · LIVE OFF · ML Model Truth · FORWARD PROOF: NOT PROVEN"
    assert api_ui_truth({"ready_for_live": False, "live_trading_enabled": False}, safe_ui)[0]
    assert not api_ui_truth({"ready_for_live": False}, "PAPER MODE · LIVE ON · ML Model Truth · FORWARD PROOF: NOT PROVEN")[0]
    assert not api_ui_truth({"ready_for_live": False}, "PAPER MODE")[0]
    assert not api_ui_truth({"ready_for_live": "false"}, safe_ui)[0]
    assert not api_ui_truth({"ready_for_live": False}, "PAPER MODE · LIVE OFF · ML Model Truth · FORWARD PROOF: REPORTED PASS")[0]


def test_api_ui_guard_rejects_live_authority_even_if_ui_says_off():
    passed, reason = api_ui_truth(
        {"ready_for_live": False, "live_trading_enabled": True}, "PAPER MODE · LIVE OFF"
    )
    assert not passed
    assert reason == "API_SAFETY_FLAG_ENABLED:live_trading_enabled"


def test_firestore_guard_requires_valid_proof_on_latest_session():
    row = {
        "date": "2026-08-11",
        "exchange_session_proof": {
            "verified": True,
            "exchange": "NSE",
            "session_date": "2026-08-11",
            "previous_session_date": "2026-08-10",
            "source_url": "https://www.nseindia.com/all-reports",
        },
    }
    assert latest_firestore_proof([row]) == (True, "LATEST_FIRESTORE_SESSION_PROOF_VERIFIED")
    assert not latest_firestore_proof([])[0]
    stale = dict(row, date="2026-08-12")
    assert not latest_firestore_proof([row, stale])[0]


def test_reconciliation_gate_negative_control_blocks_mismatch_hidden_by_zero_rate():
    assert reconciliation_negative_control() == (True, "MISMATCH_NEGATIVE_CONTROL_BLOCKED")


def test_gate_evaluator_has_no_literal_unconditional_pass():
    assert unconditional_gate_passes() == []

