# System3 No-Billing Autonomous Proof Plan

## Purpose

Use local terminal or Codespaces manual terminal instead of scheduled GitHub Actions while billing is a concern.

## Rules

- Analyzer/Paper only.
- Live trading stays disabled.
- No real broker orders.
- No private config files committed.
- No paid cloud creation.
- No fake PASS results.

## No-billing execution order

Run from the repo terminal:

```bash
git pull
python -m compileall .
npm install
npx playwright install chromium
DASHBOARD_URL=https://genesis-system3-backend.onrender.com/ui npx playwright test
```

On Windows also run:

```powershell
tools\run_truth_bridge_powershell.bat
```

## Required local proof outputs

- `reports/latest/dashboard_browser_proof/summary.json`
- `reports/latest/dashboard_browser_proof/summary.md`
- `reports/latest/system3_truth_bridge/latest.json`
- `reports/latest/system3_truth_bridge/summary.md`
- `reports/latest/production_viability_bridge/latest.json`
- `reports/latest/production_viability_bridge/summary.md`
- `reports/latest/render_log_audit/summary.json`
- `reports/latest/render_memory_audit/summary.json`

## Dashboard pass rules

PASS only if:

- dashboard loads,
- no raw Vue `{{ ... }}` text is visible,
- Analyzer/Paper mode is visible,
- Live disabled is visible,
- proof/status sections are visible.

FAIL if raw `{{ ... }}` text is visible.

## Production-readiness pass rules

Production is not live-ready unless:

- 5+ market-day prediction proof exists,
- Spearman rho target is met,
- paper lifecycle is proven on real market session,
- real broker data proof is present,
- dashboard proof passes,
- no false LIVE_READY claim exists.

## Commit proof manually

```bash
git add reports/latest tests docs tools playwright.config.ts package.json package-lock.json
git commit -m "proof: update no-billing autonomous verification"
git push
```
