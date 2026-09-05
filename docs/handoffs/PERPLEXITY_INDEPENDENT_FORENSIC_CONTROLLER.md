# Perplexity Independent Forensic Controller — Genesis System3

## Purpose

This is the durable, shareable handoff for Perplexity. It is intentionally a **read-only independent forensic/research lane** so Perplexity can work deeply in parallel without colliding with Cursor, Claude, ChatGPT, or an active PR.

Repository scope is **ONLY** `psw2025-cmd/Genesis_System3`.

Production/deployment authority is **ONLY Google Cloud Platform**, project `system3-openalgo-safe`, Cloud Run service `genesis-system3-web`, region `asia-south1`. Legacy Render deployment is retired/non-authoritative. Historical Render evidence may remain only when explicitly historical; generic programming terms such as React `render`, renderer, chart rendering, and browser rendering are unrelated and must not be deleted.

Issue **#188 is the coordination bus and P0 acceptance authority**. Perplexity must read its newest markers before each work cycle and must never rely on the SHA/status written in this document as current truth.

---

## Mandatory boot sequence — every run

Before analysis:

1. Fetch remote `origin/main` and record the exact SHA.
2. Read the newest Issue #188 coordination/status markers.
3. Enumerate every current open functional/docs PR, exact head/base, draft state, changed files, and stated owner.
4. Build a changed-file overlap map.
5. Read `AGENTS.md` and the current coordination/governance files that exist on that exact main.
6. Treat old emails, screenshots, reports, previous PR descriptions, this document's example SHA, and previous agent summaries as historical until reconciled with current GitHub/GCP truth.
7. If an active PR already owns a file/defect surface, remain read-only on that surface and report the overlap instead of creating a competing implementation.

At creation time this handoff was branched from main `1df24c0b9569cfb2acc4e77343324176f64acb25`, but that SHA is a **creation pin only**, not a permanent current-state claim.

---

## Safety / mutation boundary

Perplexity is **READ ONLY unless Issue #188 later gives it an explicit narrow implementation lane**.

Do not:

- edit production/runtime files;
- create a competing remediation PR;
- merge or close PRs;
- dispatch/rerun/cancel deployment workflows;
- deploy Cloud Run;
- rotate/mint/recover Dhan tokens;
- read or expose secret payloads, PIN, TOTP, QR, app secret, service-account keys, or PATs;
- modify Secret Manager, IAM, WIF, Scheduler, Cloud Run settings, broker settings, billing, or organization settings;
- enable LIVE trading;
- place or simulate real orders through a live endpoint;
- weaken fail-closed acceptance just to make a test green;
- retry until green without identifying the first failure.

ANALYZE/PAPER only. `LIVE=false`, order placement disabled.

---

## Truth vocabulary

Every conclusion must be one of:

- `PROVEN` — direct current evidence supports it.
- `PARTLY_PROVEN` — some required boundaries are proven, others are not.
- `UNPROVEN` — evidence is missing or stale.
- `BLOCKED` — a named dependency/access/time boundary prevents proof.

Do not use `done`, `fixed`, `current`, `latest`, `safe`, `resolved`, `production-ready`, or `no action required` without naming the exact proof and what the statement does **not** prove.

---

## Current coordination constraints to revalidate, not inherit

At creation time, open lanes included PR #330 (Render retirement) and PR #335 (single-document semantic proof harness), plus older governance/docs/dependency PRs. These may change at any moment. Perplexity must re-read GitHub before every run.

Particularly:

- **PR #330** is the existing Render-retirement writer lane. Do not create another Render purge PR. Audit it independently and report omissions/false deletions/authority conflicts.
- **PR #335** is the existing proof-harness lane intended to preserve one hydrated browser document while switching tabs. Do not duplicate its files or implementation.
- Issue #188 remains the place to expose new P0 evidence and ownership conflicts.

---

# Workstream A — Full UI feature/truth inventory

Inventory every canonical dashboard tab and all meaningful sub-surfaces visible to the user.

For every tab/card/table/chart/status/indicator capture:

`UI_ID | tab | subview | visible label | frontend component | frontend file | store/hook | API route | backend function/file | upstream source | expected production truth | current implementation evidence | placeholder/fallback behavior | freshness/source shown? | defect/state | existing PR/owner | proof needed`

Include at least Overview, Signals, Genesis, Data Integrity, Broker, option-chain views, equity-option views, market/universe views, positions/holdings/funds, Risk/Scenarios, alerts, mobile surfaces, and every canonical tab discovered from current source rather than from an old count.

Do not claim a tab works because it renders. Distinguish:

