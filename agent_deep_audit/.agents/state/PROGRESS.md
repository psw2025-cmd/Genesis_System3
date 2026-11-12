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

# Genesis System3 canonical progress - RE-VERIFY

Checkpoint: 2026-11-12 11:31 IST / 06:01 UTC. Data label: UNVERIFIED.
Base GitHub main: c6f63aec9b2e45c2871ffeed56dd7f4a58e722db.
Branch: fix/owner-nse-dhan-truth-20261112. No deployment or acceptance claimed.

- Owner NSE/Dhan rule saved in active instruction and authority documents. Check official NSE https://www.nseindia.com/ and authenticated Dhan; never assume session/LIVE from a calendar, local clock or HTTP 200.
- Canonical tracker recovered using 1,872 distinct historical check identities. Every independent verdict is UNVERIFIED; old PASS was not imported. Latest verdict per check must be used if correction rows are appended.
- Latest-main state store now represents missing market status as unknown (null), clears an old open claim when source health disappears, and preserves source last_ok instead of inventing a new verification timestamp.
- Targeted tests: 15 executed, exit 0; log reports/market_truth/pytest_receipt.log. Initial attempt failed at test setup because nested output parent was missing; corrected the test environment without weakening assertions.
- Source SHA256: 60895ad1e6b7a99613e2783d61c4a6b9ed4c7db39b3e3086542229cca08c2248.
- NSE observation at 11:31:33 IST: page reported Open at 11:30; age 93.227s, STALE. Dhan NIFTY quote timestamp 11:31:33; measured age 0.227s. Combined LIVE certification remains UNVERIFIED; independent clock and synchronized price parity missing.
- Cloud revision observed: genesis-system3-web-00131-2md; digest sha256:acbd3d376a89afd236cba747f3af60cb3cb84c5bae134b41520fcd190bc24bc5. Exact source SHA not proven.
- Desktop/mobile screenshots acquired on cloud URL; page JavaScript error count 0 at acquisition. Semantic value parity NOT verified; screen has pending broker proof and reconnecting/empty values. A later cloud API read timed out.
- No approved deployment, no production readiness certificate. Previous local changes were preserved; this repair is isolated from divergent local commits.

## Eight scans - observed limits

1. Health: endpoints initially HTTP 200; later reads timed out. Availability intermittent, not certified.
2. Freshness: nine local output files older than 6 hours; these are STALE local artifacts, not cloud feed proof.
3. Calendar/expiry: official NSE current status checked; stale source detected. Local token expiry claim ~6.1h, unverified JWT metadata; preventive renewal approval/managed-rotator verification needed. Contract expiry and corporate actions NOT fully audited.
4. Errors: five Cloud Run ERROR entries observed within prior day; root cause still open. One local log had no matching errors in last 50 lines; another expected log absent.
5. P&L: local untrusted summary arithmetic matches to 0.01; receipts/costs/slippage and cloud ledger NOT reconciled.
6. UI: desktop and mobile captured; broker proof pending, full UI/backend parity UNVERIFIED.
7. Past fails: banned acceptance generator has unconditional PASS assignments. It was never run or modified. Historical certificates remain invalid as new proof.
8. Disk/security: disk 77.18% used; changed Python AST parsed, no introduced eval/exec calls. Full dependency vulnerability scan, GCP quotas and managed-secret expiry NOT verified.

Roles: PM selected saved safety work; Developer changed only scoped source; Tester ran offline failure/unknown/PAPER checks; Auditor/Critic withheld production PASS; Risk preserved order restrictions. This is role-based review, not a claim of a separate human reviewer.

Next: push repair branch, preserve exact commit receipt, obtain separate deployment approval before merge/build because main has an auto-deploy workflow. Then verify exact deployed SHA, UI/API parity and repeat after 10 minutes.
