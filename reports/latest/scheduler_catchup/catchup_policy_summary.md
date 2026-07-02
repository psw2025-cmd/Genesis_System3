# Scheduler Catch-Up Policy — Implementation Summary

**Generated:** 2026-07-02 00:42 IST
**Policy file:** `config/system3_scheduler_catchup_policy.json`
**Engine:** `core/engine/system3_scheduler_catchup.py` (pure, unit-testable decision logic)
**Wired into:** `core/engine/system3_phase82_job_scheduler.py`'s `run_daemon()` loop

## The bug this fixes

The daemon only fired a job within ~60 seconds of its exact `schedule_time`. Any restart landing inside that window meant the job was silently skipped for the rest of the day — no retry, no visible signal. Separately, the old `last_fired`/`last_fired_date` tracking was in-memory only, so a restart could also cause a "daily" job to double-fire on the same day.

## Design

- **Fire key**: `{date}|{schedule_time}|{job_id}` — uniquely identifies one job's scheduled slot for one day.
- **Persistence**: fire keys are stored in `state['fired_keys_today']` (the scheduler's existing state JSON file), reloaded fresh every tick, reset on date rollover. This is now the *sole* source of truth for "already fired" — no in-memory dicts that reset on restart.
- **Default is no catch-up**: any job without an explicit policy entry gets `condition: "never"`, `window: 0` — fails safe.
- **Never double-fires**: once a fire key is recorded, every future evaluation for that same slot returns `SKIPPED_ALREADY_FIRED`, regardless of restarts.
- **7 honest status values**: `ON_TIME`, `CATCH_UP`, `SKIPPED_MARKET_CLOSED`, `SKIPPED_TOO_LATE`, `SKIPPED_UPSTREAM_MISSING`, `SKIPPED_ALREADY_FIRED`, `FAILED` (plus internal `PENDING` for not-yet-due).

## Per-job-type policy (23 jobs covered)

| Job category | Catch-up window | Condition |
|---|---|---|
| Pre-market checks (`datasource_health_check`, `dashboard_endpoint_coverage`) | 60 min | Only before market open |
| `auto_coordinator_premarket`, `dhan_instruments_sync` | ~65 min | Before market open (or before first lifecycle run, for instrument sync) |
| `daily_gain_rank` | 30 min | Narrow window, trading days only |
| `paper_lifecycle_proof` (+ midday/afternoon) | 60 min | Market open **AND** broker proof **AND** valid option contract proof both exist |
| `ui_market_cross_verify` (all 3) | 60 min | Market open |
| `daily_gain_validate`, `bhavcopy_download` | 120-180 min | Post-market close only |
| `daily_gain_trend`, `daily_prediction_benchmark`, `system3_post_market_pipeline`, `auto_coordinator_post_market` | 120 min | Post-market **and** upstream artifacts (performance_benchmark) exist |
| `dashboard_browser_proof` | 120 min | Post-market and API confirmed reachable |
| `paper_day_proof_pack` | 120 min | Post-market **and** browser proof + pipeline artifacts both exist |
| `signal_engine_bhavcopy` | 180 min | Only after bhavcopy is actually downloaded |
| `auto_retrain` | 180 min | Only if a real `retrain_signal.json` exists — never blind retrain |
| `self_healing_watchdog`, `weekly_repo_authority_audit` | 60-240 min | Not market/upstream dependent — wide, safe catch-up |

## Verification

14 new unit tests (`tests/test_scheduler_catchup.py`) cover all 10 required scenarios plus 4 extra edge cases. All 33 tests (14 new + 19 pre-existing) pass with zero regressions. See `test_summary.md`.
