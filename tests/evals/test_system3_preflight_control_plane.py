from datetime import datetime, timezone

from scripts.system3_preflight_control_plane import (
    MONITOR_COLUMNS,
    build_monitor_rows,
    classify_failure_relevance,
    choose_next_action,
    monitor_alerts,
    pr_is_currently_active,
    write_monitor_csv,
)


def test_current_main_failure_is_actionable_but_old_failure_is_history():
    current = {"conclusion": "failure", "head_sha": "main-sha"}
    old = {"conclusion": "failure", "head_sha": "old-sha"}
    assert classify_failure_relevance(current, main_sha="main-sha", active_pr_shas=set()) is True
    assert classify_failure_relevance(old, main_sha="main-sha", active_pr_shas=set()) is False


def test_active_pr_failure_is_actionable():
    run = {"conclusion": "failure", "head_sha": "pr-sha"}
    assert classify_failure_relevance(run, main_sha="main-sha", active_pr_shas={"pr-sha"}) is True


def test_open_pr_recency_distinguishes_current_from_historical():
    now = datetime(2026, 8, 17, 2, 30, tzinfo=timezone.utc)
    current, current_age = pr_is_currently_active(
        "2026-08-16T20:00:00Z", now=now, max_age_h=72
    )
    historical, historical_age = pr_is_currently_active(
        "2026-07-27T03:35:14Z", now=now, max_age_h=72
    )
    assert current is True
    assert current_age == 6.5
    assert historical is False
    assert historical_age > 500


def test_in_progress_current_main_deploy_blocks_url_proof_transition():
    decision = choose_next_action(
        main_sha="abc",
        workflows=[
            {
                "name": "Cloud Run Auto Deploy",
                "head_sha": "abc",
                "status": "in_progress",
                "run_number": 143,
                "relevant_failure": False,
            }
        ],
        active_prs=[],
    )
    assert decision.status == "WAITING"
    assert decision.current_step == "canonical production deployment"
    assert "exact-serving SHA" in decision.next_action


def test_current_failure_precedes_merge_or_url_transition():
    decision = choose_next_action(
        main_sha="abc",
        workflows=[
            {
                "name": "Security Audit Evidence",
                "head_sha": "abc",
                "status": "completed",
                "conclusion": "failure",
                "relevant_failure": True,
            }
        ],
        active_prs=[
            {"number": 9, "mergeable": True, "draft": False, "current_relevance": True}
        ],
    )
    assert decision.status == "WORKING"
    assert decision.current_step == "current workflow failure investigation"


def test_current_mergeable_pr_moves_to_exact_head_gate_verification():
    decision = choose_next_action(
        main_sha="abc",
        workflows=[],
        active_prs=[
            {"number": 9, "mergeable": True, "draft": False, "current_relevance": True}
        ],
    )
    assert decision.status == "WORKING"
    assert decision.current_step == "active PR gate verification"
    assert "merge immediately" in decision.next_action


def test_stale_mergeable_open_pr_does_not_block_production_truth_transition():
    decision = choose_next_action(
        main_sha="abc",
        workflows=[],
        active_prs=[
            {"number": 9, "mergeable": True, "draft": False, "current_relevance": False}
        ],
    )
    assert decision.status == "WORKING"
    assert decision.current_step == "production truth verification"


def test_no_workflow_blocker_moves_to_production_truth_verification():
    decision = choose_next_action(main_sha="abc", workflows=[], active_prs=[])
    assert decision.status == "WORKING"
    assert decision.current_step == "production truth verification"
    assert "fresh semantic production URL proof" in decision.next_action


