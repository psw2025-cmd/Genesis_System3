# Genesis System3 — Gemini Operating Contract

Read `AGENTS.md` and `docs/control_plane/LOCAL_LAPTOP_USER_DIRECTIVE_20260907.md` first.

Runtime: local Windows `http://127.0.0.1:8000`. GitHub `main` is code baseline, not local-runtime truth. GCP Cloud Run URLs are HISTORICAL_NON_AUTHORITY.

Safety: ANALYZE_MODE=1, LIVE_TRADING_ENABLED=0, SYSTEM3_LIVE_TRADING_ALLOWED=0, AUTO_EXECUTE_TRADES=0. No real orders. No secrets. No Claude-only ownership. Issue #188 is not a mandatory bus.

Current/live UI claims require a new local browser session after a recorded UTC start, plus same-session local APIs. `reports/latest/` is historical. Discover tabs dynamically; do not assume 22 tabs.
