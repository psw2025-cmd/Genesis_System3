# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-10 21:24 IST` (`2026-08-10 15:54 UTC`)

## Scope lock

- Repository: `psw2025-cmd/Genesis_System3`
- Branch audited: `main`
- Audited HEAD: `b70af343340a73ed27ca548820d5893c779ab5bd`
- Cloud target: **Google Cloud Run / Google Cloud services**
- Render is not an accepted deployment target for new work.
- Trading posture: **ANALYZER / PAPER ONLY**. Live-money trading remains disabled until separately proven.
- This file is the single continuously maintained Markdown audit summary. Do not create parallel summary Markdown reports for the same audit stream.

## Current executive verdict

| Gate | Current result | Evidence / reason |
|---|---|---|
| Repository access | PASS | GitHub repository reachable; default branch `main` |
| Last merged PR safety CI | PASS | PR #93 final head: 5/5 blocking Global Safety CI jobs PASS; GCP Dhan Token Fix CI PASS |
| PR #96 workflow checkpoint | PASS | Both associated workflows completed successfully |
| Current HEAD full verification | **NOT PROVEN** | `main` is 8 commits ahead of PR #96 merge checkpoint; 31 files changed after that merge |
| Analyzer/live-off deploy flags | PASS in workflow source | Cloud Run deploy sets `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`, `ANALYZE_MODE=1`, `SYSTEM3_MODE=ANALYZER` |
| Google Cloud migration | ACTIVE / PARTIAL | Cloud Run workflow is present; root `render.yaml` is absent; residual Render-era source wording still exists |
| Dashboard login contract | **FAIL** | Frontend does not send required JSON `api_key` body to `/api/auth/session` |
| Dashboard API-key handling | **NEEDS HARDENING** | Raw API key is retained in browser `sessionStorage` and injected into later requests despite HttpOnly cookie support |
| Audit tracker freshness | **FAIL** | generated audit text files still contain pre-cleanup source strings and do not match current HEAD |
| Real-market paper lifecycle | NOT PROVEN | Historical blocker remains until a fresh market-session proof closes it |
| Multi-day profitability / expectancy | NOT PROVEN | No fresh reproducible proof closes this historical blocker |
| Trade ready | **NO** | Current HEAD and production runtime proof are incomplete |

## Priority findings

### P0 — Dashboard login request contract is broken on current `main`

**Frontend evidence**

File: `dashboard/frontend/src/components/LoginPage.tsx`, lines `8-28`.

Current request:

```ts
const r = await fetch('/api/auth/session', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'X-API-Key': key.trim() },
  credentials: 'include',
})
```

There is **no JSON request body**.

**Backend evidence**

File: `dashboard/backend/app.py`, lines `430-485`.

The endpoint requires a Pydantic body:

```py
class DashboardAuthRequest(BaseModel):
    api_key: str

@app.post('/api/auth/session')
async def create_dashboard_session(payload: DashboardAuthRequest, request: Request):
    ...
    if not hmac.compare_digest((payload.api_key or '').strip(), _API_KEY):
        ...
```

Therefore the frontend and backend contracts do not match. The session endpoint can return FastAPI body-validation `422` before `payload.api_key` can be compared. PR #94 improved rendering of object/array validation errors, but it did not correct this request-body mismatch.

**Required closure proof**

1. Login POST sends JSON body `{"api_key":"..."}` without logging the key.
2. Valid key -> HTTP 200 and `authenticated=true`.
3. Invalid key -> HTTP 401.
4. Missing body -> expected validation failure test only.
5. `/api/auth/status` after login proves cookie-authenticated session.
6. Frontend production build PASS.
7. Auth tests PASS in CI.

### P1 — Raw dashboard API key is kept in browser `sessionStorage`

File: `dashboard/frontend/src/components/LoginPage.tsx`, lines `8-28`:

```ts
sessionStorage.setItem('s3_api_key', key.trim())
```

File: `dashboard/frontend/src/hooks/useAuth.ts`, lines `1-22`:

- reads `s3_api_key` from `sessionStorage`;
- globally injects it into axios requests;
- globally injects it into `window.fetch` requests.

Backend already creates an HttpOnly session cookie with `max_age=43200`, `httponly=True`, `secure` on HTTPS and `samesite='lax'` (`dashboard/backend/app.py`, lines `430-485`).

