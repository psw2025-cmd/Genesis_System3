# System3 Current Control Plane

Updated by ChatGPT automation on 2026-06-07.

## Non-negotiable runtime safety

- Live trading remains disabled until a separate final human approval and broker-readiness gate pass.
- Analyzer/Paper mode remains the only approved runtime mode.
- No broker credentials, API keys, OTP, TOTP, MPIN, private keys, or env files may be committed.
- Secrets must live only in GitHub Actions secrets, GCP Secret Manager, or local private secret storage. Render.com secrets are retired/non-authoritative.

## Authoritative GCP Cloud Run runtime

- Deploy workflow: `.github/workflows/cloud-run-auto-deploy.yml`
- Dockerfile: `dashboard/backend/Dockerfile`
- Backend entry: `dashboard/backend/app.py`
- Runtime command: `uvicorn dashboard.backend.app:app --host 0.0.0.0 --port 8000`
- Production: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
- UI: `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/`
- Local backend:
  - Root: `http://127.0.0.1:8000/`
  - Docs: `http://127.0.0.1:8000/docs`
  - Health: `http://127.0.0.1:8000/api/health`
  - State: `http://127.0.0.1:8000/api/state`
- `render.yaml` is retired and must not exist.

## Completed repo-side actions

1. Render.com hosting retired. GCP Cloud Run is the only production deploy.
2. Backend Dockerfile patched to run FastAPI/Uvicorn instead of raw directory listing.
3. Backend dependency `pytz` added.
4. GitHub Actions Cloud Run Auto Deploy (keyless WIF) is the deploy path.
5. Render API deploy workflows are historical/non-authoritative.
6. Full repo read-only audit workflow added.
7. Tracked root `.env` removed from current `main`.
8. Tracked `config/.env` removed from current `main`.
9. `.gitignore` hardened for env/key/generated files.
10. Phase 2 runtime map workflow added.
11. Generated file cleanup workflow added and made deterministic.
12. `Run-FullQA.ps1` changed from hardcoded `C:\Genesis_System3` to portable repo-root detection.
13. `system3-auto-verifier.yml` added for consolidated proof.

## Current phase

Phase: Post-audit cleanup and authoritative runtime stabilization.

Allowed next actions:

- Run/read proof artifacts.
- Remove tracked generated files only.
- Improve CI/report-only workflows.
- Classify duplicate files by runtime reachability.
- Document authoritative runtime map.
- Fix deployment and dashboard-health proof.

Blocked until further proof:

- Deleting duplicate source files.
- Refactoring broker/order/trading logic.
- Enabling live trading.
- Adding real broker secrets.
- Model retrain/promotion apply mode.

## Manual actions only when unavoidable

Manual action should be requested only for:

- Creating/revoking private API keys or broker credentials.
- Uploading a GitHub Actions artifact ZIP if the connector cannot download it.
- UI screenshots when GitHub/Render state is not exposed through connector tools.
- Any broker/OTP/TOTP/private credential action.

## Next recommended sequence

1. Confirm cleanup-generated workflow result.
2. Confirm system3-auto-verifier result.
3. Run a fresh Phase 2 runtime-map after cleanup.
4. Build duplicate classification matrix: runtime / test / docs / backup / generated / quarantine candidate.
5. Only after proof, propose safe quarantine branch or cleanup PR.
