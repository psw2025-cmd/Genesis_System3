# Gmail agent/GitHub mail digest (merged 2026-08-26T19:50:00Z)

Authority: Gmail is transport only (RUHI). Durable state = GitHub + Cloud.

## Access
- Probe: `gmail_api` **HAVE** (`ACCESS_PROBE_RESULT.md`)
- Full-verify pull: `reports/latest/full_cross_verify_20260826_193000/gmail_system3_threads.json` (25 messages, 14d query)
- Continuous MRI tick: `reports/latest/mri_watch/gmail_latest.json` (15 msgs, 7d query)
- Plan: `docs/handoffs/MRI_GMAIL_SCHEDULER_5MIN_CONTROL_PLAN.md`

## Material System3 follow-ups from mail (this cycle)

1. **DONE by agent:** ChatGPT + human mail demanded ruleset restore of `BLOCKING - priority workflows only` — ruleset **21581518** now has **6** required contexts (`reports/latest/full_cross_verify_20260826_193000/ruleset_21581518.json`).
2. **WATCH:** repeated Workflow Priority Guard / CodeQL failure mails on main tip — FORENSIC job hit GitHub Actions **API rate limit 403** (not a reason to remove Priority Guard).
3. **OPEN:** RHUI acceptance remains fail-closed; semantic UI + business artifact dates + auto_gates.
4. GitHub push noise on side branches (`cursor/apply-system3-0021-*`) — non-main; ignore for serving PASS.

## This MRI tick
- Live severity: **WARN** (scheduler HEALTHY + business_readiness PARTIAL overnight)
- Broker AUTH_OK; LIVE OFF; no IAM/redeploy
- Mail classes mapped into `reports/latest/mri_watch/CHECKLIST.md`

## Non-goals honored
- No Actions `schedule:`; no LIVE; no secret paste

## Other
- Claude/agent PAT push issues remain historical access theme — not blocking this loop.