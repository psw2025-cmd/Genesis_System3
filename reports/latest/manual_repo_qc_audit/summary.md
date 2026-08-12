# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12 current control loop`

> Single authority for `psw2025-cmd/Genesis_System3`. Google Cloud is the only runtime/deployment authority. LIVE remains OFF/LOCKED. No live order placement/modification/cancellation/routing is permitted. Secret payloads must never be exposed. Source, CI, Ready, browser visuals, broker reads, state, and quantitative performance remain separate evidence domains.

## 0. Current source / runtime authority

- Repository: **`psw2025-cmd/Genesis_System3` only**.
- Current repository `main`: **`12f72b0460a003093362b90b9a6131e19dc603ff`** — report-only update on top of the application source below.
- Current deployed/application source: **`eadd4be87c807ae67ba0d936d8ac50511226138d`** — merge PR #140.
- PR #130 immutable Cloud Run image provenance: **MERGED**, exact head CI green.
- PR #129 old no-key/auth cleanup: **OPEN, stale/diverged, non-mergeable**; do not wholesale merge.
- Cloud Run Auto Deploy run **`31582769776` / #74**: **COMPLETED / FAILURE**, but deployment, UI, MutationPolicy, rotator configuration and explicit rotator execution all passed before a verifier-schema failure at step 19.
- Exact serving/latest-ready revision proven by run #74: **`genesis-system3-web-00240-roh`**, 100% traffic.
- Candidate `00240-roh` was first created at **0% traffic**, immutable digest proven, HTTP-proved, then explicitly promoted to 100%.
- Deployed image digest: **`sha256:7051be6c0b40f48d852bbb76fc5a8569fabb7c09c3e017dc38d31e4f5f8d8640`**.
- Runtime posture: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- Real broker orders attempted by this remediation/proof stream: **0**.
- Dashboard contract: **public/read-only**, no dashboard API-key/login/session authority.

## 1. Current mandatory position

**UI browser-proof transport is now closed; stay on runtime identity/broker/StateTruth closure before advancing the next strict P0 dependency.**

Run #74 exact gate results:
- keyless WIF: PASS;
- Firestore runtime preflight: PASS;
- frontend build: PASS;
- guarded 0%-traffic candidate deploy + immutable digest proof: PASS;
- candidate HTTP proof + explicit 100% promotion: PASS;
- public no-key dashboard proof: **PASS**;
- 22-tab WebDriver proof: **PASS 22/22**;
- desktop/mobile screenshots: **44/44**;
- screenshot retries: **0**;
- browser trading mutations: **0**;
- MutationPolicy runtime proof: **PASS**;
- dedicated Dhan rotator deploy/configuration: PASS;
- Cloud Scheduler configuration: PASS;
- explicit rotator execution `genesis-system3-dhan-token-rotate-xchgb`: **PASS**;
- service/rotator/Scheduler safety verifier: **FAIL** only because the verifier read the wrong Cloud Run Job JSON field and produced `ROTATOR_IDENTITY_MISMATCH None`;
- sanitized runtime evidence/provenance lock: PASS for safety/provenance, operational lock remains due option-chain readiness.

**USER ACTION REQUIRED=NO.** Current blocker is repository-controlled and is being repaired in PR #141.

## 2. Run #74 UI / dashboard proof

Canonical tabs: **22**. Required automated artifact: **22 desktop + 22 mobile = 44 exact-serving screenshots**.

Run #74 artifact `public-paper-dashboard-proof-74`:
- state=`PASS`;
- tab_count=`22`;
- pass_count=`22`;
- fail_count=`0`;
- browser transport=`webdriver_single_session`;
- initial_fail_count=`0`;
- retry_count=`0`;
- desktop viewport=`1600x1000`;
- mobile viewport=`430x932`;
- API-key/login prompt rendered=`false`;
- mutation/order calls=`false`;
- exact serving revision=`genesis-system3-web-00240-roh`;
- exact deployed source=`eadd4be87c807ae67ba0d936d8ac50511226138d`.

This closes the **automated render/capture gate**, not final product-design acceptance. Every tab artifact still carries `PENDING_USER_REVIEW`.

Known visible product-quality items remain:
- mobile 430px layout still needs product review; draft PR #139 proposes a compact 58px navigation rail and remains intentionally unmerged;
- several desktop workspaces remain information-dense and need hierarchy review;
- Signals/Trade source wording must never regress to credential-request language under the permanent public-readonly architecture;
- read-heavy tabs remain sensitive to slow backend chain/scanner reads even though the WebDriver proof transport now completes deterministically.

Prevention now proven for screenshot transport: one WebDriver session, one navigation per tab, same-page mobile resize, fresh-browser retry only on actual failure, and fixed parent proof budget.

