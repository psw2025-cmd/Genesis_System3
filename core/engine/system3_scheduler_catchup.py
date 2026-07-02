"""
System3 Scheduler Missed-Job Catch-Up Policy Engine.

The daemon in system3_phase82_job_scheduler.py only fires a job when the
current time is within ~60 seconds of its schedule_time. Any restart or
deploy that happens to land inside that narrow window causes the job to
be silently skipped for the entire rest of the day, with no retry.

This module adds a conservative, per-job catch-up policy: a job that
missed its exact window may still fire late, but only within a bounded
window and only when job-type-specific safety conditions hold (market
open, upstream artifacts exist, etc). It never blindly re-runs every
missed job on restart, never double-fires the same job for the same
scheduled date/time, and defaults to "no catch-up" for any job with no
explicit policy entry.

Pure decision logic lives here with no subprocess/network side effects,
so it can be unit tested in isolation. system3_phase82_job_scheduler.py
wires this into its daemon loop and owns actually running the job.
"""

from __future__ import annotations

import json
from datetime import datetime
from datetime import time as dt_time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
CATCHUP_POLICY_JSON = PROJECT_ROOT / "config" / "system3_scheduler_catchup_policy.json"

MARKET_OPEN = dt_time(9, 15)
MARKET_CLOSE = dt_time(15, 30)


class FireStatus:
    ON_TIME = "ON_TIME"
    CATCH_UP = "CATCH_UP"
    PENDING = "PENDING"
    SKIPPED_MARKET_CLOSED = "SKIPPED_MARKET_CLOSED"
    SKIPPED_TOO_LATE = "SKIPPED_TOO_LATE"
    SKIPPED_UPSTREAM_MISSING = "SKIPPED_UPSTREAM_MISSING"
    SKIPPED_ALREADY_FIRED = "SKIPPED_ALREADY_FIRED"
    FAILED = "FAILED"


_DEFAULT_POLICY: Dict[str, Any] = {
    "default": {"catchup_window_minutes": 0, "condition": "never"},
    "jobs": {},
}


def load_policy() -> Dict[str, Any]:
    """Load the catch-up policy config. Fails safe (no catch-up for
    anything) if the file is missing or invalid — a broken policy file
    must never accidentally grant broad catch-up permission."""
    try:
        with CATCHUP_POLICY_JSON.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if "jobs" not in data or "default" not in data:
            return dict(_DEFAULT_POLICY)
        return data
    except Exception:
        return dict(_DEFAULT_POLICY)


def get_job_policy(job_id: str, policy: Dict[str, Any]) -> Dict[str, Any]:
    return policy.get("jobs", {}).get(job_id, policy.get("default", _DEFAULT_POLICY["default"]))


def make_fire_key(job_id: str, date_str: str, schedule_time: str) -> str:
    """Fire key uniquely identifies one job's scheduled slot for one day.
    Used to guarantee a job never fires twice for the same date/time,
    regardless of how many times the daemon restarts."""
    return f"{date_str}|{schedule_time}|{job_id}"


def _parse_schedule_time(schedule_time: str) -> Optional[dt_time]:
    try:
        h, m = map(int, schedule_time.split(":"))
        return dt_time(h, m)
    except (ValueError, AttributeError):
        return None


def _is_market_open_now(now: datetime, is_holiday: bool, is_weekend: bool) -> bool:
    if is_weekend or is_holiday:
        return False
    return MARKET_OPEN <= now.time() < MARKET_CLOSE


def _upstream_paths_exist(paths: List[str]) -> bool:
    for p in paths:
        full = PROJECT_ROOT / p
        if not full.exists():
            return False
        # A directory upstream dependency must be non-empty to count as "exists"
        if full.is_dir() and not any(full.iterdir()):
            return False
    return True


def _condition_always(**kwargs) -> tuple:
    return True, "no condition required"


def _condition_never(**kwargs) -> tuple:
    return False, "no catch-up policy defined for this job"


