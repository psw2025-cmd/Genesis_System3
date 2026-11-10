# Genesis System3 — Gemini operating contract

**Temporal marker:** `SYSTEM3_TEMPORAL_TRUTH_V1` — `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.
Active owner directive: `docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md`; read it and `AGENTS.md` first. September laptop-only instructions are historical.

GitHub exact approved main is code authority. Intended production is cloud-only GCP `system3-openalgo-safe` / `asia-south1`; currently no deployment certified. Laptop/mobile/Cloud Shell are optional control clients only, never required runtime or user-run command loop.

Broker authority: Dhan. Retired Render and Angel-era hosting/instructions are historical and non-authoritative for System3.

Current owner consent: autonomous GitHub fixes, tests, CI and read-only GCP verification ONLY. Never deploy, trigger a billable cloud build or mutate Cloud Run/Scheduler/IAM/secrets/billing/artifacts without separate explicit approval. Do not introduce unapproved automatic deployment.

Permanent PAPER/ANALYZE locks: `ANALYZE_MODE=1`, `PAPER_MODE=1`, `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`, `LIVE_ORDER_AUTHORITY=0`. No real orders, no order-shaped production tests, no broker secret payloads or service-account JSON keys.

A past CI check, image tag, HTTP 200 or old Cloud Run URL is historical until independently re-observed. Use fresh exact-deployed-SHA cloud API/browser/broker evidence for runtime claims. No model is sole controller; Issue #188 is context, not a substitute for proof.
