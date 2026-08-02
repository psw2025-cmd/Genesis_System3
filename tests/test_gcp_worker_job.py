import pytest

from scripts import gcp_worker_job


def test_smoke_job_is_bounded_and_analyzer_only(monkeypatch):
    monkeypatch.setenv("SYSTEM3_JOB_PUBLISH_STATE", "0")
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "0")
    monkeypatch.setenv("SYSTEM3_LIVE_TRADING_ALLOWED", "0")

    result = gcp_worker_job.run_job("smoke")

    assert result["status"] == "PASS"
    assert result["mode"] == "PAPER"
    assert result["live_trading_enabled"] is False


def test_job_rejects_any_live_flag(monkeypatch):
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "1")
    monkeypatch.setenv("SYSTEM3_LIVE_TRADING_ALLOWED", "0")
    monkeypatch.setenv("SYSTEM3_JOB_PUBLISH_STATE", "0")

    with pytest.raises(RuntimeError, match="forbidden"):
        gcp_worker_job.run_job("smoke")


def test_paper_job_needs_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "0")
    monkeypatch.setenv("SYSTEM3_LIVE_TRADING_ALLOWED", "0")
    monkeypatch.setenv("SYSTEM3_JOB_PUBLISH_STATE", "0")
    monkeypatch.setenv("SYSTEM3_ENABLE_PAPER_JOB", "0")

    with pytest.raises(RuntimeError, match="SYSTEM3_ENABLE_PAPER_JOB=1"):
        gcp_worker_job.run_job("paper-pipeline-v8")
