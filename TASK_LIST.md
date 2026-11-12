
## OWNER_NSE_DHAN_LIVE_CHECK_20261112 - current owner instruction

- Always check the actual current market using official NSE https://www.nseindia.com/
  and authenticated Dhan read-only market data. Never infer LIVE or market ON/OFF
  solely from weekday, local time, static calendars, HTTP 200, cached files or old reports.
- Verify NSE segment/session status, exchange timestamp, holidays, Muhurat and special
  sessions; inspect corporate actions before interpreting price jumps. Cross-check Dhan
  packet timestamps and same-instrument identity with NSE. Capture UTC and IST.
- LIVE requires fresh market packets (age <=60 seconds), valid positive price and
  independently checked clocks within 5 seconds. Retrieval time is not exchange time.
  A stale page that says Open is STALE, not evidence of current market status.
- Missing, denied, expired, stale or conflicting sources => UNKNOWN/UNVERIFIED or STALE;
  show the reason, never assume market closed or invent prices or green readiness.
- Dhan reads only: never call order routes or auto-renew tokens during a check.
  Do not print secrets. Stop on authentication/rate-limit errors; no retry hammering.
- Canonical mission/state: agent_deep_audit/.agents/mission and state. Other copies
  are OLD_IGNORE_DO_NOT_USE. Preserve historical evidence; do not import old PASS as proof.
- Latest owner permits autonomous discovery, backup, fixes, tests and safe branch push.
  Continue small batches; separate explicit YES still required for deployment, billing,
  IAM, secrets and deletion. No real orders. No unattended-monitoring claim without proof.

# Current canonical repair queue

- [LOCAL_TESTED] Missing market source status is unknown, not assumed closed; source last_ok is preserved. 15 targeted tests exit 0. Cloud proof pending.
- [SAVED] NSE https://www.nseindia.com/ plus read-only Dhan requirement added to active instructions. Historical docs are not live proof.
- [RECOVERED_UNVERIFIED] Canonical 1,872-check tracker; no old independent PASS promoted.
- [PENDING] Push repair branch and record exact commit; no main merge that auto-deploys without YES.
- [PENDING] Cloud source lineage, fresh NSE/Dhan/UI parity, paper receipts/costs/slippage reconciliation, managed-token expiry, cloud error root causes.
- [PENDING] Post-deployment desktop/mobile and 10-minute repeat verification.

Do not run scripts/run_1872_acceptance_pipeline.py as acceptance proof. Preserve historical outputs. Do not import divergent local commits into approved main. Deployment approval boundary: DEPLOY_REQUEST.md.

## GitHub save receipt
UTC: 2026-11-12T06:13:06.578977+00:00
Repair commit pushed: 1d57b2351eddc8364f71b5d168af961d8da9e0b8
Commit: https://github.com/psw2025-cmd/Genesis_System3/commit/1d57b2351eddc8364f71b5d168af961d8da9e0b8
Branch: fix/owner-nse-dhan-truth-20261112. Cloud deployment NOT performed. UI parity NOT certified.

## Current continuation - 2026-11-12T06:49:03.832600+00:00 UTC
PART 14 saved once and GitHub read-back verified at 2eb65f90acc832b21fd07794f3ce303b7c2c39d8 (blob 292f298a5f141e23916aebfbae3e556d0b25625d). Startup pointers added to read it every Genesis turn.
Follow-on branch: fix/source-failure-ui-truth-20261112, based on that SHA; no restart of original mission.
Implemented in small source batches: unknown startup instead of browser clock; source outage no longer CLOSED; 60-second STALE threshold; desktop/mobile/session labels preserve UNKNOWN; special-session transport reads source status. Node behavior contract is now a mandatory prebuild gate.
Validation: 31 targeted Python regressions, TypeScript typecheck, production build and all prebuild behavior contracts executed successfully. Browser visual proof is NOT PASS: attempt 1 HTTP-only isolation admitted a WebSocket session update and failed the assertion; attempt 2 isolated both transports but hung; attempt 3 added explicit 15s limits/progress output and also hung. Stopped only verified test process trees. LOOP_BLOCKER_BROWSER_SIMULATION: no fourth retry; external/tool-state investigation required before visual acceptance. Product UI remains UNVERIFIED.
Fresh source scan at 2026-11-12 12:08:45 IST / 06:38:45 UTC: official NSE calendar/session JSON APIs HTTP 200; NSE session packet age 45.58s, Dhan quote age -0.42s (within 5s tolerance); both source age checks fresh. Independent clock and synchronized UI/price parity remain UNVERIFIED. No website scraping, token renewal or order call in source probe.
Cloud read-only: serving revision 00131-2md unchanged; health HTTP 200. Local summary arithmetic matches 0.01 only, not cost/slippage/cloud receipt proof. Disk 77.38%; managed token expiry, option expiry, quotas, dependency vulnerabilities and corporate actions not fully verified. No production certification.
Correction: earlier main auto-deploy warning came from divergent local checkout. The fetched approved main workflow inventory does NOT contain cloud-run-auto-deploy.yml. Separate explicit owner deployment approval remains mandatory regardless.
Next: review pushed follow-on draft and resolve browser tooling LOOP_BLOCKER; do not deploy or claim UI PASS. Roles: PM resumed, Developer fixed source truth, Tester checked behavior/build, Auditor/Critic withheld visual and production acceptance, Risk kept PAPER/order restrictions.
