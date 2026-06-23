# System3 Production Viability Bridge

Generated UTC: `NOT_RUN_YET`

## Summary

| Field | Value |
|---|---|
| `production_live_ready` | `false` |
| `paper_analyzer_allowed` | `true` |
| `strategy_quarantined_for_live` | `true` |
| `status` | `NOT_RUN_YET` |
| `reason` | `Production viability bridge scripts are installed, but no live report has been generated yet.` |

## Blockers

| Severity | Code | Message | Action |
|---|---|---|---|
| HIGH | `PRODUCTION_VIABILITY_NOT_RUN_YET` | Production viability report has not been generated from live Truth Bridge output yet. | Run local truth bridge from cloned Genesis_System3 repo. |
| HIGH | `LIVE_DISABLED_UNTIL_PROVEN` | Live trading remains disabled until real market paper lifecycle, broker freshness, tick health, execution quality, and positive net expectancy are proven. | Keep analyzer/paper only. |

## Warnings

| Severity | Code | Message | Action |
|---|---|---|---|
| MEDIUM | `GITHUB_ACTIONS_BILLING_SAFE_MODE` | Scheduled GitHub Actions are disabled to avoid billing/minute usage. | Use local run or manual workflow only if acceptable. |
