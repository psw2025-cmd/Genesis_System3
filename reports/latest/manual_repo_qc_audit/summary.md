# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12 run #75 exact-runtime checkpoint`

> Single authority for `psw2025-cmd/Genesis_System3`. Google Cloud is the only runtime/deployment authority. LIVE remains OFF/LOCKED. No live order placement/modification/cancellation/routing is permitted. Secret payloads must never be exposed. Source, CI, Ready, browser visuals, broker reads, StateTruth, market-data truth and quantitative performance remain separate evidence domains.

## 0. Current source / runtime authority

- Repository: **`psw2025-cmd/Genesis_System3` only**.
- Application/runtime source proven by canonical deployment: **`575d75b47a51173bcc5e23d0b10e3aa7f52a7b84`** — merge PR #141.
- PR #130 immutable Cloud Run image provenance: **MERGED**, head `56a37ae3841fe5342e5359c03570b9431d52166c`, required PR CI green; merge commit `e09824188ab7c30f08c0af48cf7e27bb0a22d798`.
- PR #129 old no-key/auth cleanup: **OPEN, stale/diverged, non-mergeable**; Global Safety CI fails on head `04f27e100b53e464f5d6ba5b407d8faaff74b3ef`. Do not wholesale merge.
- Cloud Run Auto Deploy **run #75 / `31584906616`**: **COMPLETED / SUCCESS**.
- Run #75 created candidate **`genesis-system3-web-00242-bup` at 0% traffic**, proved immutable image digest + HTTP readiness, then explicitly promoted it to **100% traffic**.
- Run #75 final serving revision: **`genesis-system3-web-00242-bup` @ 100%**.
- Run #75 latest-ready revision: **`genesis-system3-web-00242-bup`**. The newly-created candidate in this run was the same revision; no later revision was created by this canonical run.
- Previous serving revision retained as rollback authority during promotion: `genesis-system3-web-00240-roh`.
- Deployed image digest: **`sha256:d38913a023f1373501470d5155beee7e47b75aa0024eb1a9b8fd4d4e9bab4928`**.
- Runtime posture: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- Real broker orders attempted by this remediation/proof stream: **0**.
- Dashboard contract: **public/read-only**, no dashboard API-key/login/session authority.

## 1. Current mandatory position

**Deployment/UI/security/identity transport is now proven end-to-end on exact main SHA. The strict active P0 operational blocker is OptionChainTruth; BrokerTruth vs StateTruth remains contradictory and must stay visible.**

Run #75 exact gate results:
- keyless WIF: PASS;
- Firestore runtime preflight: PASS;
- frontend production build: PASS;
- guarded 0%-traffic candidate deploy + immutable digest proof: PASS;
- candidate HTTP proof + explicit 100% promotion: PASS;
- public no-key dashboard proof: PASS;
- 22-tab WebDriver proof: **PASS 22/22**;
- desktop/mobile screenshots: **44/44**;
- screenshot retries: **0**;
- browser trading mutations: **0**;
- MutationPolicy runtime proof: PASS;
- dedicated Dhan rotator deploy/configuration: PASS;
- explicit rotator execution `genesis-system3-dhan-token-rotate-zxbmd`: PASS;
- service/rotator/Scheduler safety verifier: **PASS**;
- canonical public-readonly auth-status proof: PASS;
- broker no-key read proof: PASS;
- sanitized runtime evidence + provenance safety lock: PASS;
- workflow conclusion: **SUCCESS**;
- operational lock remains because all four required option chains are not proven fresh and populated.

**USER ACTION REQUIRED=NO.**

## 2. UI / dashboard — top visible priority

Run #75 artifact `public-paper-dashboard-proof-75` is exact-serving proof for SHA `575d75b47a51173bcc5e23d0b10e3aa7f52a7b84` and revision `genesis-system3-web-00242-bup`.

- canonical tabs: `22`;
- pass_count: `22`;
- fail_count: `0`;
- desktop screenshots: `22/22`;
- mobile screenshots: `22/22`;
- exact tab screenshots: **`44/44`**;
- browser transport: `webdriver_single_session`;
- retry_count: `0`;
- desktop viewport: `1600x1000`;
- mobile viewport: `430x932`;
- dashboard API-key/login prompt rendered: `false`;
- API key used: `false`;
- mutation/order calls: `false`.

