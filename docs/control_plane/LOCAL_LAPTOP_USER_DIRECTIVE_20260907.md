# Local laptop authority — user directive, 2026-09-07

The user confirmed on 2026-09-07 that Genesis System3 must run entirely on the
local Windows laptop. GCP is a past deployment and must not be used as runtime,
deployment, token, storage, monitoring or acceptance authority.

This directive supersedes conflicting Cloud Run/GCP instructions in AGENTS.md,
agent_policy.yaml, runbooks, historical reports and previous conversation
context. Earlier Claude-only ownership text does not block this work. Preserve
concurrent agents' unrelated changes.

Canonical checkout: `C:\Genesis_System3_Clean`.
GitHub `psw2025-cmd/Genesis_System3` current main is code authority.
Fresh local browser, same-session API, process identity and source provenance
establish runtime truth. Stored evidence remains historical.

Safety remains ANALYZE_MODE=1, LIVE_TRADING_ENABLED=0,
SYSTEM3_LIVE_TRADING_ALLOWED=0 and AUTO_EXECUTE_TRADES=0. Readiness work does
not authorize real orders or LIVE enablement.

The local launcher must verify ownership before stopping System3 processes,
recheck ports and process exit, fail on unknown port owners, start only
required local components, and expose startup failures honestly. Never kill
all laptop processes or unrelated port owners.
