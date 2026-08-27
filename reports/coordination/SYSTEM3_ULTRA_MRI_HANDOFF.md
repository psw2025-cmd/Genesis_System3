# System3 Ultra MRI handoff

- Owner: any capable System3 controller; no dependency on Cursor.
- Branch: `ops/system3-ultra-mri-control-plane`.
- Purpose: one reusable GitHub->GCP WIF capability scan and production proof entry point.
- Canonical workflow: `.github/workflows/system3-ultra-mri.yml`.
- Scanner: `scripts/system3_ultra_mri.py`.
- Authority doc: `docs/authority/SYSTEM3_ULTRA_MRI_CONTROL_PLANE.md`.
- Required artifact: `system3-ultra-mri-<run_number>` containing `CAPABILITY_MATRIX.csv` and `FINAL_VERDICT.*` plus canonical browser proof when available.
- `ACCESS_CERTIFIED=false` is an immediate agent-owned access-resolution/takeover event, not a status-only report.
- No raw secret payloads, IAM widening, token mint, LIVE trading or order actions are part of the scanner.
