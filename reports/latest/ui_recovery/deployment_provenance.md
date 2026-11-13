# Genesis System3 — Deployment Provenance & Untracked File Audit
- **Audited At (UTC)**: `2026-11-04T09:55:53.279440+00:00`
- **Git Branch**: `fix/scanner-219-equity-rotate`
- **Git HEAD SHA**: `d5ad4d0c7a9dc3c26ad13666fb791bb9e2a13a82`

## 1. Local Port 8008 Runtime vs Cloud Run Entrypoint Discrepancy (`BLOCKED` — `G27`, `PEND-002`, `PEND-047`, `PEND-057`)
- **Local Port 8008 Entrypoint**: `scripts/start_port_8008_clean.py` runs `uvicorn.run("content.app.app:app", host="0.0.0.0", port=8008)`.
- **Untracked Status (`git status --short`)**:
  - `?? content/app/app.py`
  - `?? content/app/dhan_account_router.py`
  - `?? content/app/verified_market.py`
  - `?? content/app/templates/premium.html`
  - `?? scripts/start_port_8008_clean.py`
- **Cloud Run Entrypoint (`dashboard/backend/Dockerfile`)**:
  - Copies repository worktree (`COPY . /app`), builds `dashboard/frontend/dist`, and executes `CMD ["python", "scripts/start_cloud_run.py"]`.
  - `scripts/start_cloud_run.py` runs `uvicorn.run("dashboard.backend.secure_app:app")`, which wraps `dashboard/backend/app.py` — **NOT** `content.app.app:app`.
  - Furthermore, any Git-based CI build (`.github/workflows/cloud-run-auto-deploy.yml`) checks out committed Git history and therefore **excludes all untracked (`??`) files** (`content/app/*`, `scripts/start_port_8008_clean.py`).
- **Required Owner Action**: Per Instruction 4 ("Do not commit, merge, or deploy without approval"), staging/committing `content/app/*` and unifying `scripts/start_cloud_run.py` with the port 8008 routes is **BLOCKED** pending explicit owner approval.
