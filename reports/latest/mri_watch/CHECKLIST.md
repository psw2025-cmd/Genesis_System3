# MRI Gmail+Scheduler watch checklist

Updated UTC: `2026-08-26T22:09:10.660470Z`

| id | pri | status | owner | title | proof |
|---|---|---|---|---|---|
| MRI-TRUTH-001 | P0 | **DONE** | AGENT | Session tick truth poll completed | `reports/latest/mri_watch/LATEST.json` |
| MRI-SCHED-001 | P0 | **WATCH** | AGENT | Scheduler business_readiness=PARTIAL | `https://genesis-system3-web-doq2wplepa-el.a.run.app/api/sche` |
| MRI-TOK-001 | P0 | **WATCH** | AGENT | Token hours_remaining=22.52 | `https://genesis-system3-web-doq2wplepa-el.a.run.app/api/brok` |
| MRI-GATES-001 | P0 | **OPEN** | AGENT | Gates 2/7 ??? LIVE stays OFF | `https://genesis-system3-web-doq2wplepa-el.a.run.app/api/auto` |
| MRI-LAG-001 | P1 | **WATCH** | AGENT | Serving SHA fb4772f9d52b ??? classify lag; no blind redeploy | `reports/latest/repo_path_audit/cloud_github_vs_laptop.json` |
| MRI-GMAIL-001 | P1 | **DONE** | AGENT | Gmail classified count=15 | `reports/latest/mri_watch/gmail_latest.json` |
| MRI-LOOP-001 | P0 | **OPEN** | HUMAN | Ensure 5-min recurrence (Task Scheduler or --loop) | `LATEST.json age < 10 minutes` |
| MRI-OTHER-1a03fc33 | P1 | **WATCH** | AGENT | [Task Update] RHUI V2 Claude Coordination: GCP proof blocked while GitHub safegu | `reports/latest/mri_watch/gmail_latest.json` |
| MRI-OTHER-1a03fc17 | P1 | **WATCH** | AGENT | [Task Update] RHUI V2 Genesis Controller: Stop local watcher and review PR block | `reports/latest/mri_watch/gmail_latest.json` |
| MRI-GH-1a03fc0c | P1 | **WATCH** | AGENT | System3: stop non-authoritative local watcher; PR #374 blocked | `reports/latest/mri_watch/gmail_latest.json` |
| MRI-OTHER-1a03fbcd | P1 | **WATCH** | AGENT | [RESOLVED - No severity] Genesis System3 /api/healthz failed | `reports/latest/mri_watch/gmail_latest.json` |
| MRI-OTHER-1a03fbbf | P1 | **WATCH** | AGENT | [ALERT - No severity] Genesis System3 /api/healthz failed | `reports/latest/mri_watch/gmail_latest.json` |
| MRI-SCHED-1a03fb53 | P0 | **WATCH** | AGENT | [psw2025-cmd/Genesis_System3] 43584e: docs(mri): Gmail+Scheduler 5-min continuou | `reports/latest/mri_watch/gmail_latest.json` |
| MRI-SCHED-1a03fb53 | P0 | **WATCH** | AGENT | [psw2025-cmd/Genesis_System3] | `reports/latest/mri_watch/gmail_latest.json` |
| MRI-OTHER-1a03fb45 | P1 | **WATCH** | AGENT | Re: [psw2025-cmd/Genesis_System3] fix: apply System3 consolidated patch 0021 (T9 | `reports/latest/mri_watch/gmail_latest.json` |
