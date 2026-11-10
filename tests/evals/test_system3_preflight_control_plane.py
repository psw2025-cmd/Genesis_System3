from datetime import datetime, timezone

from scripts.system3_preflight_control_plane import (
    classify_failure_relevance,
    choose_next_action,
    pr_is_currently_active,
    load_evidence_catalog,
)


def test_agent_evidence_catalog_has_no_missing_required_repo_authority():
    catalog = load_evidence_catalog()
    assert catalog["schema"] == "SYSTEM3_AGENT_EVIDENCE_CATALOG_V1"
    assert catalog["role"] == "discovery_index_not_live_truth"
    assert catalog["missing_required"] == []
    assert all(
        item["status"] in {
            "PRESENT",
            "ABSENT_NOT_REQUIRED",
            "UNVERIFIED_CONDITIONAL",
        }
        for item in catalog["entries"]
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
