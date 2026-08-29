# Genesis System3 — Agent Command Center (entrypoint)

**Overwrite-only.** Never create dated copies of these boards.

## Run (after every edit OR on demand)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_command_center_refresh.ps1
```

## Outputs (same paths every time)

| File | Purpose |
|---|---|
| `reports/coordination/COMMAND_CENTER.md` | Single dashboard for agents |
| `reports/coordination/ISSUES_ONLY.md` | Only OPEN/IN_PROGRESS/WATCH |
| `reports/coordination/ISSUES_MERMAID.md` | Micro-network + loops |
| `reports/coordination/TRACKING_CHECKLIST.md` | Full live checklist |
| `reports/coordination/AGENT_OPERATING_OPTIONS.xlsx` | Options + charts + levers |

## Priority rule

Excel sheet **`2_Options_Priority`**: lowest `priority_rank` + `user_involvement=LOW/NONE` first → **OPT-A1**.

## Schedules

- Hourly Windows task: pending tracker  
- Job scheduler: `pending_tracker_refresh`  
- **Post-edit:** always run command_center immediately (do not wait for schedule)
