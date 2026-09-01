# Genesis System3 — Billing Emergency + Laptop-First PAPER Runtime SSOT

**Authority marker:** `SYSTEM3_BILLING_LAPTOP_FIRST_SSOT_V1`
**Status:** LIVING DOCUMENT — update whenever evidence, architecture, cost, blockers, or migration state changes.
**Repository authority:** `psw2025-cmd/Genesis_System3` remote `main`.
**Coordination:** Issue #188 and owning PR threads.

## 1. Goal and controller rule
The user defines the outcome; agents own technical discovery, downstream-impact analysis, implementation planning, verification, recovery, and proof. Classify dependencies as VERIFIED / TO VERIFY / CONFLICT / RISK / BLOCKER. Do not require the non-coder user to discover technical impacts.

Current objective: stop unnecessary GCP cost; move development/runtime proof to a clean laptop-first architecture; make Genesis PAPER a complete simulated-trading mode; retain truthful external-agent observability; return to GCP for final deployment only when justified.

## 2. Billing emergency
August 2026 Cloud Assist analysis reported:
- Total: INR 21,086.72
- Cloud Run: INR 10,115.50
- Cloud Logging: INR 8,002.64
- Lower-risk projection: about INR 11,499.16 (about INR 9,587.56 / 45.5% saving), pending independent verification.

Cloud Assist also reported that `genesis-system3-web` has persistent memory queues, event listeners and live socket synchronization. Therefore DO NOT switch it to request-based CPU merely for savings unless repository/runtime evidence disproves that dependency.

Priorities: prevent new unnecessary spend; preserve migration/rollback evidence before destructive cleanup; classify every billed resource KEEP / STOP / SCALE-DOWN / ARCHIVE / DELETE-LATER; take zero-functional-impact savings first; treat collector cadence changes (e.g. 1m -> 3m) as functional until proven; investigate Billing Support review/possible goodwill credit without promising it.

Payment/bank controls do not erase accrued charges and are not a substitute for stopping billable resources. Do not blindly delete the project, secrets, DBs, artifacts, revisions, logs or broker configuration.

## 3. PAPER vs LIVE — OpenAlgo behavior is benchmark
### PAPER / Analyzer
- current market data where available;
- real strategy/prediction/signal computation;
- simulated execution only;
- simulated trade persisted in authoritative PAPER store/DB;
- entry/exit/qty/price/SL/TP/reason/P&L/lifecycle visible in dashboard/evidence;
- ZERO broker real-money orders.

PAPER is not working merely because forecasts/signals exist. Acceptance requires an end-to-end genuine PAPER lifecycle created by current runtime logic and persisted/displayed truthfully.

### LIVE
LIVE is separate broker-directed real-money execution and remains locked/off under existing safety authority until explicit future human break-glass authorization. PAPER debugging must never require LIVE.

### Gate investigation
Trace every candidate through `market data -> features -> strategy/prediction -> candidate -> every gate -> PAPER executor -> persistence -> API -> dashboard`. Record gate name/result/reason and whether it belongs to PAPER or LIVE-only. Re-derive the historical "5 of 7 gates" claim from current evidence; never guess the remaining two gates.

## 4. Laptop-first architecture
During development/PAPER validation:
`GitHub remote main (code authority) -> clean laptop runtime -> PAPER state -> local dashboard -> controlled observability/proof -> GitHub evidence/coordination`.

Laptop PASS is not final GCP production PASS.

Before migration map: exact SHA/branch; runtimes/dependencies; env/config; GCP Secret Manager dependencies (names only, never values); broker credential/token lifecycle and secure local replacement; DB/schema/migrations/state; market data/instruments; schedulers/jobs/collector cadence; models/artifacts; PAPER engine; APIs/backend; frontend; WebSockets/event listeners/queues; alerts; logs/metrics/heartbeats; controlled URLs/tunnels; recovery/backfill; GCP-only IAM/services; startup/shutdown; backup/rollback; retained-GCP cost.

Never put secrets in GitHub, Markdown, screenshots, issues, logs or prompts.

## 5. Laptop outage truth
Runtime states: `RUNNING`, `OFFLINE`, `RECOVERING`, `INCOMPLETE_GAP`.
Every proof includes last verified heartbeat/time and exact Git SHA. Power/hang/internet loss means no continuity assumption. Mark the exact gap. Backfill only what data can legitimately reconstruct; otherwise preserve the gap. Recovery: stale heartbeat -> OFFLINE -> restart -> verify code/config/state -> reconcile/backfill -> validate -> RECOVERING -> RUNNING only after proof.

## 6. External-AI observability
GitHub = code authority + Issue #188 coordination + durable evidence pointers. Laptop = runtime authority during laptop-first phase. Controlled HTTPS endpoint/tunnel may expose dashboard/API while online but no secrets/unsafe controls. Google Drive may archive/synchronize snapshots but is NOT the live coordination authority and does not prove runtime is online.

Every snapshot: generated-at, runtime state, Git SHA, heartbeat freshness, gap/recovery status, provenance. Stale heartbeat => OFFLINE/UNKNOWN.

