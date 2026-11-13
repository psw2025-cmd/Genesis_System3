"""Safe Cloud Run worker regression: LIVE-order locks, mock isolation, lane truth."""
from __future__ import annotations

import sys
import types

import pytest

from scripts import gcp_worker_job as worker

FORBIDDEN = (
    "LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED",
    "LIVE_ORDER_AUTHORITY", "REAL_BROKER_ORDERS",
    "AUTO_EXECUTE_TRADES", "ORDER_PLACEMENT_ALLOWED",
)


def _safe_env(monkeypatch):
    for flag in FORBIDDEN:
        monkeypatch.setenv(flag, "0")
    monkeypatch.setenv("SYSTEM3_JOB_PUBLISH_STATE", "0")


@pytest.mark.parametrize("flag", FORBIDDEN)
def test_live_flags_block_cloud_job(monkeypatch, flag):
    _safe_env(monkeypatch)
    monkeypatch.setenv(flag, "1")
    with pytest.raises(RuntimeError, match="forbidden"):
        worker.run_job("smoke")


def test_paper_smoke_reasserts_explicit_all_safety_locks(monkeypatch):
    _safe_env(monkeypatch)
    result = worker.run_job("smoke")
    assert result["status"] == "PASS"
    assert result["mode"] == "PAPER"
    assert result["live_trading_enabled"] is False
    for flag in FORBIDDEN:
        assert worker.os.environ[flag] in ("0", "false")
    assert worker.os.environ["PAPER_MODE"] == "1"


@pytest.mark.parametrize("uri,ok", [
    ("https://run.googleapis.com/v2/projects/proj/locations/asia-south1/jobs/genesis-system3-rank:run", True),
    ("https://asia-south1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/proj/jobs/genesis-system3-rank:run", True),
    ("https://asia-south1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/other/jobs/genesis-system3-rank:run", False),
    ("http://run.googleapis.com/v2/projects/proj/locations/asia-south1/jobs/x:run", False),
    ("https://run.googleapis.com/v2/projects/proj/locations/asia-south1/jobs/x:run?unsafe=1", False),
    ("https://user@run.googleapis.com/v2/projects/proj/locations/asia-south1/jobs/x:run", False),
])
def test_exact_scheduler_v1_v2_target_parser(uri, ok):
    _, valid = worker._parse_scheduler_target(uri, "proj", "asia-south1")
    assert valid is ok


def test_market_closed_rank_has_no_broker_requests(monkeypatch, tmp_path):
    _safe_env(monkeypatch)
    fake = types.ModuleType("scripts.daily_gain_rank_and_validate")
    fake.REPORT_DIR = tmp_path
    def fail_if_rank_called():
        raise AssertionError("No real market fetch during closed session")
    fake.run_ranking = fail_if_rank_called
    monkeypatch.setitem(sys.modules, "scripts.daily_gain_rank_and_validate", fake)
    monkeypatch.setattr(worker, "_business_context",
                        lambda lane: ("2026-11-13", False, "MARKET_SESSION_CLOSED"))
    monkeypatch.setattr(worker, "_artifact",
                        lambda lane, payload, source, output: dict(payload, lane=lane))
    result = worker.run_job("rank")
    assert result["status"] == "SKIPPED"
    assert result["business_status"] == "SKIPPED"
    assert result["business_reason_code"] == "MARKET_SESSION_CLOSED"
    assert result["transport_execution_status"] == "SUCCESS"


def test_missing_rank_forecast_is_pending_not_runtime_crash(monkeypatch):
    _safe_env(monkeypatch)
    fake = types.ModuleType("dashboard.backend.firestore_state_backend")
    class Backend:
        def load_artifact(self, lane):
            assert lane == "rank"
            return None
    fake.FirestoreSchedulerEvidenceBackend = Backend
    monkeypatch.setitem(sys.modules, "dashboard.backend.firestore_state_backend", fake)
    monkeypatch.setattr(worker, "_business_context",
                        lambda lane: ("2026-11-13", True, "OPEN_SESSION"))
    monkeypatch.setattr(worker, "_artifact",
                        lambda lane, payload, source, output: dict(payload, lane=lane))
    result = worker.run_job("forecast")
    assert result["status"] == "PENDING"
    assert result["business_reason_code"] == "RANK_NOT_READY"


def test_no_synthetic_history_bootstrap_into_production(monkeypatch):
    _safe_env(monkeypatch)
    with pytest.raises(RuntimeError, match="disabled"):
        worker.run_job("ml-history-bootstrap")


def test_live_paper_pipeline_remains_opt_in(monkeypatch):
    _safe_env(monkeypatch)
    monkeypatch.setenv("SYSTEM3_ENABLE_PAPER_JOB", "0")
    with pytest.raises(RuntimeError, match="SYSTEM3_ENABLE_PAPER_JOB=1"):
        worker.run_job("paper-pipeline-v8")


def test_missing_collector_permissions_cannot_claim_green(monkeypatch):
    _safe_env(monkeypatch)
    def deny():
        raise PermissionError("not authorized")
    monkeypatch.setattr(worker, "_run_scheduler_collector", deny)
    with pytest.raises(PermissionError):
        worker.run_job("scheduler-collector")
