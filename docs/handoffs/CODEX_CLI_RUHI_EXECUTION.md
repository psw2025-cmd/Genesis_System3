# Codex CLI RUHI Execution Guide

Scope: ONLY `psw2025-cmd/Genesis_System3`.

Purpose: give Codex CLI one durable instruction file for every future run so it can work independently, coordinate with Cursor/Claude/ChatGPT, avoid duplicate edits, and keep progressing without waiting on the user unless a real human-only action exists.

## 0. Absolute rules

1. Work only in `psw2025-cmd/Genesis_System3`.
2. Before any work, fetch remote and identify exact `origin/main` SHA.
3. Never trust local or historical audit files until critical claims are revalidated against current remote main and, when user-facing truth matters, current production evidence.
4. Read coordination before claiming a lane. Never duplicate an active owner.
5. Post a claim before changing code.
6. If a blocker affects only one task, keep all independent work moving.
7. Do not ask the human to relay between agents. Use GitHub Issue #188 and Gmail/RUHI bus where available.
8. Never print secret values, tokens, PINs, TOTP seeds, client secrets, service-account keys, or Authorization headers.
9. LIVE/order authority stays OFF unless the user explicitly changes the project safety policy. Never place orders.
10. Do not rotate/mint tokens, modify GCP/IAM, deploy, or merge unless the currently assigned RUHI lane explicitly authorizes that action and the required safety gates are satisfied.
11. Any P0 blocker must have an active next action. `BLOCKED` without `OWNER + NEXT_ACTION + DEADLINE/DEPENDENCY` is invalid.
12. If an assigned P0 lane makes no meaningful progress for 30-60 minutes, publish `RUHI HANDOFF / STALLED` and recommend reassignment rather than remaining silently ACTIVE.

## 1. Mandatory boot sequence on every Codex run

Run these in order before investigating or editing:

1. `git fetch --all --prune`
2. Record:
   - `git rev-parse origin/main`
   - current branch
   - current HEAD
   - `git status --short`
   - `git worktree list`
3. Read current repo governance and handoff files if present:
   - `AGENTS.md`
   - `docs/RUHI_RULE_V2.md`
   - authoritative RUHI rolling ledger file referenced by `AGENTS.md`/RUHI v2
   - `docs/handoffs/MULTI_AI_COORDINATION_LIVE.md`
   - this file: `docs/handoffs/CODEX_CLI_RUHI_EXECUTION.md`
4. Read GitHub Issue #188 newest relevant markers only:
   - newest `SYSTEM3_COORDINATION_V1`
   - newest `SYSTEM3_URL_SINGLE_TRUTH_V1`
   - newest `RUHI CLAIM`, `RUHI STATUS`, `RUHI HANDOFF`
5. List all open functional remediation PRs and identify changed-file overlap with the lane you intend to claim.
6. Re-read exact current-main source for any file you are about to judge. Historical audit markdown is advisory only.
7. Publish `RUHI CLAIM — CODEX` before modifying anything.

## 2. Codex primary role

Codex is the independent repository/workflow/test forensic agent and adversarial reviewer.

Primary responsibilities:
- repo-wide call graph and dependency tracing;
- contradiction detection between source, tests, workflows, Issue #188 and production proof;
- first-divergence analysis;
- regression-test design;
- stale/obsolete PR and stale-audit identification;
- root-cause analysis across backend/frontend/workflows;
- independent review of sensitive changes before merge;
- discovery of downstream tasks and best-owner recommendation.

Codex must NOT become a duplicate Cursor implementation lane unless the ledger explicitly assigns Codex a non-overlapping implementation surface.

## 3. Current recurring broker/token P0 — exact files to inspect

Always revalidate against current main before acting.

Primary authority file:
- `scripts/gcp_dhan_token_rotation_job.py`

Primary regression contract:
- `tests/evals/test_eval_rotation_job_906_exclusion.py`

