# Architecture decision log (append new numbered ADRs, never delete history)
**ADR-001 — 2026-10-18 — Cloud-only runtime.** System3 GCP system3-openalgo-safe is target; desktop only transient engineering control. Supersedes laptop-only historical #462.
**ADR-002 — 2026-10-18 — Owner deployment boundary.** GitHub coding/testing/read-only GCP permitted; billable infrastructure and production mutations require separate scoped approval. No push-to-deploy.
**ADR-003 — 2026-10-18 — Proof identity.** A committed receipt is only an expected-source hint; production PASS requires independently retrieved start/end actual serving SHA, immutable digest and live UI/API semantics. Never assume current main equals deployed SHA.
**ADR-004 — 2026-10-18 — Evidence truth.** Four verdicts PASS/FAIL/BLOCKED/UNKNOWN. Code flags cannot establish independent broker real_orders=0. Historical evidence stays historical. EVIDENCE.ndjson append-only.
