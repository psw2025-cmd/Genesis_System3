# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12 run #78 terminal checkpoint + retired-dashboard-secret remediation branch`

> Single authority for `psw2025-cmd/Genesis_System3`. Google Cloud is the only runtime/deployment authority. LIVE remains OFF/LOCKED. No live order placement/modification/cancellation/routing is permitted. Secret payloads must never be exposed. Source, CI, Ready, browser visuals, BrokerTruth, StateTruth, market-data truth and AlphaTruth remain separate evidence domains.

## 0. Current source / PR / runtime authority

- Repository: **`psw2025-cmd/Genesis_System3` only**.
- Current `main`: **`e47aa6eb2cf4a33e70bb64c481c9d3d7f445fd49`** — merge PR #145.
- PR #130 immutable image provenance: **MERGED**, head `56a37ae3841fe5342e5359c03570b9431d52166c`; Global Safety CI PASS; GCP Dhan Token Fix CI PASS; merge commit `e09824188ab7c30f08c0af48cf7e27bb0a22d798`.
- PR #129 permanent no-key cleanup: **OPEN / stale / non-mergeable**, head `04f27e100b53e464f5d6ba5b407d8faaff74b3ef`; Global Safety CI FAIL while GCP Dhan Token Fix, Stage 2 Safety and Workflow Priority Guard PASS. Never wholesale merge.
- Current focused remediation branch: `fix/run78-retired-dashboard-secret-scrub`; purpose is only to remove the inert retired `DASHBOARD_API_KEY` secret mount from future Cloud Run candidates and add fail-closed tests. It grants no new authority.
- Cloud Run Auto Deploy **#78 / `31598580211`**: **COMPLETED / SUCCESS** for exact SHA `e47aa6eb2cf4a33e70bb64c481c9d3d7f445fd49`.
- Run #78 candidate: **`genesis-system3-web-00246-lix`**, created at **0% traffic**, immutable digest + candidate HTTP proof PASS, then explicitly promoted to **100% traffic**.
- Serving revision: **`genesis-system3-web-00246-lix` @ 100%**.
- Latest-created/latest-ready for canonical run #78: **`genesis-system3-web-00246-lix`**.
- Previous serving rollback authority: `genesis-system3-web-00244-tug`.
- Deployed image digest: **`sha256:0c9908c94b427d42c784ccd86614e0f5ae4b42c727fa51276d03764a196d3c41`**.
- Runtime posture: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- Real broker order actions by this control loop: **0**.

## 1. Mandatory current position

**Deployment/UI/security/identity is fully proven on exact SHA `e47aa6...`. Market-data readiness improved from 0/4 to 3/4 required option chains. The strict remaining OptionChainTruth blocker is MIDCPNIFTY. BrokerTruth vs StateTruth remains contradictory. A retired `DASHBOARD_API_KEY` secret mount is inert but still physically present on the run #78 serving revision and is now under focused removal.**

Run #78 gate results:
- WIF authentication: PASS;
- static safety/syntax: PASS;
- Firestore runtime preflight: PASS;
- frontend production build: PASS;
- guarded 0%-traffic candidate + immutable digest proof: PASS;
- candidate HTTP proof + explicit promotion: PASS;
- public no-key dashboard proof: PASS;
- exact 22-tab visual proof: **PASS 22/22**;
- desktop/mobile exact tab screenshots: **44/44**;
- visual retries: **0**;
- browser trading mutations: **0**;
- MutationPolicy runtime proof: PASS;
- Dhan rotator configuration + explicit execution: PASS;
- rotator/Scheduler identity proof: PASS;
- public broker read proof: PASS;
- sanitized runtime evidence: PASS;
- provenance/public-dashboard safety lock step: PASS;
- workflow conclusion: **SUCCESS**;
- operational result: **DEPLOYMENT_LOCKED** because all required market-data readiness is not yet true.

**USER ACTION REQUIRED=NO.**

## 2. UI / dashboard — top visible priority