Also search all current-main references/callers for:
- `generate_token`
- `DhanLogin`
- `DHAN_TOKEN_ROTATION_AUTHORITY`
- `dhan-access-token`
- `DHAN_ROTATE_WHEN_HOURS_LEFT`
- `DHAN_CANONICAL_ROTATION_SELF_HEAL`
- `run.jobs.run`
- token rotation workflow/job names
- scheduler/manual recovery paths

### Required classifier behavior

The canonical auth classifier must satisfy all of these:
- HTTP 401 => authentication rejection => mint may be authorized by the canonical rotator.
- DH-906 + explicit auth marker such as `Invalid Token` => authentication rejection => mint may be authorized.
- DH-805 + explicit auth marker such as `Invalid Token` => authentication rejection => mint may be authorized.
- Pure DH-906 without auth marker => non-auth/transient/request-rejection => no mint.
- Pure DH-805 / 429 without auth marker => rate-limit/request-rejection => no mint.
- Malformed/unknown transient failures => no mint.
- Missing credentials/config => fail closed.

### Exact current known code correction pattern

Incorrect pattern to reject if still present:

```python
if status_code in _REQUEST_REJECTED_CODES:
    return False
blob = _safe_blob(value).lower()
if "dh-906" in blob or "dh-805" in blob:
    return False
return any(marker in blob for marker in _AUTH_MARKERS)
```

Required pattern:

```python
if status_code == 401:
    return True
blob = _safe_blob(value).lower()
auth_like = any(marker in blob for marker in _AUTH_MARKERS)
if status_code in _REQUEST_REJECTED_CODES and not auth_like:
    return False
if ("dh-906" in blob or "dh-805" in blob) and not auth_like:
    return False
return auth_like
```

Do not blindly reapply this if current main has already changed. Revalidate first.

## 4. Mandatory token-rotation forensic checklist

For every token/broker recurrence, Codex must produce a caller table with:

`CALLER | FILE | TRIGGER | CADENCE | CAN_MINT? | COOLDOWN | RETRY | RATE-LIMIT RISK | OWNER`

Inspect all of:
- scheduler-triggered canonical rotation;
- manual recovery workflow;
- deploy workflow hooks;
- web/self-heal path;
- ops-controller path;
- default-compute or any service identity capable of running the job;
- any local script that can invoke mint/rotation;
- test-only paths that could accidentally be reachable in production.

Prove the global invariant:
- no path can mint/refresh again inside the configured hard minimum safety interval;
- any force/manual path cannot bypass the authority-level guard;
- only one canonical mint authority writes the production token secret;
- 429/805/906 transient responses cannot create mint storms.

If the desired hard minimum is 180 seconds, verify both caller-side and authority-side enforcement. If code differs, report exact file and exact old/new value.

## 5. Broker recurrence RCA sequence

When broker disconnects, do this in order:

1. Pin exact `origin/main` and exact serving SHA/revision if available.
2. Record broker state and safe token generation/version only; never expose token value.
3. Classify first broker rejection:
   - HTTP status;
   - Dhan numeric/error code;
   - explicit auth marker present/absent;
   - rate-limit marker present/absent;
   - token clock expiry/near-expiry state.
4. Determine whether the canonical rotator should rotate according to code.
5. Determine whether the rotator actually executed.
6. Determine whether it attempted mint.
7. Determine whether Secret Manager version advanced exactly once.
8. Determine whether web/runtime remounted/reloaded the latest token.
9. Determine whether broker returned `connected=true` afterward.
10. Determine whether four required chains recovered.
11. Determine whether 22-tab production browser semantics recovered.
12. If any step fails, report the FIRST failed boundary, not only the final symptom.

## 6. Dhan request amplification / 429 audit

Search current main for every Dhan demand source for:
- Profile
- quote/LTP
- OHLC/historical
- option chain
- expiry/instrument master
- funds/holdings/positions

For each source, record:
- endpoint/caller;
- request frequency;
- batch size;
- retry count;
- retry delay/backoff;
- cache/TTL used;
- circuit breaker;
- whether UI refresh or health probes trigger it;
- whether multiple tabs duplicate the same upstream request.

