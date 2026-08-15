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
   - [x] PostCSS current direct requirement allows vulnerable 8.5.15 from the lock; upstream 8.5.23 includes the security hardening and depends on `nanoid ^3.3.16`.
   - [x] Recorded nanoid audit requires >=3.3.18 for all current high findings, so lock regeneration must resolve nanoid >=3.3.18 rather than merely satisfying PostCSS's lower bound.
6. **Pre-fix verification**
   - [x] Keep Security Audit as the failing regression.
   - [x] Keep Frontend Browser Runtime Smoke as semantic regression protection.
7. **Implementation rule**
   - [x] Reject `npm audit fix --force` because audit proposes Vite 8.2.1 major and repo evidence already shows incompatible-major risk.
   - [ ] Move to the smallest compatible patched Vite 6.4.3+ line.
   - [ ] Move PostCSS to a patched 8.5.23+ line.
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
   - [x] This child loop is recorded before the next dependency mutation.

## UI-001 — All-tab and option-chain truth

- [x] Browser contract covers all 22 current sidebar tabs.
- [x] Static regression binds verifier list exactly to Sidebar.
- [x] Option Chain gate requires broker universe breadth, equity options, expiries, contracts, strikes and ALL STRIKES visibility.
- [x] Frontend Browser Runtime Smoke #161 passed after the Bandit audit hardening/checklist change.
- [ ] Re-run after dependency remediation to ensure the toolchain upgrade does not regress UI.
- [ ] Production proof remains required after exact-main deployment.

## Closure rule

No item is `CLOSED — PROVEN` until source → tests → security → merge → exact-main deployment → runtime → broker/data → semantic UI → recurrence observation → documentation all pass on the same causal chain.
