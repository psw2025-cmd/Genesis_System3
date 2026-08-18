# ChatGPT → Cursor — post-BR2 parallel execution queue

Repository: `psw2025-cmd/Genesis_System3`
Coordination SSOT: Issue #188
GCP production authority: `system3-openalgo-safe`, `asia-south1`

BR-2 MICRO2 has been independently verified and merged.

`BR2_MICRO2_MERGE_SHA=5def9b41e3220bb59fe7e80b9bbd0e66b2f548cf`

Stale PR #277 is closed/superseded and must never be merged.

## 0. Mandatory first action

Before any edit, fetch exact current `origin/main`, latest Issue #188 comments, all open functional PRs, and changed-file ownership. Read:

- `AGENTS.md`
- `SYSTEM_STATE.md`
- `CHANGE_LOG.md`
- `docs/chatgpt_to_claude-1.md`
- this file

Do not trust the merge SHA above as current if main has advanced.

Claude owns the independent forensic/GCP/architecture C1-C9 lane in `docs/chatgpt_to_claude-1.md`. Do not duplicate Claude's call-graph, IAM, GCP serving, uptime-root-cause, or forensic tasks. If Claude posts a newly proven unowned code defect, do not claim it unless Issue #188 explicitly assigns Cursor ownership.

ChatGPT owns consolidation, controlled broker/data recovery sequencing, merge/deploy decisions, and final exact-serving production acceptance.

Cursor owns the frontend/runtime presentation waves below, one narrow PR at a time.

## 1. GitHub live-status rule

Do not disappear while working locally.

At the start of each Cursor wave post to Issue #188:

`SYSTEM3_COORDINATION_V1`
`OWNER=CURSOR`
`CURSOR_STATUS=WORKING_PROVEN`
`CURRENT_MAIN=<sha>`
`WAVE=<wave>`
`PR=<number|PENDING>`
`FILES_OWNED=<paths>`
`CLAUDE_SCOPE=docs/chatgpt_to_claude-1.md`
`OVERLAP=<NONE|details>`
`NEXT_ACTION=<single action>`
`USER_ACTION_REQUIRED=false`

For each coding PR create/update a wave status document on that PR branch:

`docs/agent_status/CURSOR_LIVE_STATUS.md`

Update it after each meaningful checkpoint **before final exact-head gates**. Once final gates begin, freeze the PR head; do not keep editing the status file afterward or the gates become stale.

At completion of each wave add a final handoff document on the same PR branch:

`docs/handoffs/CURSOR_TO_CHATGPT_<WAVE>.md`

It must contain exact base/head SHA, files, defect reproduced, tests, mandatory gates, unresolved findings, overlap verdict, LIVE/orders/token/IAM state, and `NEXT_OWNER=CHATGPT`.

Post the handoff file path to Issue #188. Never ask the user to relay technical details.

## 2. Non-blocking rule

If a wave is blocked by ownership, CI, missing live access, another active PR, or a backend dependency, post `STATE=BLOCKED` with exact evidence and immediately continue the next safe non-overlapping wave below.

Do not take ChatGPT's broker recovery/token/IAM/deploy lane. Do not take Claude's forensic lane. Do not wait idle merely because another agent is working.

## 3. CURSOR-W1 — Broker reliability UI truth

Reconstruct from exact current main; do not revive stale PR #251 blindly.

Primary target is the frontend semantics previously associated with `SystemProgressPanel` / Data Integrity broker lane.

Required truth rule:

- `connected=true` alone must never produce `Broker reliability = PASS`.
- Session/auth state and real market-data usability are separate states.
- If quote/OHLC/option-chain evidence is failed, rate-limited, stale/fallback, missing, or not proven, broker reliability must be `DEGRADED`, `BLOCKED`, or `NOT_PROVEN` as appropriate.
- Do not fabricate success when backend evidence is absent.
- Preserve LIVE=false and orders=false.

Prefer existing read-only APIs and current canonical truth contracts. Do not add independent Dhan requests from the frontend.

Before editing, search current main to identify exact components and tests. Claim only the specific files you need in Issue #188.

Mandatory regression: connected session + failed/429/805/906 market-data evidence must not render broker reliability PASS.

## 4. CURSOR-W2 — Finite WAITING/LOADING/blank-state semantics

After W1 is ready/gated, or in parallel only if files do not overlap, audit current canonical UI surfaces for permanent WAITING/LOADING/blank states.

Prioritize current production-visible pages from Issue #188, but revalidate source first.

Every affected surface must have finite states:

- loading
- ready
- degraded
- stale/fallback
- no-data
- error
- not-proven