def _condition_before_market_open(now: datetime, is_holiday: bool, is_weekend: bool, **kwargs) -> tuple:
    if is_weekend or is_holiday:
        return False, "market closed today (weekend/holiday) — pre-market catch-up not meaningful"
    if now.time() >= MARKET_OPEN:
        return (
            False,
            f"market already open ({now.time().strftime('%H:%M')} >= 09:15) — too late for pre-market catch-up",
        )
    return True, "before market open"


def _condition_before_market_open_or_before_first_lifecycle(
    now: datetime, is_holiday: bool, is_weekend: bool, state: Dict[str, Any], **kwargs
) -> tuple:
    ok, reason = _condition_before_market_open(now=now, is_holiday=is_holiday, is_weekend=is_weekend)
    if ok:
        return True, reason
    lifecycle_fired_today = any(
        k.split("|")[2].startswith("paper_lifecycle_proof") for k in state.get("fired_keys_today", [])
    )
    if not lifecycle_fired_today:
        return True, "market open but no paper_lifecycle_proof has fired yet today"
    return False, "market open and a paper_lifecycle_proof already fired today — too late"


def _condition_within_window_trading_day(now: datetime, is_holiday: bool, is_weekend: bool, **kwargs) -> tuple:
    if is_weekend or is_holiday:
        return False, "not a trading day"
    return True, "within trading-day catch-up window"


def _condition_market_open(now: datetime, is_holiday: bool, is_weekend: bool, **kwargs) -> tuple:
    if _is_market_open_now(now, is_holiday, is_weekend):
        return True, "market is open"
    return False, "market is not open"


def _condition_market_open_and_broker_and_contract_proven(
    now: datetime, is_holiday: bool, is_weekend: bool, job_policy: Dict[str, Any], **kwargs
) -> tuple:
    if not _is_market_open_now(now, is_holiday, is_weekend):
        return False, "market is not open"
    required = job_policy.get("requires_upstream", [])
    if not _upstream_paths_exist(required):
        return False, f"required upstream proof missing: {required}"
    return True, "market open and broker/contract proof present"


def _condition_post_market_close(now: datetime, is_holiday: bool, is_weekend: bool, **kwargs) -> tuple:
    if is_weekend or is_holiday:
        return False, "not a trading day"
    if now.time() < MARKET_CLOSE:
        return False, "market has not closed yet"
    return True, "post market close"


def _condition_post_market_upstream_exists(
    now: datetime, is_holiday: bool, is_weekend: bool, job_policy: Dict[str, Any], **kwargs
) -> tuple:
    ok, reason = _condition_post_market_close(now=now, is_holiday=is_holiday, is_weekend=is_weekend)
    if not ok:
        return False, reason
    required = job_policy.get("requires_upstream", [])
    if not _upstream_paths_exist(required):
        return False, f"required upstream artifact missing: {required}"
    return True, "post-market and upstream artifacts present"


def _condition_post_market_api_running(
    now: datetime, is_holiday: bool, is_weekend: bool, api_health_ok: bool = False, **kwargs
) -> tuple:
    ok, reason = _condition_post_market_close(now=now, is_holiday=is_holiday, is_weekend=is_weekend)
    if not ok:
        return False, reason
    if not api_health_ok:
        return False, "API not confirmed running (api_health_ok=False)"
    return True, "post-market and API confirmed running"


def _condition_retrain_signal_exists(job_policy: Dict[str, Any], **kwargs) -> tuple:
    required = job_policy.get("requires_upstream", ["state/retrain_signal.json"])
    if not _upstream_paths_exist(required):
        return False, "no retrain_signal.json present — nothing to catch up"
    return True, "retrain signal present"


def _condition_bhavcopy_available(job_policy: Dict[str, Any], **kwargs) -> tuple:
    required = job_policy.get("requires_upstream", ["storage/bhavcopy"])
    if not _upstream_paths_exist(required):
        return False, "bhavcopy not yet downloaded — nothing to run against"
    return True, "bhavcopy available"


