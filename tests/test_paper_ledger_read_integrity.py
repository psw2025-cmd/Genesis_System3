"""A corrupt PAPER ledger must not appear to contain zero trades."""
import pytest

from dashboard.backend.paper_pipeline_v8 import (
    _pipeline_paths, _read_jsonl, build_pipeline_status,
)


def test_corrupt_ledger_read_raises_instead_of_silently_returning_empty(tmp_path):
    path = tmp_path / "paper_orders.jsonl"
    path.write_text('{"paper_order_id":"one"}\n{corrupt\n')
    with pytest.raises(ValueError, match="PAPER_LEDGER_CORRUPT"):
        _read_jsonl(path)


def test_paper_status_reports_corruption_as_not_verified(tmp_path):
    paths = _pipeline_paths(tmp_path)
    paths["orders"].parent.mkdir(parents=True)
    paths["orders"].write_text('{"paper_order_id":"one"}\n{corrupt\n')
    status = build_pipeline_status(tmp_path)
    assert status["status"] == "NOT_VERIFIED"
    assert status["ledger_integrity"] == "FAIL"
    assert status["ledger_counts"] is None
    assert status["recent_paper_orders"] == []
    assert "PAPER_LEDGER_CORRUPT" in status["reason_if_unverified"]


def test_paper_status_counts_valid_ledger_and_recent_rows(tmp_path):
    paths = _pipeline_paths(tmp_path)
    paths["orders"].parent.mkdir(parents=True)
    paths["orders"].write_text('{"paper_order_id":"one"}\n{"paper_order_id":"two"}\n')
    status = build_pipeline_status(tmp_path)
    assert status["ledger_counts"]["paper_orders"] == 2
    assert len(status["recent_paper_orders"]) == 2
