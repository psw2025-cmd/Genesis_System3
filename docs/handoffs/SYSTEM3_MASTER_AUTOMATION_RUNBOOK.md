# Genesis System3 — Master Automation Runbook (MRI + RUHI)

**Marker:** `SYSTEM3_MASTER_AUTOMATION_RUNBOOK_V2026_08_27`  
**Primary clone (laptop working copy only):** `C:\Users\ADMIN\Genesis_System3\Genesis_System3`  
**Authority:** GitHub `main` + GCP `system3-openalgo-safe` live serving — never old laptop folders  
**Coordination bus:** Issue [#188](https://github.com/psw2025-cmd/Genesis_System3/issues/188) + `docs/RUHI_RULE_V2.md`  
**Live UI:** https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/  
**Last upgraded:** 2026-08-27 01:15 IST (MRI Gmail+Scheduler 5-min control plan + live re-verify)

> **Agent mandate:** Re-read `reports/coordination/COMMAND_CENTER.md` + `GITHUB_ACTION_MAP_STATUS.csv` + `AGENT_ACCESS_FAST_PATH.md` **first**, then `docs/RUHI_RULE_V2.md`. Laptop is TEMP. **Any access/software blocker → tell user immediately.**

---

## 0A) Visible progress board (2026-08-27 01:15 IST) — MRI Gmail+Scheduler control — DO NOT SKIP

**Evidence:** `reports/latest/mri_watch/LATEST.json` + `docs/handoffs/MRI_GMAIL_SCHEDULER_5MIN_CONTROL_PLAN.md` + `reports/latest/repo_path_audit/cloud_github_vs_laptop.json`  
**RHUI V2.2 SSOT:** `reports/coordination/RHUI_V2.2_GATE_BOARD.csv` + `RHUI_V2.2_Verification_Checklist.json`  
**Command center:** `reports/coordination/COMMAND_CENTER.md`  
**Sibling lane:** full cross-verify agent `4eeb08d0…` — do not fight; rebase docs carefully  

### Same-session live truth (Cloud + GitHub — NOT laptop)

| Item | Value |
|---|---|
| GitHub `origin/main` | `0d6955987115f88b710aca0f0f0dec68d23fa6bc` |
| Serving (runtime) | `fb4772f9d52b67a31b55ee85aab8604e525bbad6` · `genesis-system3-web` |
| Main vs serving | **DOCS_TEST_CI_ONLY_LAG** — **no blind redeploy** |
| Laptop HEAD (NON-AUTH) | `146eb69…` on `fix/p0-188…` — **ignore for PASS**; dirty tree present |
| Broker | `connected=true` · `AUTH_OK` · LIVE **OFF** · orders **OFF** · secret_v **320** · hours_remaining ~2.8 |
| `/api/system_health` | `status=ok` · QC token unknown / datasource UNKNOWN (pre-market) |
| `/api/state` | Market closed · mode PAPER · QC_FAIL WARN (NOT_READY) |
| Scheduler health | **HEALTHY** · `transport_healthy=true` · `contract_matched=true` · `business_readiness=PARTIAL` (rank/forecast/signals wrong-date overnight) · MRI tick **WARN** |
| Gates | **2/7** · `trade_ready=false` |
| Gmail MRI | **HAVE** · first continuous tick pulled **15** msgs → `reports/latest/mri_watch/gmail_latest.json` |
| **Overall RHUI V2.2** | **NOT_ACCEPTED** — HUMAN_ACTION_REQUIRED=**NO** for this MRI loop |

### Action taken this cycle

1. `git fetch` + record main / serving / laptop SHA+branch+toplevel  
2. Live dump: deploy_info, broker, system_health, state, scheduler/health, auto_gates  
3. Wrote **MRI Gmail+Scheduler 5-min Control Plan** + watcher script; first tick **WARN** (PARTIAL readiness only)  
4. **No** blind redeploy · **No** LIVE · **No** IAM/WIF  

### Do not (this cycle)

- Redeploy solely to catch docs/CI-only main tip  
- Token mint / IAM weaken / LIVE / orders  
- Add GitHub Actions `schedule:` (use Task Scheduler / `--loop` / GCP→`workflow_dispatch`)  
- Claim ACCEPTED / trade_ready from MRI tick alone  

### RHUI V2.2 root causes (unchanged domains)

1. **Gates 2/7** — expectancy / lifecycle / tick / option visibility / Spearman still collecting.  
2. **Scheduler business PARTIAL** — overnight artifact date lag; transport OK.  
3. **Serving lag** — docs/CI tip ahead of runtime SHA.

### P0 board (reconciled)

| ID | Item | Live status |
|---|---|---|
| P0-A | #188 UI parity | **OPEN** |
| P0-B | #179 / Render hosting | **HARDENED** on main (GCP-only) — serving still `fb4772f` |
| P0-C | #228 IAM | **LIKELY DONE** — do not reopen in MRI loop |
| P0-D | QC fail-closed | health/state NOT_READY pre-market — expected |
| P0-E | Cursor GitHub App | **PENDING USER** if Cloud Agent needed |
| P0-MRI | 5-min Gmail+Scheduler watch | **SCRIPT DONE** — recurrence via Task Scheduler / `--loop` |

### Need from user

**None required for MRI plan.** Optional: register Windows task (`reports/latest/mri_watch/RECURRENCE.md`).

### Agent next (no user wait)

1. Keep MRI watcher recurrence local (no Actions cron)  
2. Coordinate with sibling full-verify; merge docs carefully  
3. Re-GET scheduler after next weekday rank/forecast/signals  
4. Redeploy only when a **runtime** path under Auto Deploy filters merges to main  

User-visible pending list:

| File | Purpose |
|---|---|
| `reports/coordination/GITHUB_ACTION_MAP_STATUS.csv` | Live done/pending action map |
| `reports/coordination/COMMAND_CENTER.md` | One-page live board |
| `reports/coordination/RHUI_V2.2_GATE_BOARD.csv` | RHUI gates |
| `reports/latest/repo_path_audit/cloud_github_vs_laptop.json` | Cross-verify SSOT |

Optional later: RUHI board on live UI — **PEND-026**; Claude memory refresh — **PEND-027**; API key policy — **PEND-025**.

### Agent next (no user wait)

Paper persistence + signal file + chain UI columns (LTP%/Buildup/OI%/Vol%/Greeks) + ATM default + deploy lag + scheduler health.

### UI tab snaps (2026-08-25)

Folder: `reports/latest/ui_snaps_20260825/` (+ `INDEX.md`)

Captured: Trade Top CE, Equity CE (HDFCBANK), Paper (0 open), Multibagger (0 candidates), Positions (paper −1806 / 9 trades), Broker manual book (11 holdings + POWERGRID CE closed), Signals.

### SESSION ISSUES MASTER (read every session)

- **Live checklist (overwrite):** `reports/coordination/TRACKING_CHECKLIST.md` (+ `.json` + `session_issues_master.csv`)
- **Catalog/solutions:** `docs/handoffs/SESSION_ISSUES_MASTER.md`
- **Rule:** `.cursor/rules/session-issues-master.mdc`
- **Refresh:** `scripts/run_pending_tracker_refresh.ps1` / job `pending_tracker_refresh`
- **No dated duplicate tracking logs** — always replace canonical files
- **Loop:** implement → deploy → tracker refresh → re-snap → update statuses

---

## 0) Access confirmation (2026-08-25) — PASS

User grant transcript:

`reports/latest/access_capability/USER_GRANT_RUN_20260825_134144.log`

Probe after grant:

`reports/latest/access_capability/ACCESS_PROBE_RESULT.md` → **MISSING: (none)**

| Capability | Status |
|---|---|
| git / gh (psw2025-cmd, repo+workflow) | PASS |
| gcloud + ADC (`warghade2012@gmail.com`, project `system3-openalgo-safe`) | PASS |
| Cloud Run describe → live URL | PASS |
| Gmail API | PASS |
| Claude CLI 2.1.233 | PASS |
| Live `/api/deploy_info` + `/api/broker/status` + UI | PASS |

**Follow-up (non-blocking):** if ADC quota warning appears:

```powershell
gcloud auth application-default set-quota-project system3-openalgo-safe
```

**Permanent PATH (once, then restart Cursor/Claude):**

```powershell
[Environment]::SetEnvironmentVariable('Path', $env:Path + ';C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin', 'User')
```

Re-probe anytime:

```powershell
cd C:\Users\ADMIN\Genesis_System3\Genesis_System3
C:\Pritam_CV_Tier1_EPC\.venv-pr53\Scripts\python.exe .\scripts\system3_access_capability_probe.py
```

---

## 1) RUHI / RHUI cloud rule (always remind)

From `docs/RUHI_RULE_V2.md` (ACTIVE):

1. **Code truth** = GitHub `psw2025-cmd/Genesis_System3` `main` SHA  
2. **Runtime truth** = GCP project `system3-openalgo-safe` live serving SHA (`/api/deploy_info`)  
3. **Bus** = Issue #188 + `reports/coordination/ruhi_task_ledger.csv`  
4. Gmail = transport only; durable state must land back in GitHub  
5. Laptop repos/reports/tokens are **NON-AUTHORITATIVE**  
6. No invisible work — every batch needs PREVIOUS commitment → RESULT → NEXT commitment with proof  
7. UI DONE requires browser/URL proof on **exact serving SHA** (not CI alone)  
8. LIVE/orders stay OFF unless explicit human break-glass  
9. Prefer batches of ~20 real tasks with CSV tracking  

**Session start gate (mandatory):**

```text
git fetch origin
record origin/main SHA
GET /api/deploy_info → serving SHA
compare; if diverge, say so (deploy lag ≠ local PASS)
only then edit — only in primary clone or linked worktree
```

---

## 2) Hard bans (do not repeat)

| Ban | Why (proven) |
|---|---|
| Work in `C:\System3\Genesis_System3` | Git metadata broken (no HEAD/objects) |
| Work in parent `C:\Users\ADMIN\Genesis_System3` | Stale tip historically |
| Treat `C:\Genesis_System3` as clone | Overlay only (logs/worktrees) |
| Claim PASS from `reports/latest/` alone | Temporal truth is live URL |
| Treat all DH-906 as “rate limit / do not mint” | Live rotate logs: DH-906 + **Invalid Token** must authorize mint (PR #303) |
| Blame chain blank on UI only when broker 906 | Fix token/auth first |
| Parallel PowerShell `Add-Content` to same harness temp | Cursor wrapper lock races — serialize shells |
| Assume `gcloud` on PATH in Python/non-interactive | Need SDK bin: `C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin` |
| Soft-fail only rotator IAM, leave business-lane hard-fail | PR #300 pattern — soft-fail all least-privilege binds |
| After-hours `MARKET CLOSED` as semantic FAIL | False positive — session-open-only forbidden list |
| Deploy success = scheduler-health jq race ignored | Canary may fail after collector success — retry/diagnose health gate |
| Equity options without security-id map | Need instrument/security_id list (Dhan), not NIFTY-only assumptions |
| Trust Claude.ai / Cursor **project memory** as live truth | Memory can be weeks stale (Aug 16 paste vs Aug 25 live) — always cross-verify |
| Act on “never wait for approval / self take live trades / always highest profit” | Conflicts RUHI LIVE-OFF + proof gates + human break-glass |
| Use Claude cloud path `/home/claude/...` or Aug16 `gcp_runtime_lock` SHAs as current | Reject; use primary clone + live `/api/deploy_info` |
| Assume gcloud/Docker unavailable because Claude memory said so | False on primary laptop (access PASS); still no laptop token mint as authority |
| Use bounced Gmail `ps2025.cmd@gmail.com` | 550 5.1.1 — only `warghade2012@gmail.com` |
| Treat docs-only main tip as runtime serving lag requiring redeploy | #365 skipped Auto Deploy path-filter; keep last runtime SHA (cross-verify #3) |
| Claim “no GCP/dashboard access” without Live Proof Center | Use `reports/latest/live_proof_center/LATEST/` + PR #368 workflow (scheduled) |
| Treat pre-market 4/4 chain NOT READY as broker/token failure | Market-closed / pre-open capture must stay fail-closed; recheck after open (RHUI V2.2) |
| Treat deploy-workflow red as web deploy failure when only `observability.alert_severity_none` fails | Collector/transport can be OK; attribute workload (RHUI V2.2 → `genesis-system3-signals` stale) |
| Claim RHUI ACCEPTED from 22/22 visual tab mounts | Visual ≠ semantic API↔UI; keep NOT_ACCEPTED until semantic + scheduler + signals proof |
| Blind redeploy after exact SHA already on `00617-vif` @ 100% | Preserve revision; prove gates in continuous session |
| Blind token mint / IAM weaken / LIVE on for RHUI V2.2 blockers | No evidence supports it; HUMAN_ACTION_REQUIRED=NO |

### Live mistakes logged 2026-08-26 (RHUI V2.2)

| Mistake | Correction |
|---|---|
| Equating Auto Deploy red with failed Cloud Run promotion | Run 32923767070 promoted `fb4772f9…` → `00617-vif` @ 100%; red was scheduler severity predicate |
| Leaving prediction lane on first NSE BhavCopy 404 | #367 bounded retries (5× / 90s); effectiveness still pending scheduled run |
| Skipping same-session broker proof after control-plane fail | Market-open multi-verify re-captured AUTH_OK + 4/4 API ready |

---

## 3) Live Dhan ↔ System3 parity (HIGH PRIORITY — keep tracking)

**Full issue ledger (always update):** `reports/latest/dhan_parity/DHAN_LIVE_PARITY_ISSUES.md`  
**API snapshot:** `reports/latest/dhan_parity/DHAN_PARITY_LIVE_COMPARE.json`  
**RUHI:** §16 Dhan live market parity in `docs/RUHI_RULE_V2.md`

### Live findings 2026-08-25 (serving `719566d`, market open, broker OK)

| Pri | ID | Finding |
|---|---|---|
| P0 | P0-CHAIN-STALE | UI `/?tab=chain` = **DHAN EXPIRY SNAPSHOT**, `fetched=07:49Z` while clock ~09:09Z; still looks OK → false-green risk |
| P0 | P0-ATM-VIEW | Visible strikes **27050+** while spot **~24130** — not ATM-centered (looks like wrong chain) |
| P0 | P0-LTP-CHG | No **LTP Chg (%)** column (API has `change_percent`) |
| P0 | P0-BUILDUP | No **Buildup** column |
| P0 | P0-OI-VOL-PCT | No **OI chg (%)** / **Vol chg (%)** (absolute ChgOI/Vol only) |
| P0 | P0-GREEKS-TABLE | delta/gamma/theta/vega in API, absent from table |
| P0 | P0-DEPLOY-LAG | Serving `719566d` behind GitHub main `2c0b44a` |
| P1 | P1-EQ-SECURITY-ID | Equity options need Dhan security_id map (e.g. ANGEL ONE) |
| P1 | P1-HOLDINGS-FUNDS | `/api/holdings` + `/api/funds` → **404** vs Dhan portfolio |
| P1 | P1-CHARTS | `/api/charts/NIFTY` → **404** — no chart/graph parity |
| P1 | P1-EQ-TOP-CE | Top CE / equity scanner must match Dhan live ranks |

**Backend note:** `/api/chain/NIFTY` can return ATM-quality rows (LTP/chg%/OI/greeks) while **UI omits** Dhan columns and may show stale snapshot + deep OTM scroll.

**Agent rule:** No “chain ready / market match” PASS without same-session Dhan advancedoptionchain compare + ATM-centered LIVE badge. Missing columns = implement or label MISSING — never false-green.

Keep open:

- https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=chain  
- https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=broker  
- https://web.dhan.co/advancedoptionchain  
- https://web.dhan.co/index/positions · https://web.dhan.co/index/portfolio  
- Full list: `docs/handoffs/LIVE_PRIORITY_URLS.md`

---

## 4) Two permanent agent lanes

### Lane A — GitHub Control Agent (always on)

**Owns:** issues, PRs, Actions, workflows, branch protection signals, #188 bus posts.

Checklist each cycle:

1. `gh pr list --state open` + failing checks  
2. `gh run list --limit 10` (Auto Deploy, recovery, safety CI)  
3. Issue #188: claim surface, post RUHI STATUS when state changes  
4. `origin/main` vs live serving SHA delta → open/track deploy failure if lag  
5. Never merge without required green checks; never `--no-verify`  
6. Update ledger CSV rows DONE/PARTIAL/BLOCKED with proof links  

### Lane B — GCP MRI Agent (always on)

**Owns:** Cloud Run service/jobs, Scheduler, Secret Manager versions (metadata only), IAM denials, logs → full network blast radius → fix → re-verify.

MRI loop:

```text
symptom (UI/API)
  → serving SHA + revision
  → Cloud Run logs / job execution
  → Scheduler trigger vs job invoke
  → Secret version metadata (no token print)
  → IAM / WIF / setIamPolicy denials
  → upstream Dhan classification (901/906/429/…)
  → blast radius (web, workers, scheduler, proofs)
  → fix via PR → deploy → exact serving proof
  → broker + chain + scheduler health re-verify
```

Never mint tokens from laptop. Recovery = GitHub workflow / Cloud Run rotate job only.

---

## 5) Session automation checklist (PASS requires all checked)

Copy into status posts:

```text
[ ] Primary path = C:\Users\ADMIN\Genesis_System3\Genesis_System3 (or linked worktree)
[ ] Access probe MISSING=(none) OR gap explicitly owned
[ ] git fetch; origin/main SHA recorded
[ ] Live /api/deploy_info SHA recorded
[ ] Serving vs main delta explained if any
[ ] Broker status recorded (connected/class/secret_version) — no secrets printed
[ ] RUHI: PREVIOUS batch reconciled
[ ] Claim posted on #188 if implementing
[ ] PR + CI + (if runtime) Auto Deploy watched
[ ] Browser/UI proof on exact serving SHA for UI claims
[ ] LIVE/orders still OFF
[ ] If Claude/Cursor project memory used → cross-verify SHAs/gates/broker (see §9)
[ ] Refresh `reports/latest/pending_issues/PENDING_ISSUES_MASTER_*.csv` after live sweep
[ ] Runbook §0A progress board updated with OPEN/P0 counts
[ ] Runbook updated if new mistake/pattern found
```

---

## 6) Pending / historical work themes (track on #188 + ledger)

Do not treat this as a local TODO dump — reconcile against live GitHub/GCP each cycle:

| Theme | Notes |
|---|---|
| Serving SHA lag behind `main` | e.g. serving `719566d` while main advanced — diagnose Auto Deploy |
| Broker DH-906 / token mint classification | PR #303 merged; re-verify rotate job image includes fix |
| Scheduler health canary / contract mismatch | Named-gate / schedule contract ownership per #188 |
| Option chain parity vs Dhan (chg%, buildup, equity IDs) | Live Dhan contrast 2026-08-25 |
| Soft-fail job IAM on deploy | #300 pattern — keep least-privilege deploy green |
| After-hours semantic proof | MARKET CLOSED false positive fix |
| Paper-trade / analyzer proof visibility | User: long-standing paper proof gap — cloud proof only |
| Multi-agent progress CSV (~20/batch) | User mail 2026-08-20 practical progress rule |
| Disk / worktrees | Prefer E: when C: free < 10 GB |
| Claude.ai project memory vs live | Ingest + KEEP/REFRESH/REJECT — §9; evidence under `reports/latest/claude_memory_audit/` |
| **Master pending CSV (user-visible)** | `reports/latest/pending_issues/PENDING_ISSUES_MASTER_20260825.csv` — refresh after every live sweep |
| Prediction accuracy / paper profit gates | Live 2/7; Spearman latest_rho 0.30; expectancy negative — improve models + paper proof, not weaken gates |
| Holdings/funds/charts UI routes | Top-level 404 while broker nested funds/holdings OK — wire UI/API parity |
| Claude scheduled automations (daily audit / bug-fix / market watchdog) | Treat as helper loops; GitHub Actions + GCP Scheduler remain authority |
| Scheduler health UNHEALTHY | Live 2026-08-25 `transport_healthy=false` — MRI lane |
| Paper positions file missing + synthetic Feb P&L | Blocks UI paper truth + SYS3-BLK-008 |

---

## 7) Related authorities (do not replace)

1. `docs/RUHI_RULE_V2.md`  
2. `docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md`  
3. `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`  
4. `docs/handoffs/CANONICAL_LAPTOP_REPO_PATH.md`  
5. `docs/handoffs/LIVE_PRIORITY_URLS.md`  
6. `docs/handoffs/MULTI_AI_COORDINATION_LIVE.md`  
7. `.cursor/rules/canonical-laptop-repo-path.mdc`  
8. `scripts/system3_access_capability_probe.py`  
9. `scripts/claude_cli_access_bootstrap.md`  
10. `reports/latest/claude_memory_audit/CLAUDE_PROJECT_MEMORY_CROSS_VERIFY_20260825.md` (+ `.json`)  
11. `reports/latest/pending_issues/PENDING_ISSUES_MASTER_20260825.csv` (+ README + live sweep JSON)  
12. `docs/handoffs/SESSION_ISSUES_MASTER.md` (+ `reports/coordination/session_issues_master.csv`)

---

## 8) Continuous improvement rule

After every incident:

1. Add a **Hard ban** or **Live mistake** row here (with date + proof link).  
2. Add/adjust a checklist item that would have caught it.  
3. Post one-line RUHI STATUS on #188 pointing at the runbook diff.  
4. Prefer automation (probe/gate/test) over memory.

**First permanent task for every agent:** keep this runbook accurate, stricter, and shorter where possible — never let it go stale.

---

## 9) Claude.ai project memory — ingest, verify, cross-verify (mandatory)

**Why this section exists:** Claude project “System3” keeps long memory + scheduled jobs. User paste (2026-08-25) showed memory **Last updated Aug 16** mixed with durable goals. Agents must **ingest all of it**, then **classify**, never execute stale facts.

**Evidence (this cycle):**

- `reports/latest/claude_memory_audit/CLAUDE_PROJECT_MEMORY_CROSS_VERIFY_20260825.md`
- `reports/latest/claude_memory_audit/CLAUDE_PROJECT_MEMORY_CROSS_VERIFY_20260825.json`

### 9.1 Ingest checklist (every time memory/chat is pasted)

```text
[ ] Copy mandate / blockers / SHAs / secrets-metadata / schedules / principles into this audit folder (no secret values)
[ ] Record memory "Last updated" date vs today's gate compare
[ ] Compare memory GitHub SHA ↔ origin/main
[ ] Compare memory deployed SHA/revision ↔ /api/deploy_info + Cloud Run describe
[ ] Compare memory token secret versions ↔ broker/status token_proof (metadata only)
[ ] Hit /api/auto_gates + /api/ml/performance + chain/broker (do not trust timeout claims)
[ ] Classify each claim: KEEP | REFRESH | REJECT
[ ] Update Hard bans if a REJECT would have caused damage
[ ] Post one-line on #188 if classification changes operational priority
```

### 9.2 Durable mandate from Claude memory (KEEP — goals, not proof)

| Theme | Keep as goal |
|---|---|
| World-class India options/equity dashboard (Dhan) | Yes — UI/UX production grade, no placeholders |
| Raise **prediction accuracy** + paper P&L proof | Yes — via walk-forward, gates, not gate dilution |
| Fix all repo bugs; streaming (SSE/WS) over stale poll | Yes |
| Full chain CE/PE visibility + charts/Greeks/backtest/ML/paper tabs | Yes — UI proof on serving SHA |
| Self-healing monitor + IST job schedule + Gmail alerts | Yes — alert only `warghade2012@gmail.com` |
| Risk hard limits (₹5k / 2% SL / 3% TP / 1x / max 2) | Yes |
| Live trading OFF until **all** technical gates pass | Yes — currently **2/7** live |

### 9.3 Same-session cross-verify matrix (2026-08-25)

| Claude memory claim (Aug 16-ish) | Live truth (Aug 25 gate) | Verdict |
|---|---|---|
| GitHub SHA `a568591…` | `origin/main` = `2c0b44a…` | **REJECT** SHA |
| Deployed `a59beb8…` / rev `00199-tq5` | Serving `719566d…` / instance `00590-zab` | **REJECT** deploy identity |
| `dhan-access-token` **v45** | **v319**, `AUTH_OK`, connected | **REJECT** version |
| PRODUCTION BLOCKED trio (SHA + API key + SM mount) from `gcp_runtime_lock` | Different reality: deploy **lag** main→serving; broker OK; re-check API key separately | **REFRESH** blockers |
| `/api/auto_gates` + `/api/ml/performance` timeout 30s | Both **200 OK** | **REJECT** timeout claim |
| Gates **2/7** | **2/7** (`MODEL_ACCURACY_REPORT_PRESENT`, `EQUITY_FO_ELIGIBILITY_PROVEN`); `trade_ready=false` | **KEEP** (reconfirmed) |
| Spearman / expectancy remaining | Spearman latest_rho **0.30**; net expectancy **-196.14**; strategy quarantined | **KEEP** as work |
| Local clone `/home/claude/Genesis_System3` | Primary `C:\Users\ADMIN\Genesis_System3\Genesis_System3` | **REJECT** path |
| “gcloud/Docker unavailable; no deploy from agent” | Laptop **gcloud+ADC PASS**; still no laptop mint; deploy via GitHub→Cloud Build | **REJECT** capability myth |
| “Never wait for approval; self take trades; always highest gain” | RUHI: LIVE OFF + human break-glass for LIVE | **REJECT** as operating rule |
| Gmail: use `warghade2012@gmail.com`; never `ps2025.cmd@gmail.com` | Keep | **KEEP** |
| Safe mode: ANALYZE / LIVE off / SSE | Keep principle; re-read Cloud Run env | **KEEP** |
| Claude schedules: daily audit, bug-fix continuation, market-hours watchdog | Helper only; not GitHub/GCP truth | **REFRESH** |
| Attachments: `gcp_runtime_lock*.json`, setup logs, screenshots | Historical; useful for forensics only | **REFRESH** → archive, don’t execute |

### 9.4 Live gate detail to track (do not invent PASS)

From `/api/auto_gates` (serving session 2026-08-25):

| Gate | Pass |
|---|---|
| `ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS` | false (8 days recorded; latest ρ=0.30) |
| `POSITIVE_NET_EXPECTANCY_AFTER_COSTS` | false (net −196.14 / 9 trades) |
| `REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF` | false |
| `WEBSOCKET_TICK_HEALTH_PROVEN` | false |
| `MODEL_ACCURACY_REPORT_PRESENT` | true |
| `OPTION_STRIKE_VISIBILITY_PROVEN` | false |
| `EQUITY_FO_ELIGIBILITY_PROVEN` | true |

Open blockers include: `PROFIT_BLOCKER`, `SYS3-BLK-003`, `SYS3-BLK-005`, `SYS3-BLK-008`, `TICK_HEALTH_BLOCKER`.

### 9.5 How agents must use Claude memory going forward

1. **Ingest** every paste into `reports/latest/claude_memory_audit/` (dated).  
2. **Never** let memory override GitHub `main` + live `/api/deploy_info`.  
3. **KEEP** principles (UI truth, gates, risk, Gmail, streaming).  
4. **REFRESH** numbers (SHA, revision, secret version, timeouts, CI status).  
5. **REJECT** auto-live-trade / “always profit” / wrong paths / “no gcloud”.  
6. Progress prediction accuracy by improving models + paper proof **through gates**, not by bypassing them.  
7. Claude scheduled jobs may continue, but every claim still needs the §5 session checklist + UI proof.

---

## 10) Fix → re-snap → investigate loop (user mandate 2026-08-25)

Until `docs/handoffs/SESSION_ISSUES_MASTER.md` has no OPEN P0:

1. Read SESSION_ISSUES_MASTER first  
2. Implement highest P0 in primary clone  
3. PR → merge → Cloud Run deploy  
4. Re-snap affected UI tabs on **exact serving SHA**  
5. If still wrong → investigate root cause and repeat (do not stop after one attempt)  
6. Update issue statuses + §0A counts in the same change set  

Local laptop code without serving SHA match = **IN_PROGRESS**, never DONE.

---

## 11) Background tracking checklist (overwrite-only)

**Purpose:** Keep a single always-current pending board so every agent knows OPEN vs DONE without chat history.

| Path | Behavior |
|---|---|
| `reports/coordination/TRACKING_CHECKLIST.md` | Replaced every run |
| `reports/coordination/TRACKING_CHECKLIST.json` | Replaced every run |
| `reports/coordination/session_issues_master.csv` | Replaced every run |
| `reports/latest/tracking/TRACKING_CHECKLIST.*` | Mirror replace |

**Run:**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_pending_tracker_refresh.ps1
```

**Automation:**

- Job scheduler entry: `pending_tracker_refresh` in `config/system3_job_scheduler.json` (hourly)
- Optional Windows task: `scripts/register_pending_tracker_task.ps1`

**Ban:** Creating new dated `PENDING_*_YYYYMMDD` tracking files for routine refreshes (duplicates). Use overwrite-only paths above. Dated UI snap folders are proof archives, not the status board.

---

## 12) Command Center + Excel options (agent-first)

**One source (overwrite):** `reports/coordination/COMMAND_CENTER.md`  
**Excel:** `reports/coordination/AGENT_OPERATING_OPTIONS.xlsx`  
**Docs entry:** `docs/handoffs/AGENT_COMMAND_CENTER.md`

```powershell
# After EVERY edit (do not wait for hourly/2h schedule):
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_command_center_refresh.ps1
```

Sheets: `1_User_Actions`, `2_Options_Priority` (OPT-A1 first), `3_Pending_Live`, `4_UI_Tab_Impact`, `5_GCP_GitHub_Levers`, `6_Progress_Chart` (charts), `7_Failure_Playbook`, `8_MD_Upgrades`.

**Agent role:** read ISSUES_ONLY → pick OPT-A* → fix core → auto command_center → PR/deploy → re-snap. Stop repeating the same curl/probe commands.
