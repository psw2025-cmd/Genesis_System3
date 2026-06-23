# GitHub Billing-Free Truth Bridge Plan

## Problem

Scheduled GitHub Actions on a private repository can consume included Actions minutes. If quota is exhausted or billing/payment is blocked, automated runs may fail or create billing concern.

## Immediate safety change applied

The workflow `.github/workflows/system3-truth-bridge.yml` is now **manual only**.

The schedule was removed to stop automatic GitHub-hosted runner usage.

## Free / no-billing options

### Option A — Local run on user's PC

Use:

```bat
tools\run_truth_bridge_local.bat
```

This runs:

```bat
python scripts\system3_truth_bridge.py
python scripts\system3_production_viability_bridge.py
```

Generated reports:

```text
reports/latest/system3_truth_bridge/summary.md
reports/latest/production_viability_bridge/summary.md
```

Optional upload:

```bat
git add reports/latest/system3_truth_bridge reports/latest/production_viability_bridge
git commit -m "proof: update local truth bridge reports"
git push
```

This uses the user's PC, not GitHub-hosted runners.

### Option B — GitHub manual run only

Use only when needed:

```text
GitHub -> Actions -> System3 Truth Bridge -> Run workflow
```

This still uses GitHub Actions minutes, so avoid if billing is blocked.

### Option C — Self-hosted runner

A self-hosted runner uses the user's own machine instead of GitHub-hosted compute. This can avoid GitHub-hosted runner minute billing, but it needs careful security setup and should not be used until the user is comfortable managing it.

### Option D — Render-side report endpoint

A future improvement can add a read-only backend endpoint such as:

```text
/api/proof/truth-bridge
/api/proof/production-viability
```

This would generate reports inside Render without GitHub Actions. It will not commit to GitHub unless a secure GitHub token is configured, which is not recommended unless properly scoped.

## Current recommendation

Use Option A first:

```text
Run locally from C:\openalgo-main using tools\run_truth_bridge_local.bat
```

This is the safest zero-GitHub-billing method.

## Safety rule

No solution should ask the user for:

- broker API secret
- access token
- PIN
- OTP
- TOTP
- password
- full `.env`

The bridge must remain read-only.
