# Agent lane lock — NO DUPLICATION (2026-08-26)

**Authority:** Cloud Run live + GitHub `origin/main`. Gmail = mirror only; durable = this file + #188 + CSV.

## Active agents this session

| Agent | Where running | Lane | DO NOT touch |
|---|---|---|---|
| **Cursor (composer)** | Primary clone + coordination | Deploy MRI, docs/CSV/runbook, UI PRs from `origin/main`, merge #361 when user orders | Claude QC dup fixes |
| **Claude (terminal)** | ⚠️ Started in banned `C:\System3\Genesis_System3` but worktree `gs3-claude-qc-fix` is OK | **STOP QC duplicate work** — use **PR #361** only | New PR for same `app.py` QC fix |
| **ChatGPT** | Mail/tasks | RHUI mail, ledger semantics | Runtime deploy |
| **Codex/Perplexity/Gemini** | Read-only unless connected | Forensic read, MCP when available | Deploy, token mint |

## Duplicate detected (2026-08-26 04:12 IST)

- **PR #361** (DRAFT, CI green): `fix(qc): fail closed on runtime and health QC status` — **canonical QC fix**
- **Claude worktree** `gs3-claude-qc-fix`: same files (`app.py`, `runtime_state_store.py`) — **do not open second PR**
- **Action:** Claude → abandon local QC PR attempt; review #361 only. Cursor → owns merge/deploy after user approval.

## Gmail coordination (RUHI)

Every agent run must:
1. Read last 15 GitHub/agent mails (Gmail readonly OK)
2. Post durable update to **#188** OR update `GITHUB_ACTION_MAP_STATUS.csv`
3. Never treat mail alone as DONE — cloud proof required

Digest file: `reports/coordination/GMAIL_AGENT_DIGEST.md`

## Live truth (refresh each run)

| Field | Value |
|---|---|
| main | `8b7f8420` |
| serving | `dea6a8fe` (1 behind) |
| broker | AUTH_OK v320 |
| QC bug | health PASS vs state NOT_READY → **#361** |

## Next deploy queue (single thread)

1. User merge **#361** → exact-SHA deploy
2. Cursor PR **UI live truth banner + OptionChain** (from main, not laptop fix branch)
3. Fix Auto Deploy FAIL on main

agent-id:cursor-composer · updated: 2026-08-26T04:12 IST
