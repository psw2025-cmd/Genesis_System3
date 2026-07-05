"""
Tests for core/engine/system3_scheduler_catchup.py — the missed-job
catch-up policy engine. Covers the 10 scenarios required by the
scheduler catch-up proof task:

 1. Exact-time job still fires.
 2. Missed job within catch-up window fires once.
 3. Missed job outside catch-up window does not fire.
 4. Restart after scheduled time does not permanently hide job status.
 5. Same job does not fire twice for same date/time.
 6. Market-dependent job does not catch up when market closed.
 7. Paper lifecycle job does not run without broker proof.
 8. Paper lifecycle job does not run without valid option contract proof.
 9. Post-market proof pack does not run before upstream artifacts exist.
10. Scheduler health reports pending/missed/catchup status instead of
    empty jobs when applicable.
"""

from datetime import datetime

import pytest
import pytz

from core.engine.system3_scheduler_catchup import (
    FireStatus,
    evaluate_job_fire,
    load_policy,
    make_fire_key,
    summarize_scheduler_status,
)

IST = pytz.timezone("Asia/Kolkata")


def _ist(y, mo, d, h, mi, s=0):
    return IST.localize(datetime(y, mo, d, h, mi, s))


@pytest.fixture
def policy():
    return load_policy()


def test_exact_time_job_still_fires(policy):
    """1. A job evaluated within the ~1 minute exact-time window fires ON_TIME."""
    job = {"id": "daily_gain_rank", "schedule_time": "09:15", "market_dependent": True}
    now = _ist(2026, 7, 2, 9, 15, 20)  # Thursday, trading day
    result = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=False)
    assert result["should_fire"] is True
    assert result["status"] == FireStatus.ON_TIME


def test_missed_job_within_catchup_window_fires_once(policy):
    """2. A job missed by 20 minutes, within its 30-min catch-up window, fires as CATCH_UP."""
    job = {"id": "daily_gain_rank", "schedule_time": "09:15", "market_dependent": True}
    now = _ist(2026, 7, 2, 9, 35, 0)  # 20 min late
    result = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=False)
    assert result["should_fire"] is True
    assert result["status"] == FireStatus.CATCH_UP


def test_missed_job_outside_catchup_window_does_not_fire(policy):
    """3. A job missed by 40 minutes, past its 30-min catch-up window, does not fire."""
    job = {"id": "daily_gain_rank", "schedule_time": "09:15", "market_dependent": True}
    now = _ist(2026, 7, 2, 9, 55, 0)  # 40 min late
    result = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=False)
    assert result["should_fire"] is False
    assert result["status"] == FireStatus.SKIPPED_TOO_LATE


def test_restart_after_scheduled_time_does_not_permanently_hide_status(policy):
    """4. Simulate a restart: state is freshly loaded (no in-memory history) well
    after the job's exact window, but still inside the catch-up window — the
    job must still be evaluable and get a real status, not silently vanish."""
    job = {"id": "self_healing_watchdog", "schedule_time": "08:30", "market_dependent": False}
    # "Restart" = a fresh evaluate_job_fire call with only persisted state,
    # no in-memory history at all (exactly what a fresh process has).
    fresh_state_after_restart = {"fired_keys_today": []}
    now = _ist(2026, 7, 2, 9, 0, 0)  # 30 min late, self_healing_watchdog has a 60-min window
    result = evaluate_job_fire(job, now, policy, fresh_state_after_restart, is_holiday=False, is_weekend=False)
    assert result["status"] != FireStatus.PENDING  # must have a concrete status, not silence
    assert result["should_fire"] is True
    assert result["status"] == FireStatus.CATCH_UP


def test_same_job_does_not_fire_twice_for_same_date_time(policy):
    """5. Once a fire_key is recorded as fired, re-evaluating the same job/date/time
    returns SKIPPED_ALREADY_FIRED, even if still technically within window."""
    job = {"id": "daily_gain_rank", "schedule_time": "09:15", "market_dependent": True}
    now = _ist(2026, 7, 2, 9, 15, 10)
    first = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=False)
    assert first["should_fire"] is True

    already_fired_state = {"fired_keys_today": [first["fire_key"]]}
    second = evaluate_job_fire(job, now, policy, already_fired_state, is_holiday=False, is_weekend=False)
    assert second["should_fire"] is False
    assert second["status"] == FireStatus.SKIPPED_ALREADY_FIRED

    # Also true later in the same catch-up window
    later = _ist(2026, 7, 2, 9, 30, 0)
    third = evaluate_job_fire(job, later, policy, already_fired_state, is_holiday=False, is_weekend=False)
    assert third["should_fire"] is False
    assert third["status"] == FireStatus.SKIPPED_ALREADY_FIRED


