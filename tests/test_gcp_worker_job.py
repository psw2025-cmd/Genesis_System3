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


def test_collector_selects_newest_prior_completed_execution(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "project")
    monkeypatch.setenv("CLOUD_RUN_EXECUTION", "current")
    class Response:
        def __init__(self, body): self.body = body
        def raise_for_status(self): return None
        def json(self): return self.body
    class Session:
        def get(self, url, params, timeout):
            if url.endswith("/executions"):
                return Response({"executions": [
                    {"name": "x/older-failed", "completionTime": "2026-08-14T00:01:00Z", "createTime": "2026-08-14T00:00:00Z", "failedCount": 1, "taskCount": 1},
                    {"name": "x/newer-success", "completionTime": "2026-08-14T00:03:00Z", "createTime": "2026-08-14T00:02:00Z", "succeededCount": 1, "taskCount": 1},
                ]})
            return Response({"jobs": []})
    facts = gcp_worker_job._collect_scheduler_facts(Session())
    collector = next(row for row in facts["jobs"] if row["name"] == "genesis-system3-scheduler-collector")
    assert collector["execution"] == "newer-success"
    assert collector["completion_status"] == "EXECUTION_SUCCEEDED"


def test_collector_prefers_succeeded_prior_over_newer_failure(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "project")
    monkeypatch.setenv("CLOUD_RUN_EXECUTION", "current")
    class Response:
        def __init__(self, body): self.body = body
        def raise_for_status(self): return None
        def json(self): return self.body
    class Session:
        def get(self, url, params, timeout):
            if url.endswith("/executions"):
                return Response({"executions": [
                    {"name": "x/older-success", "completionTime": "2026-08-14T00:01:00Z", "createTime": "2026-08-14T00:00:00Z", "succeededCount": 1, "taskCount": 1},
                    {"name": "x/newer-failed", "completionTime": "2026-08-14T00:03:00Z", "createTime": "2026-08-14T00:02:00Z", "failedCount": 1, "taskCount": 1},
                ]})
            return Response({"jobs": []})
    facts = gcp_worker_job._collect_scheduler_facts(Session())
    collector = next(row for row in facts["jobs"] if row["name"] == "genesis-system3-scheduler-collector")
    assert collector["execution"] == "older-success"
    assert collector["completion_status"] == "EXECUTION_SUCCEEDED"
    assert collector["evidence_role"] == "prior_succeeded_execution"


@pytest.mark.parametrize("kind,runner", [("rank", "_run_rank_lane"), ("forecast", "_run_forecast_lane"), ("validate", "_run_validate_lane"), ("signals", "_run_signals_lane")])
def test_business_lane_is_bounded_and_live_off(monkeypatch, kind, runner):
    monkeypatch.setenv("SYSTEM3_JOB_PUBLISH_STATE", "0")
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "0")
    monkeypatch.setenv("SYSTEM3_LIVE_TRADING_ALLOWED", "0")
    monkeypatch.setattr(gcp_worker_job, runner, lambda: {"artifact_version": 1, "lane": kind})
    result = gcp_worker_job.run_job(kind)
    assert result["business_artifact"]["lane"] == kind
    assert result["live_trading_enabled"] is False


def test_cloud_workflow_has_exact_lane_identity_and_secret_boundaries():
    from pathlib import Path
    workflow = (Path(__file__).parents[1] / ".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
    assert "gs3-rank-job@" in workflow and "gs3-forecast-job@" in workflow and "gs3-signals-job@" in workflow
    assert "genesis-system3-validate" in workflow
    assert "for KIND in rank forecast validate signals" in workflow
    rank_secret_mount = "--set-secrets=DHAN_CLIENT_ID=system3-dhan-client-id:latest,DHAN_ACCESS_TOKEN=dhan-access-token:latest"
    # Secret mount string appears once in the template; rank+validate both use the same printf branch.
    assert workflow.count(rank_secret_mount) == 1
    assert "genesis-system3-validate-daily" in workflow
    assert 'schedule="5 10 * * MON-FRI"' in workflow
    assert "genesis-system3-scheduler-collector-every-minute" in workflow
    assert '--schedule="* * * * *"' in workflow
    assert "COLLECTOR_URI=\"https://run.googleapis.com/v2/projects/${GOOGLE_CLOUD_PROJECT}/locations/${GCP_REGION}/jobs/genesis-system3-scheduler-collector:run\"" in workflow
    assert "coverage.contract_matched == true" in workflow
    assert ".coverage.total == .coverage.expected_total" in workflow
    # Deploy configures/schedules business lanes but must never manufacture their evidence.
    assert "Cloud self-bootstrap" not in workflow
    assert 'gcloud run jobs execute "genesis-system3-${LANE}"' not in workflow
    assert "genesis-system3-ml-history-bootstrap" not in workflow
    assert "SYSTEM3_ALLOW_ML_HISTORY_BOOTSTRAP=1" not in workflow
    assert "genesis-system3-control-plane-verify" in workflow
    assert "for PASS in 1 2 3 4" in workflow
    assert "DEPLOY_GIT_SHA=${GITHUB_SHA}" in workflow
    assert "/api/scheduler/health?refresh=true" in workflow
    assert ".observability.alert_severity == \"none\"" in workflow
    assert ".healthy == true" in workflow
    pause = workflow.index("scheduler jobs pause genesis-system3-scheduler-collector-every-minute")
    resume = workflow.index("scheduler jobs resume genesis-system3-scheduler-collector-every-minute", pause)
    trigger = workflow.index("scheduler jobs run genesis-system3-scheduler-collector-every-minute", resume)
    assert pause < resume < trigger
    assert 'IN("READY", "PARTIAL", "PENDING", "NOT_APPLICABLE", "BLOCKED")' in workflow
