from pathlib import Path

from dashboard.backend.paper_pipeline_v8 import BLOCK_FORECAST_ONLY_CASH, BLOCK_NO_LIVE_QUOTE, build_pipeline_status, run_self_test


def test_core_pipeline_v8_selftest(tmp_path):
    result = run_self_test(tmp_path)
    assert result["status"] == "PASS"
    assert (tmp_path / "summary.md").exists()


def test_block_reason_constants():
    assert BLOCK_FORECAST_ONLY_CASH == "FORECAST_ONLY_CASH_EQUITY"
    assert BLOCK_NO_LIVE_QUOTE == "NO_LIVE_OPTION_QUOTE"