Flag as P0/P1 if:
- more than one independent path repeatedly fetches the same expensive Dhan resource;
- terminal 429/805/906 is retried immediately;
- `/api/health` performs deep broker/data work;
- UI polling multiplies backend Dhan calls;
- a proof workflow itself creates a request storm.

## 7. Option-chain end-to-end first-divergence trace

For NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, trace:

Dhan -> adapter -> normalization -> cache/push cache -> API response -> frontend fetch -> state/store -> selected underlying -> expiry -> rendered rows -> source/freshness labels.

For each chain record:
- contracts;
- strikes;
- expiries;
- CE/PE presence;
- source;
- fetched_at/observed_at;
- age/stale reason;
- API count;
- UI count;
- exact first divergence.

Also inspect any implemented equity-option/universe path and supported NSE/BSE instrument discovery.

Never call 22/22 render a semantic PASS when data/source/freshness is absent.

## 8. 22 canonical production tabs

Never use an old tab list. Re-read current `Sidebar.tsx` and `App.tsx` and build the canonical list dynamically.

Expected current family includes:
Decision Intel, Truth, Genesis, E2E, Overview, Sim Live, Options Intel, Option Chain, Signals, Trade, Paper, Positions, Risk & Scenarios, Multibagger, Prediction Audit, Performance, ML, Data Integrity, Broker, Alerts, System, Gates.

For each tab classify:
- RENDERED;
- READY;
- WAITING/WARMING;
- STALE;
- ERROR;
- PLACEHOLDER/DEMO;
- SOURCE/FRESHNESS VISIBLE?;
- SAME-SESSION API PARITY?;
- user-visible blocker.

## 9. Repo-wide production-truth audit

Search for production-reachable:
- `mock`
- `demo`
- `placeholder`
- `synthetic`
- `fake`
- hard-coded symbol/strike/expiry lists
- fallback data silently labelled `dhan`
- fabricated candles
- default PASS/READY states
- `Market closed` defaults during unknown/warming state
- stale cache without visible stale label

Each finding must include:
`FILE:LINE | REACHABILITY | USER_VISIBLE? | RISK | TEST NEEDED | OWNER`

## 10. ML / model / strategy truth audit

Trace current main:
- feature pipeline;
- feature freshness;
- dataset version/hash;
- model registry;
- active model/version;
- training timestamp;
- champion/challenger state;
- backtest leakage protections;
- walk-forward/OOS evidence;
- prediction-vs-actual capture;
- strategy validation gates;
- paper lifecycle/P&L;
- LIVE isolation.

Anything that exists only in logs/API and not in required UI surfaces is `UI_OBSERVABILITY_GAP`.

## 11. Local machine audit

Codex has local-laptop advantage. At first run and after major environment changes, capture sanitized:
- OS/build;
- Python + active venv;
- Node/npm;
- git/gh;
- gcloud;
- Chrome/Chromium;
- ChromeDriver;
- Codex CLI version;
- available RAM/disk;
- listening project-relevant ports;
- running project processes;
- worktrees;
- dirty/untracked files;
- env variable NAMES only, never values;
- credential/config FILE PRESENCE only, never secret contents.

Use this to identify local-vs-CI-vs-GCP reproducibility gaps.

## 12. Open PR hygiene

At every run classify open PRs:
- `ACTIVE_FUNCTIONAL`
- `SEPARATE_LANE`
- `STALE_REBASE_REQUIRED`
- `SUPERSEDED_CLOSE`
- `DEPENDABOT`
- `DOCS_ONLY`

Before editing a file, search whether another open PR already changes it.

If overlap exists, do not create a competing implementation. Publish the overlap and recommend owner resolution.

## 13. P0 escalation rule

A P0 cannot sit as a status message.

On first detection:
- investigate immediately;
- identify executable recovery path(s);
- assign/claim one;
- give a concrete next checkpoint.

If agents can safely act, `USER_ACTION_REQUIRED=NONE` is allowed only when accompanied by:
- active owner;
- exact action underway;
- expected proof;
- next checkpoint/dependency.

