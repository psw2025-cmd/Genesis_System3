# Claude Single Execution Authority — HISTORICAL_NON_AUTHORITY

**Authority marker:** `SYSTEM3_CLAUDE_SINGLE_EXECUTION_AUTHORITY_20260901`

**Status:** HISTORICAL_NON_AUTHORITY. Superseded 2026-09-07 by
`docs/control_plane/LOCAL_LAPTOP_USER_DIRECTIVE_20260907.md` and `AGENTS.md`.

This file is retained so forensic readers can see the 2026-09-01 Claude-only
ownership experiment. It is historical and non-authoritative.
must not recreate the retired GCP manifest (`infra/rotate-job.yaml`).

Current rules:

- No named AI is sole controller.
- Multi-agent mutation is allowed on non-overlapping dedicated branches.
- Issue #188 is historical coordination context, not a live bus.
- Runtime and acceptance are the local Windows laptop.
- GCP Cloud Run is retired as production authority.
- PAPER/ANALYZE safety is unchanged:

```
ANALYZE_MODE=1
LIVE_TRADING_ENABLED=0
SYSTEM3_LIVE_TRADING_ALLOWED=0
AUTO_EXECUTE_TRADES=0
```

zero real broker orders; no broker secret payload exposure.
