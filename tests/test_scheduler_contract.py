"""Unit tests for the scheduler control-plane SSOT."""

from dashboard.backend.scheduler_contract import (
    EXPECTED_SCHEDULER_CONTRACT,
    coverage_expectations,
    coverage_snapshot,
    expected_job_targets,
)


def test_coverage_expectations_match_contract_length():
    expected = coverage_expectations()
    assert expected["expected_total"] == len(EXPECTED_SCHEDULER_CONTRACT)
    assert expected["expected_control"] == 1
    assert expected["expected_workload"] == expected["expected_total"] - 1
    assert expected["expected_enabled"] + expected["expected_paused"] == expected["expected_total"]
    assert "genesis-system3-validate" in expected_job_targets()


def test_rotate_daily_expectation_matches_live_five_minute_trigger():
    state, target, schedule, zone, max_age_hours = EXPECTED_SCHEDULER_CONTRACT[
        "genesis-system3-dhan-token-rotate-daily"
    ]
    assert state == "ENABLED"
    assert target == "genesis-system3-dhan-token-rotate"
    assert schedule == "*/5 * * * *"
    assert zone == "Asia/Kolkata"
    assert max_age_hours == 26


def test_coverage_snapshot_contract_matched_flag():
    expected = coverage_expectations()
    resources = [{"name": name, "state": row[0]} for name, row in EXPECTED_SCHEDULER_CONTRACT.items()]
    snap = coverage_snapshot(resources)
    assert snap["contract_matched"] is True
    assert snap["total"] == expected["expected_total"]
    assert snap["expected_total"] == expected["expected_total"]
    broken = coverage_snapshot(resources[:-1])
    assert broken["contract_matched"] is False
