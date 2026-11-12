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