## 7. Clean clone/local hygiene
Preferred after forensic preflight: fresh clone from verified remote `main` becomes canonical laptop code runtime. Preserve old checkout read-only until local-only material is classified/salvaged. Do not automatically migrate venv, node_modules, caches, generated logs/builds, duplicate agent folders, temporary downloads or token files.

Separate clean clone, runtime-data/state, evidence/backups, and read-only archive. No arbitrary duplicate project folders without purpose/owner/source SHA/cleanup plan.

## 8. Laptop agent — CHECKPOINT 1 READ-ONLY PROMPT
```text
SYSTEM3 LAPTOP-FIRST MIGRATION — CHECKPOINT 1 / READ-ONLY FORENSIC PREFLIGHT

Repository authority is ONLY psw2025-cmd/Genesis_System3 remote main.
Do not modify, delete, move, clean, reset, checkout, pull, merge, stash, install, rotate credentials, start LIVE trading, deploy, or create a replacement clone yet.

Goal: produce evidence for ChatGPT controller to decide clean-clone and laptop migration.

1. Re-read current repo agent/runbook/authority instructions and latest Issue #188.
2. Identify every plausible Genesis System3 local checkout/folder. Report absolute path, size, branch, HEAD SHA, remote, ahead/behind if safely obtainable, git status, untracked/ignored footprint and last-modification evidence.
3. Inventory modified/untracked/local-only files without changing them. Classify SOURCE / CONFIG / SECRET-SENSITIVE / DB-STATE / MODEL / LOG-EVIDENCE / CACHE-BUILD / UNKNOWN.
4. Identify local DB/state stores, models, instruments, schedulers/tasks/services, environment/config and broker/runtime credential mechanisms. NEVER print secret/token/password/TOTP values; names/locations/metadata only.
5. Identify dependencies supplied by GCP: Secret Manager names, Cloud Run services/jobs, Scheduler jobs, DB/storage, Artifact Registry, IAM/service identities, URLs, logging/monitoring and other cloud-only assumptions. Do not mutate GCP.
6. Trace current PAPER path from signal through gates to simulated execution, persistence, API and dashboard. Re-derive any "5 of 7" state rather than trusting history.
7. Inventory startup/shutdown/recovery requirements and power/internet failure risks.
8. Identify genuinely local-only material that would be LOST by a fresh clone versus reproducible material.
9. Recommend but DO NOT execute the smallest salvage set and clean directory structure.
10. Produce concise evidence with exact timestamps/SHA; redact secrets.

End exactly:
WAIT FOR CHATGPT — NO MUTATION PERFORMED
```
Return the complete output to ChatGPT. ChatGPT decides Checkpoint 2.

## 9. Sequential checkpoints
0 GitHub/cloud remote evidence -> 1 laptop read-only forensic -> 2 reconciliation/salvage decision -> 3 preserve required local-only state -> 4 clean clone -> 5 secure local dependencies/config/secrets -> 6 data/runtime bootstrap -> 7 PAPER E2E proof -> 8 outage/recovery proof -> 9 external observability -> 10 evidence-approved GCP cost shutdown/retention -> 11 final GCP redeployment later.

At each checkpoint: evidence -> controller review -> decision -> next prompt. Local agent must not race through destructive checkpoints.

## 10. Ownership
ChatGPT/controller: remote GitHub/Issue/PR/workflow forensics; PAPER gate architecture; reconciliation; maintain this SSOT; prepare sequential prompts; review local evidence and choose next technical action; separate GCP-authority changes; maintain cost/migration/proof/blocker ledger.

Local agent only when required: actual laptop filesystem/runtime forensics; local-only DB/config/artifact/scheduler discovery; approved migration/bootstrap/tests; laptop-only evidence; stop at `WAIT FOR CHATGPT` boundaries.

## 11. Acceptance
### Laptop PAPER
Exact SHA/config; valid market input; strategy/prediction path; candidate + gate trace; simulated trade; authoritative DB persistence; API parity; dashboard parity; lifecycle/P&L progression; broker real-order count zero.

### Cost control
Current GCP evidence proves unnecessary workloads stopped/reduced, retained resources justified, appropriate alerts/monitoring exist, and required state is preserved.

### Final production
Laptop success is not final cloud proof. Final PASS later requires exact-serving-SHA GCP deployment plus independent live URL/UI/API semantic proof.

## 12. Living-document rule
Update this file for every material new impact: credentials, broker lifecycle, DB/state, cadence, models/data, outages, external observability, costs, architecture, gates or blockers. Record evidence/source; unresolved contradictions remain visible.

## 13. Immediate next actions
- [ ] ChatGPT remote forensic of current PAPER gate path and GCP dependencies available from GitHub.
- [ ] User later handles/authorizes required GCP Billing Console/payment/support actions with kid-level guidance.
- [ ] When laptop returns, run Checkpoint 1 prompt and return output.
- [ ] No local cleanup/fresh clone before Checkpoint 1 review.
- [ ] Stop unnecessary GCP spend while preserving migration/rollback state.
- [ ] LIVE remains locked/off.
