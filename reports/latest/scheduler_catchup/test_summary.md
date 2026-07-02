# Scheduler Catch-Up — Test Summary

**Generated:** 2026-07-02 00:40 IST
**Command:** `python -m pytest tests/test_scheduler_catchup.py tests/test_dashboard_app.py tests/test_qc_validator_dhan_aliases.py tests/test_qc_runtime_anomaly.py -v`
**Result:** ✅ 33/33 passed, 0 failed

## Required Scenarios (all 10 covered)

| # | Scenario | Test | Status |
|---|---|---|---|
| 1 | Exact-time job still fires | `test_exact_time_job_still_fires` | ✅ |
| 2 | Missed job within catch-up window fires once | `test_missed_job_within_catchup_window_fires_once` | ✅ |
| 3 | Missed job outside catch-up window does not fire | `test_missed_job_outside_catchup_window_does_not_fire` | ✅ |
| 4 | Restart after scheduled time does not permanently hide job status | `test_restart_after_scheduled_time_does_not_permanently_hide_status` | ✅ |
| 5 | Same job does not fire twice for same date/time | `test_same_job_does_not_fire_twice_for_same_date_time` | ✅ |
| 6 | Market-dependent job does not catch up when market closed | `test_market_dependent_job_does_not_catchup_when_market_closed` | ✅ |
| 7 | Paper lifecycle job does not run without broker proof | `test_paper_lifecycle_does_not_run_without_broker_proof` | ✅ |
| 8 | Paper lifecycle job does not run without valid option contract proof | `test_paper_lifecycle_does_not_run_without_valid_option_contract_proof` | ✅ |
| 9 | Post-market proof pack does not run before upstream artifacts exist | `test_post_market_proof_pack_does_not_run_before_upstream_exists` | ✅ |
| 10 | Scheduler health reports pending/missed/catchup status instead of empty jobs | `test_scheduler_health_reports_honest_status_not_empty_jobs` | ✅ |

## Extra tests added

- `test_make_fire_key_uniqueness` — fire keys differ across job_id/date/schedule_time independently
- `test_pending_job_not_yet_due_is_not_misreported_as_missed`
- `test_auto_retrain_does_not_fire_without_retrain_signal` — never blindly retrains
- `test_no_policy_entry_defaults_to_never_catchup` — conservative default confirmed

## Regression check

All 19 pre-existing tests (`test_dashboard_app.py`, `test_qc_validator_dhan_aliases.py`, `test_qc_runtime_anomaly.py`) still pass unchanged. Full raw output: `reports/latest/scheduler_catchup/test_results.txt`.
