# RHUI V2.3 — Permanent Local-Laptop-Only Migration Directive

Effective when merged.

- GitHub current main = ONLY code authority.
- Authorized Windows laptop current-main runtime = ONLY execution/runtime authority.
- Google Drive = correlated evidence/backup transport.
- Gmail = notification transport.
- GCP and all Google Cloud services = retired architecture / cleanup debt only.
- Never deploy/recreate/use GCP to prove System3.
- Continuously find every GCP dependency/reference and either remove it, replace required capability locally, mark historical-only, or track external cleanup.
- Never delete a still-required capability before local replacement is proven.
- PAPER/analyzer only; LIVE=false; orders=false.

Canonical detailed rule: `docs/RUHI_RULE_V2.md`.
Migration tracker: `reports/coordination/GCP_TO_LOCAL_ERADICATION_TRACKER.md`.
Coordination bus: Issue #188.
