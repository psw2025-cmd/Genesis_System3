# RHUI_RULE_V2.3 — Genesis System3 LOCAL-LAPTOP-ONLY Execution Contract

Status: ACTIVE when merged. Supersedes every prior RUHI/RHUI instruction that treated GCP or any Google Cloud service as System3 runtime, deployment, broker-token, evidence, or acceptance authority.

## 0. Permanent GCP prohibition and migration lock — 2026-09-03

Genesis System3 MUST NOT use GCP for runtime or acceptance. GCP is retired architecture and cleanup debt only.

Every current and future agent MUST:

1. Never deploy, execute, schedule, authenticate, store runtime state, rotate broker tokens, collect current proof, or establish acceptance through GCP.
2. Never restore/recreate Cloud Run, Cloud Scheduler, Secret Manager, Firebase, Firestore, BigQuery, Cloud Storage, Pub/Sub, Artifact Registry, WIF, GCP logging/monitoring, GCP CI/CD, or another Google Cloud dependency merely because historical code/docs reference it.
3. Continuously discover every remaining GCP reference/resource dependency/workflow/script/env mapping/credential mapping/document/test/URL/scheduler/database/storage/monitoring/cost driver/stale proof artifact related to Genesis System3.
4. Classify each discovery as `REMOVE`, `REPLACE_LOCAL`, `HISTORICAL_ONLY`, or `EXTERNAL_CLEANUP_REQUIRED`.
5. Replace every still-required GCP capability with a safe local-laptop equivalent before removing it. Preserve PAPER/analyzer functionality and evidence continuity.
6. Never allow GCP removal to break broker authentication, market data, option chains, persistence, scheduling/background work, alerts, logs, UI, prediction, ML, risk, PAPER trading, backup/recovery, or proof.
7. GitHub current `main` is the ONLY code authority. The authorized Windows laptop running fresh/current main is the ONLY runtime/execution authority.
8. Google Drive System3 logs/reports/screenshots are evidence/backup transport only. Current acceptance requires correlation to current main, capture time, local process/runtime identity, and same-session API/UI evidence.
9. Gmail is notification/transport only. Durable state belongs in GitHub Issue #188 and repository control-plane material.
10. Residual GCP billing/resources are cleanup debt and must remain tracked until independently proven removed. Never reactivate GCP to obtain proof.
11. Never use old Cloud Run URLs, serving SHA/revision, GCP secret versions, cloud screenshots/workflows/logs as current runtime evidence.
12. Deleting a GCP reference alone is not completion. Required functionality must work locally or be proven obsolete.

## 1. Current authority

1. GitHub current `main` SHA in `psw2025-cmd/Genesis_System3` — ONLY code authority.
2. GitHub Issue #188 — canonical coordination/progress bus.
3. Repository task ledger/control-plane material — ownership/dependencies/progress.
4. Authorized Windows laptop fresh/current-main checkout — ONLY runtime/execution authority.
5. Fresh local API/UI/runtime evidence from that current-main runtime.
6. Google Drive evidence only when correlated to that runtime.
7. Gmail only for transport/notification.

Non-current local branches, stale databases, stale Cursor state, old token files, old scheduler output and historical artifacts remain NON-AUTHORITATIVE.

## 2. Required local replacements

All implementation starts from fresh GitHub current main. Required replacements for retired cloud capabilities must be explicitly mapped/tested, including where applicable:

- secure local secret storage and environment-variable mapping;
- broker auth/session/TOTP/access-token lifecycle with safe refresh/rotation;
- local database/state persistence and backup/restore;
- local file/object/history storage replacing cloud data/storage;
- Windows Task Scheduler or approved local supervisor replacing Cloud Scheduler/Run jobs;
- local background workers, queues/events/websocket processes;
- local logging, health checks, watchdogs and alerts;
- local startup/restart/recovery after reboot/process failure;
- GitHub CI that validates code without deploying GCP;
- dashboard/API code that does not depend on Cloud Run metadata or cloud URLs.

LIVE trading remains disabled unless separately explicitly authorized.

## 3. Continuous GCP eradication verification

Every material forensic/controller cycle must inspect current main and recent runtime evidence for residual Google Cloud coupling. At minimum inspect `.github/workflows/**`, scripts, source, config/env templates, docs/runbooks, tests, scheduler definitions, broker/token code, DB/storage adapters, logging/alerts, UI/API metadata, package dependencies, recent Drive evidence, Gmail billing/decommission alerts, Issue #188 and active PRs.

Maintain migration inventory:

`ITEM | LOCATION | OLD_GCP_ROLE | REQUIRED_CAPABILITY | LOCAL_REPLACEMENT | STATE | PROOF | OWNER | BLOCKER`

