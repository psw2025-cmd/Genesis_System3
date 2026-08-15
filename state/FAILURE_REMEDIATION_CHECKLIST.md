# Genesis System3 — Recursive Failure Remediation Checklist

Authority: GitHub source + exact workflow artifacts + GCP runtime + production UI evidence. Historical prose never overrides newer machine evidence.

## Universal 10-step loop — apply to EVERY failure

1. **Freeze evidence**
   - [ ] Record UTC/IST timestamp, branch, exact SHA, workflow/run/job/step.
   - [ ] Save logs/artifacts before retry.
   - [ ] Record safety flags and confirm LIVE remains locked.
2. **Classify**
   - [ ] NEW vs RECURRENCE.
   - [ ] Product/runtime vs CI/proof-runner vs dependency/security vs documentation.
   - [ ] Assign one atomic work ID.
3. **Reproduce**
   - [ ] Reproduce on exact SHA where possible.
   - [ ] Prove the smallest failing input/path.
   - [ ] Reject stale evidence.
4. **Map blast radius**
   - [ ] Source files/functions.
   - [ ] APIs/jobs/workflows.
   - [ ] UI tabs and user-visible effects.
   - [ ] Security/safety implications.
5. **Root-cause research**
   - [ ] Inspect repository implementation.
   - [ ] Inspect exact machine artifact/log.
   - [ ] Check authoritative upstream advisory/docs for dependency/tool failures.
   - [ ] Compare at least two remediation paths when material.
6. **Pre-fix tests**
   - [ ] Add/reproduce a failing regression.
   - [ ] Add negative/adversarial case.
   - [ ] Confirm detector itself is not false-green.
7. **Implement smallest durable fix**
   - [ ] No global security suppression.
   - [ ] No broad retry-until-green.
   - [ ] No live-order enablement.
   - [ ] Preserve provenance and observability.
8. **Post-fix verification**
   - [ ] Focused unit/regression tests.
   - [ ] Adjacent integration tests.
   - [ ] Mandatory CI/security gates.
   - [ ] Exact-head artifact review.
9. **Production proof when applicable**
   - [ ] Merge only after gates qualify.
   - [ ] Exact main SHA deployed and serving.
   - [ ] API/broker/scheduler proof.
   - [ ] Semantic production UI proof, not screenshot-only.
10. **Recurrence and checkpoint**
   - [ ] Observe required recurrence-free window.
   - [ ] Update state/change evidence.
   - [ ] If the same class fails again, mark RECURRENCE and create a deeper 10-step child loop rather than repeating the same patch.

## Child-loop rule

If any item above fails, create a child work item with the same ten steps. Maximum depth is not limited by convenience; stop only when the causal chain is proven and the mandatory gate passes. A retry is permitted only after the failed step has a stated hypothesis and expected result.

## SEC-001 — Security Audit Evidence

Baseline artifact: `security-audit-45`, workflow run `31867610078`, original PR head `474d83d60f04104503caa91493a1bb0ac21736b0`.

### Evidence
- [x] Root pip audit: zero known vulnerabilities.
- [x] Dashboard backend pip audit: zero known vulnerabilities.
- [x] npm audit: 4 vulnerabilities = 3 HIGH + 1 MODERATE.
- [x] Bandit: 887 findings = 13 HIGH + 51 MEDIUM + 823 LOW.
- [x] 12/13 Bandit HIGH findings are the exact static terminal-clear form `os.system("cls" if os.name == "nt" else "clear")`.
- [x] 1/13 is fixed Windows argv `taskkill /F /IM python.exe /T` with `shell=True`.
- [x] LIVE flags remained locked and no order action/secret payload was recorded.

### Bandit remediation micro-checklist
- [x] Do not globally skip B602/B605.
- [x] Preserve raw Bandit HIGH counts in evidence.
- [x] Declassify only exact reviewed static code shapes.
- [x] Any changed/dynamic shell expression remains hard FAIL.
- [x] Add regression for exact static terminal clear.
- [x] Add regression for exact static Windows taskkill.
- [x] Add adversarial regression for dynamic `os.system(user_input)`.
- [x] Add adversarial regression for dynamic `subprocess.run(command, shell=True)`.
- [x] Rerun exact-head Security Audit Evidence as run `31868618851` / #48.
- [x] Confirm Bandit moved from hard FAIL to WARN while retaining all 13 raw HIGH findings.
- [x] Confirm `unreviewed_high_count=0`; reviewed findings remain explicitly enumerated.

### SEC-001.1 — npm dependency child loop

Rerun #48 still failed, but the hard-failure set narrowed from `[npm_audit, bandit]` to exactly `[npm_audit]`. This is a new child loop, not a blind retry.

1. **Freeze evidence**
   - [x] Exact head: `2c4ffb892613f886575fe9e3764c5d4b7aea8796`.
   - [x] Security run: `31868618851` / #48.
   - [x] Artifact: `security-audit-48`, ID `9242754752`, SHA-256 `5f14f4873057f7b164f1f4e47ed4c685a0a51dff465f71520e4999d5de411f74`.
