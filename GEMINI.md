# Genesis System3 — Gemini operating contract

Active owner directive: `docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md`; read it and `AGENTS.md` first. The old September laptop-only directive is historical, not operative.

GitHub exact approved main is code authority. Intended production is cloud-only GCP `system3-openalgo-safe` / `asia-south1`. Laptop/mobile/Cloud Shell are optional control clients only. No local System3 runtime or user-run command loop.

Current owner consent: autonomous GitHub fixes, tests, CI, and read-only GCP verification only. Never deploy, trigger a billable cloud build, mutate Cloud Run/Scheduler/IAM/secrets/billing or enable automatic deployment absent separate explicit approval. Preserve PAPER/ANALYZE: `ANALYZE_MODE=1`, `PAPER_MODE=1`, `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`, `LIVE_ORDER_AUTHORITY=0`. No real orders or secret payloads.

Fresh exact-deployed-SHA cloud API/browser/broker evidence is required for runtime claims. A past CI check, image tag, HTTP response or old Cloud Run URL is historical until independently re-observed. No one model is sole controller. Issue #188 is context, not a substitute for fresh proof.