Automated render/capture is closed for this exact deployment. Product-design acceptance remains separate: artifact entries retain `PENDING_USER_REVIEW`. Draft PR #139 mobile compact-rail work remains isolated and must not be treated as merged/runtime truth.

## 3. Mutation / execution safety

Run #75 MutationPolicy runtime proof: **PASS**.

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

Never weaken these gates to clear data/operational blockers.

## 4. Permanent sentinels / BrokerTruth / StateTruth

Run #75 sanitized exact-serving evidence:

### `/api/health`
- HTTP `200`;
- `status=ok`;
- `mode=PAPER`;
- endpoint latency ~`340 ms`.

### `/api/broker/status`
- HTTP `200`;
- `connected=true`;
- token source=`GCP_SECRET_MANAGER_DYNAMIC`;
- loaded token secret version=`86`;
- latest enabled metadata version=`86`;
- token value exposed=`false`;
- `live_trading_enabled=false`;
- `order_placement_allowed=false`;
- broker probe latency field ~`208 ms`;
- total endpoint latency ~`12.38 s`;
- `error_present=true` remains visible and is not collapsed into a green badge.

### `/api/state`
- HTTP `200`;
- `mode=PAPER`;
- `broker_connected=false`.

Typed conclusion: **DIRECT BROKER READ CONNECTED, BUT StateTruth CONTRADICTS IT — NOT CLOSED.**

### Disconnect / recurrence / root cause / remediation / prevention ledger

1. **StateTruth recurrence — still active in run #75.** `/api/broker/status connected=true` while `/api/state broker_connected=false`. Root cause remains not yet proven. Remediation: preserve both typed authorities and trace state propagation/freshness instead of overwriting either. Prevention closure: one canonical broker-state authority or explicit versioned/freshness reconciliation with CAS evidence.
2. **Token-version recurrence — improved/closed for this snapshot.** Run #74 had runtime token version 82 while latest metadata was 83. Run #75 shows runtime loaded version 86 and latest enabled metadata version 86. Root cause of earlier skew remains compatible with bounded cache/rotation timing. Prevention: expose safe loaded/latest version freshness only; canonical provider remains the only token source.
3. **Legacy rotator identity recurrence — repaired and proven.** Older executions included default compute-SA/failed secret state. Run #75 deployed and executed `genesis-system3-dhan-token-rotate-zxbmd` successfully under `genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com`. Remediation: dedicated rotator identity + Scheduler identity; web runtime remains invoke-only. Prevention: schema-aware exact-SA verifier now passes and must remain fail-closed.
4. **Run #74 verifier false failure — closed.** Root cause was stale Cloud Run Job JSON-path parsing that returned `ROTATOR_IDENTITY_MISMATCH None`. PR #141 introduced schema-aware recognized v1/v2 parsing with regression tests. Run #75 step 19 passes exact rotator/Scheduler identity proof.
5. **Legacy auth-status verifier mismatch — closed.** Canonical mode is `public_readonly`, not `auth_disabled`. Run #75 requires simultaneously `required=false`, `configured=false`, `authenticated=false`, `mode=public_readonly`, `credential_surface=REMOVED`, `session=null`; step 20 passes. This is stricter, not weaker.
6. **Broker endpoint error field — still active.** Run #75 direct broker proof is connected and read-only but sanitized summary still reports `error_present=true`. Root cause is not proven by the summary artifact; do not suppress it. Remediation: correlate the safe error classification with broker status/state propagation without exposing payloads. Prevention closure: typed non-secret error code/class + freshness timestamp and reconciled StateTruth.

## 5. Dhan rotator / Scheduler authority

Run #75 control-plane proof:
- rotator Job SA: `genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com`;
- explicit execution `genesis-system3-dhan-token-rotate-zxbmd`: **SUCCESS**, ~14.82 s execution;
- Scheduler: **ENABLED**;
- schedule=`30 7 * * *`;
- time zone=`Asia/Kolkata`;
- Scheduler OAuth identity=`gs3-scheduler@system3-openalgo-safe.iam.gserviceaccount.com`;
- target: canonical Cloud Run Job `:run` endpoint only;
- LIVE/order flags remain OFF in Job configuration;
- secret payloads were not exposed.

## 6. Market-data truth — active strict blocker

Broker authentication is not market-data readiness.

Run #75 evidence for NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY:
- HTTP `200` for all four;
- source=`dhan`;
- source priority=`dhan_only_no_rows`;
- spot available=`true`;
- `contract_count=null`;
- `fetched_at_utc=null`;
- each chain request ~`8.4 s`;
- `all_required_chains_ready=false`.

