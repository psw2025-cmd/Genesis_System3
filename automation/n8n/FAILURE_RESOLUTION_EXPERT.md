# Dedicated Failure-Resolution Expert — Execution Contract

Scope: LEGACY Genesis System3 only. This is an orchestrator workstream specification, **not** proof that an independent worker is deployed.

## Intake and priority
- Ingest latest GitHub workflow runs, job steps, logs, head SHA, and existing open repair PRs.
- Deduplicate by `workflow_id + head_sha + normalized failure signature`.
- Priority: trading-safety regression > required CI failure > UI/browser regression > stale evidence > nonblocking quality warning.
- Only one writer owns a particular file/branch. Other reviewers may analyze in parallel but cannot race writes.

## Repair state machine
`DISCOVERED → TRIAGED → REPRODUCED → PATCHED → LOCAL_TESTED → CI_RUNNING → VERIFIED → CLOSED`.
Use `BLOCKED` with precise missing dependency if no executable route exists. Never promote to VERIFIED from a green unrelated workflow.

## Required proof fields
`failure_id`, `first_seen_utc`, `last_seen_utc`, `repo`, `head_sha`, `workflow_run_url`, `failed_job_id`, `failed_step`, `error_signature`, `root_cause_file_line`, `reproduction_command`, `fix_branch`, `fix_commit_sha`, `test_commands`, `test_exit_codes`, `post_fix_run_urls`, `verification_state`, `next_action`.
Measure `time_to_triage`, `time_to_reproduce`, `time_to_fix`, `time_to_verified` from actual timestamps, never estimates.

## Current high-priority incident
- Global Safety CI https://github.com/psw2025-cmd/Genesis_System3/actions/runs/43999881870: frontend browser job failure.
- Browser smoke https://github.com/psw2025-cmd/Genesis_System3/actions/runs/43999881899: `genesis:lazy_content_still_loading`, `mobile_genesis:render_not_proven`.
- Browser artifact https://github.com/psw2025-cmd/Genesis_System3/actions/runs/43999881899/artifacts/14291453346.
- Root cause: **not yet established**. Loading fallback is a symptom, not proof of import, API or rendering fault.
- Next executable action: inspect frontend tab mapping, lazy import, suspense/error boundary, browser harness readiness condition and browser console/network errors; reproduce; fix source or a demonstrated harness race; run browser smoke for all 23 tabs on desktop and mobile.
- Acceptance: both required workflows conclude success on the same corrected SHA; the Genesis tab renders real content with no unresolved fallback. Uploaded screenshot alone is insufficient.

## Safety
Keep PAPER_MODE=1, LIVE_ORDER_AUTHORITY=0, REAL_BROKER_ORDERS=0, LIVE_TRADING_ENABLED=0, ORDER_PLACEMENT_ALLOWED=false. Never suppress assertions, bypass branch protection, fake production proof, enable real orders or use provider secrets with untrusted PR code.