CONDITION_HANDLERS: Dict[str, Callable[..., tuple]] = {
    "always": _condition_always,
    "never": _condition_never,
    "before_market_open": _condition_before_market_open,
    "before_market_open_or_before_first_lifecycle": _condition_before_market_open_or_before_first_lifecycle,
    "within_window_trading_day": _condition_within_window_trading_day,
    "market_open": _condition_market_open,
    "market_open_and_broker_and_contract_proven": _condition_market_open_and_broker_and_contract_proven,
    "post_market_close": _condition_post_market_close,
    "post_market_upstream_exists": _condition_post_market_upstream_exists,
    "post_market_api_running": _condition_post_market_api_running,
    "retrain_signal_exists": _condition_retrain_signal_exists,
    "bhavcopy_available": _condition_bhavcopy_available,
}


def evaluate_job_fire(
    job: Dict[str, Any],
    now: datetime,
    policy: Dict[str, Any],
    state: Dict[str, Any],
    is_holiday: bool = False,
    is_weekend: bool = False,
    api_health_ok: bool = False,
) -> Dict[str, Any]:
    """
    Decide whether `job` should fire right now, on-time or as a catch-up.

    Returns a dict: {"should_fire": bool, "status": str, "reason": str,
    "fire_key": str, "minutes_late": float}

    `state["fired_keys_today"]` must be a list of fire_key strings already
    fired today (persisted across restarts) — this is the sole source of
    truth for "already fired", not any in-memory dict, so a restart can
    never cause a duplicate fire nor forget a fire happened.
    """
    job_id = job["id"]
    schedule_time = job.get("schedule_time") or job.get("schedule", "")
    today_str = now.strftime("%Y-%m-%d")
    fire_key = make_fire_key(job_id, today_str, schedule_time)

    fired_today = set(state.get("fired_keys_today", []))
    if fire_key in fired_today:
        return {
            "should_fire": False,
            "status": FireStatus.SKIPPED_ALREADY_FIRED,
            "reason": "already fired for this exact date/schedule_time",
            "fire_key": fire_key,
            "minutes_late": None,
        }

    target_time = _parse_schedule_time(schedule_time)
    if target_time is None:
        return {
            "should_fire": False,
            "status": FireStatus.SKIPPED_TOO_LATE,
            "reason": f"unparseable schedule_time: {schedule_time!r}",
            "fire_key": fire_key,
            "minutes_late": None,
        }

    target_dt = now.replace(hour=target_time.hour, minute=target_time.minute, second=0, microsecond=0)
    minutes_since = (now - target_dt).total_seconds() / 60.0

    if minutes_since < -1.0:
        return {
            "should_fire": False,
            "status": FireStatus.PENDING,
            "reason": f"not due yet — fires at {schedule_time} IST",
            "fire_key": fire_key,
            "minutes_late": minutes_since,
        }

    if abs(minutes_since) <= 1.0:
        return {
            "should_fire": True,
            "status": FireStatus.ON_TIME,
            "reason": "within exact-time firing window",
            "fire_key": fire_key,
            "minutes_late": minutes_since,
        }

    job_policy = get_job_policy(job_id, policy)
    window = float(job_policy.get("catchup_window_minutes", 0))

    if minutes_since > window:
        return {
            "should_fire": False,
            "status": FireStatus.SKIPPED_TOO_LATE,
            "reason": f"{minutes_since:.0f} min late, exceeds catch-up window of {window:.0f} min",
            "fire_key": fire_key,
            "minutes_late": minutes_since,
        }

    condition_name = job_policy.get("condition", "never")
    handler = CONDITION_HANDLERS.get(condition_name, _condition_never)
    ok, reason = handler(
        now=now,
        is_holiday=is_holiday,
        is_weekend=is_weekend,
        state=state,
        job_policy=job_policy,
        api_health_ok=api_health_ok,
    )

    if not ok:
        # Distinguish a market-closed/non-trading-day skip from a generic
        # upstream-missing skip so /api/scheduler/health can report the
        # honest reason.
        _market_closed_markers = ("market", "trading day", "weekend", "holiday")
        status = (
            FireStatus.SKIPPED_MARKET_CLOSED
            if any(m in reason.lower() for m in _market_closed_markers)
            else FireStatus.SKIPPED_UPSTREAM_MISSING
        )
        return {
            "should_fire": False,
            "status": status,
            "reason": reason,
            "fire_key": fire_key,
            "minutes_late": minutes_since,
        }

    return {
        "should_fire": True,
        "status": FireStatus.CATCH_UP,
        "reason": f"catch-up fire ({minutes_since:.0f} min late): {reason}",
        "fire_key": fire_key,
        "minutes_late": minutes_since,
    }


