# System3 — Claude / multi-agent operating notes

**Active owner directive:** `docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md`. Read it and `AGENTS.md` first. The local-laptop 2026-09-07 directive and older cloud-exit passages are historical, not active. This file does not grant Claude exclusive ownership.

Intended System3 production: GCP `system3-openalgo-safe` / `asia-south1`; GitHub exact approved main is code authority. Laptop/Cloud Shell is a temporary control client, never production. **Current authorization:** GitHub repair/testing and read-only GCP checks only. Request separate owner consent before cloud/billing/IAM/secret/scheduler/deploy/image-push mutation. No automatic push-to-production workflow without authorization.

Safety: `ANALYZE_MODE=1`, `PAPER_MODE=1`, `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`, `LIVE_ORDER_AUTHORITY=0`; no real broker order actions, credential exposure or service-account JSON keys. Independent, fresh runtime evidence required before any PASS claim.
