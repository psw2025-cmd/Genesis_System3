# Parallel Audit — broker_auth

- Status: **BLOCKED**
- Blockers: `1`

## Findings
- Broker UI has token-aware connected logic.
- Backend has broker diagnose endpoint for env/token probe.
- Backend checks Dhan env presence in diagnose route.

## Blockers
- Actual Dhan auth cannot be proven by static repo; needs Render API probe and user refreshed token if invalid.

## Required fixes
- User must refresh/update Dhan read-only token securely if Render probe shows invalid/expired.
- Visual proof must show Broker panel BLOCKED/TOKEN ERROR or valid broker proof; no misleading CONNECTED.
