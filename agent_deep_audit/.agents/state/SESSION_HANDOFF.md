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

# Genesis canonical handoff - 2026-11-12 11:31 IST / 06:01 UTC

Read canonical OWNER_GOALS, MASTER_CONTRACT_FINAL, EVIDENCE_PASS_CONTRACT, PROGRESS, BLOCKERS and tracker. Latest owner requires direct official NSE https://www.nseindia.com/ and read-only Dhan checks; never infer LIVE from time/calendar/cached status.

Repair branch: fix/owner-nse-dhan-truth-20261112, based on fetched main c6f63aec9b2e45c2871ffeed56dd7f4a58e722db. Original workspace changes preserved. Safe-market-state patch has 15 offline tests with exit 0; no cloud deployment.

Tracker: 1,872 unique historical IDs recovered, all independent verdicts UNVERIFIED. No production certificate, independent-review certification or UI parity claim.

Observed serving revision: genesis-system3-web-00131-2md. Desktop/mobile screenshots exist; screen has pending broker proof and empty values. Later API reads timed out. NSE source stale at final check, Dhan quote fresh; combined market LIVE UNVERIFIED. Local token expiry metadata preventive warning, no renewal attempted.

Next: review exact branch/commit and raw receipts; do not merge into push-triggered deployment without separate explicit YES. Remaining cloud/data/UI evidence must be checked after any authorized deployment, including 10-minute repeat. PAPER/ANALYZE only; no order routes or token renewal during read-only checks.