def test_market_dependent_job_does_not_catchup_when_market_closed(policy):
    """6. A market-open-gated job does not catch up on a weekend, even within its window."""
    job = {"id": "ui_market_cross_verify", "schedule_time": "10:00", "market_dependent": True}
    now = _ist(2026, 7, 4, 10, 20, 0)  # Saturday, 20 min "late" but market never opens on weekends
    result = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=True)
    assert result["should_fire"] is False
    assert result["status"] == FireStatus.SKIPPED_MARKET_CLOSED


def test_paper_lifecycle_does_not_run_without_broker_proof(tmp_path, monkeypatch, policy):
    """7. paper_lifecycle_proof's catch-up condition requires broker_truth_summary.json
    to exist. Without it, catch-up must be refused even if market is open."""
    import core.engine.system3_scheduler_catchup as catchup_mod

    monkeypatch.setattr(catchup_mod, "PROJECT_ROOT", tmp_path)
    job = {"id": "paper_lifecycle_proof", "schedule_time": "09:30", "market_dependent": True}
    now = _ist(2026, 7, 2, 9, 50, 0)  # 20 min late, market open, within window
    # Neither broker_truth_summary.json nor instrument_tradability_summary.json exist under tmp_path
    result = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=False)
    assert result["should_fire"] is False
    assert result["status"] == FireStatus.SKIPPED_UPSTREAM_MISSING


def test_paper_lifecycle_does_not_run_without_valid_option_contract_proof(tmp_path, monkeypatch, policy):
    """8. Even with broker proof present, missing instrument_tradability proof
    (valid option contract) must also block the catch-up fire."""
    import core.engine.system3_scheduler_catchup as catchup_mod

    monkeypatch.setattr(catchup_mod, "PROJECT_ROOT", tmp_path)
    broker_dir = tmp_path / "reports" / "latest" / "broker_truth"
    broker_dir.mkdir(parents=True)
    (broker_dir / "broker_truth_summary.json").write_text("{}")
    # instrument_tradability_summary.json deliberately NOT created

    job = {"id": "paper_lifecycle_proof", "schedule_time": "09:30", "market_dependent": True}
    now = _ist(2026, 7, 2, 9, 50, 0)
    result = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=False)
    assert result["should_fire"] is False
    assert result["status"] == FireStatus.SKIPPED_UPSTREAM_MISSING


def test_post_market_proof_pack_does_not_run_before_upstream_exists(tmp_path, monkeypatch, policy):
    """9. paper_day_proof_pack requires dashboard_browser_proof status.json and the
    post-market pipeline output — without them, no catch-up even post-market."""
    import core.engine.system3_scheduler_catchup as catchup_mod

    monkeypatch.setattr(catchup_mod, "PROJECT_ROOT", tmp_path)
    job = {"id": "paper_day_proof_pack", "schedule_time": "16:15", "market_dependent": True}
    now = _ist(2026, 7, 2, 17, 0, 0)  # well post-market, within the 120-min window
    result = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=False)
    assert result["should_fire"] is False
    assert result["status"] == FireStatus.SKIPPED_UPSTREAM_MISSING

    # Now create the required upstream artifacts and confirm it becomes eligible
    (tmp_path / "reports" / "latest" / "dashboard_browser_proof").mkdir(parents=True)
    (tmp_path / "reports" / "latest" / "dashboard_browser_proof" / "status.json").write_text("{}")
    (tmp_path / "reports" / "latest" / "performance_benchmark").mkdir(parents=True)
    (tmp_path / "reports" / "latest" / "performance_benchmark" / "benchmark_summary.md").write_text("x")

    result2 = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=False)
    assert result2["should_fire"] is True
    assert result2["status"] == FireStatus.CATCH_UP