**Risk:** keeping the raw key in browser-accessible storage increases exposure to any successful same-origin XSS. The HttpOnly cookie exists specifically so normal post-login API access does not need the raw key repeatedly exposed to JavaScript.

**Recommended target state:** API key used only once to establish the server-side/HttpOnly session; remove raw-key persistence and routine header reinjection from browser code after login.

### P1 — Current HEAD is ahead of the last proven PR checkpoint

Last merged checkpoint reviewed here:

- PR #96 merge: `d3a97fd3bca1587f90ea5ecf0794dfb9c1ed8599`
- Current `main`: `b70af343340a73ed27ca548820d5893c779ab5bd`
- Difference: **8 commits ahead**, **31 files changed**.

Post-PR #96 changes include:

- frontend source status/terminology changes;
- `useData.ts` logic and payload-field renames;
- `BrokerPanel.tsx` changes;
- rebuilt frontend distribution assets;
- new audit tracking text files.

The GitHub combined-status query for current HEAD returned no status contexts in this audit. This does not prove no Actions ran, but it means **current HEAD cannot be marked CI-proven from the evidence gathered here**.

### P1 — Audit tracking files are stale relative to current source

Current file `audit/remaining_status_terms.txt` still records old code such as:

- `CLOUD_UNAVAILABLE`
- `RENDER_UNAVAILABLE`
- `blockedPaper`
- `blockedChain`
- `blocked_reason`
- older `EndToEndProof` function/label names.

But current source has already moved to terms including:

- `CLOUD_DEGRADED`
- `RENDER_DEGRADED`
- `pendingProof`
- `pending_reason`
- `proofReason`
- `isLiveTradingPending`.

`audit/PENDING_placeholders_filelist.txt` is more current and contains only three files:

1. `dashboard/frontend/src/components/BrokerPanel.tsx`
2. `dashboard/frontend/src/components/ErrorBanner.test.tsx`
3. `dashboard/frontend/src/hooks/useData.ts`

The stale tracking artifact must not be used as authoritative current-source proof until regenerated against the audited HEAD.

### P2 — Cloud Run deployment env list contains a duplicate key

File: `.github/workflows/cloud-run-auto-deploy.yml`, lines `118-132`.

The `--update-env-vars` string contains `REQUIRE_API_KEY=true` **twice**.

The values are identical, so this is not evidence that auth is disabled, but it makes the deployment contract needlessly ambiguous and should be reduced to one authoritative entry.

The same line correctly preserves analyzer/live-off flags:

- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- `ANALYZE_MODE=1`
- `SYSTEM3_MODE=ANALYZER`

### P2 — Google Cloud migration is not fully cleaned of Render-era source terminology

Confirmed:

- Root `render.yaml`: **absent** on current `main`.
- Primary deployment workflow: `.github/workflows/cloud-run-auto-deploy.yml`.
- Current `dashboard/frontend/src/components/TopBar.tsx`, around line `92`, still recognizes `RENDER_DEGRADED` as a legacy transient state.
- `dashboard/backend/app.py`, around lines `340-360`, still contains a comment referring to using `DEFER_INSTRUMENT_WARMUP=1 on Render`.

These are not proof of an active Render deployment, but they are residual migration debt. New runtime/configuration work must use Google Cloud terminology and behavior only.

### P2 — Frontend status-field rename requires contract verification

Current `dashboard/frontend/src/hooks/useData.ts` renamed fallback payload fields from `blocked_reason` to `pending_reason` in multiple paths.

Repository search at current HEAD shows `pending_reason` only in the frontend `useData.ts`, while `blocked_reason` remains referenced in proof/runtime tooling such as `tools/system3_broker_chain_semantic_gate.py` and existing audit artifacts.

This does **not yet prove a production API break**, because the backend may return `message`/`status` fields that preserve behavior. It does prove that a targeted API-contract test is required before calling the terminology migration complete.

## Recent merge / CI evidence

### PR #93 — login page + 12-hour auth session

- Merged: `2026-08-10`
- Merge commit: `8e5a79eede0766c458360a8fcb513627b0c0e860`
- Changed files: `6`
- Final head: `28ac9987fe7bf6196fe4ce9cb3ae0bc1540f368d`
- Global Safety CI run `31373602151`: **SUCCESS**
  - workflow policy and trading safety: PASS
  - Python compile proof: PASS
  - architecture and trading safety gate: PASS
  - full proof pack validation: PASS
  - frontend production build: PASS
