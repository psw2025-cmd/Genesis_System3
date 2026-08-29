# RHUI_RULE_V2.2 — Genesis System3 Cloud-Only Multi-Agent Execution Contract

Status: ACTIVE when merged. Supersedes prior RUHI/RHUI rules that allowed local-laptop execution or local forensic authority.

## 0. Current acceptance lock (material change — 2026-08-26)

**Overall RHUI V2.2 = NOT_ACCEPTED** until the gate board in `reports/coordination/RHUI_V2.2_GATE_BOARD.csv` is all green for acceptance criteria.

Pinned **runtime** serving (do not blind-redeploy): SHA `fb4772f9d52b67a31b55ee85aab8604e525bbad6` · revision `genesis-system3-web-00617-vif` @ 100%.

GitHub `main` tip may advance with **docs/tools-only** commits (e.g. `afd28722…` #365 Render lock). That is **DOCS_ONLY_LAG**, not runtime drift, when Cloud Run Auto Deploy path-filters skip the push. Do not redeploy solely to equalize docs tips.

Mandatory multi-verify artifacts:

- `docs/handoffs/RHUI_V2.2_MATERIAL_CHANGE.md`
- `reports/coordination/RHUI_V2.2_Verification_Checklist.json`
- `reports/latest/rhui_v22_verify/` (+ latest `cross_verify_*` folder)
- `reports/latest/repo_path_audit/cloud_github_vs_laptop.json`
- Issue #188 `SYSTEM3_COORDINATION_V1` comments

Fail-closed distinctions agents must keep:

1. Cloud Run deploy PASS ≠ scheduler-health PASS ≠ RHUI ACCEPTED.  
2. 22/22 visual tab mounts ≠ semantic API↔UI acceptance.  
3. Pre-market 4/4 NOT READY ≠ broker/token failure (recheck after open).  
4. `observability.alert_severity_none` failure is an observability predicate — attribute the workload (current: `genesis-system3-signals` stale) before touching tokens/IAM.  
5. #367 code on serving ≠ prediction evidence proven (wait for genuine 18:45 IST signals run).  
6. Docs-only `main` tip ahead of serving ≠ failed deploy (check Auto Deploy path filters before workflow_dispatch).

## 1. Single source of truth

All agents (ChatGPT, Cursor, Claude, Codex and any future agent) must reconstruct current state from:

1. GitHub current `main` SHA in `psw2025-cmd/Genesis_System3` — **only code authority**.
2. GitHub Issue #188 — canonical shared technical/progress bus.
3. `reports/coordination/ruhi_task_ledger.csv` — task ownership, dependencies, progress and proof.
4. `docs/handoffs/MULTI_AI_COORDINATION_LIVE.md` — coordination snapshot.
5. Authoritative GCP `system3-openalgo-safe` — **only runtime/deployment authority**.
6. Gmail only as transport/notification; durable state must be reflected back into GitHub.

Local laptop repos, local branches, local databases, local Cursor state/history, local token files, local schedulers, local reports and local historical artifacts are **NON-AUTHORITATIVE**. They must not be used for execution, deployment, broker/token recovery, proof or acceptance.

## 2. Cloud-only execution lock

All implementation must start from a fresh remote GitHub `main` in a clean cloud-capable lane.

Forbidden:

- deploying from a laptop checkout;
- minting/rotating broker tokens from a laptop;
- using local `.env`, token files, databases or scheduled tasks as current truth;
- copying a local file/branch into current main because it existed historically;
- using local screenshots/logs as production acceptance;
- allowing a local Cursor/IDE agent to become runtime authority.

Any useful historical idea must be re-derived from current GitHub main, independently reviewed, and implemented through the normal GitHub PR → CI → merge → GCP deploy → exact-serving proof flow.

## 3. No invisible work

Every meaningful agent status must reconcile:

- `RULE_VERSION`
- `BATCH_ID`
- `CURRENT_MAIN_SHA`
- `SERVING_SHA`
- `MARKET_PHASE`
- `PREVIOUS_BATCH_COMMITMENT`
- `PREVIOUS_BATCH_RESULT`
- `COMPLETED_WITH_PROOF`
- `NOT_COMPLETED`
- `BLOCKERS_OR_CONFUSION`
- `HANDOFF_REQUIRED`
- `NEXT_BATCH_COMMITMENT`
- `USER_ACTION_REQUIRED`

A task is not complete because code exists, CI is green, a PR merged or an API returned 200. Completion requires the proof class defined in the ledger.

## 4. Rolling batch rule

Default next batch is the highest-priority executable work, normally up to 20 real tasks.

Every new RHUI status must reconcile the previous batch task-by-task:

- `DONE`: acceptance criteria met and proof recorded.
- `PARTIAL`: some criteria met; remaining work explicit.
- `BLOCKED`: exact blocker and owner/access dependency recorded.
- `SUPERSEDED`: newer task/fix invalidated it; link replacement.
- `NOT_STARTED`: explain why skipped.

Unfinished commitments may not silently disappear.

## 5. Proof hierarchy

For user-visible dashboard behavior, proof priority is:

1. Production dashboard URL rendered in a real browser on exact serving SHA.
2. Screenshot/video/browser artifact tied to URL + timestamp + serving SHA.
3. UI semantic assertion/result tied to exact serving SHA.
4. Same-session backend/API correlation.
5. CI/unit tests.
6. Source/docs only.

For UI tasks, levels 4–6 alone cannot yield `DONE`.

A route-render PASS is not a semantic/data-readiness PASS. Blank/WAITING/placeholder/false-green state fails unless it is explicitly truthful for the current state.

## 6. Specialist ownership

- **ChatGPT**: controller/consolidator, task ownership, acceptance criteria, GitHub/GCP coordination, contradiction resolution, PR/merge/deploy/proof decisions.
- **Claude**: independent cloud/GCP/UI/API forensic verifier and adversarial cross-checker.
- **Cursor/Codex/other coding agents**: implementation only from current GitHub main in cloud/remote lanes; no local-laptop authority.
- **Other agents**: claim a bounded lane in Issue #188/ledger before modifying overlapping files.

Multiple agents may investigate independently; only one implementation writer owns a functional root-cause/file lane.

## 7. Broker/token authority

Broker/token operations are cloud-only.

Canonical authority:

- GCP Secret Manager;
- isolated Cloud Run job `genesis-system3-dhan-token-rotate`;
- approved Cloud Scheduler authority;
- guarded GitHub manual-recovery workflow only when preconditions prove it is required.

The web runtime and local machines must never mint/rotate tokens.

Never blind-mint or retry-until-green. Recovery requires current evidence, single-flight/cooldown protection and metadata-only proof. Do not expose token/PIN/TOTP values.

Broker acceptance requires, on exact current serving revision:

- `/ui` visibly shows broker connected;
- same-session `/api/broker/status` confirms usable broker state;
- token source is canonical dynamic GCP authority, with metadata only;
- NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY have positive contracts/strikes and truthful source/freshness;
- no contradictory WAITING/CLOSED/stale-success state;
- `LIVE=false` and `orders=false`.

`connected=true` alone is not full acceptance.

## 8. Paper-trade acceptance

Do not mark paper trading complete until a real market-session production proof demonstrates:

market data → scanner/ranker → signal decision → paper/analyzer path → persisted paper record → dashboard row → P&L/position update.

Zero live-order safety remains mandatory:

- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`

unless a separate explicit live-trading authorization is given later.

## 9. Dashboard truth contract

The user should be able to judge progress from the authoritative production URL, not from logs or agent narrative.

All 22 current canonical tabs must be audited region-by-region. Each visible card/badge/table/chart/status/empty-state should be classified as one of:

- `PASS_TRUTHFUL`
- `PASS_DERIVED_TRANSPARENT`
- `STALE_EXPLICIT`
- `DEGRADED_EXPLICIT`
- `UNKNOWN_EXPLICIT`
- `PLACEHOLDER`
- `HARDCODED`
- `DEMO_OR_MOCK`
- `FALSE_GREEN`
- `MISLEADING`
- `MISSING`
- `BROKEN`
- `NOT_APPLICABLE`

User-visible DONE requires exact-current-main Cloud Run revision at 100% traffic and fresh browser proof.

## 10. Stages and progress measurement

Use:

`DISCOVERED -> ROOT_CAUSE_PROVEN -> PATCHED -> TESTED -> EXACT_HEAD_GATED -> MERGED -> DEPLOYED -> UI_PROVEN -> STABILITY_PROVEN -> COMPLETE`

Each meaningful report must publish task counts and reconcile:

`PREVIOUS_TARGET -> ACTUAL_RESULT -> PROOF -> DELTA -> NEXT_TARGET_BATCH`.

Progress percentages must come from task states, not estimates.

## 11. No stale-claim rule

Before starting or reporting a task, verify current remote main, current serving SHA/revision and latest shared RHUI state. Old SHA/revision/email/artifact proof is historical and cannot drive current acceptance.

## 12. Failure and regression rule

Any recurrence after a claimed fix reopens the task or creates a linked regression. Current production truth overrides historical green status.

## 13. Human escalation boundary

The user is not a routine coordination relay.

Human action is allowed only for genuine external owner-only boundaries such as:

- billing/subscription/funding;
- identity/consent;
- official broker account/MFA/credential reset;
- unavailable external permission with no safe cloud bridge;
- destructive action requiring explicit approval;
- explicit LIVE trading approval.

Routine repo, CI, deploy, broker-status, scheduler, UI and proof work remains agent-owned.

## 14. Safety

Do not weaken IAM/WIF, expose secret values, mint/rotate tokens unnecessarily, enable live trading, place/modify/cancel live orders, dilute gates or accept retry-until-green behavior merely to make proof pass.

## 15. Definition of a useful agent cycle

A useful cycle produces at least one of:

- a newly completed task with required proof;
- a materially narrowed root cause with evidence;
- a tested bounded remediation;
- a resolved access/coordination blocker;
- a regression converted into an owned task;
- a new exact-serving browser/API truth observation.

Pure restatement of old status does not count as progress.

## 16. Dhan live market parity (HIGH PRIORITY)

System3 production UI/API must be continuously compared to **live Dhan** (`web.dhan.co`) for every market-visible surface. Cloud serving SHA + browser proof beat laptop reports.

### Mandatory compare surfaces

1. Index option chain: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX, BANKEX  
2. Equity option chain (underlying search + security_id mapping)  
3. Top CE / equity option scanner ranks  
4. Positions, portfolio/holdings, funds (read-only)  
5. Charts/graphs and any visual market widgets  
6. Header meta: spot, change%, ATM IV, PCR, lot, days-to-expiry, market open/closed  

### Required chain columns (match Dhan advanced option chain)

LTP, **LTP Chg (%)**, OI, **OI chg (%)**, Volume, **Vol chg (%)**, **Buildup**, IV, Bid, Ask, Strike, Delta, Gamma, Theta, Vega.

Absolute-only ChgOI/Vol without % and without Buildup/LTP Chg/Greeks = **NOT full match**.

### Freshness / false-green bans

- During market hours, chain must be **LIVE** (age gated) or explicitly **STALE/DEGRADED** — never `status=OK` on an old EXPIRY SNAPSHOT while claiming live readiness.  
- Default chain view must center **ATM ± N**, not deep OTM strikes that look like a wrong underlying.  
- Equity options require Dhan **security_id** / scrip-master mapping; index-only proofs cannot close equity tasks.  
- Missing chart/holdings/funds routes must be labeled MISSING/BROKEN — not silent 404 behind a green broker badge.

### Live tracking evidence (keep updated)

- Issue ledger path: `reports/latest/dhan_parity/DHAN_LIVE_PARITY_ISSUES.md`  
- API compare: `reports/latest/dhan_parity/DHAN_PARITY_LIVE_COMPARE.json`  
- Keep open: production `/?tab=chain` + `/?tab=broker` and Dhan advancedoptionchain / positions / portfolio  

A batch that claims “chain ready” without same-session Dhan parity proof is **NOT DONE**.

## 17. Agent project-memory is not authority

Claude.ai / Cursor / ChatGPT **project memory**, chat recaps, scheduled Claude jobs, and uploaded lock files are **ingest-only**.

Rules:

1. Ingest useful goals into GitHub (`docs/handoffs/SYSTEM3_MASTER_AUTOMATION_RUNBOOK.md` §9 + `reports/latest/claude_memory_audit/`).
2. Cross-verify every SHA, revision, secret **version**, timeout, and blocker against GitHub `main` + live `/api/deploy_info` + `/api/broker/status` + `/api/auto_gates` in the same session.
3. Classify claims: **KEEP** (principle) / **REFRESH** (re-fetch numbers) / **REJECT** (false or unsafe).
4. Reject any memory that enables LIVE orders, weakens gates, or says “never wait for human approval” for LIVE/break-glass.
5. Claude scheduled automations are helpers — they do not replace GitHub Actions or GCP Scheduler truth.
