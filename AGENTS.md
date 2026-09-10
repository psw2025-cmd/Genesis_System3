# Genesis System3 — Universal Agent Operating Contract

**Scope:** `psw2025-cmd/Genesis_System3` only.

## Mandatory authority

- GitHub current `main` is the only code/configuration authority.
- The authorized Windows laptop checkout `C:\Genesis_System3_Clean` is the only execution/runtime authority.
- GitHub Issue #188 is the canonical coordination bus.
- Fresh evidence from the currently running exact-main laptop instance is required for current health/readiness claims.
- Gmail is secondary asynchronous evidence only.

## Mandatory preflight

Before substantive work: fetch remote `main`, read Issue #188, inspect active PR ownership, identify the current-main localhost dashboard URL/port, and reconcile available fresh laptop provenance. Never promote stale local evidence to current truth.

## Independent verifier contract

Read-only verifier lanes inspect exact main, local checkout/worktree provenance when available, process/service identity, backend/UI reachability, broker metadata without values, NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY source/freshness/contracts, all 22 UI tabs semantically, API↔UI contradictions, scheduler/background workers, local DB/state, and logs/alerts. Report root-cause options without mutating runtime in verifier mode.

## Broker authority

Broker credentials/tokens are local-laptop-only after migration. Use only the current-main approved local secure-secret/environment mapping. Never expose tokens, PINs, TOTP seeds, private keys, or credentials. No blind mint/rotation and no weakening safeguards. Broker acceptance requires fresh current-main `/ui` connected state plus same-session API and 4/4 chain proof.

## Safety boundary

- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- Real broker order count must remain zero.
- Never place, modify, cancel, or square off real orders.

## UI lifecycle

Canonical tabs: `decision-intel`, `truth`, `genesis`, `e2e-proof`, `overview`, `sim-live`, `options-intel`, `chain`, `signals`, `trade`, `paper`, `positions`, `risk-scenarios`, `multibagger`, `prediction-audit`, `performance`, `ml`, `data-integrity`, `broker`, `alerts`, `system`, `gates`.

A render/HTTP PASS is insufficient. Each tab requires semantic data/state validation and same-session API comparison where applicable.

## Engineering behavior

When an issue is found: reproduce from an authoritative source, determine root cause, check active ownership, implement the smallest safe fix on a fresh branch, run focused/full required tests, merge only through normal governance, then obtain fresh laptop runtime proof. Human action is requested only for genuine external-account/MFA/consent/billing or unavoidable laptop-access boundaries.
