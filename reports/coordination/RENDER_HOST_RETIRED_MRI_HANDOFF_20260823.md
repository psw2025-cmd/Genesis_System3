# MRI handoff — Render.com hosting retired (GCP Cloud Run only)

**Marker:** `SYSTEM3_COORDINATION_V1` + `SYSTEM3_TEMPORAL_TRUTH_V1`  
**Investigation UTC:** `2026-08-23T12:23:21Z`  
**This file is a handoff, not live runtime truth.**

## One-line truth

Repo authority for deploy is GCP Cloud Run only. Production is **already** Cloud Run. PR **#330** retires leftover Render.com authority/tools/docs. It is **not serving** until merge + new SHA proof.

## Exact identities

| Item | Value | Class |
|---|---|---|
| PR | https://github.com/psw2025-cmd/Genesis_System3/pull/330 | current GitOps |
| Branch | `cursor/retire-render-gcp-only-46b5` | current |
| Exact PR head | `22155657e70cc2020fad5cf05ce8f3906b9aff74` | current at write |
| Base | `main` = `e6da6b469b2a10d7641ac17390d98b62b30340f9` (#328) | current at write |
| Serving SHA (GET `/api/deploy/info` at `2026-08-23T12:23:21Z`) | `e6da6b469b2a10d7641ac17390d98b62b30340f9` | HISTORICAL after this timestamp |
| Service | `genesis-system3-web` / `asia-south1` / `system3-openalgo-safe` | authority |
| UI | `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/` | authority |
| `deploy_target` | `gcp-cloud-run` | proven at that GET |
| `render_git_commit_legacy` | `""` | proven at that GET |
| LIVE | `false` | proven at that GET |
| `render.yaml` | ABSENT | proven locally + eval |
| Competing Perplexity Render PR | NONE. Only #330 is the retire-host PR | proven `2026-08-23T12:23:21Z` |

## MRI role ownership

| Role | Actor | Can do now | Must not do |
|---|---|---|---|
| Preparation / scan / eval / PR | This Cloud Agent run `bc-6d7e5982-db5f-40c1-9466-5dff3eff46b5` | DONE for repo side | Merge, orders, LIVE |
| Merge-capable | GitHub user `psw2025-cmd` (`admin=true`) | Merge #330 when exact-head CI green | Weaken LIVE / gates |
| Deploy-capable | `Cloud Run Auto Deploy` on `push` to `main` (`dashboard/**` is in this PR) | Auto-fires after merge | Manual Render deploy |
| Serving-SHA verifier | Any agent | GET `/api/deploy/info` **after** merge; require SHA contains `22155657e` or the merge commit | Reuse this file as “now” |
| Live-UI verifier | Any agent **after SHA match** | New Chrome session + `scripts/gcp_live_ui_snapshot.py` 22 tabs | Vite/local as production |
| Issue #188 poster | Merge-capable or next agent with write | Post `SYSTEM3_COORDINATION_V1` after SHA verify | Ask user to relay |
| This Cloud Agent merge | NO. `ManagePullRequest` has no merge. Token write on merge is false | — | Do not stall waiting for chat |

## What is already PROVEN (repo)

- `render.yaml` must not exist; presence is a fail-closed blocker (`render_yaml_present_retired_host`).
- `get_deploy_info` does not read `RENDER_GIT_COMMIT` / `RENDER_SERVICE_NAME` / `RENDER_GIT_BRANCH`.
- Authority docs no longer keep Render as runtime.
- Leftover Render-named tools are retired stubs (Cloud Run report; fail only if `render.yaml` returns).
- Eval `tests/evals/test_render_hosting_retired.py` — 15 passed locally. Hostname parse via `urlparse` (CodeQL substring alert fixed).
- Blocking CI on this head was green at write time. GitHub `CodeQL` status = `NEUTRAL` (prior fail on `d7561d6e9` is historical).

## What is UNPROVEN / next-agent only

1. **#330 merged into `main`.** This agent cannot merge.
2. **Cloud Run serving SHA includes this head.** Do not assume Auto Deploy from this file.
3. **Post-merge 22-tab production UI.** Sunday/closed market is not a data PASS.
4. **Mass-delete of `reports/latest/render_*`.** Forensic toolkit `DELETE_PROVEN_100` only. Do not delete from filename match.
5. **Closing stale Render PRs** `#65`, `#83` — historical; do not resume as current deploy.

## Downstream playbook (execute in order, no user wait)

### Step 0 — Revalidate (do not trust this file as now)

```bash
date -u +%Y-%m-%dT%H:%M:%SZ
git fetch origin main
git rev-parse origin/main
gh pr view 330 --json isDraft,mergeable,headRefOid,statusCheckRollup
curl -sS https://genesis-system3-web-doq2wplepa-el.a.run.app/api/deploy/info
```

If `headRefOid` ≠ `22155657e70cc2020fad5cf05ce8f3906b9aff74`, use the **new** head. If another Render-retire PR appeared, do not open a third.

### Step 1 — Merge (merge-capable only)

If exact-head mandatory CI is green and `mergeable=MERGEABLE`: merge #330 to `main`. Do not wait for chat.

### Step 2 — Deploy watch

`dashboard/backend/app.py` is in the PR → `Cloud Run Auto Deploy` must start on the merge push.  
`STATUS=WAITING` until the new revision is Ready. Do not run acceptance on SHA `e6da6b469`.

### Step 3 — Serving SHA

New GET `/api/deploy/info` after deploy Ready. PASS only if:

- `git_sha` is the merge commit or contains `22155657e`
- `deploy_target=gcp-cloud-run`
- `cloud_provider=google_cloud`
- `live_trading_enabled=false`
- `render_git_commit_legacy=""`

### Step 4 — Fresh UI proof

New Chrome/WebDriver session **after** SHA match:

```bash
python scripts/gcp_live_ui_snapshot.py
python scripts/system3_temporal_truth_guard.py
```

22 tabs. Render-only HTTP 200 is not semantic PASS.

### Step 5 — Coordinate and continue loop

- Post Issue #188 `SYSTEM3_COORDINATION_V1` with new SHA + verdict.
- Update `reports/latest/autonomous_loop/BACKLOG.md` row **R1** to `VERIFIED LIVE` only after Step 3+4.
- Next loop work is **not** another Render purge. Resume `next_id` from `reports/latest/continuous_closure/resume_state.json` (historically C1) **after** re-reading current resume JSON.
- Open gates (A2 Spearman, A3 signals) stay OPEN. Do not invent ρ/prices.

## Hard bans for every downstream agent

- Do not recreate `render.yaml`.
- Do not deploy to Render.com / onrender.com.
- Do not mint/paste Dhan secrets. Token path = `genesis-system3-dhan-token-rotate` only.
- Do not enable LIVE / `AUTO_EXECUTE_TRADES`.
- Do not strip UI visual-proof “RENDER” docs (they mean draw the UI).
- Do not mass-delete `reports/latest/render_100_agent_swarm/`.
- Do not open a second “delete all render” PR.
- Do not treat `connected=true` as market-data PASS.
- Do not treat this handoff, `reports/latest/`, or CI green as current production after time passes.

## Safety lock (unchanged)

`ANALYZE_MODE=1`  
`LIVE_TRADING_ENABLED=0`  
`SYSTEM3_LIVE_TRADING_ALLOWED=0`  
`AUTO_EXECUTE_TRADES=0`  
Broker: Dhan only.

## USER_ACTION

NONE for Render retirement. Merge is `psw2025-cmd` (or any later merge-capable actor), not the user in chat.
