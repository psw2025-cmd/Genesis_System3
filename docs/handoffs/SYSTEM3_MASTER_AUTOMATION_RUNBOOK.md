# Genesis System3 â€” Master Automation Runbook (MRI + RUHI)

**Marker:** `SYSTEM3_MASTER_AUTOMATION_RUNBOOK_V2026_08_27`  
**Primary clone (laptop working copy only):** `C:\Users\ADMIN\Genesis_System3\Genesis_System3`  
**Authority:** GitHub `main` + GCP `system3-openalgo-safe` live serving â€” never old laptop folders  
**Coordination bus:** Issue [#188](https://github.com/psw2025-cmd/Genesis_System3/issues/188) + `docs/RUHI_RULE_V2.md`  
**Live UI:** https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/  
**Last upgraded:** 2026-08-27 00:05 IST (post-#369 merge + live proof; docs/test-only lag)

> **Agent mandate:** Re-read `reports/coordination/COMMAND_CENTER.md` + `GITHUB_ACTION_MAP_STATUS.csv` + `AGENT_ACCESS_FAST_PATH.md` **first**, then `docs/RUHI_RULE_V2.md`. Laptop is TEMP. **Any access/software blocker â†’ tell user immediately.**

---

## 0A) Visible progress board (2026-08-27 00:05 IST) â€” post-#369 live proof â€” DO NOT SKIP

**Evidence:** `reports/latest/repo_path_audit/cloud_github_vs_laptop.json` + `reports/latest/post369_live_proof_20260827_000506/`  
**RHUI V2.2 SSOT:** `reports/coordination/RHUI_V2.2_GATE_BOARD.csv` + `RHUI_V2.2_Verification_Checklist.json`  
**Command center:** `reports/coordination/COMMAND_CENTER.md`  
**Protection:** `main.protected=true` Â· ruleset `21581518` (`main-protection-fail-closed`) **active**

### Same-session live truth (Cloud + GitHub â€” NOT laptop)

| Item | Value |
|---|---|
| GitHub `origin/main` | `6cda50c3f00457baba897fcf7e9732693a8f1e3e` â€” **#369** squash (**test-only** CodeQL forensic redaction) |
| Serving (runtime) | `fb4772f9d52b67a31b55ee85aab8604e525bbad6` â€” **#367** Â· `genesis-system3-web-00617-vif` @ **100%** |
| Main vs serving | **DOCS/TEST_ONLY_LAG** â€” #369 adds only `tests/test_dhan_rotator_forensic_redaction.py`. **Do not redeploy** to equalize. |
| Laptop HEAD (NON-AUTH) | dirty primary clone â€” **ignore for PASS**; docs from clean worktree |
| Broker | `connected=true` Â· `AUTH_OK` Â· LIVE **OFF** Â· orders **OFF** Â· token secret v320 |
| `/api/health` | `status=ok` Â· PAPER Â· qc **NOT_READY** (`NO_QC_DATA`) |
| Scheduler health | **HEALTHY** Â· `alert_severity=none` Â· transport OK |
| Signals | `genesis-system3-signals-92lf5` **EXECUTION_SUCCEEDED** |
| Gates | incomplete â€” RHUI still open |
| **Overall RHUI V2.2** | **NOT_ACCEPTED** â€” HUMAN_ACTION_REQUIRED=**NO** |

### Action taken this cycle

1. Pre-merge gate #369 CLEAN â†’ squash-merge â†’ `6cda50c3f004`  
2. Confirmed `main.protected=true` + ruleset `21581518` active  
3. Live dump: deploy_info, broker/status, health, scheduler/health â†’ `reports/latest/post369_live_proof_20260827_000506/`  
4. Classified #369 as **test-only** â€” **no blind redeploy** of `genesis-system3-web-00617-vif`  
5. Updated runbook Â§0A, RUHI Â§0, COMMAND_CENTER, map CSV, SSOT JSON, #188  

### Do not (this cycle)

- Redeploy solely to catch docs/test tip `#369`  
- Token mint / IAM weaken / LIVE / orders  
- Claim ACCEPTED â€” RHUI remains NOT_ACCEPTED  

### RHUI V2.2 root causes (unchanged domains)

1. **Signals/ML** â€” `92lf5` succeeded; keep monitoring next cadence.  
2. **Scheduler** â€” transport HEALTHY; business readiness may still be PARTIAL.  
3. **QC / semantic UI** â€” health NOT_READY; RHUI gates incomplete.

### P0 board (reconciled)

| ID | Item | Live status |
|---|---|---|
| P0-A | #188 UI parity | **OPEN** |
| P0-B | #179 / Render hosting | **HARDENED** on main (#365) â€” serving still GCP `#367` |
| P0-C | #228 IAM | **LIKELY DONE** â€” no IAM changes this cycle |
| P0-D | #361 QC fail-closed | **MERGED earlier**; health still NOT_READY |
| P0-E | Cursor GitHub App | **PENDING USER** if Cloud Agent needed |
| PR-369 | CodeQL forensic test | **MERGED** `6cda50c3f004` â€” runtime unchanged |

### Need from user

**None for this cycle.** HUMAN_ACTION_REQUIRED=**NO**.

### Agent next (no user wait)

1. Land docs PR `docs/post-369-live-proof-20260827` when CI green  
2. Continue semantic 22-tab / RHUI gate work  
3. Redeploy only when a **runtime** path under Auto Deploy filters merges to main  

---

## Hard bans (always)

- No IAM / WIF / LIVE / orders enable without explicit user mandate + proof  
- No blind redeploy solely for docs/test-only tip  
- Truth = GitHub main + live `/api/deploy_info` (not laptop)  
- Never work in `C:\System3\Genesis_System3`  

## Live priority URLs

See `docs/handoffs/LIVE_PRIORITY_URLS.md`.