def test_monitor_csv_projects_issues_prs_actions_with_exact_columns(tmp_path):
    snapshot = {
        "captured_at_utc": "2026-08-24T12:00:00+00:00",
        "main_sha": "main-sha",
        "issues_inventory": [
            {
                "number": 188,
                "title": "UI closure",
                "state": "open",
                "updated_at": "2026-08-24T11:00:00Z",
                "labels": ["P0"],
                "html_url": "https://example.test/issues/188",
            }
        ],
        "open_pull_requests": [
            {
                "number": 9,
                "title": "Fix proof",
                "mergeable": True,
                "mergeable_state": "blocked",
                "draft": False,
                "head_sha": "pr-sha",
                "base_sha": "main-sha",
                "updated_at": "2026-08-24T11:30:00Z",
                "html_url": "https://example.test/pull/9",
            }
        ],
        "actionable_runs": [],
        "workflow_inventory": [
            {
                "id": 7,
                "name": "Safety",
                "state": "active",
                "latest_run": {
                    "id": 70,
                    "status": "completed",
                    "conclusion": "success",
                    "head_sha": "main-sha",
                    "updated_at": "2026-08-24T11:40:00Z",
                    "html_url": "https://example.test/actions/70",
                },
            }
        ],
    }
    rows = build_monitor_rows(snapshot)
    assert [row[MONITOR_COLUMNS[0]] for row in rows] == ["Issues", "PullRequests", "Actions"]
    assert rows[0][MONITOR_COLUMNS[2]] == "Open"
    assert rows[1][MONITOR_COLUMNS[3]].startswith("Repository review/protection gate")
    assert rows[2][MONITOR_COLUMNS[2]] == "Passed"
    path = write_monitor_csv(rows, tmp_path / "monitor.csv")
    assert path.read_text(encoding="utf-8-sig").splitlines()[0] == ",".join(
        f'"{column}"' for column in MONITOR_COLUMNS
    )


def test_monitor_alerts_include_conflict_and_failed_action():
    snapshot = {
        "captured_at_utc": "2026-08-24T12:00:00+00:00",
        "main_sha": "main-sha",
        "issues_inventory": [],
        "open_pull_requests": [
            {
                "number": 10,
                "title": "Conflict",
                "mergeable": False,
                "mergeable_state": "dirty",
                "head_sha": "conflict-sha",
                "base_sha": "main-sha",
            }
        ],
        "actionable_runs": [],
        "workflow_inventory": [
            {
                "id": 8,
                "name": "Audit",
                "state": "active",
                "latest_run": {
                    "id": 80,
                    "status": "completed",
                    "conclusion": "failure",
                    "relevant_failure": True,
                    "head_sha": "main-sha",
                    "failed_jobs": [
                        {
                            "name": "audit",
                            "failed_steps": [{"name": "verify", "conclusion": "failure"}],
                        }
                    ],
                },
            }
        ],
    }
    alerts = monitor_alerts(build_monitor_rows(snapshot))
    assert alerts == ["#10 / Conflict", "8 / Audit"]


def test_disabled_historical_workflow_is_closed_not_alerted():
    snapshot = {
        "captured_at_utc": "2026-08-24T12:00:00+00:00",
        "main_sha": "main-sha",
        "issues_inventory": [],
        "open_pull_requests": [],
        "actionable_runs": [],
        "workflow_inventory": [
            {
                "id": 99,
                "name": "Retired Render workflow",
                "state": "disabled_manually",
                "latest_run": {"id": 999, "status": "completed", "conclusion": "failure"},
            }
        ],
    }
    rows = build_monitor_rows(snapshot)
    assert rows[0][MONITOR_COLUMNS[2]] == "Closed"
    assert rows[0][MONITOR_COLUMNS[3]].startswith("RETIRED_OR_DISABLED_WORKFLOW")
    assert monitor_alerts(rows) == []


def test_historical_latest_failure_stays_visible_but_is_not_an_alert():
    snapshot = {
        "captured_at_utc": "2026-08-24T12:00:00+00:00",
        "main_sha": "main-sha",
        "issues_inventory": [],
        "open_pull_requests": [],
        "actionable_runs": [],
        "workflow_inventory": [
            {
                "id": 100,
                "name": "Historical audit",
                "state": "active",
                "latest_run": {
                    "id": 1000,
                    "status": "completed",
                    "conclusion": "failure",
                    "relevant_failure": False,
                    "head_sha": "old-sha",
                },
            }
        ],
    }
    rows = build_monitor_rows(snapshot)
    assert rows[0][MONITOR_COLUMNS[2]] == "Failed"
    assert rows[0][MONITOR_COLUMNS[3]].startswith("HISTORICAL_HEAD_FAILURE")
    assert monitor_alerts(rows) == []