1. route/tab exists;
2. component renders;
3. API returns data;
4. data is real and correctly sourced;
5. frontend store converges;
6. rendered semantics match API/store;
7. production exact-serving proof exists.

---

# Workstream B — Waiting/loading/empty/demo semantic scan

Perform full tracked-repo searches for user-visible or truth-affecting states including variants of:

`WAITING`, `LOADING`, `NO DATA`, `NO TIME-SERIES`, `UNPROVEN`, `DEMO`, `MOCK`, `SYNTHETIC`, `PLACEHOLDER`, `FALLBACK`, hardcoded market values, hardcoded option contracts, fake freshness/source, default `CLOSED`, default disconnected, and silent empty arrays.

For every hit classify:

- legitimate fail-closed state;
- transient startup state with bounded convergence;
- stale state that can persist incorrectly;
- test/demo-only safe code;
- production-reachable synthetic/mock defect;
- documentation only;
- unrelated term.

Return exact path, symbol/function/component and evidence. Never recommend removing a fail-closed state merely because a semantic proof rejects it; first determine why it persists.

---

# Workstream C — API → store → UI first-divergence maps

For Overview, Signals, Genesis, Data Integrity, Broker, market overview, option chains, and equity-option views map:

`upstream → backend adapter/function → cache/snapshot → API route → HTTP response → frontend poll/fetch → Zustand/store/hook → selector/derived state → component → rendered text/table/chart`

Identify:

- multiple competing truth sources;
- stale batch data suppressing fresher broker status;
- cache TTL mismatch;
- startup hydration races;
- tab/document reload effects;
- independent polling loops;
- frontend default state that can survive successful API responses;
- missing source/freshness propagation;
- API field-name/schema mismatch;
- fail-open fallback or synthetic substitution.

For each suspected divergence label hypothesis separately from proof. State the smallest observation/test that would convert it to PROVEN.

---

# Workstream D — Dhan demand-amplification and reliability audit

Find every current-main caller of Dhan:

- Profile;
- Funds;
- Holdings;
- Positions;
- OHLC/historical;
- Quote/LTP;
- WebSocket/feed;
- Expiry list;
- Option chain;
- security/instrument master;
- any recovery/auth/token-related call.

Matrix:

`caller ID | file | function | endpoint/type | initiating route/job/browser loop | cadence | startup behavior | retry behavior | cache TTL | process-local/global | instance amplification risk | terminal handling 429/805/808/906 | source/freshness output | owner/PR | finding`

Explicitly verify whether `429`, broker code `805`, `808`, and `906` are terminal/suppressed where intended. Identify any retry, nested request, tab reload, startup, scheduler, health-check, or multi-instance behavior capable of multiplying Dhan demand.

Do not rotate a token to test an amplification theory.

---

# Workstream E — NSE/BSE universe and derivatives completeness

Do not equate four index chains with complete market support.

From current source determine implementation and proof status for:

- NSE equities;
- BSE equities;
- supported indices;
- equity futures;
- index futures;
- index options;
- **equity option chains**;
- expiries;
- all strikes vs ATM-window truncation;
- contract discovery from security/instrument master;
- source and freshness propagation;
- expected broker-universe count vs API count vs rendered UI count.

Return missing paths/features and whether each gap is source-code, API integration, store/UI, proof-only, market-session-only, or GCP runtime dependent.

---

# Workstream F — Render retirement independent verification

GCP is the only production/deployment authority.

Search tracked current-main files and filenames for platform-specific legacy patterns including:

- `render.com`;
- `onrender.com`;
- `render.yaml` / `render.yml`;
- Render deploy hooks;
- Render production/service/environment wording;
- Render URLs;
- Render-specific CI/status/health scripts;
- instructions claiming laptop/Render is production authority;
- obsolete Render memory/ephemeral-files assumptions that still alter runtime behavior.

Classify every hit as:

`REMOVE_ACTIVE_LEGACY | REPLACE_WITH_GCP_AUTHORITY | KEEP_HISTORICAL_NON_AUTHORITATIVE | KEEP_UNRELATED_RENDER_TERM | NEEDS_REVIEW`

Important: do **not** blindly delete generic `render`, `renderer`, `rendering`, React render code, charts, templates, or browser-render terminology.

Audit existing PR #330 rather than opening a second purge lane. Produce omissions and unsafe/overbroad deletions as review evidence.

Completion means every active production/deployment path, workflow, runbook, agent rule and production-proof instruction resolves to GCP, while retained Render mentions are explicitly historical or unrelated programming terms.

---

# Workstream G — Browser/proof-harness quality audit

Independently audit the semantic/browser proof architecture.

Determine:

- whether the SPA is reloaded between tabs;
- whether one continuously hydrated document/session is required;
- how document identity/time origin is proven;
- whether the test waits for bounded convergence rather than fixed arbitrary sleep alone;
- what API/store/network evidence is captured in the same session;
- whether screenshots can pass while semantic data is wrong;
- false-positive and false-negative conditions;
- whether desktop/mobile proofs are semantically equivalent;
- whether forbidden `WAITING/LOADING` checks incorrectly reject legitimate closed-market states;
- whether market-open acceptance is separated from weekend/closed-market behavior.

Review PR #335 as the existing implementation lane. Return findings; do not duplicate it.

---

# Workstream H — Production-grade dashboard / future-AI capability gap research

Compare the architecture and user-visible observability—not trading-profit claims—with strong modern trading/data/ML dashboard practices.

Prioritize capabilities that make the system more truthful and diagnosable:

- source provenance per datum;
- freshness/age and stale thresholds;
- WebSocket state/reconnect/backfill status;
- request/feed latency;
- broker auth/session health distinct from market-data health;
- option-chain completeness metrics;
- universe coverage metrics;
- degraded-mode reason and failover source;
- model version/evidence/confidence/calibration;
- feature/data drift;
- data-quality checks;
- prediction horizon and timestamp;
- explainability/feature contribution where technically valid;
- audit trail and reproducibility;
- API/store/UI parity diagnostics;
- mobile information density and operational visibility;
- safe read-only incident timeline.

Do not recommend decorative visual complexity unless it improves decisions, provenance, diagnostics, accessibility, or observability.

Separate:

`already implemented | partially implemented | source-only/no production proof | missing | research recommendation`

---

# Workstream I — Recurrence-prevention matrix

Search Issue #188 and current source for recurring defect families. At minimum investigate:

- Dhan `906` auth/session recurrence;
- `429/805` request-rate collapse;
- option-chain collapse;
- stale batch vs broker-status convergence;
- cold-start/warming races;
- UI `WAITING/LOADING` persistence;
- semantic proof false positives/false negatives;
- exact-serving SHA drift;
- direct-main/governance bypass;
- Render authority reintroduction;
- mock/synthetic production leakage.

For each:

`defect | previous evidence | current prevention mechanism | regression test | runtime guard | production proof | recurrence still possible? | exact missing prevention`

A one-time fix is not recurrence prevention. Mark PROVEN only when structural code/test/governance evidence exists.

---

# Workstream J — Agent liveness and ownership verification

Perplexity must not treat assignment as work.

For every currently named owner in Issue #188 (ChatGPT, Cursor, Claude, Perplexity, or future agents), report:

`OWNER | ASSIGNED_LANE | LAST_FRESH_GITHUB_EVIDENCE | TIMESTAMP | STATE | OVERLAP | NEXT_ACTION`

Allowed states:

- `WORKING_PROVEN`
- `WAITING/UNPROVEN`
- `BLOCKED`
- `COMPLETE`

Fresh evidence includes commit/head movement, PR/comment/checkpoint, workflow/test result, artifact, or explicit Issue #188 marker. If an agent has no fresh evidence after handoff, say so.

---

# Workstream K — Next-20 independent priorities

After every substantial scan return exactly 20 highest-value unresolved items:

`ID | Priority | User-visible UI impact | Exact file/function/workflow | Evidence/root cause | Existing PR/owner | Overlap risk | Recommended next action | Required focused test | Required production proof | State`

Rules:

- rank P0 before cosmetic work;
- no duplicate tasks;
- if blocked, continue with another non-overlapping read-only item;
- do not assign implementation to yourself unless Issue #188 explicitly changes your lane;
- identify the **NEXT_OWNER** for each actionable row.

---

## Required evidence outputs

Prefer committing nothing during the read-only lane. Publish results through the mechanism available to Perplexity/user, and provide an Issue-#188-ready block. If later explicitly authorized to create evidence files, use these canonical suggested paths rather than inventing duplicates:

- `reports/coordination/perplexity_ui_truth_matrix.csv`
- `reports/coordination/perplexity_api_store_ui_map.csv`
- `reports/coordination/perplexity_dhan_caller_matrix.csv`
- `reports/coordination/perplexity_universe_derivatives_gap.csv`
- `reports/coordination/perplexity_render_retirement_audit.csv`
- `reports/coordination/perplexity_recurrence_matrix.csv`
- `reports/coordination/perplexity_next20.csv`
- `reports/coordination/PERPLEXITY_FORENSIC_EXECUTIVE.md`

Do not create these files merely to show activity. Evidence must be reproducible and current-main pinned.

---

## Required Issue #188 checkpoint format

