# ChatGPT → Cursor — BR-2 MICRO2 execution instructions

CURRENT_MAIN=cabc8eb1217464a0871e06b1a209adbfe6eae032
SERVING_SHA=cabc8eb1217464a0871e06b1a209adbfe6eae032
LIVE=false
ORDERS=false
NEXT_OWNER=CURSOR
WAVE=BR2_MICRO2_RUNTIME_QC_OBSERVER_ONLY

## Authority and temporal truth

This instruction was prepared after independently re-reading GitHub current main, Issue #188, PR #279 handoff, merged PR #278, current `dashboard/backend/app.py`, and tests-only PR #277.

The request-scoped production capture recorded in `docs/CHATGPT_MUST_REVIEW_NOW.md` was captured at `2026-08-18T04:23:12Z`: main and serving SHA matched `cabc8eb1217464a0871e06b1a209adbfe6eae032`; broker was disconnected with `DHAN_REQUEST_REJECTED_906`; Secret Manager generation reported v267; health was `not_ready/BROKER_NOT_READY`; market was open; gates were 2/7; LIVE/orders were false. Treat that capture as historical after its timestamp. Re-probe before making any newer "current/live" claim.

Before editing, fetch `origin/main` again. If main is no longer `cabc8eb1217464a0871e06b1a209adbfe6eae032`, rebuild this task from the new exact main and re-check overlap before modifying files. Never blindly transplant old `app.py` hunks.

## Ownership / anti-duplication lock

Cursor is assigned only the BR-2 MICRO2 implementation wave by this instruction.

Before mutation:

1. Re-read the newest Issue #188 coordination markers.
2. Enumerate all current open functional PRs and exact heads.
3. List changed files for each active runtime PR.
4. Confirm no active PR/agent currently owns `dashboard/backend/app.py` for another wave.
5. Confirm BR-2 MICRO2 is not already present on current main or another active implementation branch.
6. If overlap exists, STOP mutation, post `STATE=BLOCKED_COORDINATION` to Issue #188, name the conflicting PR/file/owner, and continue only read-only analysis.

PR #279 is docs/coordination only. Do not add runtime implementation to PR #279.

PR #277 is intentionally tests-only and based on older main `32026834...`. Do not merge #277 as-is and do not treat it as the implementation. Reuse/reconstruct its regression intent on the new BR-2 MICRO2 branch from exact current main. Once the replacement BR-2 PR exists, mark #277 as superseded only through normal coordination; do not silently discard its contract.

## Proven defect to remove

Current main `dashboard/backend/app.py` still contains `/api/qc/runtime` code that imports/uses:

- `DataSourceManager`
- `fetch_chain_for_api`
- `_run_blocking`

and creates a per-underlying live chain fetch equivalent to:

```python
def _fetch_chain():
    return fetch_chain_for_api(DataSourceManager(), underlying)

fetched = await _run_blocking(_fetch_chain, timeout=45.0)
```

This makes runtime QC a second Dhan consumer instead of an observer. During broker/rate-limit incidents it can multiply Dhan demand independently of the canonical `/api/chain/{underlying}` path.

Current main already provides canonical observer sources that must be reused:

- `_chain_from_push_cache(sym)` — pushed/micro-loop snapshot authority
- `_cache_get(key, ttl_s)` — local canonical TTL cache
- `_TTL_CHAIN` / existing chain cache-key convention

Do not introduce a new cache, a second broker client, a second lock, a new worker, another retry loop, or another token authority.

## Required smallest implementation

Create a narrow branch/PR from exact current main for BR-2 MICRO2.

Primary runtime file:

- `dashboard/backend/app.py`

Regression test file:

- reconstruct/adapt `tests/test_br2_runtime_qc_observer_contract.py` from PR #277 onto the new exact-main branch

Change `/api/qc/runtime` only as much as required so that, for each required underlying, it observes data in this order:

1. **Pushed snapshot first** via `_chain_from_push_cache(underlying)`.
2. **Canonical local TTL cache second** via `_cache_get(...)` using the same chain cache key/TTL convention used by the canonical chain API.
3. **Fail closed with explicit no-data state** if neither source exists.

Runtime QC must perform **zero independent live Dhan option-chain requests**.

Inside the `/api/qc/runtime` block there must be no runtime use of:

- `DataSourceManager`
- `fetch_chain_for_api`
- `_run_blocking` for chain acquisition
- direct requests/httpx broker calls
- token refresh/rotation
- retry/backoff loops that themselves call Dhan

Do not change the canonical `/api/chain/{underlying}` live acquisition behavior in this MICRO2 wave unless a directly necessary compile/test fix is unavoidable and separately justified in the PR.

## Fail-closed truth requirements

If no pushed/TTL snapshot exists for an underlying:

- `contracts` must remain empty, never synthetic/demo/fabricated.
- `total_contracts` must remain zero for the missing data.
- QC must not imply PASS/readiness from absence.
- Preserve explicit source/status/error/freshness truth where the existing schema permits.
- `overall_passed` must remain false when required runtime evidence is absent/invalid.
- `live_trading_enabled` must remain `False`.
- `order_placement_allowed` must remain `False`.

Do not relabel stale cache as fresh Dhan live data. If the canonical cache object already contains degraded/stale/source metadata, preserve it rather than normalizing it to a false success.

## Preserve BR-2 MICRO1 behavior

Do not regress the already-merged terminal retry suppression/taxonomy for:

- HTTP 429
- Dhan 805
- Dhan 808
- Dhan 906

MICRO2 removes a duplicate demand source; it must not reintroduce retries for these terminal conditions or reinterpret 906 as token-expired if current taxonomy says otherwise.

## Mandatory regression/adversarial tests

