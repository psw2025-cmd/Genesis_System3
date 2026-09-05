# Evidence Index — 20260816T062501Z

## Authority pins

- GitHub main: `c763ecf048478842688373cf674eb56a7dc04aa9`
- Serving: `a48e7b3c7c086a21352f718355d1c12d4a48955b`
- UI: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui

## Request-scoped live

- Playwright 22-tab texts/screenshots: local scratch `reports/latest/full_cloud_ui_forensic_scratch/lane_a_ui/` (not committed as binaries)
- Live API captures: `supporting_lane_extracts/live_api__*`
- Chain summary: `supporting_lane_extracts/live_api__chains__summary_compact.json`

## GCP

- Service/jobs/scheduler/secrets metadata under `supporting_lane_extracts/lane_c_gcp__*`

## Source forensics (worktree `Genesis_System3_audit_main_c763ecf`)

- Lane B/D/E/F FINDINGS copied into supporting extracts

## GitHub Actions observed (main push)

- Full Cloud Audit failure: run 31929124559
- Frontend Browser Smoke failure: 31929124562
- Security Audit Evidence failure: 31929124573
- CodeQL success: 31929124551

## Safety

- LIVE=false, order_actions=false, secret_payload_exposed=false

## POST-RECOVERY RCA ADDENDUM (v257→v258) — appended 2026-08-16T07:45:00Z

- Does **not** overwrite original audit capture timestamps above.
- Addendum: `21_POST_RECOVERY_V257_V258` → `21_POST_RECOVERY_RCA_ADDENDUM_V257_V258.md`
- Machine pack: `supporting_lane_extracts/RCA_POST_RECOVERY_V257_V258.json`
- Scope: root-cause of early TOKEN_EXPIRED_OR_INVALID; authorities; 429 graph; H1–H8; preserve v258 connected LIVE=false.
- No functional code/deploy/mint/IAM mutation in this addendum.
