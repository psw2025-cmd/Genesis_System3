
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
