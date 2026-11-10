"""Unit tests for the scheduler control-plane SSOT."""

from pathlib import Path

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
    assert (
        expected["expected_enabled"] + expected["expected_paused"]
        == expected["expected_total"]
    )
    assert "genesis-system3-validate" in expected_job_targets()


def test_rotate_daily_expectation_matches_repository_contract():
    state, target, schedule, zone, max_age_hours = EXPECTED_SCHEDULER_CONTRACT[
        "genesis-system3-dhan-token-rotate-daily"
    ]
    assert state == "ENABLED"
    assert target == "genesis-system3-dhan-token-rotate"
    assert schedule == "*/5 * * * *"
    assert zone == "Asia/Kolkata"
    assert max_age_hours == 26


def test_retired_gcp_rotation_manifest_cannot_reintroduce_competing_cadence():
    repo_root = Path(__file__).resolve().parents[1]
    assert not (repo_root / "infra" / "rotate-job.yaml").exists()

    authority = (
        repo_root / "docs" / "control_plane" / "CLAUDE_SINGLE_EXECUTION_AUTHORITY.md"
    ).read_text(encoding="utf-8")
    assert "historical and non-authoritative" in authority
    assert "must not recreate the retired GCP manifest" in authority


def test_coverage_snapshot_contract_matched_flag():
    expected = coverage_expectations()
    resources = [
        {"name": name, "state": row[0]}
        for name, row in EXPECTED_SCHEDULER_CONTRACT.items()
    ]
    snap = coverage_snapshot(resources)
    assert snap["contract_matched"] is True
    assert snap["total"] == expected["expected_total"]
    assert snap["expected_total"] == expected["expected_total"]
    broken = coverage_snapshot(resources[:-1])
    assert broken["contract_matched"] is False
