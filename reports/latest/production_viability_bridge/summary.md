# System3 Production Viability Bridge

Generated UTC: `2026-06-23T21:27:27.3732048Z`

## Summary

| Field | Value |
|---|---|
| `generated_utc` | `2026-06-23T21:27:27.3732048Z` |
| `runner` | `PowerShell-NoPython` |
| `production_live_ready` | `False` |
| `paper_analyzer_allowed` | `True` |
| `strategy_quarantined_for_live` | `True` |
| `reason` | `Production/live readiness remains blocked until real market paper lifecycle, broker freshness, tick health, execution quality and positive net expectancy are proven.` |

## Blockers

| Severity | Code | Message |
|---|---|---|
| HIGH | `LIVE_DISABLED_UNTIL_PROVEN` | Live trading remains disabled until all production gates pass. |
| HIGH | `WEBSOCKET_TICK_HEALTH_NOT_PROVEN` | WebSocket tick health proof is not available from PowerShell bridge. |
| HIGH | `FRICTION_EXPECTANCY_NOT_PROVEN_POSITIVE` | Positive expectancy after all costs is not proven. |