`/api/scanner/top_contract_gainers` timed out again at ~`30.06 s`.

Typed conclusion: **OptionChainTruth NOT READY**. `DEPLOYMENT_LOCKED` remains correct because all four required chains are not proven fresh and populated. HTTP 200 and spot availability are insufficient.

## 7. PR / CI lanes

- PR #130: **MERGED**; head Global Safety CI PASS and GCP Dhan Token Fix CI PASS; immutable digest resolver/deployer lineage is runtime-proven by runs #74/#75.
- PR #129: **OPEN / non-mergeable**; head Global Safety CI FAIL, other historical GCP checks pass. Selective current-main reimplementation only; no wholesale merge.
- PR #121 observability: **OPEN / non-mergeable**; selectively salvage request IDs, redacted synthetics, uptime/SLO/runbooks only after current strict blocker work; no wholesale merge.
- PR #125 OperationsTruth: **OPEN / non-mergeable**; selectively salvage typed inventory/SLO evidence only; no wholesale merge.
- PR #139 mobile compact rail: draft/currently non-authoritative; requires refresh + exact deployed visual proof before any merge decision.
- PR #141: **MERGED**; its repaired runtime identity/public-readonly verifier is proven by run #75 SUCCESS.

Current-main code-search still finds `REQUIRE_API_KEY` references in `dashboard/backend/security_policy.py`; references must be interpreted by semantics, not string presence. Runtime proof establishes dashboard credential authority is absent (`public_readonly`, API key unmounted). Any active legacy session/login authority reintroduction remains forbidden.

## 8. P0 dependency truth

| Dependency | Current truth | Closure condition |
|---|---|---|
| Firestore runtime | VERIFIED | preserve |
| Deployment source/digest/provenance | VERIFIED run #75 | preserve |
| Exact-serving 22-tab browser proof | **PASS 22/22** | preserve |
| Desktop/mobile screenshots | **PASS 44/44** | product review separate |
| Public no-key dashboard | VERIFIED | preserve strict canonical auth status |
| MutationPolicy | **VERIFIED runtime PASS** | preserve |
| Rotator/Scheduler identity | **VERIFIED runtime PASS** | preserve |
| `/api/health` | **200 / ok / PAPER** | preserve |
| Broker direct read | **200 / connected / read-only** | reconcile error field + StateTruth |
| StateTruth/domain CAS | PARTIAL | converge broker state + CAS/freshness proof |
| OptionChainTruth | **NOT READY** | four populated/fresh chains |
| ScannerTruth | **NOT READY** | after OptionChainTruth/root cause |
| AlphaTruth | INSUFFICIENT_EVIDENCE | reproducible larger evidence |
| Real-money readiness | **NO** | all safety/data/reconciliation gates; LIVE stays locked |

## 9. AlphaTruth

Quantitative performance targets remain goals, not claims. Current authoritative evidence remains insufficient: 5 days / 8 trades / 50% win rate / net P&L `-102636.35`. **AlphaTruth=`INSUFFICIENT_EVIDENCE`**. No model auto-promotion or live risk increase is authorized.

## 10. Current checkpoint

- Application/runtime source SHA: **`575d75b47a51173bcc5e23d0b10e3aa7f52a7b84`**.
- Cloud Run run #75: **SUCCESS**.
- Serving/latest-created-in-run/latest-ready: **`genesis-system3-web-00242-bup`**, serving **100%**.
- UI exact-serving proof: **22/22 tabs; 44/44 screenshots; zero retries; zero mutations**.
- Health: **HTTP 200 / ok / PAPER**.
- Broker: **HTTP 200 / connected=true / token v86 / latest secret v86 / LIVE=false / orders=false / error_present=true**.
- StateTruth: `/api/state broker_connected=false` => **broker state contradictory / not closed**.
- Rotator/Scheduler identity: **PASS**.
- Required option chains: **NOT READY** (`contract_count` and `fetched_at_utc` absent on all four).
- Scanner: timeout ~30 s => **NOT READY**.
- Runtime lock: **DEPLOYMENT_LOCKED** solely by current lock evaluator because all four required option chains are not fresh/populated.
- LIVE/order authority: **OFF / LOCKED / FALSE**.
- Real order actions: **0**.
- **USER ACTION REQUIRED=NO.**