2. **Classify**
   - [x] Dependency/security hard failure.
   - [x] Not a CI infrastructure failure.
3. **Reproduce**
   - [x] `npm audit` again reports 4 vulnerabilities: 3 HIGH + 1 MODERATE.
   - [x] Current installed Vite is 5.4.21; current PostCSS is 8.5.15.
4. **Blast radius**
   - [x] Direct: `vite`, `postcss`.
   - [x] Transitive: `esbuild`, `nanoid`.
   - [x] Frontend build/proof only; trading authority unchanged.
5. **Root-cause research**
   - [x] Vite advisory affects `<=6.4.2`; patched Vite 6 line starts at 6.4.3.
   - [x] Official Vite 6.4.3 manifest depends on `esbuild ^0.25.0`, removing the recorded esbuild `<=0.24.2` advisory path.
   - [x] PostCSS current direct requirement allows vulnerable 8.5.15 from the lock; upstream 8.5.23 includes security hardening.
   - [x] Recorded nanoid audit requires >=3.3.18 for all current high findings, so lock regeneration must resolve nanoid >=3.3.18.
6. **Pre-fix verification**
   - [x] Keep Security Audit as the failing regression.
   - [x] Keep Frontend Browser Runtime Smoke as semantic regression protection.
7. **Implementation rule**
   - [x] Reject `npm audit fix --force` because audit proposes incompatible-major movement.
   - [ ] Move to the smallest compatible patched Vite 6.4.3+ line.
   - [ ] Move PostCSS to a patched line.
   - [ ] Regenerate package-lock deterministically so esbuild >=0.25.0 and nanoid >=3.3.18 are actually resolved.
8. **Post-fix verification**
   - [ ] `npm ci` succeeds without `--force`.
   - [ ] `npm audit` has 0 HIGH/CRITICAL.
   - [ ] Frontend production build passes.
   - [ ] 22-tab browser smoke passes.
   - [ ] Security Audit Evidence passes.
9. **Production protection**
   - [ ] No merge until all mandatory PR-head gates pass.
10. **Checkpoint**
   - [x] This child loop is recorded before dependency mutation.

### SEC-001.2 — Bandit mixed-snippet declassification bypass child loop

Independent PR review found that Bandit's `code` field can contain neighboring context lines. The original declassifier searched the entire compacted snippet, so a reviewed static shell command on an adjacent line could mask a different dynamic B602/B605 finding.

1. **Freeze evidence**
   - [x] Review thread `PRRT_kwDORagLIM6ZemY0`, medium severity, `scripts/security_audit_summary.py`.
   - [x] Affected pre-fix logic used substring membership against the whole `code` snippet.
2. **Classify**
   - [x] Security-detector false-green risk, not application runtime failure.
3. **Reproduce**
   - [x] Existing tests lacked mixed safe+unsafe neighboring-line fixtures.
   - [x] Constructed adversarial B605/B602 snippets where line 9 is allowlisted and Bandit `line_number=10` is dynamic.
4. **Blast radius**
   - [x] Security Audit Evidence trustworthiness affected.
   - [x] No broker/order runtime code affected.
5. **Root cause**
   - [x] Declassification was bound to snippet content, not Bandit's exact finding line.
6. **Pre-fix/adversarial regression**
   - [x] Add mixed-snippet B605 case.
   - [x] Add mixed-snippet B602 case.
   - [x] Add ambiguous unnumbered multi-line fail-closed case.
7. **Implementation**
   - [x] Added `_bandit_finding_source_line()` that maps only `line_number` from numbered Bandit context.
   - [x] Exact equality required for the two reviewed command shapes.
   - [x] Missing/ambiguous mapping returns empty and remains hard FAIL.
8. **Post-fix verification**
   - [ ] Exact-head unit/security workflow must pass on current head.
   - [ ] Raw 13 HIGH findings must remain visible.
   - [ ] No dynamic/mixed fixture may declassify.
9. **Production protection**
   - [x] This detector fix does not authorize deploy/merge by itself.
10. **Checkpoint**
   - [x] Source fix commit `7cb07b8beaf848d019529636c79d05dddecdd676`.
   - [x] Adversarial-test commit `abf43afa78586f988942a3c4e875d1f6edb3ea38`.
   - [ ] Close only after exact-head mandatory gates and security artifact inspection.

## UI-001 — All-tab and option-chain truth

- [x] Browser contract covers all 22 current sidebar tabs.
- [x] Static regression binds verifier list exactly to Sidebar.
- [x] Option Chain gate requires broker universe breadth, equity options, expiries, contracts, strikes and ALL STRIKES visibility.
- [x] Prior frontend browser smokes passed after proof hardening.
- [ ] Current exact-head smoke must pass after latest security/QC changes.
- [ ] Production proof remains required after exact-main deployment.

## UI-002 — Local-vs-production proof provenance incident

### Root cause already proven
- [x] Frontend Browser Runtime Smoke serves the built Vite UI from `127.0.0.1`; it is a local render/runtime harness.
- [x] Its 22 screenshots can prove tab mounting and visual state but cannot prove authoritative GCP broker connectivity.
- [x] The GCP production visual-proof path is separate: `scripts/gcp_ui_tab_visual_proof.py` with source `real_deployed_cloud_run_ui` and Cloud Run service discovery.
- [x] Therefore `Dhan · Waiting` in local smoke is not equivalent to production broker disconnect.