Run #78 artifact `public-paper-dashboard-proof-78` is exact-serving evidence for revision `genesis-system3-web-00246-lix` and SHA `e47aa6eb2cf4a33e70bb64c481c9d3d7f445fd49`.

- canonical tabs: `22`;
- pass: `22/22`;
- fail: `0`;
- desktop screenshots: `22/22`;
- mobile screenshots: `22/22`;
- exact tab screenshots: **`44/44`**;
- retry count: `0`;
- browser transport: `webdriver_single_session`;
- `/ui` HTTP: `200`;
- dashboard API-key prompt rendered: `false`;
- API key used for dashboard reads: `false`;
- browser mutation/order calls: `false`.

Automated render/capture is closed for this exact deployment. Product-design review is a separate evidence domain; draft PR #139 mobile compact-navigation work remains non-authoritative until refreshed, CI-proven, merged and deployed.

## 3. Mutation / execution safety

Run #78 MutationPolicy proof: **PASS**.

- manifest=`ENFORCED`;
- write routes=`33`;
- unknown=`0`;
- duplicate=`0`;
- public dashboard read-only=`true`;
- control authority configured=`false`;
- live mutation=`HARD_DENY`;
- live approval=`HARD_DENY`;
- worker authority=`DEDICATED_WORKER_TOKEN`;
- paper mutation probe => 403 `PAPER_MUTATION_AUTHORITY_REQUIRED`;
- live mutation probe => 423 `LIVE_MUTATION_LOCKED`;
- invalid worker probe => 401 `WORKER_AUTH_INVALID`;
- unknown mutation probe => 403 `MUTATION_CAPABILITY_UNKNOWN`;
- live order endpoints called=`false`;
- paper mutation handlers called=`false`;
- secret values exposed=`false`.

Never weaken these gates to clear broker or market-data blockers.

## 4. Permanent sentinels / BrokerTruth / StateTruth

Run #78 exact-serving sanitized evidence:

### `/api/health`
- HTTP `200`;
- `status=ok`;
- `mode=PAPER`;
- latency ~`316.6 ms`.

### `/api/broker/status`
- HTTP `200`;
- `connected=true`;
- token source=`GCP_SECRET_MANAGER_DYNAMIC`;
- loaded secret version=`92`;
- loaded at=`2026-08-12T12:59:32.372663+00:00`;
- expires at=`2026-08-13T12:35:30+00:00`;
- hours remaining ~`23.6`;
- broker probe latency field ~`43 ms`;
- endpoint total latency ~`12.394 s`;
- token value exposed=`false`;
- `live_trading_enabled=false`;
- `order_placement_allowed=false`;
- `error_present=true` remains visible.

### `/api/state`
- HTTP `200`;
- `mode=PAPER`;
- `broker_connected=false`;
- endpoint latency ~`5.31 s`.

Typed conclusion: **DIRECT BROKER READ CONNECTED, StateTruth SAYS DISCONNECTED — CONTRADICTION OPEN / NOT CLOSED.**

### Disconnect / recurrence / root-cause / remediation / prevention ledger

