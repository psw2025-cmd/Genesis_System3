# ChatGPT → Claude instruction — independent forensic/non-blocking lane

Repository: `psw2025-cmd/Genesis_System3`

Authoritative production: GCP project `system3-openalgo-safe`, region `asia-south1`.

Current main at instruction creation: `cabc8eb1217464a0871e06b1a209adbfe6eae032`.

Coordination SSOT: Issue `#188`.

## 0. Operating rule

Do not wait idle when one task is blocked. If a task is blocked by ownership, unavailable GCP access, missing browser access, CI still running, rate-limit safety, or another agent's active file ownership, mark that task `BLOCKED` with exact evidence in Issue #188 and immediately continue the next non-overlapping read-only task in this file.

Do not duplicate Cursor or ChatGPT implementation. One functional file area has one active owner.

Do not ask the user to relay technical messages. Keep all technical progress, blockers, evidence, and handoffs in GitHub Issue #188.

## 1. Mandatory read-before-work sequence

Before any investigation or mutation, re-fetch and read current truth in this order:

1. exact remote `main` SHA;
2. latest comments in Issue #188;
3. `AGENTS.md` and `CLAUDE.md` if present;
4. `SYSTEM_STATE.md`;
5. `CHANGE_LOG.md`;
6. `docs/CHATGPT_MUST_REVIEW_NOW.md`;
7. `docs/chatgpt_to_cursar-5.md` so you know Cursor's current lane and must not overlap it;
8. current open PRs, exact heads, bases, changed files, reviews and mandatory checks;
9. PR #279 coordination docs;
10. PR #277 only as BR-2 MICRO2 regression-contract reference; do not merge its stale head;
11. current deployment workflow and Dhan token-rotation/scheduler code;
12. current broker/data request paths and runtime health code.

Do not trust any SHA, owner, workflow status or serving revision in this file after you begin. Revalidate first.

## 2. Current ownership lock — verify before relying on it

Latest intended split:

- Cursor: BR-2 MICRO2 implementation from exact current main, using `docs/chatgpt_to_cursar-5.md`.
- ChatGPT: consolidation, independent gating, sequencing, and later controlled recovery/deploy/live acceptance.
- Claude: independent forensic/GCP/architecture/contradiction lane.

Claude must not edit Cursor-owned BR-2 implementation files while that lane is active, especially `dashboard/backend/app.py`, unless Issue #188 explicitly reassigns ownership.

If Cursor has not actually started, do not silently take over. Record `CURSOR_LIVENESS=WAITING_UNPROVEN` with evidence and ask `NEXT_OWNER=CHATGPT` to decide reassignment. Continue your non-overlapping forensic tasks meanwhile.

## 3. First required GitHub checkpoint

Immediately after the read-before-work baseline, post to Issue #188:

`SYSTEM3_COORDINATION_V1`

`WAVE=CLAUDE_FORENSIC`

`OWNER=CLAUDE`

`CLAUDE_STATUS=WORKING_PROVEN`

`CURRENT_MAIN=<full sha>`

`ACTIVE_PRS=<numbers>`

`FILES_OWNED_BY_CLAUDE=NONE`

`CURSOR_LIVENESS=<WORKING_PROVEN|WAITING_UNPROVEN|BLOCKED|COMPLETE>`

`CHATGPT_LIVENESS=<WORKING_PROVEN|WAITING_UNPROVEN|BLOCKED|COMPLETE>`

`OVERLAP=<NONE|details>`

`NEXT_TASK=C1`

`USER_ACTION_REQUIRED=false`

This checkpoint is mandatory because assignment alone is not proof that an agent is working.

## 4. Task queue — execute in order, but skip blocked tasks and continue

### C1 — Exact current ownership/overlap/liveness audit

Read all current functional PRs and latest Issue #188 markers.

Produce a matrix of:

- functional area;
- owner;
- PR;
- head SHA;
- changed files;
- last fresh evidence time;
- liveness classification;
- overlap/conflict.

Classifications: `WORKING_PROVEN`, `WAITING_UNPROVEN`, `BLOCKED`, `COMPLETE`.

If another agent is assigned but has no fresh evidence, report it immediately. Do not assume work is happening locally.

