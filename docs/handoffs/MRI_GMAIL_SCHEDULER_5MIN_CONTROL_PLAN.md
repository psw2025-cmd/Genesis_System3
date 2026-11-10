# Genesis_System3 — Continuous Gmail + Scheduler MRI Control Plan

**Marker:** `MRI_GMAIL_SCHEDULER_5MIN_CONTROL_PLAN_V2026_08_27`  
**Written:** 2026-08-27T01:12 IST (session live cross-verify)  
**Authority:** GitHub `origin/main` + live Cloud Run APIs — laptop is working copy only  
**Primary clone only:** `C:\Users\ADMIN\Genesis_System3\Genesis_System3`  
**Hard ban:** never work in `C:\System3\Genesis_System3`  
**Coordination:** Issue [#188](https://github.com/psw2025-cmd/Genesis_System3/issues/188)  
**Sibling lane:** full cross-verify agent `4eeb08d0-ea45-496c-adbb-25692e8d20ec` — do not fight; rebase/merge docs carefully  

**Mirror copy:** `reports/latest/mri_plan/MRI_GMAIL_SCHEDULER_5MIN_CONTROL_PLAN.md`  
**Watcher:** `scripts/system3_mri_gmail_scheduler_watch.py` → `reports/latest/mri_watch/`

---

## A. Objective / fail-closed principles

### Objective
Run a continuous MRI control loop (target cadence **every 5 minutes**) that:
1. Polls live System3 health surfaces (scheduler first, then deploy/broker/gates).
2. Triages System3 + Google Cloud Gmail alerts into a durable checklist.
3. Updates coordination artifacts and posts material deltas to #188.
4. Never invents PASS from laptop files alone.

### Fail-closed principles (non-negotiable)

| Rule | Meaning |
|---|---|
| No IAM / WIF edits | Diagnose identity/scheduler problems; do not weaken IAM or mint new WIF bindings in this loop |
| No LIVE / orders | `live_trading_enabled` must stay `false`; never place or enable live orders |
| Truth order | (1) GitHub `main` SHA (2) live `/api/deploy_info` git_sha (3) laptop HEAD is NON-AUTH |
| Primary clone only | `C:\Users\ADMIN\Genesis_System3\Genesis_System3` (+ linked worktrees of that `.git`) |
| Never `C:\System3\Genesis_System3` | Broken Git archive — no HEAD/objects |
| Never blind redeploy | Serving may lag `main` for docs/test/CI-only tips — classify lag; redeploy only for runtime path changes |
| Gmail = transport | Mail informs triage; durable state = GitHub + live APIs + runbook/coordination files |
| Actions `schedule:` banned | Recurrence via Windows Task Scheduler, local python loop, or GCP Cloud Scheduler → `workflow_dispatch` only |

### Session truth gate (every start / every material claim)

```text
1) git fetch origin
2) record: GitHub/origin/main SHA
3) record: live Cloud Run git_sha from /api/deploy_info
4) record: laptop HEAD + branch + toplevel path
5) only then edit — and only in primary clone / linked worktree
```

### Same-session truth snapshot (this plan write)

| Plane | Value |
|---|---|
| GitHub `origin/main` | `0d6955987115f88b710aca0f0f0dec68d23fa6bc` |
| Live serving | `fb4772f9d52b67a31b55ee85aab8604e525bbad6` (`genesis-system3-web`) |
| Lag class | **DOCS_TEST_CI_ONLY_LAG** — do **not** blind redeploy |
| Laptop HEAD (NON-AUTH) | `146eb69b…` on `fix/p0-188-bankex-paced-cache-20260824` — dirty tree |
| Toplevel | `C:\Users\ADMIN\Genesis_System3\Genesis_System3` |
| Broker | `connected=true` · `AUTH_OK` · LIVE **OFF** · orders **OFF** · secret_v **320** |
| Scheduler | `healthy=true` · `status=HEALTHY` · `business_readiness=PARTIAL` (artifact date lag overnight) · contract_matched |
| Gates | **2/7** · `trade_ready=false` · LIVE stays OFF |
| Ruleset | `main-protection-fail-closed` id `21581518` |
| Gmail token path | Present (private-config; never paste secrets in chat) |

---

## B. Sources under MRI (exact URLs / paths)

### B1. Live HTTP (poll every tick)

| ID | Purpose | URL |
|---|---|---|
| L-DEPLOY | Serving SHA / region / LIVE flag | https://genesis-system3-web-doq2wplepa-el.a.run.app/api/deploy_info |
| L-BROKER | AUTH + token proof (no values) | https://genesis-system3-web-doq2wplepa-el.a.run.app/api/broker/status |
| L-HEALTH | System health / QC | https://genesis-system3-web-doq2wplepa-el.a.run.app/api/system_health |
| L-STATE | Public state / market / alerts | https://genesis-system3-web-doq2wplepa-el.a.run.app/api/state |
| L-SCHED | Scheduler contract + jobs + artifacts | https://genesis-system3-web-doq2wplepa-el.a.run.app/api/scheduler/health?refresh=true |
| L-GATES | Auto gates board | https://genesis-system3-web-doq2wplepa-el.a.run.app/api/auto_gates |
| L-UI | Human UI | https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/ |
| L-UI-BROKER | Broker tab | https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=broker |

Full list: `docs/handoffs/LIVE_PRIORITY_URLS.md`

### B2. GCP (MRI read; presence / status only for secrets)

| Area | Console / resource |
|---|---|
| Project | `system3-openalgo-safe` · region `asia-south1` |
| Cloud Run service | https://console.cloud.google.com/run/detail/asia-south1/genesis-system3-web/metrics?project=system3-openalgo-safe |
| Jobs | `genesis-system3-forecast`, `rank`, `signals`, `validate`, `dhan-token-rotate`, `scheduler-collector` |
| Scheduler | https://console.cloud.google.com/cloudscheduler?project=system3-openalgo-safe |
| Logging | Cloud Run job logs for signals/forecast/rank/validate/rotate (severity + last execution) |
| Secret Manager | Presence / version metadata only — https://console.cloud.google.com/security/secret-manager?project=system3-openalgo-safe — **never log secret values** |

Expected scheduler contract (from live `/api/scheduler/health`): **9** resources · **6** ENABLED · **3** PAUSED · `contract_matched=true`.

### B3. GitHub

| Item | URL / note |
|---|---|
| Repo | https://github.com/psw2025-cmd/Genesis_System3 |
| `main` tip | https://github.com/psw2025-cmd/Genesis_System3/commits/main |
| #188 | https://github.com/psw2025-cmd/Genesis_System3/issues/188 |
| Actions | https://github.com/psw2025-cmd/Genesis_System3/actions |
| Auto Deploy | `.github/workflows/cloud-run-auto-deploy.yml` |
| Live Proof Center | `docs/handoffs/LIVE_PROOF_CENTER.md` + `reports/coordination/System3_LIVE_PROOF_CENTER.xlsx` |
| Ruleset | `main-protection-fail-closed` (`21581518`) — required contexts; direct push to `main` blocked → PR only |

### B4. Gmail (ALL System3 + Google Cloud related)

**Query (read-only):**

```text
(System3 OR Genesis_System3 OR genesis-system3 OR RHUI OR RHUI OR "issue #188"
 OR "Cloud Run" OR "Cloud Scheduler" OR "Workflow Priority Guard" OR CodeQL
 OR billing OR "security alert" OR uptime OR "Google Cloud"
 OR psw2025-cmd OR system3-openalgo-safe) newer_than:7d
```

**Classes to triage:** uptime / billing / security / Cloud Run / Scheduler alerts / Actions failures / token-rotate noise / ChatGPT-RUHI instructions.

**Credential (local only — never paste in chat):**  
`C:\Pritam_CV_Tier1_EPC\Piping-E3D-Job-Intelligence\private-config\gmail_token.json`  
Env override: `SYSTEM3_GMAIL_TOKEN_PATH`.

**Prior proof:** `reports/latest/full_cross_verify_20260826_193000/gmail_system3_threads.json`  
**Digest:** `reports/coordination/GMAIL_AGENT_DIGEST.md`

### B5. Local coordination files (update contract targets)

| File | Role |
|---|---|
| `docs/handoffs/SYSTEM3_MASTER_AUTOMATION_RUNBOOK.md` | §0A progress board |
| `docs/RUHI_RULE_V2.md` | Fail-closed rules |
| `docs/handoffs/MRI_GMAIL_SCHEDULER_5MIN_CONTROL_PLAN.md` | This plan |
| `reports/coordination/COMMAND_CENTER.md` | One-page board |
| `reports/coordination/TRACKING_CHECKLIST.md` (+ `.json`) | Live pending checklist |
| `reports/coordination/GITHUB_ACTION_MAP_STATUS.csv` | Action map |
| `reports/coordination/GMAIL_AGENT_DIGEST.md` | Mail triage mirror |
| `reports/coordination/RHUI_V2.2_GATE_BOARD.csv` | Gate SSOT |
| `reports/latest/repo_path_audit/cloud_github_vs_laptop.json` | Truth compare |
| `reports/latest/mri_watch/LATEST.json` | Last 5-min tick |
| `reports/latest/mri_watch/TICK_LOG.jsonl` | Append-only ticks |
| `reports/latest/mri_watch/CHECKLIST.csv` | Actions taken/needed |
| `reports/latest/mri_watch/CHECKLIST.md` | Human-readable checklist |
| `reports/latest/access_capability/ACCESS_PROBE_RESULT.md` | Capability HAVE/MISSING |

---

## C. Every-5-minute loop design

### C1. What to poll each tick (ordered)

1. **Truth skim:** `deploy_info.git_sha` vs cached `origin/main` (refresh main SHA at least hourly or on WARN/FAIL).
2. **Scheduler:** `/api/scheduler/health?refresh=true` — healthy, coverage.contract_matched, alert_severity, business_readiness, rotate last_attempt.
3. **Broker:** `/api/broker/status` — connected, auth_classification, hours_remaining, LIVE flags.
4. **Gates:** `/api/auto_gates` — gates_passing/total, trade_ready, open_blockers (summary only).
5. **Health/state (light):** `/api/system_health` status + QC; `/api/state` market + alert codes (truncate).
6. **Gmail (optional if token):** list ≤15 newest matching messages; classify; map to checklist IDs.
7. **Write:** `LATEST.json`, append `TICK_LOG.jsonl`, refresh `CHECKLIST.csv`/`.md`.
8. **Escalate if material:** update runbook §0A + COMMAND_CENTER + #188 comment (rate-limit: max 1 #188 comment / 30 min unless FAIL).

### C2. Decision tree

```text
OK
  criteria: sched healthy + contract_matched + broker AUTH_OK + LIVE off
            + deploy reachable + (gmail optional OK or BLOCKED-documented)
  actions: write LATEST.json severity=OK; append tick; no #188; no runbook churn

WARN
  criteria: business_readiness PARTIAL | token hours_remaining < 1.0
            | gates drop | artifact wrong-date overnight | Gmail Actions flaky
            | main↔serving lag grows but still docs/test/CI class
  actions: re-GET live endpoints once; update CHECKLIST WATCH rows;
           if still WARN after re-verify → touch COMMAND_CENTER + runbook §0A notes;
           #188 only if NEW vs last tick material_fingerprint

FAIL
  criteria: sched unhealthy OR transport_healthy=false OR contract_matched=false
            | broker not AUTH_OK | LIVE unexpectedly true | deploy_info unreachable
            | rotate job EXECUTION_FAILED | secret missing (presence check)
  actions: re-verify live immediately (2nd GET);
           update runbook §0A with OPEN/P0 counts;
           post #188 brief with evidence paths;
           NEVER blind redeploy; NEVER LIVE; NEVER IAM weaken
```

### C3. Exact actions matrix

| Severity | Re-verify live | Update §0A | Update CSVs/MD | #188 | Redeploy | LIVE/IAM |
|---|---|---|---|---|---|---|
| OK | no (single poll) | no | tick only | no | no | no |
| WARN | yes (once) | if persistent | yes WATCH | if material delta | no | no |
| FAIL | yes (twice) | **yes** | yes OPEN/P0 | **yes** | only if runtime SHA proof demands + human/agent deploy path | **never** |

### C4. Gmail triage → checklist mapping

| Mail class | Checklist ID pattern | Owner | Default severity |
|---|---|---|---|
| Cloud Scheduler miss / job fail | `MRI-SCHED-*` | AGENT | FAIL if live confirms |
| Cloud Run revision / crash | `MRI-RUN-*` | AGENT | WARN→FAIL after live |
| Billing / quota | `MRI-BILL-*` | HUMAN | WARN |
| Security / suspicious login | `MRI-SEC-*` | HUMAN | FAIL (notify only) |
| Uptime / monitoring | `MRI-UP-*` | AGENT | WARN until live OK |
| Actions / Priority Guard / CodeQL | `MRI-GH-*` | AGENT | WARN (rate-limit noise) |
| ChatGPT / RUHI instruction | `MRI-RUHI-*` | AGENT | write durable file + #188 |
| Token / Secret Manager | `MRI-TOK-*` | AGENT | WARN if hours_remaining low |

Gmail never alone flips PASS. Live APIs must confirm.

---

## D. Checklist schema

### Fields

| Field | Type | Notes |
|---|---|---|
| `id` | string | Stable e.g. `MRI-SCHED-001` |
| `priority` | `P0`/`P1`/`P2` | P0 = serving/auth/scheduler/LIVE safety |
| `title` | string | One line |
| `status` | `OPEN`/`WATCH`/`DONE`/`BLOCKED`/`N_A` | |
| `how_to` | string | Exact steps (no secrets) |
| `owner` | `AGENT`/`HUMAN` | |
| `proof_required` | string | URL or report path that must exist |
| `last_seen_utc` | ISO | |
| `source` | `live`/`gmail`/`github`/`gcp` | |
| `actions_taken` | string | What agent already did |

### Seed items (this session)

| id | pri | status | owner | title | proof_required |
|---|---|---|---|---|---|
| MRI-TRUTH-001 | P0 | DONE | AGENT | Session truth gate recorded | `reports/latest/repo_path_audit/cloud_github_vs_laptop.json` |
| MRI-SCHED-001 | P0 | WATCH | AGENT | Scheduler HEALTHY but business_readiness PARTIAL (artifact dates) | live `/api/scheduler/health` |
| MRI-TOK-001 | P0 | WATCH | AGENT | Token hours_remaining low overnight; rotate job ENABLED `*/5` | broker `token_proof.hours_remaining` |
| MRI-GATES-001 | P0 | OPEN | AGENT | Gates 2/7 — trade_ready false (expected; LIVE off) | `/api/auto_gates` |
| MRI-LAG-001 | P1 | WATCH | AGENT | main `0d69559` vs serving `fb4772f` — docs/CI lag; no blind redeploy | deploy_info + origin/main |
| MRI-GMAIL-001 | P1 | OPEN | AGENT | Continuous Gmail classify into MRI checklist | `reports/latest/mri_watch/gmail_latest.json` |
| MRI-LOOP-001 | P0 | OPEN | AGENT | Install 5-min recurrence (Task Scheduler / python loop) | `reports/latest/mri_watch/LATEST.json` fresh <10m |
| MRI-188-001 | P1 | OPEN | AGENT | Point #188 at this MRI plan | issue comment URL |

---

## E. Runbook update contract

When **live cross-verify changes** (new severity, SHA change, auth change, scheduler contract break):

| Artifact | Update rule |
|---|---|
| `docs/handoffs/SYSTEM3_MASTER_AUTOMATION_RUNBOOK.md` §0A | Replace same-session table: main SHA, serving SHA, lag class, broker, scheduler, gates, overall |
| `docs/RUHI_RULE_V2.md` | Only if rule text itself changes (rare) |
| `reports/coordination/COMMAND_CENTER.md` | Mirror §0A one-pager |
| `reports/coordination/TRACKING_CHECKLIST.md` (+ json/csv) | Refresh OPEN/WATCH/DONE from live |
| `reports/coordination/GITHUB_ACTION_MAP_STATUS.csv` | Mark MRI loop rows |
| `reports/coordination/GMAIL_AGENT_DIGEST.md` | Replace with latest mail triage summary |
| `reports/latest/repo_path_audit/cloud_github_vs_laptop.json` | Overwrite truth compare |
| `docs/handoffs/MRI_GMAIL_SCHEDULER_5MIN_CONTROL_PLAN.md` | Update §F DONE/PENDING + truth snapshot when plan semantics change |
| Issue #188 | Brief pointer / material FAIL only |

**PR rule:** ruleset blocks direct `main` push — open PR for docs changes; rebase if sibling agent landed first.

---

## F. What already DONE vs PENDING (re-verified live — not invented)

### DONE (proven this session or prior durable proof)

| Item | Proof |
|---|---|
| Access probe HAVE gmail/gh/gcloud/live | `ACCESS_PROBE_RESULT.md` 2026-08-27 01:00 IST |
| Gmail one-shot pull (14d, 25 msgs) | `gmail_system3_threads.json` |
| Ruleset restore 6 required contexts | ruleset `21581518` |
| Scheduler transport + contract matched | live `healthy=true`, `contract_matched=true` |
| Broker AUTH_OK, LIVE off | live broker JSON |
| Token rotate schedule ENABLED | `genesis-system3-dhan-token-rotate-daily` `*/5` Asia/Kolkata |
| Prior scheduler UNHEALTHY (PEND-002) cleared | TRACKING_CHECKLIST DONE |
| This MRI plan written | this file + `reports/latest/mri_plan/` mirror |

### PENDING / WATCH

| Item | Why |
|---|---|
| Continuous 5-min watcher recurrence | Script + task instructions this session; OS task may need local register |
| Gmail continuous classify | Wire into watcher (token present) |
| business_readiness PARTIAL | Overnight wrong-date artifacts — expect clear after next weekday rank/forecast/signals |
| Gates 2/7 | Structural RHUI blockers — not a 5-min flip |
| Serving lag behind main | Docs/CI-only — wait for runtime merge or intentional deploy |
| #188 MRI plan pointer | Post after plan write |
| RHUI V2.2 NOT_ACCEPTED | Sibling full-verify lane; do not claim ACCEPTED |
| Dirty laptop branch | NON-AUTH; do not use for PASS |

### Explicitly NOT done / do not claim

- Blind redeploy to erase docs lag  
- LIVE enable  
- IAM/WIF changes  
- Secret value reads  

---

## G. Human priority paths (rating 1–5)

| Rating | Path | Why |
|---|---|---|
| **5** | Keep LIVE off; do not paste secrets in chat | Safety |
| **5** | Keep Dhan web open for parity reference | https://web.dhan.co/ |
| **5** | Primary Cursor folder = `C:\Users\ADMIN\Genesis_System3\Genesis_System3` | Avoid broken archive |
| **4** | Read #188 + Live Proof Center when agent posts FAIL | Coordination |
| **4** | Approve PRs to `main` when MRI docs/runtime land | Ruleset |
| **3** | Optional: register Windows Task for 5-min watcher | Recurrence without Actions cron |
| **3** | Optional: Cursor GitHub App if Cloud Agent lane needed | P0-E |
| **2** | Billing/security Gmail that only human can resolve | Escalation |
| **1** | Cosmetic UI polish unrelated to MRI FAIL | Defer |

---

## H. Explicit non-goals

- Enabling LIVE trading or order placement  
- IAM policy edits, WIF pool changes, key minting  
- Adding GitHub Actions `schedule:` triggers (policy ban)  
- Blind Cloud Run redeploy to chase docs-only `main` tip  
- Working in `C:\System3\Genesis_System3` or other non-primary paths  
- Pasting OAuth client secrets / refresh tokens / access tokens into chat  
- Claiming RHUI ACCEPTED / trade_ready from this loop alone  
- Fighting sibling full-cross-verify agent; duplicate useless redeploys  
- Reading or dumping Secret Manager **values** (presence/version only)  
- Using Gmail as durable SSOT (mirror/transport only)

---

## I. Recurrence options (allowed)

### Preferred A — Windows Task Scheduler (local MRI laptop)

```powershell
cd C:\Users\ADMIN\Genesis_System3\Genesis_System3
# example: every 5 minutes
schtasks /Create /TN "System3_MRI_Gmail_Scheduler_Watch" /SC MINUTE /MO 5 /TR "C:\Python310\python.exe scripts\system3_mri_gmail_scheduler_watch.py" /F
```

### Preferred B — foreground / background python loop

```powershell
cd C:\Users\ADMIN\Genesis_System3\Genesis_System3
python scripts\system3_mri_gmail_scheduler_watch.py --loop --interval-sec 300
```

### Allowed C — GCP Cloud Scheduler → GitHub `workflow_dispatch`

Use existing dispatchable workflow (e.g. preflight) — **do not** add Actions `schedule:`.

### Forbidden

```yaml
on:
  schedule:
    - cron: "*/5 * * * *"   # PROHIBITED
```

---

## J. Implementation deliverables (this change set)

1. This plan (docs + reports mirror)  
2. `scripts/system3_mri_gmail_scheduler_watch.py`  
3. First tick outputs under `reports/latest/mri_watch/`  
4. Runbook §0A refresh from this session’s live verify  
5. #188 brief pointer  
6. PR to `main` for docs (no direct push)

---

**End of plan.**