1. **BrokerTruth vs StateTruth recurrence — ACTIVE.** `/api/broker/status connected=true` while `/api/state broker_connected=false`. Root cause remains unproven. Remediation: preserve both authorities and trace broker-state propagation/version/freshness; never overwrite one with the other. Prevention closure: one canonical broker-state authority or explicit versioned reconciliation/CAS evidence.
2. **Broker error field recurrence — ACTIVE.** Direct read is connected/read-only yet `error_present=true`. Root cause is not safely classified in current sanitized evidence. Remediation: add/consume a typed non-secret error class/code and freshness timestamp; correlate without exposing broker payload/token. Prevention: fail-closed typed error taxonomy plus StateTruth reconciliation.
3. **Rotator execution recurrence — RECOVERED BUT REQUIRES HISTORY.** Recent execution `genesis-system3-dhan-token-rotate-sfkx2` failed with exit code 2; a subsequent execution `...-mvs28` succeeded and run #78 explicit execution `...-4vfv9` also succeeded. Current job/Scheduler identity proof is PASS under the dedicated rotator and Scheduler accounts. Root cause of `sfkx2` is not proven by sanitized summary. Remediation: preserve the failed execution in history and correlate safe failure class before declaring recurrence permanently closed. Prevention: exact identity + explicit execution proof every deployment, zero secret payload exposure.
4. **Legacy/default rotator identity recurrence — CONTROLLED.** Historical executions included default compute identity; current job uses `genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com`. Scheduler uses `gs3-scheduler@system3-openalgo-safe.iam.gserviceaccount.com`. Prevention: schema-aware exact-SA verification remains mandatory.
5. **Token-version skew recurrence — CURRENTLY HEALTHY.** Run #78 runtime loaded version is `92`; token is fresh with ~23.6h remaining. Secret payload was not accessed. Continue exposing only safe metadata/version/freshness.
6. **Retired dashboard-secret mount — ACTIVE CLEANUP GAP.** Run #78 revision metadata still contains secret-backed environment name `DASHBOARD_API_KEY`. Runtime dashboard authority remains absent because serving boundary scrubs retired credential input and `/api/auth/status` proves `public_readonly`; nevertheless physical mount retention violates the permanent credential-surface-removal objective. Root cause: canonical deploy removal list scrubbed `API_KEY` but not `DASHBOARD_API_KEY`. Remediation branch now adds `DASHBOARD_API_KEY` to every candidate `--remove-secrets` command and fails closed if the existing `API_KEY` scrub disappears. Prevention: regression tests for presence, idempotence, and malformed remove-secret contracts; exact next-serving revision must prove the mount absent before closure.
7. **Runtime lock wording precision defect — ACTIVE REPORTING DEFECT ONLY.** Lock output says “All four required option chains are not fresh and populated,” while run #78 evidence actually proves 3/4 ready and MIDCPNIFTY alone not ready. Do not weaken the lock; improve future blocker detail to enumerate failing symbols only.

## 5. Dhan rotator / Scheduler authority

Run #78 current control-plane proof:
- rotator Job SA: `genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com`;
- explicit execution `genesis-system3-dhan-token-rotate-4vfv9`: **SUCCESS**;
- Scheduler state: **ENABLED**;
- schedule=`30 7 * * *`;
- timezone=`Asia/Kolkata`;
- Scheduler OAuth identity=`gs3-scheduler@system3-openalgo-safe.iam.gserviceaccount.com`;
- target: canonical Cloud Run Job `:run` endpoint;
- LIVE/order flags remain OFF;
- secret payloads exposed: none.

## 6. Market-data truth — strict active blocker

Broker authentication is not market-data readiness.

Run #78 exact-serving chain evidence:

| Symbol | HTTP | Source priority | Contracts | Fresh timestamp | Stale | Truth |
|---|---:|---|---:|---|---|---|
| NIFTY | 200 | `dhan_last_verified_snapshot` | 160 | `2026-08-12T12:56:36.608230+00:00` | false | READY |
| BANKNIFTY | 200 | `dhan_last_verified_snapshot` | 160 | `2026-08-12T12:57:00.134661+00:00` | false | READY |
| FINNIFTY | 200 | `dhan_last_verified_snapshot` | 160 | `2026-08-12T12:57:36.848346+00:00` | false | READY |
| MIDCPNIFTY | 200 | `dhan_only_no_rows` | none | none | not proven | **NOT READY** |

- readiness: **3/4 required chains**;
- MIDCPNIFTY spot is present but usable contract rows/fresh timestamp are absent;
- MIDCPNIFTY request latency ~`8.364 s`;
- `/api/scanner/top_contract_gainers` still times out at ~`30.078 s`.

Current source RCA boundary:
- `DataSourceManager` maps MIDCPNIFTY to Dhan security ID `442`, segment `IDX_I`;
- it prefers Dhan `expiry_list`, then requests option chain, parses usable CE/PE rows, and only then stamps expiry;
- the emergency calendar fallback still uses an obsolete Monday assumption and requires correction, but the normal path prefers broker expiry-list data, so that fallback is **not yet proven as the run #78 MIDCPNIFTY root cause**;
- because NIFTY/BANKNIFTY/FINNIFTY are healthy in the same run, the remaining failure is narrowed to MIDCPNIFTY-specific underlying/expiry/API-response/parser/data-availability behavior rather than broad Dhan auth failure.

