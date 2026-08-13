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


def test_scheduler_collector_is_bounded_and_live_off(monkeypatch):
    monkeypatch.setenv("SYSTEM3_JOB_PUBLISH_STATE", "0")
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "0")
    monkeypatch.setenv("SYSTEM3_LIVE_TRADING_ALLOWED", "0")
    monkeypatch.setattr(gcp_worker_job, "_run_scheduler_collector", lambda: {"evidence_version": 1})
    result = gcp_worker_job.run_job("scheduler-collector")
    assert result["scheduler_evidence"]["evidence_version"] == 1
    assert result["live_trading_enabled"] is False


def test_collector_paginates_and_parses_actual_target(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "project")
    class Response:
        def __init__(self, body): self.body = body
        def raise_for_status(self): return None
        def json(self): return self.body
    class Session:
        def __init__(self): self.calls = []
        def get(self, url, params, timeout):
            self.calls.append((url, dict(params), timeout))
            if "cloudscheduler" in url:
                if not params.get("pageToken"):
                    return Response({"jobs": [{"name": "x/genesis-system3-forecast-daily", "state": "ENABLED", "httpTarget": {"uri": "https://run.googleapis.com/v2/projects/project/locations/asia-south1/jobs/genesis-system3-forecast:run"}}], "nextPageToken": "next"})
                return Response({"jobs": []})
            return Response({"jobs": []})
    session = Session()
    facts = gcp_worker_job._collect_scheduler_facts(session)
    row = next(r for r in facts["resources"] if r["name"] == "genesis-system3-forecast-daily")
    assert row["target_job"] == "genesis-system3-forecast"
    assert any(call[1].get("pageToken") == "next" for call in session.calls)


def test_collector_rejects_malformed_nonlist(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "project")
    class Response:
        def raise_for_status(self): return None
        def json(self): return {"jobs": {"bad": True}}
    class Session:
        def get(self, url, params, timeout): return Response()
    with pytest.raises(RuntimeError, match="Malformed"):
        gcp_worker_job._collect_scheduler_facts(Session())


@pytest.mark.parametrize("uri", [
    "http://run.googleapis.com/v2/projects/p/locations/r/jobs/j:run",
    "https://evil.example/v2/projects/p/locations/r/jobs/j:run",
    "https://user@run.googleapis.com/v2/projects/p/locations/r/jobs/j:run",
    "https://run.googleapis.com/v2/projects/other/locations/r/jobs/j:run",
    "https://run.googleapis.com/v2/projects/p/locations/other/jobs/j:run",
    "https://run.googleapis.com/v2/projects/p/locations/r/jobs/j:run?x=1",
    "https://run.googleapis.com/v2/projects/p/locations/r/jobs/j:run#x",
])
def test_scheduler_target_uri_is_structurally_exact(uri):
    assert gcp_worker_job._parse_scheduler_target(uri, "p", "r")[1] is False


def test_scheduler_target_uri_accepts_exact_v2_target():
    assert gcp_worker_job._parse_scheduler_target("https://run.googleapis.com/v2/projects/p/locations/r/jobs/j:run", "p", "r") == ("j", True)


def test_collector_timeout_prevents_evidence_collection(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "project")
    class Session:
        def get(self, url, params, timeout): raise TimeoutError("bounded timeout")
    with pytest.raises(TimeoutError):
        gcp_worker_job._collect_scheduler_facts(Session())
