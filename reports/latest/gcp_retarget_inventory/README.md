# GCP retarget inventory (pre deep-verify)

## Canonical production
- URL: https://genesis-system3-web-doq2wplepa-el.a.run.app
- Target: gcp-cloud-run
- Config: config/cloud_runtime.json

## Runtime files updated
- dashboard/backend/app.py (/api/deploy/info, diagnose, approve)
- dashboard/frontend/src/config.ts (block onrender VITE_API_BASE_URL)
- dashboard/frontend/src/hooks/useData.ts (Cloud Run messages)
- dashboard/frontend/src/components/TopBar.tsx
- dashboard/frontend/src/components/LiveTradingGate.tsx
- scripts/gcp_cloud_run_auto_deploy.py (PUBLIC_BACKEND_URL env)
- tools/cloud_runtime_check.py
- tools/promote_to_cloud.py
- scripts/dashboard_api_verify.py
- check_integrity.py
- .env.example
- deploy/gcp/README.md
- dashboard/backend/Dockerfile (frontend epoch)

## Intentionally NOT changed
- Historical reports/docs under reports/latest/*render*
- tools/sync_render_secrets.py (legacy break-glass)
- .github workflows already using a.run.app

## Localhost note
- Quota/review failures: use localhost
- Local stack: http://127.0.0.1:8000
