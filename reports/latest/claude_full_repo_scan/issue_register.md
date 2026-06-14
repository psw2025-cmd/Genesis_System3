# Claude Full Repo Issue Register

- Generated UTC: `2026-06-14T11:41:13.967300+00:00`
- Total issues/findings: `4`

| Severity | Category | File | Issue |
|---|---|---|---|
| CRITICAL | safety_secrets | `` | Secret-style patterns found: 96. Review redacted report; rotate any real exposed credential. |
| MEDIUM | config_runtime | `` | localhost/live-mode references found: 3366. Review for dashboard/deploy/runtime leakage. |
| MEDIUM | repo_cleanup | `` | Duplicate/same-name candidates found: 138. Requires runtime authority before delete/archive. |
| LOW | code_debt | `` | TODO/FIXME/HACK markers found: 473. |