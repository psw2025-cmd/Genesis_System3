# Broker Truth Proof — Phase 6

**Generated:** 2026-07-02 16:26 IST
**Classification:** `BROKER_CONNECTED_REAL`

## Evidence

- `/api/broker/status`: `connected: true`, `error: null`, `order_placement_allowed: false`, `live_trading_enabled: false`
- `/api/health` broker block: `connected: true`, `status: "connected"`

## Real finding: web/worker token divergence (architecture gap, not silently patched)

Web and worker each maintain their **own independent copy** of `DHAN_ACCESS_TOKEN` and each independently runs `refresh_token()`. There's no mechanism for a successfully-refreshed token on one side to reach the other. Earlier this session, the worker's watchdog reported "Token OK — 12h remaining" (its own refresh succeeded) while the web service simultaneously reported `TOKEN_EXPIRED_OR_INVALID` (its separate copy was stale) — confirmed by direct log comparison. As of this snapshot, the web side has also successfully refreshed (likely via a restart-triggered `refresh_token()` call), so both are currently connected — but this divergence can recur any time the two services' refresh cycles fall out of sync. **Not fixed this session** — would need a new sync mechanism (e.g., push-based, matching the scheduler-health pattern); documented honestly rather than papered over.

## Fix confirmations

- **PR #49 (TOTP window-race fix)**: confirmed working — no more `Invalid TOTP` errors in logs after deploy.
- **PR #50 (token-lock race fix)**: confirmed — the specific double-call-within-0.3s race no longer reproduces.
- **`Token can be generated once every 2 minutes` error**: observed once, immediately after the credential-sync redeploy (before the lock fix took effect in that fresh boot). Not observed since.
- **PR #52 (timezone import fix)**: confirmed working — `/api/scheduler/health/push` no longer crashes with `NameError`, and `/api/scheduler/health` correctly shows `received: true` with real job data.

## Secrets handling

No token/PIN/TOTP/secret values were printed anywhere in this report or during this session's investigation — only presence booleans, lengths, key names, and status strings.