## 3. Mutation / execution safety

Run #74 MutationPolicy runtime proof: **PASS**.

- manifest state=`ENFORCED`;
- write routes=`33`;
- unknown routes=`0`;
- duplicate routes=`0`;
- public dashboard read-only=`true`;
- control authority configured=`false`;
- live mutation=`HARD_DENY`;
- live approval=`HARD_DENY`;
- worker authority=`DEDICATED_WORKER_TOKEN`;
- paper probe => 403 `PAPER_MUTATION_AUTHORITY_REQUIRED`;
- live probe => 423 `LIVE_MUTATION_LOCKED`;
- invalid worker probe => 401 `WORKER_AUTH_INVALID`;
- unknown mutation probe => 403 `MUTATION_CAPABILITY_UNKNOWN`;
- live order endpoints called=`false`;
- paper mutation handlers called=`false`;
- secret values exposed=`false`.

Do not weaken these gates to clear operational blockers.

## 4. Broker / token / StateTruth — mandatory read-only truth

Fresh run #74 sanitized evidence:
- `/api/health`: **HTTP 200**, `status=ok`, `mode=PAPER`;
- `/api/broker/status`: **HTTP 200**, `connected=true`;
- token source=`GCP_SECRET_MANAGER_DYNAMIC`;
- broker-loaded Secret Manager token version=`82`;
- latest enabled access-token secret version observed by metadata=`83`;
- token value exposed=`false`;
- LIVE trading enabled=`false`;
- order placement allowed=`false`;
- broker probe latency field ~`935 ms`;
- total broker-status endpoint latency ~`12.35 s`;
- broker summary `error_present=true`;
- `/api/state`: **HTTP 200**, `broker_connected=false`.

Typed broker conclusion: **DIRECT BROKER READ CONNECTED, BUT StateTruth CONTRADICTS IT — NOT CLOSED.** Do not collapse this into a single green broker badge.

### Disconnect / recurrence / root cause / remediation / prevention ledger

1. **StateTruth recurrence:** direct `/api/broker/status connected=true` while `/api/state broker_connected=false` persisted from run #73 into run #74. Root cause is not yet proven. Remediation is to keep both authorities visible and trace state propagation rather than overwrite one with the other. Prevention condition: one typed broker authority or explicit freshness/versioned reconciliation with CAS evidence.
2. **Token-version recurrence:** broker runtime loaded version 82 while Secret Manager metadata already observed latest enabled version 83. This is compatible with bounded token-cache timing but must remain explicit. Remediation: dynamic source + bounded cache + version metadata. Prevention condition: expose safe loaded/latest version freshness without token payload and re-load only through canonical provider.
3. **Legacy invocation/identity recurrence:** runtime evidence contains older failed web-runtime/self-heal executions, including a run #74-era web invocation that failed, while the explicit automation execution `xchgb` succeeded under `genesis-system3-dhan-rotator@...`. Remediation: dedicated rotator identity is deployed and Scheduler uses `gs3-scheduler@...`; web runtime has invoke-only authority. Prevention condition: prove current configured Job identity from control-plane JSON, then remove any obsolete web-runtime secret mint/read privileges once no longer required.
4. **Run #74 verifier false failure:** step 19 returned `ROTATOR_IDENTITY_MISMATCH None` although the explicit rotator execution succeeded with `serviceAccountName=genesis-system3-dhan-rotator@...`. Root cause is a stale JSON path in the workflow verifier: it expected `spec.template.template.serviceAccount*`, while current `gcloud run jobs describe --format=json` uses the nested v1 Job shape. Remediation PR #141 introduces a fail-closed schema-aware parser plus regression tests. Prevention: accept only recognized v1/v2 identity fields, fail on missing/ambiguous/wrong identity, and keep the dedicated expected SA exact-match gate.
5. **Next latent auth-proof defect found before rerun:** workflow step 20 still expected legacy `.mode == "auth_disabled"` although serving canonical status is `public_readonly`. PR #141 changes the assertion to require **all** canonical fields simultaneously: `required=false`, `configured=false`, `authenticated=false`, `mode=public_readonly`, `credential_surface=REMOVED`, `session=null`. This tightens rather than weakens the no-credential proof.

## 5. Dhan rotator / Scheduler authority

Run #74 control-plane truth:
- Cloud Run Job deployment: PASS;
- intended Job SA: `genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com`;
- explicit execution `genesis-system3-dhan-token-rotate-xchgb`: **successful**;
- successful execution spec records dedicated rotator `serviceAccountName`;
- Scheduler state=`ENABLED`;
- schedule=`30 7 * * *`;
- time zone=`Asia/Kolkata`;
- Scheduler OAuth identity=`gs3-scheduler@system3-openalgo-safe.iam.gserviceaccount.com`;
- Scheduler target is only the canonical Cloud Run Job `:run` endpoint;
- LIVE/order flags remain off in the Job configuration.

