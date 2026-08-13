# Genesis System3 Manual Repository QC Master Audit

Updated: `2026-08-13 run #82 closure + current control loop`.

> **Single master authority** for `psw2025-cmd/Genesis_System3`. Google Cloud / Cloud Run is the runtime authority. LIVE remains OFF/LOCKED. No live order placement, modification, cancellation or routing is permitted. A merge, green CI, Ready revision, screenshot or HTTP 200 never equals real-money readiness by itself.

## 0. Exact current authority

- Repository: **`psw2025-cmd/Genesis_System3` only**.
- Current repository `main`: **`87076ec0b91e1e366a1c331af8017c4416434232`** — merge PR #156, tooling-only public-readonly watcher cleanup.
- Latest complete guarded **application/runtime source**: **`008f6ef18032b5ffb42a4b8b7c8fff6e78a6338b`** — merge PR #155.
- Cloud Run Auto Deploy: **run #82 / `31652417414` / SUCCESS**.
- Exact serving/latest-ready/latest-created revision proved by run #82: **`genesis-system3-web-00256-por`**.
- Traffic: **`genesis-system3-web-00256-por` / 100%**.
- Candidate was created at **0% traffic**, proved, then explicitly promoted.
- Candidate image provenance: **immutable digest verified** (`sha256:90e480b92869a413539ef15db76179b99a1905719cea1be90340cb280d7f0c90`).
- Runtime posture: **ANALYZER / PAPER**.
- `LIVE_TRADING_ENABLED=0`.
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`.
- `AUTO_EXECUTE_TRADES=0`.
- Public dashboard: **credential-free / public-readonly**.
- Dashboard API key mounted: **false**.
- Secret payload exposed by proof: **false**.
- Real live-order actions in this control loop: **0**.

PR #156 changes only proof tooling/tests and therefore does not supersede run #82 as the application runtime authority.

## 1. Mandatory control-loop position

`VERIFY -> SELECT -> FORENSIC RCA -> MULTIPLE SOLUTIONS -> CHOOSE LOWEST-RISK ROOT-CAUSE FIX -> PATCH -> REGRESSION/INTEGRATION/SMOKE -> PR -> EXACT CI -> MERGE -> GUARDED DEPLOY IF RUNTIME-AFFECTING -> EXACT RUNTIME/UI PROOF -> UPDATE THIS MASTER -> CLOSE`

Permanent operating rule:
- A non-user blocker is **not** a status-report deliverable.
- Create/attach a dedicated forensic closure task.
- Map all affected callers, APIs, jobs, UI consumers, caches, tests and runtime paths.
- Compare multiple technically valid remediations before selecting one.
- Never weaken a gate, threshold, freshness rule, MutationPolicy or LIVE lock to obtain green status.
- Report closure only after reproducible proof; interrupt the user only for a genuine user-controlled action or hard safety boundary.

## 2. PR / CI authority

### PR #130 — immutable Cloud Run digest provenance

- State: **MERGED / CLOSED**.
- Exact head: `56a37ae3841fe5342e5359c03570b9431d52166c`.
- Merge: `e09824188ab7c30f08c0af48cf7e27bb0a22d798`.
- Exact-head Global Safety CI: **PASS**.
- Exact-head GCP Dhan Token Fix CI: **PASS**.
- Canonical deploy entrypoint uses immutable Artifact Registry repository+digest proof.

### PR #129 — stale no-key cleanup lane

- State: **OPEN / NON-MERGEABLE**.
- Exact head: `04f27e100b53e464f5d6ba5b407d8faaff74b3ef`.
- Global Safety CI: **FAIL**.
- GCP Dhan Token Fix CI: **PASS**.
- GCP Stage 2 Safety: **PASS**.
- Workflow Priority Guard: **PASS**.
- Never wholesale merge/rebase this stale lane. Salvage only focused current-main-safe slices.

### PR #154 — StateTruth precedence repair

- State: **MERGED**.
- Merge: `f90545eb34cb047ac4b72bcd10917e136a2c52af`.
- Root cause addressed: Firestore mode could allow stale `health.json` broker truth to override the same-cycle direct Dhan probe.
- Remediation: stale local health file is no longer authoritative broker state in Firestore runtime; current direct broker truth wins fail-closed.

### PR #155 — bounded Cloud Dhan broker status probe

- State: **MERGED**.
- Merge/application SHA: `008f6ef18032b5ffb42a4b8b7c8fff6e78a6338b`.
- Root cause addressed: generic Dhan status path could perform serial SDK + REST work under the web request deadline, producing ~12 s degraded status despite a valid dynamic token.
- Remediation: Cloud runtime uses one bounded read-only Dhan profile probe; Secret Manager dynamic reload and canonical rotator remain unchanged.
- Regression coverage includes connected cache, invalid-token classification, bounded timeout and HTTP 401 behavior.

### PR #156 — permanent watcher public-readonly cleanup

- State: **MERGED**.
- Merge/current main: `87076ec0b91e1e366a1c331af8017c4416434232`.
- Exact head: `8983bba92aa9cf52af6bc6d9d9124c7bcf4efcb9`.
- Exact-head Global Safety CI: **PASS**.
- Removed legacy `DASHBOARD_API_KEY` / `X-API-Key` / `/api/auth/session` authority from `tools/permanent_live_log_watch.mjs`.
- Permanent watcher now proves anonymous GET-only `public_readonly` / `credential_surface=REMOVED` plus `/api/health` and `/api/broker/status` sentinels.
- Regression contract forbids retired auth/session markers and order place/modify/cancel routes.

### Parallel stale lanes

- PR #121 Observability: **open/non-mergeable**; only current-main-safe read-only correlation, redacted synthetic, uptime/runbook concepts are eligible for selective salvage.
- PR #125 OperationsTruth: **open/non-mergeable**; only typed read-only inventory/SLO/operations evidence is eligible for selective salvage.

## 3. Exact Cloud Run run #82 deployment truth

Run #82 (`31652417414`) completed **SUCCESS** on application SHA `008f6ef18032b5ffb42a4b8b7c8fff6e78a6338b`.

- Previous serving traffic: `genesis-system3-web-00254-kiy` / 100%.
- Candidate: `genesis-system3-web-00256-por`.
- Initial candidate traffic: **0%**.
- Candidate image digest proof: **PASS**.
- Candidate HTTP proof: **PASS**.
- Public no-key dashboard proof: **PASS**.
- MutationPolicy proof: **PASS**.
- Dhan rotator/Scheduler configuration: **PASS**.
- Explicit rotation execution: **PASS**.
- Runtime identity/safety proof: **PASS**.
- Public broker read gate: **PASS**.
- Sanitized runtime evidence: **PASS**.
- Provenance/public-dashboard safety lock: **PASS**.
- Explicit promotion: **PASS**.
- Final serving traffic: **`genesis-system3-web-00256-por` / 100%**.

## 4. UI/dashboard exact proof — run #82

Artifact `public-paper-dashboard-proof-82`:

- Matrix state: **PASS**.
- Canonical tabs: **22**.
- Tabs passed: **22/22**.
- Tabs failed: **0**.
- Desktop tab screenshots: **22/22**.
- Mobile tab screenshots: **22/22**.
- Exact tab screenshots: **44/44**.
- Canonical dashboard screenshot: **1 additional PNG**.
- Total PNG proof files: **45**.
- Retry captures: **0**.
- Browser transport: **single-session WebDriver matrix**.
- Browser trading mutations called: **false**.
- API-key prompt rendered: **false**.
- API key sent: **false**.
- Session cookie sent: **false**.
- `/ui`: HTTP **200**.
- `/api/auth/status`: HTTP **200**, `mode=public_readonly`, `required=false`, `credential_surface=REMOVED`.
- Expected/deployed SHA match: **true** (`008f6ef...`).

UI rendering proof is green for the exact serving application source. This does not override red market-data/readiness gates.

## 5. Permanent health / broker / StateTruth sentinels — run #82

### `/api/health`

- HTTP: **200**.
- `status=ok`.
- `mode=PAPER`.
- Sanitized round-trip: approximately **321 ms**.

### `/api/broker/status`

- HTTP: **200**.
- `connected=true`.
- `error_present=false`.
- token source: **`GCP_SECRET_MANAGER_DYNAMIC`**.
- Secret Manager version: **110**.
- token value exposed: **false**.
- broker-reported internal latency: approximately **31 ms**.
- endpoint round-trip: approximately **1.79 s**.
- LIVE trading enabled: **false**.
- order placement allowed: **false**.

### `/api/state`

- HTTP: **200**.
- `mode=PAPER`.
- `broker_connected=true`.
- data source: **`BROKER_CONNECTED_MARKET_CLOSED`**.
- state version in sample: **9872**.
- round-trip: approximately **273 ms**.

### Closure verdict

The run #80 contradiction (`/api/broker/status connected=true` while `/api/state broker_connected=false`) is **RESOLVED on exact serving SHA `008f6ef...`** after PR #154 + PR #155.

Measured prevention evidence:
- broker endpoint degraded latency reduced from about **12.36 s** in run #80 to about **1.79 s** in run #82;
- `error_present` changed from **true** to **false**;
- StateTruth now agrees with direct BrokerTruth: **true / true**.

Do not reopen this incident without new contradictory runtime evidence.

## 6. Dhan token rotator / Scheduler — run #82

- Dedicated rotation execution `genesis-system3-dhan-token-rotate-z5sbm`: **SUCCESS**.
- Dynamic token secret version observed by serving runtime: **110**.
- Token value exposed: **false**.
- Scheduler: **ENABLED**.
- Schedule: **`30 7 * * *`**.
- Timezone: **Asia/Kolkata**.
- Intended identities remain separated: web runtime, dedicated rotator and Scheduler service accounts.
- No user PIN/TOTP/OAuth action required in this cycle.

## 7. MutationPolicy / capability safety — run #82

Artifact `mutation-policy-runtime-proof-82`:

- State: **PASS**.
- Capability manifest: **ENFORCED**.
- Write routes: **33**.
- Unknown write routes: **0**.
- Duplicate write routes: **0**.
- Public dashboard read-only: **true**.
- Control authority configured: **false**.
- Worker authority: **dedicated worker token**.
- PAPER unauthorized mutation: **403**.
- LIVE mutation: **423 / HARD LOCK**.
- Invalid worker token: **401**.
- Unknown mutation capability: **403**.
- Paper mutation handlers called by proof: **false**.
- Live order endpoints called by proof: **false**.
- Secret values exposed: **false**.

## 8. Current OptionChainTruth — run #82

- **NIFTY:** source Dhan; **160 contracts**; fresh snapshot available.
- **BANKNIFTY:** source Dhan; **160 contracts**; fresh snapshot available.
- **FINNIFTY:** Dhan spot available but option rows unavailable (`dhan_only_no_rows`) in the final run #82 sample.
- **MIDCPNIFTY:** Dhan spot available but option rows unavailable (`dhan_only_no_rows`) in the final run #82 sample.
- Required four-chain readiness: **NOT PROVEN**.

Dedicated forensic closure task: **Issue #157 — `P0 forensic closure: FINNIFTY/MIDCPNIFTY chain and scanner readiness`**.

Current forensic facts already established:
- index security IDs in current code are NIFTY=13, BANKNIFTY=25, FINNIFTY=27, MIDCPNIFTY=442 and use `IDX_I`;
- Dhan Option Chain API officially requires underlying security ID + segment + an active expiry and is rate-limited around one unique request per 3 seconds;
- current `DataSourceManager` prefers Dhan `expiry_list`, but its calendar fallback is an outdated next-Monday rule shared by every index;
- current NSE contract specifications use Tuesday expiry; FINNIFTY and MIDCPNIFTY have monthly option expiries rather than the old weekly structure;
- therefore expiry selection/fallback is an active forensic surface and must be proven against runtime metadata before closure, not guessed.

No readiness gate has been relaxed while this investigation is open.

## 9. Current ScannerTruth — run #82

`/api/scanner/top_contract_gainers` did not complete within the external deterministic proof budget (~30 s).

Forensic dependency facts:
- scanner index board contains NIFTY, BANKNIFTY, FINNIFTY and MIDCPNIFTY;
- scanner creates its own DataSourceManager and fetches index chains;
- DataSourceManager serializes Dhan option-chain traffic with a process-wide lock and ~3.4 s minimum gap;
- each cold index chain can require expiry-list + option-chain requests, so four-index cold fan-out can consume most/all of a 30 s external proof budget;
- unresolved no-row chains can further consume the same serialized budget.

Scanner readiness remains fail-closed. Issue #157 owns the combined chain/scanner root-cause closure; the fix must reduce redundant Dhan work or reuse authoritative chain truth rather than merely increasing the acceptance timeout.

## 10. Runtime health / latency tail — run #82

- Sanitized 24h sample: no HTTP 5xx in the captured evidence.
- Unhandled exceptions: **0**.
- Crash/restart category: **0**.
- OOM category: **0**.
- P50 latency: approximately **44 ms**.
- P95 latency: approximately **12.04 s**.
- P99 latency: approximately **12.08 s**.

Tail latency remains relevant to the chain/scanner forensic task; broker-status latency itself is no longer the dominant 12 s path.

## 11. Readiness gates

Latest repository auto-gate report remains conservative:
- `REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF`: **PASS**.
- `MODEL_ACCURACY_REPORT_PRESENT`: **PASS**.
- `ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS`: **FAIL**.
- `POSITIVE_NET_EXPECTANCY_AFTER_COSTS`: **FAIL**.
- `WEBSOCKET_TICK_HEALTH_PROVEN`: **FAIL**.
- `OPTION_STRIKE_VISIBILITY_PROVEN`: **FAIL**.
- `EQUITY_FO_ELIGIBILITY_PROVEN`: **FAIL**.

Trade ready: **false**. Analyzer-ready status must remain evidence-based; no failed performance threshold may be edited merely to create a green result.

## 12. Current strict work queue

1. **Issue #157:** prove and close FINNIFTY/MIDCPNIFTY no-row cause plus bounded deterministic scanner path.
2. **P0-3 SafetyTruth + ExecutionEligibility:** one typed canonical snapshot; unknown/stale/unsafe dependency must block; LIVE remains hard denied.
3. **Option strike / F&O eligibility:** prove current instrument universe and required contract visibility.
4. **Tick/feed health:** prove bounded analyzer feed health; WebSocket requirement stays mandatory for any future execution authority.
5. **Model performance:** improve and re-evaluate actual expectancy and multi-day predictive accuracy without weakening acceptance criteria.

## 13. Historical incident / prevention ledger

- Earlier competing Dhan token-writer incident: canonical authority is now dynamic GCP Secret Manager + isolated rotator/Scheduler.
- Earlier Firestore 403: dedicated web-runtime Firestore grant resolved the startup prerequisite; current deploy preflight passes.
- Earlier tag-vs-digest provenance weakness: PR #130 replaced it with immutable repository+digest proof.
- Run #79 raw-Chrome proof timeout: PR #152 removed redundant standalone Chrome authority; canonical WebDriver matrix now proves rendering.
- Run #80 BrokerTruth/StateTruth contradiction and ~12 s broker probe: **closed by PR #154 + #155 + run #82**.
- Legacy dashboard API-key/session residue in permanent watcher: **closed by PR #156**; regression contract prevents reintroduction there.
- Stale PR #129 remains non-authoritative; never wholesale merge.
- `conflict_120826_0310` remains quarantined; plaintext credential material must never be quoted or merged. Independent user-side credential rotation is a separate exposure-remediation matter if not already completed.
- Render is legacy migration debt only; Google Cloud is the runtime target.

## 14. Safety authority

- LIVE: **OFF / LOCKED**.
- Real order actions in this proof loop: **0**.
- Public dashboard: **credential-free / read-only**.
- Dashboard API key: **not required / not mounted**.
- Worker authority: separate dedicated token.
- Dhan token value: **never exposed**.
- No gate was weakened to obtain green status.
- No live/order place/modify/cancel endpoint was exercised.
