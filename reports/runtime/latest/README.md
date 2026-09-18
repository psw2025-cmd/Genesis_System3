# Runtime Latest Snapshots

Authority marker: `SYSTEM3_RUNTIME_LATEST_SNAPSHOT_CONTRACT_V1`

This directory contains **small sanitized latest-state summaries only** so external agents can inspect current laptop runtime truth from GitHub without committing raw live logs, databases, browser recordings, secrets, or high-frequency telemetry.

Expected files when implemented by the runtime/status publisher:

- `runtime_status.json`
- `runtime_status.md`
- `dashboard_semantic_summary.json`
- `scheduler_status.json`
- `latest_mri_summary.json`
- `latest_mri_summary.md`
- `gcp_exit_status.json` (temporary until full GCP closure)

Rules:

1. Raw live logs remain under `C:\Genesis_System3_Runtime\logs` and rotate locally.
2. These snapshots update only on material state changes or bounded checkpoints, not every tick/minute.
3. No secret/token/PIN/TOTP payloads.
4. No raw SQLite/DB, market-history dump, huge transcript, browser video, or screenshot collection.
5. `latest` is not historical authority. Material incidents/migration checkpoints are promoted to bounded evidence with manifest/checksum and referenced in Issue #188.
6. Replacing a tracked file does not erase Git history, so keep snapshots compact and update sparingly.
7. Generated values must come from measured runtime truth. Never create placeholder PASS data merely because a path is required.

Canonical operating rules: `docs/control_plane/SYSTEM3_LOCAL_LAPTOP_GITHUB_OPERATING_STANDARD.md`.
