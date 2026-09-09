# Genesis System3 Governance

## Authority

- Code/config authority: GitHub `psw2025-cmd/Genesis_System3` current `main`.
- Runtime/execution/acceptance authority: authorized Windows laptop `C:\Genesis_System3_Clean` only.
- Current dashboard authority: the localhost URL/port defined by current-main configuration.
- Coordination bus: GitHub Issue #188.
- Broker authority: Dhan through the approved local secure-secret lifecycle.

## Temporal truth

Stored reports, screenshots, prior PASS results, CI results, and earlier runtime sessions are historical context. Claims about current health require fresh evidence from the currently running exact-main laptop instance.

## Acceptance gate

A current acceptance verdict requires: exact `HEAD==origin/main` provenance (or explicitly reconciled working-tree provenance), active process/PID and listener identity, backend and `/ui` reachability, broker metadata without secret values, same-session 4/4 required index-chain source/freshness/contracts, API↔UI consistency, scheduler/background-worker health, local DB/state consistency, logs/alerts reconciliation, and semantic verification of all 22 canonical tabs.

Missing, stale, contradictory, or unavailable evidence is `NOT_PROVEN`/`BLOCKED`, never PASS.

## Safety governance

- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- Real order count must remain zero.
- No secret/token/PIN/TOTP/private-key exposure.

## Change governance

Inspect current `main` and active PR ownership before mutation. Use normal branch/PR review. Do not overwrite parallel ownership. Runtime acceptance occurs only after merged code is freshly proven on the authorized laptop.
