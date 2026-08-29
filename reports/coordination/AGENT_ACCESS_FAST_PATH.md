# Agent access — fastest unblock options (2026-08-26)

Authority: RUHI cloud-only. Gmail = transport; GitHub #188 + this CSV = durable truth.

## Live truth (now)

| Field | Value |
|---|---|
| GitHub main | `8b7f8420` (#360) |
| Serving | `dea6a8fe` (#262) — 1 commit behind |
| Broker | AUTH_OK v319 ~2h · LIVE OFF |
| QC bug | `/api/health` qc=PASS but `/api/state` qc=NOT_READY → **#361 fixes** |
| Auto Deploy | Recent main merges **FAIL** — deploy path not green |

## Priority agents: Cursor · Claude · ChatGPT · Codex · Perplexity · Gemini

| Agent | What it needs | User action (max access, no token paste) | Agent can do |
|---|---|---|---|
| **Cursor Cloud** | GitHub App on `Genesis_System3` | [Cursor Integrations → GitHub → select repo](https://cursor.com/dashboard) → start Cloud Agent | Code/PR/CI once connected |
| **Claude Code/CLI** | `gh auth` + repo write | Re-auth after PAT regenerate; org allow push | Local/cloud CLI from primary clone |
| **ChatGPT / Codex** | GitHub connector or PAT read | Enable repo read; use #188 bus for writes | Research + task updates via mail/issue |
| **Perplexity** | Read-only GitHub + live URLs | Share public deploy_info + issue links only | Forensic read; no deploy |
| **Gemini Spark** | MCP server URL (not `/ui`) | Do **not** use dashboard URL; needs MCP endpoint if ever added | N/A until MCP deployed |

## Fastest paths (ranked)

### OPT-A — ~2–6h (recommended)
1. **You:** Cursor → GitHub App → `Genesis_System3` → new Cloud Agent  
2. **You:** Mark **#361** ready → merge (all CI green)  
3. **Agent:** MRI Auto Deploy failure → one exact-SHA deploy  
4. **Proof:** `/api/deploy_info` == main; `/api/health` + `/api/state` qc aligned; browser snap  

### OPT-B — parallel UI (~same day after deploy)
1. Agent opens OPT-A1 UI PR from **origin/main** worktree (not laptop fix branch)  
2. You approve merge → deploy → re-snap vs Dhan  
3. **Do not close #188** until serving SHA proof  

### OPT-C — one-time access pack (~15 min you)
1. GitHub org: confirm `psw2025-cmd` agents can push via App or fine-grained PAT (contents+actions read, PR write)  
2. Re-issue tokens after **PAT regenerated** mail  
3. **No** webhooks, **no** token paste in chat, **no** LIVE enable  

## Hard bans (do not)

- Enable LIVE trading  
- Paste tokens / add GitHub webhooks for access  
- Enable SHA-only Actions yet  
- Loop Dhan rotation  
- Close #188 on CI-only  
- Treat stale ChatGPT mail about #361 as current  

## Files all agents must read first

1. `reports/coordination/GITHUB_ACTION_MAP_STATUS.csv`  
2. `reports/coordination/COMMAND_CENTER.md`  
3. `docs/RUHI_RULE_V2.md`  
4. Issue [#188](https://github.com/psw2025-cmd/Genesis_System3/issues/188) latest broadcast comment  

agent-id:cursor-composer · run-id:live-reconcile-20260826
