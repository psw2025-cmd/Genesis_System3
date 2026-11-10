# COMMAND CENTER (overwrite — single source)

**Do not re-run ad-hoc curl/probe spam.** Refresh this file instead.

```powershell
# After ANY edit OR anytime (idempotent):
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_command_center_refresh.ps1
```

## Access / token metadata

| Field | Value |
|---|---|
| policy_id | `ACC-POL-CC-20260825` |
| policy_version | `1.0.0` |
| signature_status | `UNSIGNED_PENDING_VAULT` |
| signed_by | `agent-id:cursor-composer` |
| last_run_id | `local-20260829T095803Z` |
| token_id | `dryrun-local-20260829T095803Z` |
| token_ttl | `0s-mint-denied` |
| mint_status | `DENIED until signature_status=VERIFIED` |
| smoke_passed | `False` |
| last_audit_entry_id | `aud-e927287e74b6` |
| notify_channel | `issue:#188` |
| approver_email | `warghade2012@gmail.com` |

## Live snapshot

| Field | Value |
|---|---|
| UTC | 2026-08-29T09:58:06.700212+00:00 |
| Serving | `01a4592f4c68c120a26b4fd955d1aff655b82e33` |
| Gates | 3/7 trade_ready=False |
| Broker | AUTH_OK v323 |
| Scheduler healthy | True |
| LIVE | False |
| OPEN / IN_PROGRESS / DONE | 21 / 6 / 3 |
| P0 active | 17 |

## Open these artifacts (always same paths)

| Artifact | Path |
|---|---|
| Issues only | `reports/coordination/ISSUES_ONLY.md` |
| Mermaid network | `reports/coordination/ISSUES_MERMAID.md` |
| Full checklist | `reports/coordination/TRACKING_CHECKLIST.md` |
| Options Excel | `reports/coordination/AGENT_OPERATING_OPTIONS.xlsx` |
| Access policy | `reports/coordination/ACCESS_POLICY.yaml` |
| Audit log | `reports/coordination/AUDIT_LOG.jsonl` |
| Smoke last | `reports/coordination/SMOKE_TEST_LAST.json` |
| Catalog | `docs/handoffs/SESSION_ISSUES_MASTER.md` |
| Runbook | `docs/handoffs/SYSTEM3_MASTER_AUTOMATION_RUNBOOK.md` |

## First priority for any agent

1. Read `ISSUES_ONLY.md`  
2. Open Excel sheet `2_Options_Priority` → **OPT-A1**  
3. If local fixes pending → get user **commit+PR** then deploy proof  
4. After edit finish → **run this command_center immediately** (do not wait for hourly schedule)  
5. Re-snap UI; flip DONE only on serving SHA  

## User minimal involvement

Primary path + approve PR + LIVE OFF + optional Dhan confirm. Everything else agent-automated.