def summarize_scheduler_status(
    config: Dict[str, Any],
    state: Dict[str, Any],
    now: Optional[datetime] = None,
    policy: Optional[Dict[str, Any]] = None,
    is_holiday: bool = False,
    is_weekend: bool = False,
    api_health_ok: bool = False,
) -> Dict[str, Any]:
    """
    Aggregate today's per-job fire status into the honest counts
    /api/scheduler/health needs. Consumed directly by that endpoint (see
    dashboard/backend/app.py) so both share one source of truth instead
    of the endpoint re-deriving its own (possibly inconsistent) counts.

    jobs={} alone must never mean "fatal" if nothing was due yet — jobs
    not yet fired are re-evaluated live (via evaluate_job_fire) against
    the current moment so pending_jobs_today / catchup_eligible_jobs /
    missed_jobs_today reflect "if the daemon ticked right now", not a
    stale snapshot from the last tick that happened to run.
    """
    jobs = [j for j in config.get("jobs", []) if j.get("id")]
    enabled_jobs = [j for j in jobs if j.get("enabled", False)]
    status_today: Dict[str, str] = state.get("jobs_status_today", {})
    fired_keys_today = state.get("fired_keys_today", [])

    fired_today: List[str] = []
    pending_today: List[str] = []
    missed_today: List[str] = []
    catchup_eligible_today: List[str] = []
    skipped_today: List[str] = []

    for job in enabled_jobs:
        job_id = job["id"]
        recorded_status = status_today.get(job_id)

        if recorded_status in (FireStatus.ON_TIME, FireStatus.CATCH_UP):
            fired_today.append(job_id)
            continue
        if recorded_status == FireStatus.FAILED:
            missed_today.append(job_id)
            continue

        sched = job.get("schedule_time", "daily")
        if sched.lower() == "daily" or now is None or policy is None:
            # "daily" jobs have no time window to be "late" against, and
            # without a `now`/policy we can't dry-run evaluate — fall back
            # to the last recorded status or PENDING.
            if recorded_status in (FireStatus.SKIPPED_MARKET_CLOSED, FireStatus.SKIPPED_UPSTREAM_MISSING):
                skipped_today.append(job_id)
            else:
                pending_today.append(job_id)
            continue

        decision = evaluate_job_fire(
            job=job,
            now=now,
            policy=policy,
            state={"fired_keys_today": fired_keys_today},
            is_holiday=is_holiday,
            is_weekend=is_weekend,
            api_health_ok=api_health_ok,
        )
        live_status = decision["status"]
        if live_status == FireStatus.PENDING:
            pending_today.append(job_id)
        elif live_status == FireStatus.CATCH_UP:
            catchup_eligible_today.append(job_id)
        elif live_status == FireStatus.SKIPPED_TOO_LATE:
            missed_today.append(job_id)
        elif live_status in (FireStatus.SKIPPED_MARKET_CLOSED, FireStatus.SKIPPED_UPSTREAM_MISSING):
            skipped_today.append(job_id)
        else:
            pending_today.append(job_id)

    return {
        "configured_jobs_count": len(jobs),
        "enabled_jobs_count": len(enabled_jobs),
        "fired_jobs_today": fired_today,
        "pending_jobs_today": pending_today,
        "missed_jobs_today": missed_today,
        "catchup_eligible_jobs": catchup_eligible_today,
        "skipped_jobs_today": skipped_today,
    }
