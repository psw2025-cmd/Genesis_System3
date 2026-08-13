# Genesis System3 Manual Repository QC Master Audit

Updated: `2026-08-13 run #83 closure`.

> **Single master authority** for `psw2025-cmd/Genesis_System3`. Google Cloud / Cloud Run is the runtime authority. LIVE remains OFF/LOCKED. No live order placement, modification, cancellation or routing is permitted. A merge, green CI, Ready revision, screenshot or HTTP 200 never equals real-money readiness by itself.

## 0. Exact current authority

- Repository: **`psw2025-cmd/Genesis_System3` only**.
- Application/runtime source: **`e778db4c22044f58830bd2afdc2f4d0a4614d451`** — merge PR #159.
- Cloud Run Auto Deploy: **run #83 / `31655170470` / SUCCESS**.
- Exact serving/latest-ready/latest-created revision: **`genesis-system3-web-00260-mit`**.
- Traffic: **100%** to `genesis-system3-web-00260-mit`.
- Candidate was created at **0% traffic**, proved, then explicitly promoted.
- Candidate image immutable digest: **`sha256:8814c2684b1153dbcd93d15270d5f06c4540a97dba4fe97039be80752960d0c8`**.
- Runtime posture: **ANALYZER / PAPER**.
- `LIVE_TRADING_ENABLED=0`.
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`.
- `AUTO_EXECUTE_TRADES=0`.
- Public dashboard: **credential-free / public-readonly**.
- Secret payload exposed by proof: **false**.
- Real live-order actions in this control loop: **0**.
- Runtime evidence lock: **`ANALYZER_LOCKED`**; operational runtime blockers in run #83 evidence: **0**.
- Production-grade/live claim allowed: **false**; performance/execution-readiness gates remain separate and must be proven honestly.

## 1. Mandatory control-loop rule

`VERIFY -> SELECT -> FORENSIC RCA -> MULTIPLE SOLUTIONS -> CHOOSE LOWEST-RISK ROOT-CAUSE FIX -> PATCH -> REGRESSION/INTEGRATION/SMOKE -> PR -> EXACT CI -> MERGE -> GUARDED DEPLOY IF RUNTIME-AFFECTING -> EXACT RUNTIME/UI PROOF -> UPDATE THIS MASTER -> CLOSE`

Permanent operating rule:
- A non-user blocker is **not** a status-report deliverable.
- Create/attach a dedicated forensic closure task.
- Map affected callers, APIs, jobs, UI consumers, caches, tests and runtime paths.
- Compare multiple technically valid remediations before selecting one.
- Never weaken a gate, threshold, freshness rule, MutationPolicy or LIVE lock to obtain green status.
- Report closure only after reproducible proof; interrupt the user only for a genuine user-controlled action or hard safety boundary.

## 2. PR / CI authority

### PR #130 — immutable Cloud Run digest provenance
- State: **MERGED / CLOSED**.
- Exact head: `56a37ae3841fe5342e5359c03570b9431d52166c`.
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
- Never wholesale merge/rebase this stale lane; salvage focused current-main-safe slices only.

### PR #154 / #155 — BrokerTruth + StateTruth closure
- Both **MERGED**.
- PR #154 prevents stale local health truth from overriding same-cycle direct broker truth in Firestore runtime.
- PR #155 makes the Cloud broker probe bounded and read-only.
- Run #82 and run #83 prove `/api/broker/status connected=true` and `/api/state broker_connected=true` simultaneously.

### PR #156 — permanent watcher public-readonly cleanup
- **MERGED**, exact-head required CI **PASS**.
- Removed active legacy dashboard key/session dependency from the permanent watcher.

### PR #158 — run #82 master refresh
- **MERGED** after exact-head Global Safety PASS.

### PR #159 — deterministic closed-market scanner
- **MERGED**.
- Exact head: `b65e95ae344f8c139af040680299a0884caca09a`.
- Merge/application SHA: **`e778db4c22044f58830bd2afdc2f4d0a4614d451`**.
- Exact-head GCP Dhan Token Fix CI: **PASS**.
- Exact-head Global Safety blocking jobs: **PASS** including full proof-pack/backend pytest.
- Root-cause fix was deployed and proved by Cloud Run #83.

### Parallel stale lanes
- PR #121 Observability: **open/non-mergeable**; selective read-only correlation/synthetic/runbook concepts only.
- PR #125 OperationsTruth: **open/non-mergeable**; selective typed read-only inventory/SLO concepts only.
- Neither is a wholesale merge candidate.

## 3. Cloud Run run #83 deployment truth

Run #83 completed **SUCCESS** on `e778db4c22044f58830bd2afdc2f4d0a4614d451`.

- Previous serving revision: `genesis-system3-web-00256-por`.
- Candidate: **`genesis-system3-web-00260-mit`**.
- Initial candidate traffic: **0%**.
- Candidate Ready: **true**.
- Immutable image provenance: **PASS**.
- Candidate HTTP proof: **PASS**.
- Public no-key dashboard proof: **PASS**.
- MutationPolicy proof: **PASS**.
- Dhan rotator/Scheduler configuration: **PASS**.
- Explicit Dhan rotation execution: **PASS**.
- Runtime identity/safety proof: **PASS**.
- Public read-only broker gate: **PASS**.
- Sanitized runtime evidence: **PASS**.
- Provenance/public-dashboard safety lock: **PASS**.
- Explicit promotion: **PASS**.
- Final serving/latest-ready/latest-created authority: **`genesis-system3-web-00260-mit` / 100%**.

## 4. UI/dashboard exact proof — run #83

Artifact `public-paper-dashboard-proof-83`:

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
- `/ui`: HTTP **200**.
- Serving revision: `genesis-system3-web-00260-mit`.
- Expected/deployed SHA match: **true**.

## 5. Permanent health / broker / StateTruth sentinels — run #83

### `/api/health`
- HTTP: **200**.
- `status=ok`.
- `mode=PAPER`.
- Sanitized round-trip: approximately **313.3 ms**.

### `/api/broker/status`
- HTTP: **200**.
- `connected=true`.
- `error_present=false`.
- token source: **`GCP_SECRET_MANAGER_DYNAMIC`**.
- Secret Manager version: **111**.
- token value exposed: **false**.
- broker-reported internal latency: approximately **40 ms**.
- endpoint round-trip: approximately **488.7 ms**.
- LIVE trading enabled: **false**.
- order placement allowed: **false**.

### `/api/state`
- HTTP: **200**.
- `mode=PAPER`.
- `broker_connected=true`.
- data source: **`BROKER_CONNECTED_MARKET_CLOSED`**.
- state version in sample: **9931**.
- round-trip: approximately **314.3 ms**.

### BrokerTruth/StateTruth verdict
- **CONVERGED**: `true / true`.
- No recurrence of the run #80 contradiction in run #83.

## 6. OptionChainTruth — run #83

The same sanitized runtime evidence proves all four required index chains simultaneously available as fresh Dhan snapshots:

- **NIFTY:** HTTP 200, Dhan, **160 contracts**, stale=false, ~775.8 ms.
- **BANKNIFTY:** HTTP 200, Dhan, **160 contracts**, stale=false, ~1068.5 ms.
- **FINNIFTY:** HTTP 200, Dhan, **160 contracts**, stale=false, ~779.2 ms.
- **MIDCPNIFTY:** HTTP 200, Dhan, **160 contracts**, stale=false, ~794.7 ms.
- `all_required_chains_ready=true`.

Run #82 had FINNIFTY/MIDCPNIFTY no-row samples. Run #83 proves the no-row condition is **not currently recurring**. The exact historical cause of those two no-row samples is not asserted without proof.

A separate latent prevention finding remains: `DataSourceManager` prefers Dhan `expiry_list`, but its last-resort calendar fallback is stale and should not remain a production authority. This is prevention/hardening work, not a current run #83 chain outage.

## 7. ScannerTruth incident — CLOSED by PR #159 + run #83

### Run #82 failure
- `/api/scanner/top_contract_gainers` exceeded the external deterministic proof budget at approximately **30.06 s**.

### Proven root cause
- The route already preferred cached/shared/disk evidence.
- When no cached after-hours board existed, the market-closed path still invoked the cold scanner builder.
- Cold scanner construction fanned out index Dhan option-chain reads.
- `DataSourceManager` serializes Dhan option-chain traffic behind a process-wide lock with approximately 3.4 s minimum pacing; expiry-list + option-chain work can consume multiple paced slots.
- The internal after-hours scanner allowance could extend to roughly **180 s**, incompatible with the bounded external sentinel.

### Alternatives evaluated
- **Increase the acceptance timeout:** rejected because it hides latency rather than fixing the cause.
- **Parallelize Dhan calls aggressively:** rejected because it conflicts with Dhan pacing/rate-limit safety and can worsen empty-chain behavior.
- **Reuse existing cache/EOD truth and suppress cold after-hours network fan-out:** selected as the lowest-risk root-cause fix.

### Remediation
PR #159 makes Cloud Run after-hours fallback deterministic and network-free once market-hours detection proves the market is closed; existing cache/shared/disk evidence remains preferred. Open/local behavior is preserved, and detector failure does not falsely suppress normal scanning.

Regression tests prove:
1. closed-market Cloud path cannot call the chain/network fetch;
2. normal open/local fetch behavior remains intact;
3. market-detector failure preserves the existing scanner path.

### Run #83 closure proof
- `/api/scanner/top_contract_gainers`: **HTTP 200**.
- Valid JSON: **true**.
- Round-trip: approximately **573.3 ms**.
- Status: **`eod_snapshot`**.
- Prior ~30 s timeout: **not reproduced**.

Scanner timeout incident: **CLOSED**.

## 8. Dhan token rotator / Scheduler — run #83

- Dedicated rotation execution `genesis-system3-dhan-token-rotate-ptg6s`: **SUCCESS**.
- Serving runtime dynamic token secret version: **111**.
- Token value exposed: **false**.
- Scheduler: **ENABLED**.
- Schedule: **`30 7 * * *`**.
- Timezone: **Asia/Kolkata**.
- Web runtime, dedicated rotator and Scheduler identities remain separated.
- No user PIN/TOTP/OAuth action required in this cycle.

## 9. MutationPolicy / capability safety — run #83

Artifact `mutation-policy-runtime-proof-83`:

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

## 10. Runtime evidence verdict — run #83

- Repository source matches deployment: **true**.
- `broker_read_only_ready=true`.
- `all_required_chains_ready=true`.
- Runtime lock: **`ANALYZER_LOCKED`**.
- Operational blockers in this runtime evidence: **[]**.
- Production-grade/live claim allowed: **false**.

Interpretation: the Cloud Run/UI/broker/four-chain/scanner runtime path is currently green for analyzer/PAPER operation. This is **not** proof of profitable or real-money trading readiness.

## 11. Remaining readiness work

The prior repository auto-gate report predates run #83 and must not be treated as current proof where run #83 has superseding evidence. Next control-loop priorities are:

1. **Regenerate SafetyTruth + ExecutionEligibility** from current-main/current-runtime evidence.
2. Re-evaluate option-strike/F&O eligibility and feed/tick-health gates against the now-green four-chain runtime rather than repeating stale results.
3. Continue model-performance closure: positive net expectancy after costs and sustained multi-day predictive accuracy must pass from actual evidence; thresholds may not be weakened.
4. Selectively salvage only current-main-safe observability/OperationsTruth ideas from PR #121/#125.
5. Remove the latent calendar-expiry guess as an authority and prefer bounded cached Dhan expiry metadata/fail-closed behavior.

Trade-ready/live-ready remains **false** until all independent execution/performance/safety gates are reproducibly green.

## 12. Incident / prevention ledger

- Competing Dhan token writers: canonical authority is dynamic GCP Secret Manager + isolated rotator/Scheduler.
- Firestore runtime 403: dedicated web-runtime IAM prerequisite now passes.
- Tag-vs-digest provenance weakness: **closed by PR #130**.
- Raw-Chrome UI proof timeout: **closed by PR #152**; canonical WebDriver matrix is visual authority.
- Run #80 BrokerTruth/StateTruth contradiction + slow broker probe: **closed by PR #154/#155**, reconfirmed run #83.
- Legacy dashboard key/session residue in permanent watcher: **closed by PR #156**.
- Run #82 scanner ~30 s timeout: **closed by PR #159 + run #83**, now ~573 ms after-hours.
- Run #82 FINNIFTY/MIDCPNIFTY no-row sample: **not recurring in run #83**; both now fresh Dhan 160-contract snapshots. Historical cause not invented.
- Latent stale calendar expiry fallback: **prevention task required**; it must never override authoritative Dhan expiry metadata silently.
- PR #129 remains stale/non-authoritative; never wholesale merge.
- `conflict_120826_0310` remains quarantined; any credential material there must never be quoted or merged.

## 13. USER ACTION authority

Current control-loop engineering/runtime work requires **no user action**. User action should be requested only for a genuinely user-controlled permission, consent or credential operation that cannot be safely completed through existing automation.