No endless spinner may be treated as PASS simply because the React component mounted.

Use bounded frontend waiting/timeouts where appropriate; do not invent data.

Create a separate narrow PR if this wave touches different files.

## 5. CURSOR-W3 — Risk & Scenarios truth

Reconstruct the current Risk & Scenarios issue from exact main.

Goals:

- no infinite spinner;
- no mutation-shaped request for a read-only display path;
- no hard-coded/demo risk values shown as current runtime truth;
- authoritative values only, otherwise explicit `NO_DATA` / `NOT_PROVEN` / `DEGRADED`;
- bounded failure state;
- no LIVE/order enablement.

Add adversarial tests for backend unavailable/no data and stale/fallback states.

Do not change broker/token recovery logic.

## 6. CURSOR-W4 — Alerts + transport/broker semantics + mobile

Reconstruct current Alerts/mobile defects from exact main.

Required:

- WebSocket transport connectivity is not broker/data readiness.
- `No active alerts` only when the alert feed successfully loaded and is genuinely empty.
- show explicit error/not-proven when the feed failed.
- 375x667, 390x844, 430x932: no overlap, clipping, hidden controls, or horizontal overflow on affected canonical tabs.

Keep this frontend-only unless a proven backend contract gap is separately assigned.

## 7. CURSOR-W5 — Source/freshness/degraded-state presentation audit

Only after W1-W4 or when their files do not overlap.

Audit critical market-data surfaces for visible:

- source
- observed/fetched time
- freshness
- stale reason
- fallback/degraded state
- session truth where applicable

Do not create a new data source. Consume canonical backend truth only.

Any missing backend field is `BACKEND_CONTRACT_GAP`; post it to Issue #188 for ChatGPT/Claude assignment rather than inventing frontend values.

## 8. What Cursor must NOT do

Do not:

- rotate/mint Dhan tokens;
- mutate IAM/WIF;
- execute Cloud Run rotator job;
- change Secret Manager payloads;
- enable LIVE;
- place/modify/cancel orders;
- run retry-until-green loops;
- start the final 22-tab production acceptance or 60-minute closure window;
- revive stale PR #277 or #251 as-is;
- reformat all of `dashboard/backend/app.py` merely to satisfy Black;
- fold unrelated pre-existing Flake8/Black debt into a functional UI wave;
- duplicate Claude's C1-C9 forensic work.

Pre-existing lint debt must be recorded separately with exact lines and `NEXT_OWNER=CHATGPT`; do not broaden a wave to fix unrelated file-wide style.

## 9. Testing for every Cursor code wave

For each wave:

1. reproduce current defect from exact main;
2. add regression/adversarial test;
3. implement smallest fix;
4. focused tests;
5. relevant typecheck/build/lint for changed files;
6. current 22-tab static contract where frontend changes affect canonical tabs;
7. Global Safety;
8. Security Audit Evidence;
9. CodeQL;
10. SonarQube;
11. Frontend Browser Runtime Smoke;
12. other mandatory workflow triggered by changed files;
13. inspect unresolved changed-line security/review findings.

Head/base movement invalidates prior gates.

Do not claim production PASS from local/browser/CI proof.

## 10. Maximum useful parallelism

While ChatGPT performs controlled broker/data recovery and Claude performs C1-C9 forensics, Cursor should keep moving through W1-W5 **only where file ownership does not overlap**.

If W1 is waiting on CI, start read-only analysis/preparation for W2/W3/W4 on separate files, but do not create conflicting concurrent PRs that edit the same component tree.

One functional file area = one owner = one active PR.

## 11. Final Cursor wave completion

Cursor is not complete after W1 alone.

Continue through every currently applicable W1-W5 task until each is one of:

`MERGED`, `READY_FOR_GATE`, `BLOCKED_BACKEND`, `NOT_APPLICABLE`, or `SUPERSEDED`.

Final Cursor summary file:

`docs/handoffs/CURSOR_TO_CHATGPT_FULL_UI_TRUTH_WAVE.md`

It must list every wave, PR/head, files, tests/gates, remaining blockers, backend contract gaps, Claude findings consumed, and next owner.

Post to Issue #188:

`CURSOR_STATUS=COMPLETE`
`FINAL_HANDOFF_FILE=docs/handoffs/CURSOR_TO_CHATGPT_FULL_UI_TRUTH_WAVE.md`
`NEXT_OWNER=CHATGPT`
`USER_ACTION_REQUIRED=false`

Do not perform final production acceptance; ChatGPT will coordinate exact-main deploy/proof after all prerequisite runtime/UI waves are merged.