At minimum reconstruct the PR #277 contract so it proves:

1. `/api/qc/runtime` contains no `DataSourceManager`, `fetch_chain_for_api`, or chain `_run_blocking` acquisition path.
2. `/api/qc/runtime` consults `_chain_from_push_cache` before TTL cache.
3. `/api/qc/runtime` falls back to `_cache_get` with the canonical `chain_...` cache key convention.
4. Missing push + missing TTL cache returns explicit empty/no-data fail-closed state with zero contracts.
5. LIVE/order fields remain false.

Add a behavioral adversarial test, not only static token inspection:

- monkeypatch every possible live chain/network acquisition function reachable from this route to raise a distinctive exception such as `NETWORK_CHAIN_CALL_FORBIDDEN_BR2_MICRO2`;
- seed a pushed snapshot and prove `/api/qc/runtime` succeeds/observes it without invoking the forbidden network function;
- separately seed only the TTL cache and prove the route observes it without invoking network;
- with both caches empty, prove the route returns fail-closed no-data without invoking network.

The test must fail if runtime QC ever creates an independent network chain request again.

Where practical, assert push snapshot precedence over TTL cache by putting distinguishable values/sources in both and proving the pushed snapshot wins.

## Focused verification before CI

Run the smallest focused set first, including:

```bash
python -m pytest tests/test_br2_runtime_qc_observer_contract.py -q
python -m pytest tests/test_br1_dhan_auth_reliability.py -q
```

Also run directly related runtime-QC/chain tests already present in the repo, including `tests/test_qc_runtime_anomaly.py` and any current chain cache/push contract tests discovered on exact main.

Compile the changed Python files and run the repository's normal lint/static checks relevant to them.

Do not weaken or skip tests because they expose an existing contradiction. Record contradictions in Issue #188 and fix only if they are inside this wave's proven dependency.

## Exact-head mandatory gate

After implementation, push the narrow BR-2 MICRO2 PR and pin its exact head SHA.

Run/require all mandatory workflows triggered/relevant for that exact head, including as applicable:

- Genesis System3 Global Safety CI
- Security Audit Evidence
- CodeQL Security Audit
- SonarQube Audit
- GCP Dhan Token Fix CI
- GCP Stage 2 Safety Checks
- Frontend Browser Runtime Smoke if repository policy triggers it
- Workflow Priority Guard if current policy requires it

A green workflow summary does not override an unresolved changed-line security finding.

If the PR head/base changes, invalidate prior gate evidence and rerun/re-check the exact new head.

Do not merge on partial CI.

## Merge criteria

BR-2 MICRO2 is merge-eligible only when all are true:

- exact branch is based/reconstructed on then-current main;
- no file ownership overlap exists;
- focused observer/no-network tests pass;
- existing Dhan reliability tests remain green;
- all mandatory exact-head gates are green;
- no unresolved relevant security/code-scanning finding remains;
- LIVE=false and orders=false remain locked;
- no token/IAM/GCP mutation is included;
- diff remains the smallest observer-only runtime change plus regression tests.

After merge, record exact merge SHA in Issue #188.

## What NOT to do in this wave

Do not:

- rotate/mint Dhan token from web/runtime QC;
- run repeated broker recovery attempts;
- change Secret Manager payloads;
- change IAM/WIF/service-account roles;
- enable self-heal token minting;
- deploy merely to make tests green;
- run the full 22-tab acceptance yet;
- start the 60-minute closure window yet;
- perform LIVE/order operations;
- work on frontend Risk/Alerts/WAITING semantic fixes concurrently in this same PR;
- merge stale PR #277 directly.

## Post-merge next sequence

After BR-2 MICRO2 merges:

1. Re-read exact new main and Issue #188.
2. Confirm no runtime-QC independent Dhan chain demand remains.
3. Only then move to the controlled broker/data recovery lane.
4. Broker recovery must use the canonical rotator Job authority only; web/runtime QC must never mint.
5. Prove broker session separately from real Dhan market-data usability; `connected=true` alone is not a PASS.
6. Prove at least one read-only quote/OHLC path and the four required index chains.
7. Then address full supported-universe/source/freshness/API↔UI parity.
8. Then Cursor frontend semantic fixes can resume.
9. Deploy exact current main only after prerequisite runtime/UI changes and mandatory gates are complete.
10. Final closure requires fresh exact-serving-SHA production browser proof and the required uninterrupted market-session stability window; CI/docs alone are not final PASS.

## Required Issue #188 progress format

At branch creation / ready-for-gate / merge, post concise markers using:

```text
SYSTEM3_COORDINATION_V1
WAVE=BR2_MICRO2_RUNTIME_QC_OBSERVER_ONLY
OWNER=CURSOR
CURRENT_MAIN=<full sha>
PR=<number>
HEAD=<full sha>
STATE=<IN_PROGRESS|BLOCKED|READY_FOR_GATE|MERGED>
FILES_OWNED=dashboard/backend/app.py,tests/test_br2_runtime_qc_observer_contract.py
OVERLAP=<NONE|details>
FOCUSED_TESTS=<result>
MANDATORY_GATES=<result>
LIVE=false
ORDERS=false
TOKEN_MUTATION=false
IAM_MUTATION=false
NEXT_OWNER=<CURSOR|CHATGPT|LIVE_RECOVERY_LANE>
NEXT_ACTION=<one exact action>
USER_ACTION_REQUIRED=false
```

If blocked by another agent/PR, do not ask the user to relay. Post the conflict directly to Issue #188.

## User action

`USER_ACTION_REQUIRED=false` for this wave unless a genuine human-only break-glass permission/credential problem is independently proven. Routine GitHub, CI, code, coordination, and read-only diagnosis are agent-owned.
