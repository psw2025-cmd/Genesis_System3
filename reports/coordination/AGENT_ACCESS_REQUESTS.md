# Secrets & access — max agent speed (2026-08-26)

**You provide once → all agents unblock. Never paste token values in chat.**

| # | Resource | Who needs it | Why | How to grant |
|---|---|---|---|---|
| 1 | **Cursor GitHub App** on `Genesis_System3` | Cursor Cloud Agent | Push/PR/CI without laptop | [cursor.com/dashboard](https://cursor.com/dashboard) → Integrations → GitHub → select repo |
| 2 | **GitHub fine-grained PAT** (regenerated) | Claude CLI, Codex, scripts | Push blocked since ~20th | Settings → Developer → PAT → contents+PR write → re-auth `gh auth login` on each agent host |
| 3 | **GitHub org/repo access** for `psw2025-cmd` | All agents | Same as ACTION mail | Apply settings from Gmail "ACTION: Genesis System3 agent access" |
| 4 | **RENDER_API_KEY** (optional) | Agent automation | Verify #179 Render OFF via API | render.com → Account → API Keys → store in GCP Secret Manager only |
| 5 | **SYSTEM3_CC_SIGNER_KEY** (optional) | CI policy mint | Signed ACCESS_POLICY | GCP Secret Manager + approver warghade2012@gmail.com |
| 6 | **Cursor billing / Bugbot quota** | Cloud Agent | Agent runs stop when quota hit | Cursor dashboard billing |
| 7 | **ChatGPT connector** | ChatGPT tasks | Read repo + post updates | ChatGPT → connect GitHub read |
| 8 | **Gemini Spark MCP** | Gemini | Custom app needs MCP URL not `/ui` | Deploy MCP server first (future) |
| 9 | **Perplexity** | Forensic read | Optional | Share public URLs only |
| 10 | **Gmail readonly+send** | Cursor coordination | ✅ Already OK | Token at private-config path |

**Already have (no action):** gcloud ADC, live Cloud Run HTTP, broker via Secret Manager (cloud rotator), gh CLI.

**Hard bans:** LIVE trading · token paste in chat · Dhan rotation loop · GitHub webhooks for access