### Permanent prevention checklist
- [x] Local harness declares `PROOF_SCOPE=LOCAL_NON_PRODUCTION`.
- [x] Local harness declares `PRODUCTION_AUTHORITY=False`.
- [x] Local harness declares `BROKER_CONNECTIVITY_PROVEN=False`.
- [x] Local manifest writes `production_claim_allowed=false`.
- [x] Local manifest records localhost/Vite origin.
- [x] Static regression forbids flipping local production/broker authority to true.
- [x] Static regression proves GCP production harness remains separate.
- [ ] Current exact-head Frontend Browser Runtime Smoke must regenerate proof.
- [ ] Local reports must never be used as production broker evidence.

### Production broker UI proof checklist — all mandatory
- [ ] Resolve Cloud Run URL from GCP.
- [ ] Record expected Git SHA and serving revision.
- [ ] Require deployed SHA equality with expected current main.
- [ ] Record traffic percentage.
- [ ] `/api/health` HTTP 200 and lightweight.
- [ ] `/api/broker/status` HTTP 200, sanitized, latency recorded.
- [ ] Overview says Dhan CONNECTED/READY.
- [ ] Broker tab says CONNECTED/PROOF READY.
- [ ] System tab says Broker PROVEN/CONNECTED.
- [ ] Data Integrity has no broker-data blocker.
- [ ] WebSocket state matches realtime claim.
- [ ] Non-placeholder index/equity/equity-option data visible.
- [ ] Equity option expiries/contracts/strikes > 0; ALL STRIKES visible.
- [ ] API counts correlate with UI.
- [ ] Refresh and second browser session repeat assertions.
- [ ] Zero credential injection, mutation or order call.
- [ ] Screenshot + semantic JSON + revision/SHA metadata in one artifact.

### Broker-connected claim rule
A broker-connected statement is allowed only when Overview + Broker + System agree in the same production proof window and production API/runtime evidence agrees. A local browser artifact can never satisfy this rule.

## AUTO-001 — Automation self-verification checklist

Every automated checker must itself be tested before its result can be trusted.

1. **Identity/provenance** — [ ] workflow, trigger, exact SHA, runner and proof scope recorded.
2. **Positive case** — [ ] known-good fixture produces PASS.
3. **Negative case** — [ ] known-bad fixture produces FAIL.
4. **Adversarial case** — [ ] stale/wrong-SHA/wrong-URL/placeholder/mixed-snippet evidence cannot pass.
5. **Freshness** — [ ] generated/source timestamps present where applicable.
6. **Authority** — [ ] production claims require deployed GCP authority.
7. **Safety** — [ ] LIVE locked; zero order/mutation actions.
8. **Failure behavior** — [ ] exact blocker/path/expected/observed/next action emitted.
9. **Retry behavior** — [ ] bounded retry only for proven transient transport failure.
10. **Recurrence behavior** — [ ] repeated class increments recurrence and creates child loop.

## AUTO-002 — Required automation chain for Issue #188

- [ ] Repository/sidebar ↔ 22-tab browser contract.
- [ ] Local render/runtime smoke with `LOCAL_NON_PRODUCTION` provenance.
- [ ] Frontend type/build smoke.
- [ ] Security Audit Evidence.
- [ ] CodeQL.
- [ ] Global Safety.
- [ ] Exact-main Cloud Run deployment.
- [ ] Exact serving SHA/revision/traffic proof.
- [ ] Production `/api/health` proof.
- [ ] Production broker status + sanitized token provenance proof.
- [ ] Dhan rotator reliability proof.
- [ ] Scheduler/job configuration proof.
- [ ] Production semantic browser proof for Overview/Broker/System/Data Integrity.
- [ ] NSE/BSE equity and supported index coverage.
- [ ] Index/equity derivatives coverage.
- [ ] Multiple index/equity option chains and expiries.
- [ ] Full supported strike visibility and CE/PE coverage.
- [ ] Quote freshness/stale labeling.
- [ ] WebSocket reconnect/resubscribe proof.
- [ ] Rate-limit/backoff/circuit-breaker proof.
- [ ] Broker-outage degraded-mode UI proof.
- [ ] Backend API ↔ production UI parity proof.
- [ ] Repeat-browser refresh proof.
- [ ] 60-minute uninterrupted market-session observation after prerequisites are green.

### Automation failure handling
If any automation item fails: freeze logs/artifact; classify FAIL/BLOCKED/CI_INFRASTRUCTURE; create 10-step child loop; state hypothesis before retry; add regression/adversarial test; implement smallest durable fix; focused rerun; adjacent rerun; complete mandatory chain; update checklist only from fresh machine evidence.

## Closure rule

No item is `CLOSED — PROVEN` until source → tests → security → merge → exact-main deployment → runtime → broker/data → semantic UI → recurrence observation → documentation all pass on the same causal chain.
