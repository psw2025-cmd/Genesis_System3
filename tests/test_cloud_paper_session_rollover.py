"""Regression: paper positions, history and IDs must survive a new session.

Run: python -m pytest -q tests/test_cloud_paper_session_rollover.py
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from dashboard.backend.cloud_paper_engine import CloudPaperEngine


IST = timezone(timedelta(hours=5, minutes=30))


def test_new_session_preserves_unsettled_positions_and_audit_history():
    engine = object.__new__(CloudPaperEngine)
    engine.session_date = "2026-11-06"
    engine.seq = 42
    engine.open_positions = [{"position_id": "POS_0042", "status": "OPEN"}]
    engine.closed_positions = [{"position_id": "POS_0041", "status": "CLOSED"}]

    with patch(
        "dashboard.backend.cloud_paper_engine._now_ist",
        return_value=datetime(2026, 11, 9, 9, 15, tzinfo=IST),
    ):
        engine._reset_if_new_day()

    assert engine.session_date == "2026-11-09"
    assert engine.seq == 42
    assert engine.open_positions == [{"position_id": "POS_0042", "status": "OPEN"}]
    assert engine.closed_positions == [{"position_id": "POS_0041", "status": "CLOSED"}]


def test_same_session_keeps_existing_state():
    engine = object.__new__(CloudPaperEngine)
    engine.session_date = "2026-11-09"
    engine.seq = 12
    engine.open_positions = [{"position_id": "POS_0012"}]
    engine.closed_positions = []

    with patch(
        "dashboard.backend.cloud_paper_engine._now_ist",
        return_value=datetime(2026, 11, 9, 15, 15, tzinfo=IST),
    ):
        engine._reset_if_new_day()

    assert engine.seq == 12
    assert len(engine.open_positions) == 1
