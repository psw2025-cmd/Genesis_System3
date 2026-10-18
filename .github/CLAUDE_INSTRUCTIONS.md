# System3 — Claude / multi-agent operating notes

**Temporal marker:** `SYSTEM3_TEMPORAL_TRUTH_V1` — `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.
**Active owner directive:** `docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md`. Read it and `AGENTS.md` first. The September local-laptop directive and older GCP-exit clauses are historical, not active. Claude is not sole controller.

Intended System3 production: GCP `system3-openalgo-safe` / `asia-south1`; GitHub exact approved main is code authority. Laptop/Cloud Shell is optional control client, never production. Dhan is the broker authority. Retired Render and Angel-era hosting/instructions are historical and non-authoritative for System3.

**Current authorization:** GitHub repair/testing and read-only GCP checks ONLY. Request separate owner consent before any cloud/billing/IAM/secret/scheduler/deploy/image-push mutation. Do not make push-to-production automatic. Existing budget notifications are not hard caps.

Safety: `ANALYZE_MODE=1`, `PAPER_MODE=1`, `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`, `LIVE_ORDER_AUTHORITY=0`; no real broker orders, order-shaped real-broker tests, credential exposure or service-account JSON keys. Independent fresh evidence is mandatory before a production PASS claim.
