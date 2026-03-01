# Production Dashboard Guide

End-to-end guide for running the System3 Ultra Dashboard in production.

---

## Quick Start

```batch
START_FULL_DASHBOARD_SYSTEM.bat
```

This script:
1. Checks Python, Node.js, npm
2. Sets up venv and installs dependencies
3. Runs bootstrap (creates outputs/, health.json, positions_live.json, ml_performance.json)
4. Starts backend (port 8000)
5. Starts frontend (port 3000)
6. Opens Chrome

---

## Production Verification

After startup, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_production_dashboard.ps1
```

Checks:
- Bootstrap complete
- Backend health
- Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- Critical API endpoints (state, positions, chain, ML)
- Frontend responding

---

## Production Build (Optional)

To serve the built frontend instead of dev server:

```powershell
cd dashboard\frontend
$env:VITE_DEBUG="0"
npm run build
```

Output: `dashboard/frontend/dist/`

To serve: Use a static file server (e.g. nginx, or `npx serve dist`) pointing to the backend at port 8000 for API.

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `SYSTEM3_REAL_ONLY` | 1 | 0 = allow synthetic data when market closed |
| `SYSTEM3_DEBUG` | 0 | 1 = verbose error details, tracebacks in API |
| `VITE_DEBUG` | (unset) | 0 = suppress API_BASE console logs (production) |

---

## Security

- **Backend**: Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy)
- **CORS**: Allows all origins (adjust for production if needed)
- **Rate limiting**: 0.1s delay per request to avoid broker rate limits

---

## Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/api/health` | Full health + broker + market status |
| `/health` | Alias for /api/health |
| `/healthz` | Kubernetes-style health check |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Backend not responding | Run from repo root: `python -m uvicorn dashboard.backend.app:app --host 127.0.0.1 --port 8000` |
| Frontend blank | Check console (F12); verify API_BASE = http://localhost:8000 |
| CORS errors | Backend uses allow_origins=["*"]; ensure backend is running |
| Empty tabs | Run `scripts\populate_demo_data_for_dashboard.ps1` for demo data |
