# Genesis System3 — Live Multi-Agent Controller Queue

AGENT_NAME=ChatGPT Controller
AGENT_LANE=D
AGENT_ROLE=Controller / Reconciliation / Next-Task Dispatch

**Status:** ACTIVE / LIVING
**Authority relation:** Companion live queue to `GENESIS_SYSTEM3_BILLING_LAPTOP_FIRST_SSOT.md` and Issue #188. This file is for rapidly changing agent work, contradictions, and next tasks. Durable policy remains in the SSOT.

## Mandatory read order for every agent
1. `docs/control_plane/GENESIS_SYSTEM3_BILLING_LAPTOP_FIRST_SSOT.md`
2. this `GENESIS_SYSTEM3_AGENT_LIVE_QUEUE.md`
3. latest Issue #188
4. current remote `main`
5. relevant open PR/workflow ownership

Every shared write must start with `AGENT_NAME=`, `AGENT_LANE=`, `AGENT_ROLE=`.

## Controller reconciliation — 2026-09-01

### Lane A / Codex
A3 immutable preservation + clean clone: **accepted as independently corroborated evidence**, not authority-cutover proof.

A4 secure bootstrap was reported PASS by Codex, including a new supervisor and fail-closed off-market PAPER tick. However Claude independently found two root-level issues in that A4 evidence:

1. `state/gain_rank_history.json` last committed 2026-06-14 is still being used to generate 2026-09-01-dated forecasts. Trade execution is separately blocked by the real-quote gate, but forecast generation itself is not freshness-gated.
2. The clean laptop runtime is now writing a third state root under `C:\Genesis_System3_Clean\state` / `outputs`, in addition to the older local state and Firestore/cloud state. This creates a concrete split-brain risk unless exactly one runtime-state SSOT is selected.

Therefore controller status for **A4 = PARTIAL / REOPENED FOR ROOT FIX**, not final PASS.

#### Lane A immediate tasks
A4.1 — Forecast freshness authority
- Trace every input to `paper_pipeline_v8`/supervisor forecast generation.
- Prevent stale committed history from being silently treated as current prediction input.
- Define explicit freshness/provenance fields and fail-closed behavior for stale forecast source.
- Add regression tests reproducing the 2026-06-14 -> 2026-09-01 stale-source symptom.
- Do not weaken the existing real Dhan quote gate.

A4.2 — Single local state SSOT
- Inventory every local + Firestore state root touched by supervisor/PAPER/API/UI.
- Choose one authoritative laptop runtime state root, with explicit import/archive/read-only treatment for others.
- Keep code checkout separate from mutable runtime state/evidence where practical.
- Prove restart uses the same state root and does not fork a new ledger.

A4.3 — Supervisor durability
- Ensure the supervisor change is captured through normal Git branch/PR governance rather than existing only as an untracked laptop file.
- Add tests for startup, restart, duplicate-worker prevention, stale heartbeat, and LIVE/order locks.

A5 remains **BLOCKED** until A4.1/A4.2/A4.3 are independently verified. Market-hours observation can be prepared in parallel, but no PAPER lifecycle PASS may be claimed from stale forecast input or split state.

### Lane B / Google-AGI
B2/B3/B4 plans are useful but exact cost/SKU/savings claims remain qualified because programmatic actual billing line items are unavailable.

B5 pre-cutover measurement was reported PASS. Controller accepts the query-suite/planning value, but these statements require independent evidence before authority:
- that uptime/health probes are the **primary** contributor to billed Logging ingestion;
- exact attribution of the 192.84 GiB derived volume;
- the INR 695–1,475 future monthly range.

#### Lane B immediate tasks
B5.1 — Measured logging attribution
- Use read-only Logging/Monitoring metrics to estimate bytes/entries by resource, logName, endpoint/path, severity, and job.
- Distinguish observed counts/bytes from tariff-derived estimates.
- Produce retained-vs-excluded sample classes for any proposed filter.

B5.2 — Exclusion safety proof
- Prove proposed filters cannot remove broker/token failure, PAPER lifecycle, prediction/evaluation, deploy/revision, security/audit, WARNING/ERROR/CRITICAL, or production-proof evidence.
- Provide exact rollback + validation queries.
- No sink mutation yet.

B5.3 — Residual cost uncertainty
- Keep `BILLING_ACTUAL_UNAVAILABLE` explicit.
- Give ranges with assumptions, not guaranteed savings.
- Cross-check scheduler/job invocation counts and retained cloud dependencies.

B4 execution remains **BLOCKED** until Lane A replacement proof is accepted.

### Lane C / Claude + Perplexity
Claude has already provided valuable independent A3 confirmation and found the stale-forecast/state-root contradiction. Continue immediately.

#### Claude next
C3.1 — independently verify any Codex fix for stale forecast freshness and state-root SSOT.
C3.2 — verify the new supervisor cannot create real broker orders and that no alternate code path bypasses the PAPER-only lock.
C3.3 — verify API/UI compatibility claim only after actual API wiring exists; a JSON schema/output file alone is not sufficient proof of UI parity.

#### Perplexity next — distinct target
P1 — independently audit current-main repository architecture for:
- forecast source freshness and provenance,
- `CLOUD_PAPER_ENGINE=0` ownership,
- PAPER persistence/API/UI path,
- hidden alternate state roots,
- GitHub Actions/WIF assumptions for laptop-first migration.

P2 — independently review Google/AGI B5 cost attribution and identify which claims are measured, inferred, or tariff-derived. Do not duplicate Claude's local filesystem verification unless acting as explicit second-source verification.

### Lane D / ChatGPT Controller
- Track Issue #188 material agent writes.
- Reconcile contradictions promptly.
- Keep SSOT + this live queue aligned.
- Update next tasks before agents exhaust safe work.
- Do not authorize destructive cloud/local actions from agent self-declared PASS alone.

## Stop / safety locks
No LIVE trading. No real broker order placement/modification/cancellation. No blind GCP shutdown/scale, logging exclusion, secret deletion, cadence change, state deletion, or legacy local cleanup. Any such action requires prerequisite proof and controller reconciliation.

## Non-idle rule
An agent finishing the listed task must immediately re-read this file + Issue #188 and take the next highest-priority safe non-conflicting task. `IDLE`, `NO TASK`, `WAITING FOR CHATGPT`, and `WAIT FOR USER` are invalid while safe unresolved work exists.
