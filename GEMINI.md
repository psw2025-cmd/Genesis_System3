
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

# Genesis System3 — Gemini operating contract

**Temporal marker:** `SYSTEM3_TEMPORAL_TRUTH_V1` — `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.
Active owner directive: `docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md`; read it and `AGENTS.md` first. September laptop-only instructions are historical.

GitHub exact approved main is code authority. Intended production is cloud-only GCP `system3-openalgo-safe` / `asia-south1`; currently no deployment certified. Laptop/mobile/Cloud Shell are optional control clients only, never required runtime or user-run command loop.

Broker authority: Dhan. Retired Render and Angel-era hosting/instructions are historical and non-authoritative for System3.

Current owner consent: autonomous GitHub fixes, tests, CI and read-only GCP verification ONLY. Never deploy, trigger a billable cloud build or mutate Cloud Run/Scheduler/IAM/secrets/billing/artifacts without separate explicit approval. Do not introduce unapproved automatic deployment.

Permanent PAPER/ANALYZE locks: `ANALYZE_MODE=1`, `PAPER_MODE=1`, `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`, `LIVE_ORDER_AUTHORITY=0`. No real orders, no order-shaped production tests, no broker secret payloads or service-account JSON keys.

A past CI check, image tag, HTTP 200 or old Cloud Run URL is historical until independently re-observed. Use fresh exact-deployed-SHA cloud API/browser/broker evidence for runtime claims. No model is sole controller; Issue #188 is context, not a substitute for proof.
