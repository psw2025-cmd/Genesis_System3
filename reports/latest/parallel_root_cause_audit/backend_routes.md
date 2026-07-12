# Parallel Audit — backend_routes

- Status: **BLOCKED**
- Blockers: `2`

## Findings
- Active broker funds route is implemented in app.py.
- Active broker live positions route is implemented in app.py.

## Blockers
- Modular routers are imported but disabled; fixes in dashboard/backend/routers may not affect production routes.
- Synthetic data generator import still exists in backend; verify REAL_ONLY blocks it from displayed trading truth.

## Required fixes
- Move critical fixed logic into active dashboard/backend/app.py routes or safely complete router migration without duplicate routes.
- Add proof that synthetic generator is never used for live scanner/chain/model/paper truth.
