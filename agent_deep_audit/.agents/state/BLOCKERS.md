# RE-VERIFY - historical PASS/RESOLVED below is not current certification

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

# Genesis System3 canonical blockers - no acceptance granted

Observed: 2026-11-12 11:31 IST / 06:01 UTC; base SHA c6f63aec9b2e45c2871ffeed56dd7f4a58e722db.

## OPEN: SOURCE_FRESHNESS_AND_UI_PROOF

Root cause: source observations and serving image do not establish synchronized, fresh NSE/Dhan/UI evidence. At 11:31 IST NSE session source age was 93.227s; Dhan quote age 0.227s. Cloud screen shows pending broker proof/reconnecting and empty values. Later cloud API requests timed out.
Fix used: refuse LIVE certification, preserve timestamped observations, use unknown for absent source status and preserve source last_ok. Desktop/mobile screenshots acquired; no claim of semantic parity.
Prevention: source timestamps <=60s plus independent clock <=5s and same-instrument UI/API parity required. Source price differences observed asynchronously are not labeled market errors.
If recurring: inspect actual collector/worker leases and source age; never clear QC errors or fabricate green state.

## OPEN: DEPLOYMENT_APPROVAL_AND_SOURCE_LINEAGE

Root cause: serving digest cannot be linked to an independently proven source SHA; local branch diverges from approved main. Main workflow can deploy automatically after source changes.
Fix used: dedicated repair branch from fetched origin/main; preserve unrelated dirty work. No main push/merge, image build, deployment, IAM/secret mutation or real order call performed.
Prevention: separate explicit owner approval before cloud mutation or a merge that triggers it. See DEPLOY_REQUEST.md.
Rollback target: prior observed traffic revision 00131-2md, NOT certified as a known-good product.

## OPEN: PREVENTIVE_TOKEN_EXPIRY

Root cause: existing local token payload claims expiry in approximately 6.1 hours. This metadata is not authenticated proof of cloud-secret validity.
Fix used: read expiry metadata only; no token renewal or secret mutation.
Prevention: verify managed rotation and expiry metadata read-only; obtain separate owner approval before any required rotation.

## OPEN: REMAINING_EVIDENCE

Cloud errors, paper receipts/cost/slippage reconciliation, dependency vulnerabilities, quotas, contract expiry and corporate-action audit remain UNVERIFIED. No bypass or production PASS.

## Historical continuity correction

CANONICAL_NOT_FOUND: local path repaired by recovering historical check identities into canonical tracker, all UNVERIFIED. Missing-path issue corrected; proof and push acceptance are separate. Earlier unconditional PASS certificates are historical claims only.
Test setup failure: missing nested basetemp parent; corrected parent and disabled unrelated auto-loaded pytest plugins. Subsequent 15 tests exit 0. No assertions weakened.

## GitHub save receipt
UTC: 2026-11-12T06:13:06.578977+00:00
Repair commit pushed: 1d57b2351eddc8364f71b5d168af961d8da9e0b8
Commit: https://github.com/psw2025-cmd/Genesis_System3/commit/1d57b2351eddc8364f71b5d168af961d8da9e0b8
Branch: fix/owner-nse-dhan-truth-20261112. Cloud deployment NOT performed. UI parity NOT certified.

## Baseline repeat - 2026-11-12 11:43 IST / 06:13 UTC
Draft PR: https://github.com/psw2025-cmd/Genesis_System3/pull/617 (repair head 1d57b2351eddc8364f71b5d168af961d8da9e0b8). Repeat is more than 10 minutes after first cloud screenshot. Health/state HTTP 200 and desktop screenshot acquired; mobile repeat timed out. No UI/API parity or sticky-fix certification; repair has NOT been deployed. Several hosted safety/architecture/compile/frontend gates passed at repair head; remaining security/full-proof checks pending at observation.

## Current continuation - 2026-11-12T06:49:03.832600+00:00 UTC
PART 14 saved once and GitHub read-back verified at 2eb65f90acc832b21fd07794f3ce303b7c2c39d8 (blob 292f298a5f141e23916aebfbae3e556d0b25625d). Startup pointers added to read it every Genesis turn.
Follow-on branch: fix/source-failure-ui-truth-20261112, based on that SHA; no restart of original mission.
Implemented in small source batches: unknown startup instead of browser clock; source outage no longer CLOSED; 60-second STALE threshold; desktop/mobile/session labels preserve UNKNOWN; special-session transport reads source status. Node behavior contract is now a mandatory prebuild gate.
Validation: 31 targeted Python regressions, TypeScript typecheck, production build and all prebuild behavior contracts executed successfully. Browser visual proof is NOT PASS: attempt 1 HTTP-only isolation admitted a WebSocket session update and failed the assertion; attempt 2 isolated both transports but hung; attempt 3 added explicit 15s limits/progress output and also hung. Stopped only verified test process trees. LOOP_BLOCKER_BROWSER_SIMULATION: no fourth retry; external/tool-state investigation required before visual acceptance. Product UI remains UNVERIFIED.
Fresh source scan at 2026-11-12 12:08:45 IST / 06:38:45 UTC: official NSE calendar/session JSON APIs HTTP 200; NSE session packet age 45.58s, Dhan quote age -0.42s (within 5s tolerance); both source age checks fresh. Independent clock and synchronized UI/price parity remain UNVERIFIED. No website scraping, token renewal or order call in source probe.
Cloud read-only: serving revision 00131-2md unchanged; health HTTP 200. Local summary arithmetic matches 0.01 only, not cost/slippage/cloud receipt proof. Disk 77.38%; managed token expiry, option expiry, quotas, dependency vulnerabilities and corporate actions not fully verified. No production certification.
Correction: earlier main auto-deploy warning came from divergent local checkout. The fetched approved main workflow inventory does NOT contain cloud-run-auto-deploy.yml. Separate explicit owner deployment approval remains mandatory regardless.
Next: review pushed follow-on draft and resolve browser tooling LOOP_BLOCKER; do not deploy or claim UI PASS. Roles: PM resumed, Developer fixed source truth, Tester checked behavior/build, Auditor/Critic withheld visual and production acceptance, Risk kept PAPER/order restrictions.