PR #141 is the current repair lane for the **proof parser**, not for widening runtime authority.

## 6. Market-data truth

Broker authentication is not market-data readiness.

Fresh run #74 evidence for NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY:
- HTTP 200;
- source=`dhan`;
- source priority=`dhan_only_no_rows`;
- spot can be available;
- `contract_count` authority is missing/null;
- `fetched_at_utc` authority is missing/null;
- each request is roughly 25 seconds;
- `all_required_chains_ready=false`.

`/api/scanner/top_contract_gainers` also timed out at ~30 seconds in run #74.

Typed conclusion: **OptionChainTruth NOT READY**. Current runtime lock remains `DEPLOYMENT_LOCKED` only because **all four required option chains are not fresh and populated**. HTTP 200 and spot availability are insufficient.

## 7. Current PR / CI lanes

- PR #130: merged; immutable digest resolver/deployer lineage complete and CI-green.
- PR #129: open, stale/diverged, non-mergeable; Global Safety historically failing. Selective current-main reimplementation only.
- PR #121 observability: stale/non-mergeable; selectively salvage request IDs, redacted synthetics, uptime/SLO/runbook pieces only after current runtime gate.
- PR #125 OperationsTruth: stale/non-mergeable; selectively salvage typed OperationsTruth/SLO evidence only after current runtime gate.
- PR #139 mobile UI compact rail: draft, stale-base relative to current main; refresh/review after runtime-proof lane is green, then deploy screenshots before any merge.
- **PR #141**: current focused runtime-proof repair. Files: canonical workflow + schema-aware identity verifier + tests + this master report. Merge prohibited until all exact required CI gates are green.

## 8. P0 dependency truth

| Dependency | Current truth | Closure condition |
|---|---|---|
| Firestore runtime | VERIFIED | preserve |
| Deployment source/digest/provenance | VERIFIED run #74 | preserve |
| 22-tab exact-serving browser proof | **PASS 22/22** | preserve |
| Desktop/mobile screenshot artifact | **PASS 44/44** | product review still pending |
| Public no-key dashboard | VERIFIED exact-serving | preserve strict canonical auth status |
| MutationPolicy | **VERIFIED runtime PASS** | preserve |
| Rotator/Scheduler identity | runtime evidence positive; verifier false-failed | PR #141 CI + rerun step 19 |
| BrokerTruth | direct connected, StateTruth contradiction | reconcile typed authorities |
| StateTruth/domain CAS | PARTIAL | converge broker state + CAS proof |
| OptionChainTruth | **NOT READY** | four populated/fresh chains |
| ScannerTruth | NOT READY | after OptionChainTruth |
| AlphaTruth | INSUFFICIENT_EVIDENCE | reproducible larger evidence |
| Real-money readiness | **NO** | all safety/data/reconciliation gates; LIVE stays locked |

## 9. AlphaTruth

Quantitative performance targets remain goals, not claims.

Current authoritative evidence remains insufficient: 5 days / 8 trades / 50% win rate / net P&L `-102636.35`. **AlphaTruth=`INSUFFICIENT_EVIDENCE`**. Historical larger frozen holdout also failed performance. No model auto-promotion or live risk increase is authorized.

## 10. Current checkpoint

- Repository main: **`12f72b0460a003093362b90b9a6131e19dc603ff`**.
- Deployed/application source: **`eadd4be87c807ae67ba0d936d8ac50511226138d`**.
- Serving/latest-ready: **`genesis-system3-web-00240-roh` @ 100%**.
- Run #74 overall: **FAIL only at stale rotator-identity verifier** after UI/MutationPolicy/rotator execution success.
- UI automated proof: **22/22 tabs; 44/44 screenshots; zero retries; zero mutations**.
- Health: **200 / ok / PAPER**.
- Broker: **200 / direct connected / token v82 / latest secret v83 / LIVE false / orders false**, but `/api/state broker_connected=false` => **CONTRADICTORY / NOT CLOSED**.
- Scheduler: **ENABLED**, `30 7 * * *`, `Asia/Kolkata`, dedicated scheduler identity.
- Required option chains: **NOT READY**.
- Runtime lock: **DEPLOYMENT_LOCKED** because all four required option chains are not fresh/populated.
- PR #141: active remediation; merge only after exact CI green, then rerun canonical deploy/runtime proof.
- LIVE/order authority: **OFF / LOCKED / FALSE**.
- **USER ACTION REQUIRED=NO.**