Typed conclusion: **OptionChainTruth = 3/4 READY; MIDCPNIFTY NOT READY; DEPLOYMENT_LOCKED remains correct.**

## 7. PR / CI lanes

- PR #130: MERGED, exact-head required CI PASS; digest resolver/provenance path proven by run #78.
- PR #129: OPEN/non-mergeable; selective semantics only, no wholesale merge.
- PR #121 observability: OPEN/non-mergeable; request IDs, redacted synthetics, uptime/SLO/runbook concepts may be selectively salvaged after P0 work.
- PR #125 OperationsTruth: OPEN/non-mergeable; typed inventory/SLO evidence may be selectively salvaged after P0 work.
- PR #139 mobile compact navigation: draft/non-authoritative.
- Current focused branch `fix/run78-retired-dashboard-secret-scrub`: removes only the obsolete dashboard secret mount and adds regression proof; no LIVE/order mutation.

## 8. Current dependency matrix

| Dependency | Current truth | Closure condition |
|---|---|---|
| Deployment source/digest/provenance | VERIFIED run #78 | preserve |
| 0%-candidate safety | VERIFIED | preserve |
| Exact-serving UI tabs | **22/22 PASS** | preserve |
| Desktop/mobile screenshots | **44/44 PASS** | product review separate |
| Public no-key dashboard | VERIFIED | remove residual retired secret mount |
| MutationPolicy | VERIFIED PASS | preserve HARD_DENY |
| Rotator/Scheduler identity | VERIFIED PASS | classify historical failed execution safely |
| `/api/health` | **200 / ok / PAPER** | preserve |
| Broker direct read | **200 / connected / read-only** | reconcile error field + StateTruth |
| StateTruth broker | **false** | reconcile with BrokerTruth |
| OptionChainTruth | **3/4 READY** | MIDCPNIFTY populated + fresh |
| ScannerTruth | NOT READY | resolve MIDCPNIFTY then retest |
| Retired dashboard secret surface | PARTIAL | next exact-serving revision has no `DASHBOARD_API_KEY` mount |
| AlphaTruth | INSUFFICIENT_EVIDENCE | reproducible larger evidence |
| Real-money readiness | **NO** | all safety/data/reconciliation gates; LIVE stays locked |

## 9. AlphaTruth

No profitability/readiness claim is authorized. Historical evidence remains insufficient and negative. Model auto-promotion, risk increase and live execution remain forbidden until reproducible quantitative evidence and every safety/data gate pass.

## 10. Exact current checkpoint

- Repository `main`: **`e47aa6eb2cf4a33e70bb64c481c9d3d7f445fd49`**.
- Cloud Run run #78: **SUCCESS**.
- Serving/latest-created/latest-ready: **`genesis-system3-web-00246-lix`**, serving **100%**.
- Deployed digest: `sha256:0c9908c94b427d42c784ccd86614e0f5ae4b42c727fa51276d03764a196d3c41`.
- UI: **22/22 tabs; 44/44 screenshots; 0 retries; 0 mutations**.
- Health: **HTTP 200 / ok / PAPER**.
- Broker direct: **HTTP 200 / connected=true / token v92 / LIVE=false / orders=false / error_present=true**.
- StateTruth: **broker_connected=false — CONTRADICTION OPEN**.
- Rotator/Scheduler: **current proof PASS**, with one recent failed execution retained in recurrence history.
- OptionChainTruth: **3/4 READY; MIDCPNIFTY NOT READY**.
- Scanner: **timeout ~30.078 s**.
- Retired `DASHBOARD_API_KEY` secret mount: **present on run #78 serving revision; focused removal patch in progress**.
- Runtime lock: **DEPLOYMENT_LOCKED**.
- Real order actions: **0**.
- LIVE: **OFF / LOCKED**.
- **USER ACTION REQUIRED=NO.**