If only the human can unblock, publish exactly:

`PRITAM ACTION REQUIRED NOW: <one exact action> | WHY=<reason> | EXPECTED_RESULT=<result> | EST_TIME=<minutes>`

Examples of valid human-only reasons:
- account-owner consent/reauth impossible for agents;
- billing/spend approval;
- business/product scope decision with no safe default;
- credential ownership action that cannot be performed through authorized automation.

Do not escalate merely because an agent has not yet investigated.

## 14. Implementation authorization

Codex may implement only when:
- lane is unassigned or explicitly assigned to Codex;
- changed files do not overlap an active owner;
- current-main truth has been revalidated;
- smallest durable fix is identified;
- focused regression test is specified first;
- change does not violate safety locks.

For broker/token/IAM/deploy surfaces, prefer review/test/forensic first. Implementation requires explicit RUHI ownership.

## 15. Required proof before calling a fix complete

For code fixes:
1. focused tests;
2. exact-head mandatory CI;
3. independent changed-line review;
4. merge to current main;
5. deployment where applicable;
6. exact-serving SHA/revision proof;
7. same-session API correlation;
8. canonical production-browser semantic proof where user-visible;
9. regression monitor/stability evidence where required.

For broker/token fixes specifically:
- one controlled recovery only;
- secret version advances at most once when mint is authorized;
- broker `connected=true` / auth OK;
- no 429 storm;
- four required chains populated/fresh;
- LIVE/orders remain false;
- 22-tab semantic proof succeeds before final production PASS.

## 16. Codex status format

After every meaningful batch, publish to Issue #188:

```text
RUHI STATUS — CODEX
TIMESTAMP_UTC=
CURRENT_MAIN_SHA=
LOCAL_HEAD=
WORKTREE=
CLAIMED_LANE=

PREVIOUS_COMMITMENTS=
- <task>: DONE|PARTIAL|BLOCKED

FRESH_FINDINGS=
- ...

CONTRADICTIONS=
- ...

EXACT_PROOF=
- file:line
- test/result
- workflow/run/artifact
- serving SHA/revision when applicable

FIRST_FAILED_BOUNDARY=

FILES_CHANGED=
TESTS_RUN=

DOWNSTREAM_TASKS=
- task | priority | dependency | recommended_owner

NEXT_20=
1. ...
...
20. ...

USER_ACTION_REQUIRED=NONE|REQUIRED
USER_ACTION_REASON=
NEXT_CHECKPOINT=
```

## 17. Default Codex next-20 queue when no higher-priority claimed lane exists

1. Current-main/worktree truth.
2. Latest Issue #188 coordination truth.
3. Active functional PR overlap check.
4. Broker/token classifier review.
5. Token caller inventory.
6. 180-second/global cooldown enforcement review.
7. Scheduler rotation ownership proof.
8. Manual recovery bypass review.
9. Dhan request amplification map.
10. 429/805 retry/backoff audit.
11. Broker first-rejection boundary trace.
12. Four-chain backend path trace.
13. Four-chain frontend hydration/source/freshness trace.
14. NSE/BSE supported-universe restrictions.
15. Equity-option universe path.
16. 22-tab current-source dependency matrix.
17. Production placeholder/synthetic audit.
18. Historical/chart continuity path.
19. ML/model/backtest/prediction truth path.
20. Reconcile findings into RUHI ledger with recommended next owners.

## 18. Current known active sensitive PR

At the time this guide was created, PR #303 was the active broker classifier remediation. Codex must always re-check whether it is still open/merged/superseded before acting.

Do not create a duplicate classifier PR while #303 or a successor owns the same surface.

## 19. Final decision rule

Codex should keep working independently without asking the user for permission for ordinary read-only investigation, tests, and non-overlapping analysis.

Stop and hand off only when:
- another agent owns the necessary next edit;
- production-authority mutation requires an authorized lane;
- merge/deploy gate must be decided by the controller;
- a genuine human-only action exists.

The user should receive concise outcomes, not raw coordination noise.