def test_scheduler_health_reports_honest_status_not_empty_jobs(policy):
    """10. summarize_scheduler_status must classify jobs into pending / missed /
    catchup_eligible / skipped / fired rather than reporting an undifferentiated
    empty jobs={} for everything, when jobs are configured but not yet fired."""
    config = {
        "jobs": [
            {"id": "daily_gain_rank", "schedule_time": "09:15", "enabled": True, "market_dependent": True},
            {"id": "bhavcopy_download", "schedule_time": "18:30", "enabled": True, "market_dependent": True},
            {"id": "weekly_repo_authority_audit", "schedule_time": "19:00", "enabled": True, "days": ["Friday"]},
        ]
    }
    state = {"jobs_status_today": {}, "fired_keys_today": []}

    # 9:35 IST — daily_gain_rank is 20 min late (catchup eligible), bhavcopy_download
    # is far in the future (pending).
    now = _ist(2026, 7, 2, 9, 35, 0)
    summary = summarize_scheduler_status(
        config, state, now=now, policy=policy, is_holiday=False, is_weekend=False, api_health_ok=False
    )
    assert summary["configured_jobs_count"] == 3
    assert summary["enabled_jobs_count"] == 3
    assert "daily_gain_rank" in summary["catchup_eligible_jobs"]
    assert "bhavcopy_download" in summary["pending_jobs_today"]
    # Not an undifferentiated empty result — every enabled job is accounted for
    total_classified = (
        len(summary["fired_jobs_today"])
        + len(summary["pending_jobs_today"])
        + len(summary["missed_jobs_today"])
        + len(summary["catchup_eligible_jobs"])
        + len(summary["skipped_jobs_today"])
    )
    assert total_classified == summary["enabled_jobs_count"]


def test_make_fire_key_uniqueness():
    """fire_key must differ across job_id, date, and schedule_time independently."""
    k1 = make_fire_key("job_a", "2026-07-02", "09:15")
    k2 = make_fire_key("job_b", "2026-07-02", "09:15")
    k3 = make_fire_key("job_a", "2026-07-03", "09:15")
    k4 = make_fire_key("job_a", "2026-07-02", "09:30")
    assert len({k1, k2, k3, k4}) == 4


def test_pending_job_not_yet_due_is_not_misreported_as_missed(policy):
    """A job whose schedule_time hasn't arrived yet today must be PENDING,
    never SKIPPED_TOO_LATE or any other 'something went wrong' status."""
    job = {"id": "bhavcopy_download", "schedule_time": "18:30", "market_dependent": True}
    now = _ist(2026, 7, 2, 9, 0, 0)  # long before 18:30
    result = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=False)
    assert result["should_fire"] is False
    assert result["status"] == FireStatus.PENDING


def test_auto_retrain_does_not_fire_without_retrain_signal(tmp_path, monkeypatch, policy):
    """auto_retrain must never blindly retrain — only when retrain_signal.json exists."""
    import core.engine.system3_scheduler_catchup as catchup_mod

    monkeypatch.setattr(catchup_mod, "PROJECT_ROOT", tmp_path)
    job = {"id": "auto_retrain", "schedule_time": "16:00", "market_dependent": False}
    now = _ist(2026, 7, 2, 16, 30, 0)  # 30 min late, within the 180-min window
    result = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=False)
    assert result["should_fire"] is False
    assert result["status"] == FireStatus.SKIPPED_UPSTREAM_MISSING

    (tmp_path / "state").mkdir(parents=True)
    (tmp_path / "state" / "retrain_signal.json").write_text("{}")
    result2 = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=False)
    assert result2["should_fire"] is True
    assert result2["status"] == FireStatus.CATCH_UP


def test_no_policy_entry_defaults_to_never_catchup():
    """A job with no explicit policy entry and no 'default' override must
    never catch up — conservative default per requirement 2."""
    policy = {"default": {"catchup_window_minutes": 0, "condition": "never"}, "jobs": {}}
    job = {"id": "totally_unconfigured_job", "schedule_time": "09:15", "market_dependent": False}
    now = _ist(2026, 7, 2, 9, 20, 0)  # 5 min late
    result = evaluate_job_fire(job, now, policy, {"fired_keys_today": []}, is_holiday=False, is_weekend=False)
    assert result["should_fire"] is False