### C2 — Current-main workflow failure correlation

Fresh Gmail/GitHub evidence has shown failures on current-main around the latest deployment wave, including Cloud Run Auto Deploy, Frontend Browser Runtime Smoke, Full Cloud Audit and GCP Dhan Token Fix CI, plus recurring uptime alert/resolved flapping.

Independently inspect only current/relevant runs. For each failure determine:

- exact run/job/step;
- whether it is caused by the known broker/Dhan problem, BR-2 demand amplification, deploy/IAM, test regression, or an independent defect;
- whether rerunning is safe/useful or would only reproduce the known failure;
- next owner.

Do not rerun repeatedly just to get green.

If exact logs are inaccessible, mark `NOT_PROVEN` and continue C3.

### C3 — Dhan demand call graph outside Cursor's MICRO2 lane

Read-only. Map every current code path that can generate Dhan quote/OHLC/option-chain/Profile requests.

At minimum inspect:

- `core/data/datasource_manager.py`;
- dashboard backend routes;
- scanner/ranker/background loops;
- marketfeed/websocket code;
- health/broker probes;
- deployment/browser/audit proof harnesses;
- scheduler/jobs;
- self-heal/token recovery triggers;
- cache-miss/expiry discovery paths.

For each caller record trigger, frequency, cache-first behavior, retries, terminal-error handling and owner.

The goal is to find any additional amplification edge NOT covered by Cursor's `/api/qc/runtime` MICRO2 work.

Do not edit Cursor-owned files. If you find a separate unowned edge, post a narrow candidate task to Issue #188 with non-overlapping file paths and `NEXT_OWNER=CHATGPT` for assignment.

### C4 — GCP serving/deploy truth

Read-only unless explicitly reassigned.

Verify:

- exact serving revision;
- serving SHA if exposed;
- traffic allocation;
- service account;
- LIVE/order flags;
- self-heal flags;
- current Secret Manager references by name/version only, never payload;
- latest deploy state;
- whether `SERVING_SHA == CURRENT_MAIN`.

Classify `EXACT_SHA` or `SERVING_SHA_DRIFT`.

If GCP access is unavailable, post `C4=BLOCKED_ACCESS` and immediately continue C5.

### C5 — IAM/token-rotator authority forensic

Read-only.

Determine who can execute `genesis-system3-dhan-token-rotate`, including permissions inherited from project roles such as `run.admin`, `run.developer`, or `Editor`.

Check scheduler identity, GitHub/WIF identities, web runtime identity, default compute, ops-controller/recovery identities if present.

Output:

`STRICT_SCHEDULER_ONLY=PASS|FAIL|NOT_PROVEN`

Do not mutate IAM. If blocked by access, continue C6.

### C6 — Health/uptime root-cause map

Read-only.

Investigate recurring uptime ALERT→RESOLVED flapping.

Verify whether `/api/health` is constant-time and dependency-free, whether it invokes broker/Dhan/external network, cold-start/deploy effects, timeout thresholds, and whether current browser/deploy checks create synchronous downstream load.

Output:

`HEALTH_CONSTANT_TIME=PASS|FAIL|NOT_PROVEN`

If a separate unowned defect is proven in non-overlapping files, propose a narrow task; do not implement without ownership assignment.

### C7 — Broker semantics cross-check

Read-only.

Separate these states:

- session/auth connection;
- Profile usability;
- quote usability;
- OHLC usability;
- option-chain usability;
- rate-limit state;
- stale-cache fallback;
- data-ready state.

Never treat `connected=true` alone as broker reliability PASS.

If live/read-only request testing would risk additional Dhan amplification while MICRO2 is unfinished, do not probe aggressively. Use the freshest safe evidence and mark current truth `NOT_PROVEN` where required.

### C8 — UI/API contradiction map

Read-only while Cursor owns UI/runtime implementation lanes.

Map exact component/API contradictions for:

- broker reliability;
- WAITING/LOADING forever;
- blank/no-data states;
- stale cache shown as fresh;
- Risk & Scenarios;
- Alerts/WebSocket transport vs broker readiness;
- option-chain source/freshness/completeness;
- API count vs UI count.