Required migration lifecycle:

`DISCOVERED -> LOCAL_REPLACEMENT_DESIGNED -> REPLACED -> TESTED -> CURRENT_MAIN -> LOCAL_RUNTIME_PROVEN -> GCP_REFERENCE_REMOVED -> COMPLETE`

For obsolete functionality:

`DISCOVERED -> PROVEN_OBSOLETE -> REMOVED -> CURRENT_MAIN -> REGRESSION_CHECKED -> COMPLETE`

Unfinished items may never silently disappear.

## 4. Proof hierarchy

1. Fresh authorized local-laptop browser from current GitHub main.
2. Screenshot/video/browser artifact tied to capture time + current main SHA + local runtime identity.
3. Same-runtime UI semantic assertions.
4. Same-session local backend/API correlation.
5. Current-main CI/unit/integration tests.
6. Source/docs only.

Render PASS is not semantic readiness. Blank/WAITING/placeholder/false-green states fail unless explicitly truthful.

## 5. Broker/token authority

Broker/token operations are LOCAL-LAPTOP-ONLY. Credentials use secure local storage and secret values must never be committed to GitHub or uploaded to Drive/Gmail. Token lifecycle must be single-flight/rate-limit aware; no blind minting/retry-until-green. Evidence is metadata-only and never exposes token/PIN/TOTP values.

Broker acceptance requires visible local UI plus same-session local `/api/broker/status`, required market-data capability, truthful source/freshness, positive applicable NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY contracts/strikes, and `LIVE=false`/orders disabled. `connected=true` alone is insufficient.

## 6. PAPER acceptance

PAPER trading is complete only after applicable real-market-session local proof demonstrates:

market data -> scanner/ranker -> signal -> PAPER/analyzer decision -> persisted local paper record -> dashboard row -> P&L/position update -> restart/reconciliation persistence.

Mandatory safety remains:

- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`

## 7. Dashboard truth

All 22 canonical tabs must be audited semantically on the authorized local runtime. Visible states are classified `PASS_TRUTHFUL`, `PASS_DERIVED_TRANSPARENT`, `STALE_EXPLICIT`, `DEGRADED_EXPLICIT`, `UNKNOWN_EXPLICIT`, `PLACEHOLDER`, `HARDCODED`, `DEMO_OR_MOCK`, `FALSE_GREEN`, `MISLEADING`, `MISSING`, `BROKEN`, or `NOT_APPLICABLE`.

User-visible DONE requires current-main local runtime plus fresh same-session browser/API proof. Cloud Run URLs/revisions are forbidden as current acceptance evidence.

## 8. No stale claims

Before starting/reporting, verify remote current main, authorized local runtime identity and latest Issue #188 state. Old SHA/email/Drive/cloud artifacts are historical unless freshly correlated.

## 9. Agent ownership

ChatGPT remains controller/consolidator. Coding agents implement from current GitHub main with bounded ownership coordinated through Issue #188/active PRs. Local runtime agents execute/test/prove on the authorized laptop without becoming code authority. No agent may reintroduce GCP as a shortcut.

## 10. Human escalation

The user is not the routine technical operator. Agents own safe repo/local-runtime work whenever connected tools permit it. Human action is only for genuine owner-only boundaries such as billing/account closure, identity/consent, broker MFA/account reset, unavailable laptop permission, destructive external deletion requiring approval, or explicit LIVE authorization.

## 11. Safety

Do not expose secrets, enable LIVE trading, place/modify/cancel live orders, dilute gates, blind-rotate broker credentials, delete irreplaceable state, or remove a required cloud capability before its local replacement and backup are proven.

## 12. Action-over-narrative

Every material cycle must produce an execution delta whenever possible: implementation, test, current-main reconciliation, local proof, migration inventory update, stale-GCP removal, or blocker resolution. Repeated commentary without advancing known work is non-compliant.

## 13. GCP exit completion

GCP exit is COMPLETE only when:

1. Current main has no active System3 dependency requiring GCP.
2. Every required former GCP capability has a tested local replacement or is proven obsolete.
3. No GitHub workflow can automatically recreate/deploy System3 to GCP.
4. Local startup/scheduling/secrets/state/logging/backups/recovery are proven.
5. Broker/data/UI/PAPER/ML/risk/alerts lifecycle is proven locally from current main.
6. Residual GCP billing/resources are independently confirmed removed or recorded as owner-only external cleanup debt.
7. Historical GCP documentation/evidence is clearly historical and cannot become current authority.
8. Issue #188 and active PR ownership contain no contradictory cloud-authority instruction.

Until all eight are proven, report `GCP_EXIT_INCOMPLETE`, continue local implementation/verification, and NEVER restore GCP to close the gap.