Use this exact structure when a write-capable coordinator posts Perplexity's result:

```text
SYSTEM3_COORDINATION_V1
AGENT=PERPLEXITY
MODE=READ_ONLY_FORENSIC
MAIN_SHA=<fresh exact main>
EVIDENCE_TIMESTAMP=<UTC>
STATE=<WORKING_PROVEN|WAITING/UNPROVEN|BLOCKED|COMPLETE>

PREVIOUS_COMMITMENT:
- ...

ACTUAL_RESULT:
- ...

PROOF:
- GitHub paths/PRs/issues/workflows/artifacts/production evidence

NEW_P0:
- NONE or exact finding

OVERLAP:
- NONE or exact PR/file/owner conflict

NEXT_OWNER:
- ...

NEXT_20:
1. ...
...
20. ...

HUMAN_ACTION_REQUIRED=NO|YES
HUMAN_ACTION_REASON=<only genuine human boundary>
```

---

## Coordination with ChatGPT, Cursor and Claude

### ChatGPT controller

ChatGPT owns consolidation: fresh authority, Issue #188 state, overlap, exact-head acceptance, contradictions, liveness, dependency release, deployment/production proof tracking, and final closure decision. Perplexity should give ChatGPT evidence that can be independently rechecked, not conclusions that require trust.

### Cursor

Cursor is the preferred narrow implementation agent for its explicitly claimed file/PR lanes. Perplexity should identify defects and review existing Cursor PRs, but must not edit Cursor-owned files while the lane is active.

### Claude

Claude is an independent GCP/architecture/forensic verifier unless Issue #188 assigns a narrow implementation lane. Perplexity should compare evidence, highlight contradictions, and avoid duplicating Claude's active work.

### Perplexity

Perplexity owns broad independent repository research/forensics under this document. Its value is breadth, cross-checking, current-source mapping, outside research where useful, and identifying gaps before implementation.

---

## Production acceptance rules

Never infer production PASS from source/CI alone.

For runtime-affecting changes, final acceptance requires a new exact-serving Cloud Run proof and new browser evidence from the canonical production URL. Track independently:

- GitHub main SHA;
- serving SHA and Cloud Run revision;
- deployment timestamp/traffic;
- `LIVE=false`;
- order placement disabled/no order mutation;
- broker session/auth truth;
- real Dhan data usability;
- Profile/Funds/Holdings/Positions as required;
- four required index chains with contracts/strikes/source/freshness;
- NSE/BSE/equity/equity-option universe parity;
- API → store → rendered UI parity;
- persistent WAITING/LOADING/blank/demo states;
- WebSocket/reconnect/rate-limit/degraded behavior;
- required uninterrupted market-session stability window.

`connected=true` alone is never broker reliability PASS.

---

## User-visible success standard

For every finding, answer: **what will the user actually see on `/ui` when this is fixed and proven?**

Examples of acceptable proof language:

- Overview shows fresh NIFTY/BANKNIFTY values with source and age matching same-session API/store evidence.
- Option Chain shows real Dhan contracts/strikes rather than an empty/placeholder table.
- Equity option discovery exposes broker-master symbols beyond the four index underlyings.
- Broker tab distinguishes authenticated session from market-data health and degraded/rate-limited state.
- Data Integrity displays exact serving SHA, source/freshness and meaningful failure reason.

Do not call a backend-only improvement complete for a user-visible defect.

---

## Final response contract for every Perplexity cycle

Return:

`CURRENT_MAIN → ACTIVE_OWNERS → PROVEN_FACTS → ASSUMPTIONS → UI_MATRIX → DATA_FLOW_MAP → DHAN_CALLER_MATRIX → UNIVERSE_GAPS → RENDER_GAPS → PROOF_GAPS → RECURRENCE_MATRIX → AGENT_LIVENESS → NEXT_20 → UI_IMPACT → BLOCKERS → HUMAN_ACTION`

If evidence is too large, provide compact summaries plus exact artifact/path references; never omit the exact source needed for another agent to verify the claim.

---

## Completion condition for the Perplexity lane

Perplexity's forensic lane is COMPLETE only when:

1. all workstreams A–K have current-main-pinned evidence;
2. every identified P0/P1 has an owner or explicit blocker;
3. active PR overlap is reconciled;
4. Render retirement is independently classified rather than keyword-deleted;
5. UI/API/store/Dhan call paths are mapped sufficiently for a narrow implementer to act;
6. recurrence gaps are distinguished from one-time fixes;
7. Next-20 is deduplicated against Issue #188/current PRs;
8. no production/runtime mutation was performed by this lane.

This does **not** close Issue #188. Issue #188 closes only when its production acceptance contract is independently proven.