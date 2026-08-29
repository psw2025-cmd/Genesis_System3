# RUHI Dashboard Outcome Contract

## Permanent rule
Every agent task must begin with the user-visible production outcome and work backward through the full execution chain. A task is not complete because code exists, tests pass, CI is green, a PR merged, an API returned 200, or a backend job succeeded.

For any task that can affect the user experience, the required chain is:

USER GOAL -> LIVE DASHBOARD TAB/CARD/TABLE/CHART -> FRONTEND STATE -> API -> BACKEND LOGIC -> DATA/PROVIDER -> GCP RUNTIME/CONFIG -> DEPLOYED EXACT SHA -> LIVE BROWSER PROOF.

If a task is backend-only, it must still expose a truthful dashboard status/proof card or control-plane surface so the user can see the result without reading logs.

## Mandatory TASK_OUTCOME_CARD
Before implementation, every agent must record:
- TASK_ID
- USER_VISIBLE_GOAL
- TARGET_DASHBOARD_TAB
- TARGET_VISIBLE_RESULT
- CURRENT_VISIBLE_FAILURE
- ROOT_CAUSE_LAYER
- REQUIRED_API_OR_STATE
- REQUIRED_PROVIDER_OR_DATA
- REQUIRED_GCP_SETTING_OR_RUNTIME
- ACCESS_RESOLUTION_CARD_ID if any access/provider blocker exists
- IMPLEMENTATION_OWNER
- INDEPENDENT_VERIFIER
- EXACT_ACCEPTANCE_PROOF
- USER_ACTION_REQUIRED=YES/NO

## Required execution sequence
1. Observe the live production URL first and capture the current visible failure.
2. Correlate the exact visible element with frontend state and its API calls.
3. Trace the API to backend logic, data source/provider, and GCP runtime/configuration.
4. If any access/provider/GCP setting blocks the path, immediately apply `RUHI_ACCESS_PROVIDER_BLOCKER_CONTRACT.md`; never stop at “no access”.
5. Implement the smallest root-cause fix from current GitHub `main` in the claimed lane.
6. Add regression tests that fail pre-fix and pass post-fix where practical.
7. Pass protected exact-head CI.
8. Merge through PR and deploy only when runtime-affecting.
9. Verify exact-serving SHA/revision in GCP.
10. Reopen the production dashboard in a real browser and prove the target tab/card/table/chart now shows the expected truthful result.
11. Cross-check same-session API/state/provider evidence against the visible UI.
12. Record proof in Issue #188/task ledger and only then mark DONE.

## Completion states
- DISCOVERED: visible problem observed.
- ROOT_CAUSE_PROVEN: failing layer proven.
- PATCHED: code/config prepared.
- TESTED: meaningful regression proof passes.
- EXACT_HEAD_GATED: required checks pass on exact PR head.
- MERGED: canonical GitHub code.
- DEPLOYED: runtime-affecting change is serving.
- UI_PROVEN: live dashboard visibly shows the correct result.
- STABILITY_PROVEN: result remains correct through repeated checks/expected session transitions.
- COMPLETE: all required proof recorded.

Only `UI_PROVEN` or `COMPLETE` may be described to the user as fixed for a user-visible issue.

## Forbidden shortcuts
Agents must not:
- call a dashboard issue fixed from backend/API tests alone;
- use HTTP 200 as semantic proof;
- treat 22/22 tab mounts as content correctness;
- hide WAITING/EMPTY/STALE/HARDCODED/PLACEHOLDER states just to make a gate green;
- claim PASS when evidence is missing;
- ask the user to coordinate agents or manually relay routine technical status;
- report an access/GCP/provider blocker without fastest fix, fallbacks, exact settings path, owner, proof, and parallel work;
- deploy docs/test-only commits merely to match GitHub HEAD;
- allow local/laptop evidence to override GCP production truth.

## Dashboard-first prioritization
When several issues exist, prioritize the issue that most directly prevents the user from seeing truthful actionable production information. The default order is:
1. production liveness and exact-serving truth;
2. broker/data connectivity truth;
3. market session/freshness truth;
4. Overview/critical summary visibility;
5. NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY and equity/options data visibility;
6. signals/decision intelligence;
7. PAPER lifecycle and P&L visibility;
8. QC/gates/model evidence;
9. secondary analytics/feature expansion;
10. docs/reporting cleanup.

## Owner boundary
Routine repo, CI, GCP diagnostics, deployment, browser proof, API/UI tracing, and provider diagnostics remain agent-owned. Owner escalation is allowed only for genuine billing/identity/consent/account-MFA/new-permission/destructive/LIVE-trading boundaries, and must use kid-level exact instructions.

## Core principle
Every agent must be able to answer: “What exact thing will the user see on the live dashboard when my work is complete?” If there is no answer, the task is not yet defined well enough to execute.
