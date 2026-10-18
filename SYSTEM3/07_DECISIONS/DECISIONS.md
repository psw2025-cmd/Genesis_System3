# Architecture decision log (append new numbered ADRs, never delete history)
**ADR-001 — 2026-10-18 — Cloud-only runtime.** System3 GCP system3-openalgo-safe is target; desktop only transient engineering control. Supersedes laptop-only historical #462.
**ADR-002 — 2026-10-18 — Owner deployment boundary.** GitHub coding/testing/read-only GCP permitted; billable infrastructure and production mutations require separate scoped approval. No push-to-deploy.
**ADR-003 — 2026-10-18 — Proof identity.** A committed receipt is only an expected-source hint; production PASS requires independently retrieved start/end actual serving SHA, immutable digest and live UI/API semantics. Never assume current main equals deployed SHA.
**ADR-004 — 2026-10-18 — Evidence truth.** Four verdicts PASS/FAIL/BLOCKED/UNKNOWN. Code flags cannot establish independent broker real_orders=0. Historical evidence stays historical. EVIDENCE.ndjson append-only.

**ADR-005 — 2026-10-18 — Proof/approval separation.** Release-lineage file cannot authorize billable deployment and cannot mark production PASS; it only supplies a full expected source SHA for subsequent independent live proof. Without it, main UI workflow must exit BLOCKED quickly with a manifest, never skip the required production check. Separate owner consent controls any future cloud mutation.

**ADR-006 — 2026-10-18 — Sensitive proof output.** Never echo the full production manifest or unsanitized upstream/UI diagnostic strings in CI logs; allowlisted summaries and redaction tests are mandatory. An Advanced Security code-scanning FAIL blocks merge even when its enclosing Actions workflow is SUCCESS.
