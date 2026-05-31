# PR17 Global Repo Cleanup and Deploy Safety Proof

This report records repository status verified online before any further deploy work.

## Base

- Repository: `psw2025-cmd/Genesis_System3`
- Base branch: `main`
- PR17 branch: `pr17/global-cleanup-deploy-safety-20260531`
- Latest verified main merge before PR17: `0e7a54ac79bd57e4d5df550aa3e36cd6c5334bc8`

## Open PRs

| PR | Status | Meaning | Action |
|---:|---|---|---|
| #11 | Open | Stale backend deploy PR. It overlaps later merged Docker work from PR #13, #15, and #16. | Do not merge as-is. |
| #1 | Open | Stale analysis PR that includes generated virtual environment content under `.venv-dashboard`. | Do not merge as-is. |

## Recent merged PRs

| PR | Meaning |
|---:|---|
| #16 | Corrected accidental double dashboard backend path. |
| #15 | Updated backend Docker references, then corrected by PR #16. |
| #13 | Added backend Docker path proof workflow and backend Dockerfile path proof. |
| #12 | Added root runtime authority inventory report only. |
| #10 | Added blocking root architecture and trading safety gate. |

## Backend Docker path truth

- Root `backend/` is not the proven backend path.
- Proven backend path is `dashboard/backend/`.
- Proven backend Dockerfile path is `dashboard/backend/Dockerfile`.
- Build context should remain repository root when root modules are needed.
- Backend image name remains `ghcr.io/psw2025-cmd/genesis_system3/genesis-backend:latest`.

## Deploy readiness

| Area | Status |
|---|---|
| Backend Docker path | PARTIAL PASS |
| CD backend path after PR #16 | PARTIAL PASS |
| Production Azure deploy proof | WARN - not fully proven |
| Dashboard live-data truth | WARN - shell only, live feeds not proven |
| Duplicate/stale cleanup | WARN - inventory exists, cleanup not completed |

## Protected areas not changed by PR17

- trading logic
- broker configuration
- database files
- model artifacts
- live runtime mode files

## Final status

| Gate | Result |
|---|---|
| Start from latest main | PASS |
| Avoid stale PR #11 merge | PASS |
| Avoid high-risk PR #1 merge | PASS |
| Runtime trading files untouched | PASS |
| Docker/backend truth documented | PASS |
| Production deploy fully proven | WARN |
| Stale PR cleanup completed | WARN |

## Recommended next step

Close or supersede PR #11 and PR #1 after this report is reviewed. Then create a fresh production deploy proof PR from latest main.