- GCP Dhan Token Fix CI run `31373602159`: **SUCCESS**
  - Python compile/unit contracts: PASS
  - frontend production build: PASS
  - analyzer-only safety grep: PASS

Important: the green CI proves that commit set passed the configured jobs. It did not catch the frontend/backend login payload mismatch described above, so the auth test coverage is incomplete.

### PR #95 — authenticated broker/status proof check

- Merged: `2026-08-10`
- Merge commit: `180ff7d4f5250cf2c038b6bbf15d9a1f2e1047b8`
- Scope: CI-only broker/status proof authentication using `X-API-Key`.
- Application trading logic: not changed by this PR.

### PR #96 — UI status cleanup / MLPerformance repair

- Merged: `2026-08-10`
- Merge commit: `d3a97fd3bca1587f90ea5ecf0794dfb9c1ed8599`
- Final head: `f523606145a5c3e8d503cf876625991bf554f267`
- Changed files: `6`
- Global Safety CI: **SUCCESS**
- GCP Dhan Token Fix CI: **SUCCESS**

After this merge, eight additional commits landed on `main`, so PR #96 green status is a checkpoint, not proof of current HEAD.

## V5 consolidation checkpoint — historical verified snapshot

File: `docs/audit/V5_CONSOLIDATION_VALIDATION.md`.

Recorded snapshot:

- backend direct routes: `183 -> 183`, removed `0`;
- frontend navigation tabs: `16 -> 22`;
- frontend production build: PASS;
- dashboard application tests: `7/7 PASS`;
- security/deployment contract tests: `24/24 PASS`;
- Python and shell syntax: PASS;
- production npm vulnerabilities: `0`;
- frontend-embedded reusable API key: removed;
- live trading: disabled;
- deployment performed at that checkpoint: no.

This remains useful historical evidence but is **not current-HEAD proof** because later auth, CI and UI changes occurred after it.

## Google Cloud deployment posture

Current workflow source proves the intended deployment posture:

- Cloud Run service deployment;
- Google Secret Manager integration;
- Dhan access-token dynamic source;
- token rotation Cloud Run Job / Scheduler;
- one active service instance maximum in the enforcement step;
- analyzer mode and live trading off.

What is still required before the cloud runtime can be called current and proven:

1. successful deployment of the exact audited HEAD;
2. sanitized Cloud Run revision/image/commit provenance;
3. `/api/health` proof;
4. authenticated `/api/broker/dhan/status` proof;
5. authenticated funds/holdings/positions read-only proof;
6. mandatory Dhan option-chain proof;
7. dashboard browser proof against that same revision;
8. analyzer/live-off flags proven from deployed runtime, not just workflow source.

## Historical unresolved runtime / trading gates carried forward

These were present in the previous master report and remain open unless fresh evidence explicitly closes them:

- `real_market_analyzer_paper_lifecycle_not_proven`
- `nse_comparison_proof_missing`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` is retained as a **required safety state**, not a defect.

Previous automated snapshot had:

- Dhan schema audit: PASS
- Dashboard browser proof: PASS
- Trader requirements audit: BROKER_OFFLINE
- Real market data proof: PASS_WITH_WARNINGS
- Truth bridge: PASS
- Production viability: NOT_PROVEN

None of those older passes may be used to claim current Cloud Run production readiness without same-revision fresh proof.

## Next safest one-step sequence

1. **Fix and test the dashboard auth contract first**: send the JSON `api_key` body expected by the backend, then remove raw API-key persistence/header reinjection in favor of the existing HttpOnly session cookie.
2. Remove the duplicate `REQUIRE_API_KEY=true` deployment env entry.
3. Regenerate the audit tracking text files from the exact new HEAD; no stale trackers.
4. Run the full blocking Global Safety CI plus GCP Dhan Token Fix CI against the resulting PR/head.
5. Re-run frontend production build and auth-specific tests including valid/invalid/missing-body/session-cookie cases.
6. Deploy that exact commit to Google Cloud Run only.
7. Collect post-deployment runtime proof tied to revision + image digest + commit SHA.
8. During market hours, run real Dhan chain + analyzer paper lifecycle + reconciliation proof.
9. Only after multi-day positive costed expectancy and lifecycle truth are reproducible may trade-readiness be reassessed.

## Hard safety rule

Any future change that can place, modify, cancel, or route a live order remains out of scope unless separately authorized and proven safe. Analyzer/Paper mode must remain the default, and a failed or missing proof gate must never be converted into a readiness claim by changing UI wording alone.