Post actionable file/component/API mapping to Issue #188, without editing overlapping files.

### C9 — Full market-data acceptance readiness

Classify each current area as `PASS`, `PARTIAL`, `BLOCKED`, `FAIL`, or `NOT_PROVEN`:

- NSE equities;
- BSE equities;
- NSE/BSE indices where supported;
- equity derivatives;
- index derivatives;
- index option chains;
- equity option chains;
- instrument discovery/search;
- quote freshness;
- candles/charts;
- WebSocket reconnect/resubscribe;
- source/freshness/degraded state;
- API/UI parity.

No final PASS from code/docs/API alone.

## 5. Non-blocking execution rule

A blocked task must never block the whole Claude lane.

Use this behavior:

- ownership blocked → continue read-only elsewhere;
- GCP access blocked → continue GitHub/source/workflow analysis;
- browser/live access blocked → continue architecture/IAM/call-graph analysis;
- workflow still running → analyze another independent task;
- rate-limit/token safety blocks live probe → use existing safe evidence and continue static/request-path analysis;
- Cursor actively owns file → do not touch it; inspect a different functional area;
- no unowned safe implementation exists → remain forensic and produce evidence, not duplicate code.

Only stop the entire lane for a genuine safety break-glass condition.

## 6. Update cadence in GitHub

Do not disappear while working locally.

Post a concise Issue #188 checkpoint after each completed task C1-C9, or immediately on any blocker/contradiction/overlap.

Every checkpoint must include:

`SYSTEM3_COORDINATION_V1`

`WAVE=CLAUDE_FORENSIC`

`OWNER=CLAUDE`

`CLAUDE_STATUS=<WORKING_PROVEN|BLOCKED|COMPLETE>`

`CURRENT_MAIN=<sha>`

`TASK=<C1..C9>`

`RESULT=<PASS|PARTIAL|FAIL|BLOCKED|NOT_PROVEN>`

`EVIDENCE=<exact PR/SHA/file/run/revision>`

`FILES_OWNED_BY_CLAUDE=<NONE or paths>`

`OVERLAP=<NONE|details>`

`NEXT_TASK=<task>`

`NEXT_OWNER=<CLAUDE|CURSOR|CHATGPT>`

`USER_ACTION_REQUIRED=false`

If a genuinely human-only action is required, set `USER_ACTION_REQUIRED=true` and state the single exact action plus why no agent/tool can perform it.

## 7. When Claude may implement

Default is read-only forensic work.

Claude may create a code PR only if ALL are true:

- defect is independently proven;
- current main re-fetched;
- no active PR/owner overlaps the functional area;
- the task is not already Cursor- or ChatGPT-owned;
- Issue #188 records Claude ownership before mutation;
- fix is narrow and testable;
- no token/IAM/LIVE/order mutation is required.

For any Claude implementation: regression test first, smallest fix, focused tests, relevant mandatory exact-head gates, then independent gate. Never reuse old gate evidence after head/base movement.

## 8. Safety invariants

Always preserve:

- GCP is production authority;
- legacy Render is non-authoritative;
- LIVE=false;
- orders=false;
- no real order action;
- no secret payload exposure;
- no SA-key creation;
- no blind token mint/rotation;
- no IAM/WIF weakening;
- no retry-until-green behavior;
- no production PASS from CI/docs alone.

## 9. Final Claude completion condition

Claude is not "complete" merely because one forensic report exists.

Complete this wave only when C1-C9 have each reached an evidence-backed terminal state (`PASS`, `FAIL`, `PARTIAL`, `BLOCKED`, or `NOT_PROVEN`), all discovered unowned defects have an owner/next action in Issue #188, and there is no unresolved ownership overlap.

Final marker:

`CLAUDE_STATUS=COMPLETE`

`DUPLICATE_WORK_FOUND=<true|false>`

`UNOWNED_BLOCKERS=<NONE|list>`

`NEXT_OWNER=<CURSOR|CHATGPT>`

`USER_ACTION_REQUIRED=<false|true>`

Do not perform final production acceptance; that remains the independent exact-serving deployment/browser gate after implementation waves are merged.