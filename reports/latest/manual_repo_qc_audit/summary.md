# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12 04:22 IST`

> This file is the single authority for the current Genesis System3 remediation stream. `PATCHED`/`MERGED`/green PR CI never imply `CLOSED`; exact serving-revision runtime proof is required where applicable. Historical milestones are retained below in condensed evidence form.

## 0. Scope, revision truth and safety lock

- Repository authority: **`psw2025-cmd/Genesis_System3` only**.
- Deployment target: **Google Cloud only**. Render is non-authoritative migration debt.
- Latest **application/source HEAD** before this report-only update: **`8126f85f531655f0313cc52a74491a9049410269`** (merge PR #119).
- Runtime posture: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- No live broker order was enabled, placed, modified, cancelled or routed by this remediation stream.
- PAPER dashboard viewing is intentionally **public/read-only**. It must not ask for a dashboard API key.
- Public visibility is never mutation authority. Worker ingestion retains a separate Secret-Manager-backed token and mutation capabilities remain fail-closed.

## 1. Smart-cascade position

Mandatory flow:

`1 VERIFY -> 2 SELECT -> 3 ROOT CAUSE -> 4 DESIGN -> 5 PATCH -> 6 TEST -> 7 PR -> 8 CI -> 9 FIX/RETEST -> 10 MERGE -> 11 POST-MERGE VERIFY -> 12 PREP -> 13 USER GCP ONLY IF GENUINELY REQUIRED -> 14 DEPLOY VERIFY -> 15 RUNTIME TEST -> 16 USER DHAN AUTH ONLY IF REQUIRED -> 17 FULL EVIDENCE -> 18 CLOSED`

### Current position

**STEP 13 — genuine Google Cloud IAM human boundary.**

All controllable repository work for the current deployment blocker has been taken through source patch, PR CI, merge and exact-main deployment preflight. The remaining failure is not a dashboard-key requirement and not a code/test failure: the GitHub WIF deployment identity lacks project-IAM authority needed to grant the dedicated Cloud Run web runtime its required Firestore data role.

**USER ACTION REQUIRED: YES — one narrow Google Cloud IAM binding only. No secret/token/PIN/TOTP is requested.**

## 2. Current executive verdict

| Area | Verdict | Evidence / next condition |
|---|---|---|
| PAPER dashboard view without API key | **VERIFIED / CLOSED for stated requirement** | Real `/ui` runtime proof previously passed; key prompt paths now also removed from active frontend source in PR #119 |
| Dashboard API-key workflow semantics | **PATCHED / CI VERIFIED** | PR #116 + #117 removed obsolete key-absence and self-matching false failures |
| Active dashboard credential-entry UI | **PATCHED / CI VERIFIED** | PR #119 removed LoginPage/useAuth and converted AuthUnlock to passive public-read contract error |
| Firestore runtime authority | **BLOCKED — STEP 13** | Dedicated web runtime needs `roles/datastore.user`; automation SA cannot read/set project IAM |
| Current exact-main deployment | **BLOCKED / NOT DEPLOYED** | Run #61 stops at Firestore IAM preflight before candidate deploy |
| Serving revision safety | **PROTECTED** | Failed candidates receive 0% traffic; last proven serving revision retained 100% traffic |
| MutationPolicy | **PARTIAL / CI VERIFIED, runtime proof pending** | Runtime probe is skipped until exact current main can deploy |
| SafetyTruth / ExecutionEligibility | **OPEN P0** | next after MutationPolicy runtime closure |
| PreTradeRiskService | **OPEN P0** | next dependency after SafetyTruth |
| AccountTruth | **OPEN P0-P1** | not yet authoritative for risk decisions |
| PaperLedger/Reconciliation | **PARTIAL / OPEN P0** | PR #99 fixed one dual-authority route; durable append-only lifecycle remains |
| StateTruth | **OPEN P0-P1** | Firestore is required; domain CAS/versioned authority still incomplete |
| DeploymentTruth V2 | **PARTIAL / OPEN P0** | serving-revision binding/digest/IAM identity chain still incomplete |
| WorkCoordinator/idempotency | **OPEN P0-P1** | pending |
| OptionChainTruth / StreamTruth / ScannerTruth / PredictionTruth | **OPEN P1** | pending after P0 chain |
| Institutional UI/A11Y | **OPEN P1** | one real desktop render proven; responsive/keyboard/axe/console proof pending |
| Real-money readiness | **NO** | LIVE stays OFF/LOCKED |

## 3. Dashboard no-key remediation — exact evidence

### Previously runtime-verified product behavior

PR #107 merged as `a875876ecf64a44706b3fc57fe0a3f8f00991337` and PR #108 merged as `7a127f5452d0b337db7d6af294f21d4879dd78a0`.

Exact Cloud Run Auto Deploy run `31507282801` succeeded and published:
- `public-dashboard/runtime-proof = SUCCESS`;
- `cloud-run/runtime-proof = SUCCESS`.

Real headless-Chrome `/ui` evidence proved:
- actual SYSTEM3 product UI rendered;
- no dashboard API-key prompt rendered;
- no API key used;
- PAPER visible;
- LIVE OFF visible;
- anonymous `/ui`, `/api/auth/status`, `/api/state` and `/api/health` access succeeded;
- `REQUIRE_API_KEY=false`;
- `API_KEY` not mounted;
- worker token remained separate.

### PR #116 — remove obsolete key-absence workflow failures

PR #116 head `32cfb8fdfc508cd2fb93a245cdb4f2349a196653`, merge **`b7f402ee7ce3fb0f4da682516e38c8c65a82a951`**.

Changed the GCP evidence/CI contract so the approved secure PAPER state is:
- `REQUIRE_API_KEY=false`;
- `API_KEY` unmounted;
- API key plaintext exposure = false;
- `dashboard_public_readonly=true`;
- worker secret remains required;
- LIVE flags remain hard OFF.

A key being **re-enabled, mounted or exposed** is now a violation. A key being absent is **not** a failure.

The same PR fixed secondary artifact-failure behavior so skipped upstream proof does not create misleading duplicate failures.

All exact-head PR safety/build/proof gates passed before merge.

### PR #117 — eliminate static-guard self-match

PR #117 head `b23a4f63a00cb088f9e6f78dc69aff3a906a7927`, merge **`abe1cabfcf276d78af1cd9c461f8de2562d0ee99`**.

Root cause: static WIF guards embedded the exact forbidden legacy credential marker text and then searched the workflow for that text, so the assertion matched itself.

Fix: construct legacy markers without embedding the literal forbidden tokens and scan executable/non-comment lines. Real legacy service-account-key use still fails; self-reference no longer does.

All exact-head PR gates passed.

### PR #119 — remove remaining frontend key-prompt paths

PR #119 head `b89ad1e3bd221e63b8fa8977bd5858f162fc8ac3`, merge **`8126f85f531655f0313cc52a74491a9049410269`**.

Changes:
- `AuthUnlock.tsx` is now a passive **Public read contract error** notice; it has no password field, key state, submit action or `/api/auth/session` call;
- deleted obsolete `LoginPage.tsx`;
- deleted obsolete `useAuth.ts`;
- deleted obsolete `scripts/gcp_session_runtime_proof.py` that enforced the superseded key/session design;
- added regression tests preventing those credential-entry paths from returning.

PR #119 Global Safety CI passed all blocking jobs, including frontend production build and full backend/proof-pack validation. GCP Dhan/WIF safety CI also passed.

**Conclusion:** no dashboard API key is required for PAPER dashboard viewing, and active frontend key-entry paths are removed. Do not restore them.

## 4. Genuine current deployment blocker — Firestore IAM

### Exact failed candidate forensic proof

After the false key/static gates were removed, exact source `abe1cabfcf276d78af1cd9c461f8de2562d0ee99` reached the real Cloud Run candidate deployment in run `31542005028`.

Cloud Build completed. Candidate revision:
`genesis-system3-web-00210-huf`.

The candidate bound `0.0.0.0:8080` and then failed required state startup with Firestore:
`PermissionDenied: 403 Missing or insufficient permissions`.

The state backend deliberately failed closed because `SYSTEM3_STATE_BACKEND=firestore` and `SYSTEM3_STATE_BACKEND_REQUIRED=1`. This is correct safety behavior; local-file fallback was not enabled.

The failed candidate received **0% traffic**. Previous serving revision `genesis-system3-web-00199-tq5` remained at **100% traffic**.

### PR #118 — repo-side permanent IAM prerequisite

PR #118 head `fa905fa8428b61ac8b54980e145ae09f0b62853f`, merge **`776eab796a31d081e2f8932ad2e90d4a03983731`**.

Implemented:
- `scripts/gcp_runtime_iam_preflight.py`;
- dedicated web runtime identity check;
- required predefined Firestore role `roles/datastore.user`;
- WIF/bootstrap provisioning contract for the dedicated web runtime;
- Firestore remains required/fail-closed;
- public no-key dashboard and LIVE-OFF invariants retained;
- exact contract tests added.

All four exact-head PR #118 suites passed before merge.

### Exact Step-13 proof

Post-merge run `31543355143` failed at `Ensure required Firestore IAM for web runtime` **before candidate creation**.

The workflow authenticates as:
`genesis-system3-automation@system3-openalgo-safe.iam.gserviceaccount.com`.

That identity cannot read project IAM policy (`projects.getIamPolicy` denied), therefore it cannot prove or add `roles/datastore.user` to:
`genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com`.

Current main/source `8126f85f531655f0313cc52a74491a9049410269` triggered run **`31544001655` (Cloud Run Auto Deploy #61)** and reproduced the same boundary:
- WIF authentication: PASS;
- static safety/syntax: PASS;
- worker Secret Manager prerequisite: PASS;
- Firestore IAM preflight: **FAIL**;
- candidate deploy: skipped;
- dashboard-key requirement: **not a blocker**;
- LIVE remains OFF/LOCKED.

This is the first genuine human-only Step-13 dependency.

## 5. Step-13 required Google Cloud action

Grant only the required predefined Firestore data role to the dedicated web runtime service account:

```bash
gcloud projects add-iam-policy-binding system3-openalgo-safe \
  --member="serviceAccount:genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com" \
  --role="roles/datastore.user" \
  --condition=None
```

Optional read-back proof:

```bash
gcloud projects get-iam-policy system3-openalgo-safe \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/datastore.user AND bindings.members:serviceAccount:genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com" \
  --format="table(bindings.role,bindings.members)"
```

Do **not** send any GCP credential, service-account key, broker PIN, TOTP or token into chat.

After this one binding is confirmed, the assistant-owned cascade resumes automatically:
1. rerun current exact-main deployment;
2. Firestore preflight must PASS;
3. create 0%-traffic candidate;
4. exact candidate must become Ready;
5. prove `/ui` opens without API key and capture real screenshot;
6. prove MutationPolicy runtime allow/deny matrix without any broker-order action;
7. promote only the exact proven revision to 100% traffic;
8. verify current serving SHA/revision/traffic/safety evidence;
9. fix any further failure and repeat;
10. only then advance to the next P0 dependency.

## 6. P0-2 MutationPolicy status

Merged foundations:
- PR #102 CapabilityManifest (`1d7e06a0f661a873528d96bcc685dc7b0af87f58`);
- `secure_app.py` capability-aware runtime policy;
- UNKNOWN/live mutation/live approval fail-closed;
- public reads do not create mutation authority;
- worker ingestion uses separate worker authority.

**Current status: PARTIAL / CI VERIFIED / RUNTIME PROOF BLOCKED BY STEP 13.**

The deploy workflow already contains safe mutation-policy runtime sentinels. They are currently skipped only because the exact current application cannot start with required Firestore state until the IAM binding above exists.

## 7. DeploymentTruth correction still open

A separate evidence defect remains: `scripts/gcp_runtime_evidence.py` can derive environment/SHA from service template/latest candidate metadata even while 100% traffic remains on an older serving revision. Therefore `source_matches_deployment=true` is not sufficient by itself.

Required correction before DeploymentTruth V2 can close:
- choose the actual `status.traffic` revision carrying 100% serving traffic;
- describe that exact revision;
- read image, service account, safe environment and `DEPLOY_GIT_SHA` from that revision;
- report 0%-traffic candidate separately;
- compare GitHub SHA only to the actual serving revision;
- require immutable image digest in the final chain.

**Status: OPEN / READY TO PATCH after Step-13 deployment resumes.**

## 8. Remaining P0 order

1. Public PAPER dashboard/no-key — **VERIFIED/CLOSED for viewing requirement**.
2. MutationPolicy runtime enforcement — **runtime proof pending Step 13**.
3. SafetyTruth + ExecutionEligibility.
4. PreTradeRiskService.
5. AccountTruth + AccountSnapshotCoordinator.
6. Durable PaperLedger + ReconciliationService.
7. StateTruth + domain CAS.
8. DeploymentTruth V2 / immutable digest + serving-revision authority + identity separation.
9. WorkCoordinator/idempotency.

Then P1:
OptionChainTruth -> StreamTruth -> ScannerTruth -> PredictionTruth -> institutional UI/accessibility/observability.

## 9. Parallel `conflict_120826_0310` salvage lane

Branch remains untrusted/stale intake and must never be merged wholesale.

Last verified divergence: heavily behind current main; re-check before every salvage action.

Security quarantine:
- branch contains a committed plaintext broker credential file;
- never quote the credential value;
- never merge that file;
- affected credential remains classified exposed until independent rotation is proven;
- do not force-rewrite shared history without explicit authorization.

Current salvage classifications:
- `connection_stability.py`: **ADAPT**;
- broker token-health read model/UI: **ADAPT**;
- real-data multibagger engine/UI: **ADAPT / RECOMMENDED after P0**;
- F&O eligibility / health digest: **ADAPT after truth-contract review**;
- branch token mint/persist writer: **REJECT**;
- AuthGate/LoginPage restore: **REJECT**;
- `.emergent` webhook cron as runtime authority: **REJECT**;
- stale generated reports/dist as source authority: **REJECT**;
- unrelated note/editor `design_guidelines.json`: **REJECT**.

Primary P0 remediation continues independently; salvage work must never weaken current safety/deployment authority.

## 10. Closure discipline

- Merge != closure.
- PR-head green != merged-revision runtime proof.
- 0%-traffic failed candidate != serving deployment.
- `latestReadyRevisionName`/service template != serving traffic authority.
- UNKNOWN/STALE/ERROR remain fail-closed.
- No profitability or real-money readiness claim is permitted without reproducible lifecycle/risk/model evidence.
- LIVE stays OFF/LOCKED.

**CURRENT USER ACTION REQUIRED: YES — Step 13, the single narrow Firestore IAM binding in Section 5.**
