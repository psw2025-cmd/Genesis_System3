# Genesis System3 — Master Automation Runbook (MRI + RUHI)

**Marker:** `SYSTEM3_MASTER_AUTOMATION_RUNBOOK_V2026_08_27`
**Primary clone (laptop working copy only):** `C:\Users\ADMIN\Genesis_System3\Genesis_System3`
**Authority:** GitHub `main` + GCP `system3-openalgo-safe` live serving — never old laptop folders
**Coordination bus:** Issue [#188](https://github.com/psw2025-cmd/Genesis_System3/issues/188) + `docs/RUHI_RULE_V2.md`
**Live UI:** https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/
**Last upgraded:** 2026-08-27 01:10 IST (full cross-verify #4; ruleset Priority Guard restored)

> **Agent mandate:** Re-read `reports/coordination/COMMAND_CENTER.md` + `GITHUB_ACTION_MAP_STATUS.csv` + `TODO_CHECKLIST_FULL_VERIFY.md` **first**, then `docs/RUHI_RULE_V2.md`. Laptop is TEMP. **Any access/software blocker → tell user immediately.**

---

## 0A) Visible progress board (2026-08-27 01:10 IST) — full cross-verify #4 — DO NOT SKIP

**Evidence:** `reports/latest/repo_path_audit/cloud_github_vs_laptop.json` + `reports/latest/full_cross_verify_20260826_193000/`
**RHUI V2.2 SSOT:** `reports/coordination/RHUI_V2.2_GATE_BOARD.csv`
**Command center:** `reports/coordination/COMMAND_CENTER.md`
**TODO:** `reports/coordination/TODO_CHECKLIST_FULL_VERIFY.md`
**Protection:** ruleset `21581518` **active** with **6** required contexts (Priority Guard restored)
**Sibling plan (do not compete):** continuous 5-min Gmail+scheduler MRI → `docs/handoffs/MRI_GMAIL_SCHEDULER_5MIN_CONTROL_PLAN.md`

### Same-session live truth (Cloud + GitHub — NOT laptop)

| Item | Value |
|---|---|
| GitHub `origin/main` | `0d6955987115f88b710aca0f0f0dec68d23fa6bc` — **#371** tip (docs; includes #370/#369) |
| Serving (runtime) | `fb4772f9d52b67a31b55ee85aab8604e525bbad6` — **#367** · `genesis-system3-web-00617-vif` @ **100%** |
| Main vs serving | **DOCS/TEST/CI_ONLY_LAG** — **Do not redeploy** to equalize |
| Laptop HEAD (NON-AUTH) | primary clone OK; dirty feature branch ignored for PASS |
| Broker | `connected=true` · `AUTH_OK` · LIVE **OFF** · orders **OFF** · secret v320 |
| `/api/health` | `status=ok` · PAPER · qc **NOT_READY** (`NO_QC_DATA`) |
| Scheduler health | **HEALTHY** transport · business **PARTIAL** (wrong-date rank/forecast/signals) |
| Signals | prior `92lf5` SUCCEEDED; `signals-daily` last attempt `2026-08-26T13:15Z` |
| Gates | **2/7** · trade_ready=false |
| Ruleset 21581518 | **6** contexts including `BLOCKING - priority workflows only` |
| Gmail intake | **DONE** — 25 threads in evidence dir |
| **Overall RHUI V2.2** | **NOT_ACCEPTED** — HUMAN_ACTION_REQUIRED=**NO** (ruleset fixed by agent) |

### Action taken this cycle

1. Truth gate + live API dump → `full_cross_verify_20260826_193000/`
2. Gmail System3 pull + ACCESS_PROBE
3. Restored ruleset sixth required check (Gmail/#188 correction)
4. Refreshed COMMAND_CENTER, gate board, map CSV, TRACKING, TODO checklist, RUHI §0, runbook §0A
5. Deferred continuous 5-min MRI control plan to sibling agent

### Do not (this cycle)

- Redeploy solely to catch docs/test tip `#371`
- Token mint / IAM weaken / LIVE / orders / force-push
- Claim RHUI ACCEPTED
- Invent a competing 5-min Gmail/scheduler plan (sibling owns it)

### Live mistakes logged 2026-08-27

| Mistake | Correction |
|---|---|
| Assert `HUMAN_ACTION_REQUIRED=NO` while ruleset omitted Priority Guard | Always re-GET ruleset contexts before no-action claims; restored sixth check |

### RHUI V2.2 root causes (unchanged domains)

1. **Semantic UI** — mounts ≠ API↔UI acceptance.
2. **Scheduler business** — wrong-date rank/forecast/signals artifacts.
3. **Auto gates** — 2/7; ML/expectancy/paper/tick/visibility still fail.

### P0 board (reconciled)

| ID | Item | Live status |
|---|---|---|
| P0-A | #188 UI parity | **OPEN** |
| P0-B | #179 / Render | **HARDENED** (#365) |
| P0-C | #228 deploy authority | **WATCH** — lag classified docs/test |
| RULE | Priority Guard ruleset | **DONE** this cycle |
| P0-E | Cursor GitHub App | optional later |

### Need from user

**None required for ruleset.** Optional later: Cursor GitHub App; triage stale open docs PRs.

### Agent next (no user wait)

1. Land this full-verify docs PR when CI green
2. Sibling: MRI 5-min Gmail+scheduler control plan
3. Runtime #188 OptionChain only via PR→CI→deploy→serving re-snap
4. Redeploy only on **runtime** path merges

---

## Hard bans (always)

- No IAM / WIF / LIVE / orders enable without explicit user mandate + proof  
- No blind redeploy solely for docs/test-only tip  
- Truth = GitHub main + live `/api/deploy_info` (not laptop)  
- Never work in `C:\System3\Genesis_System3`  

## Live priority URLs

See `docs/handoffs/LIVE_PRIORITY_URLS.md`.
