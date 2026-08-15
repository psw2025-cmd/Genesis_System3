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

## SEC-001 — Security Audit Evidence #45

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
- [ ] Rerun exact-head Security Audit Evidence.
- [ ] Confirm Bandit moves from hard FAIL to WARN/PASS without hiding raw counts.

### npm remediation micro-checklist
- [x] Identify vulnerable direct/transitive packages: `vite`, `postcss`, `nanoid`, `esbuild`.
- [x] Verify upstream fixed Vite 6 line begins at 6.4.3 for the current Windows `server.fs.deny` advisory.
- [x] Verify esbuild <=0.24.2 is patched at 0.25.0 for the recorded advisory.
- [x] Reject blind `npm audit fix --force` because it can force incompatible major toolchain changes.
- [ ] Determine exact current lockfile dependency graph and peer constraints.
- [ ] Select smallest compatible patched Vite/PostCSS line.
- [ ] Regenerate lockfile deterministically.
- [ ] Run `npm ci`, build, type/browser smoke, and `npm audit`.
- [ ] Require 0 HIGH/CRITICAL before Security Audit can pass.
- [ ] Keep moderate findings visible; remediate where compatible rather than suppressing.

## UI-001 — All-tab and option-chain truth

- [x] Browser contract covers all 22 current sidebar tabs.
- [x] Static regression binds verifier list exactly to Sidebar.
- [x] Option Chain gate requires broker universe breadth, equity options, expiries, contracts, strikes and ALL STRIKES visibility.
- [ ] Re-run after every security/dependency change to ensure toolchain remediation did not regress UI.
- [ ] Production proof remains required after exact-main deployment.

## Closure rule

No item is `CLOSED — PROVEN` until source → tests → security → merge → exact-main deployment → runtime → broker/data → semantic UI → recurrence observation → documentation all pass on the same causal chain.
