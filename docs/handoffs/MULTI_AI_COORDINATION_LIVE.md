# Genesis System3 — Multi-Agent Live Handoff

Updated: 2026-08-26 13:40 IST (cross-verify #3 main×cloud×laptop)
Rule target: `docs/RUHI_RULE_V2.md` (RHUI_RULE_V2.2)
Task authority: `reports/coordination/ruhi_task_ledger.csv` + `GITHUB_ACTION_MAP_STATUS.csv` + `RHUI_V2.2_GATE_BOARD.csv`
Primary P0 issue: #188
Lane lock: `reports/coordination/AGENT_LANE_LOCK.md`
Gmail protocol: read mail → post #188 + CSV (mail alone ≠ DONE)
RHUI V2.2 handoff: `docs/handoffs/RHUI_V2.2_MATERIAL_CHANGE.md`
Cross-verify SSOT: `reports/latest/repo_path_audit/cloud_github_vs_laptop.json`

## Live truth (Cloud only — 2026-08-26 13:40 IST)

| Field | Value |
|---|---|
| GitHub main | `afd28722…` (#365 Render lock — **docs/tools only**) |
| Serving (runtime) | `fb4772f9…` (#367) · `genesis-system3-web-00617-vif` @ 100% |
| Main vs serving | **DOCS_ONLY_LAG** (Auto Deploy path-filter skipped #365) — not failed deploy |
| Laptop | `146eb69…` / `fix/p0-188…` — NON-AUTH |
| Broker | AUTH_OK · LIVE OFF · orders OFF |
| 4/4 chains API | `required_symbols_ready=true` (recheck) |
| QC | health **NOT_READY** ↔ state **NOT_READY** |
| Scheduler | UNHEALTHY — `alert_severity=warning` ← **signals stale** |
| #367 effectiveness | PENDING (18:45 IST) |
| RHUI V2.2 | **NOT_ACCEPTED** · HUMAN_ACTION=NO |

## Agent lanes (no duplication) — RHUI V2.2 agreement

| Agent | Lane | Blocked from |
|---|---|---|
| **Cursor** | Live multi-verify, runbook/CSV/SSOT, scheduler attribution, #188 | Blind redeploy; token mint |
| **Claude** | Adversarial check of signals stale + post-18:45 #367 logs | New QC PR; laptop authority |
| **ChatGPT** | RHUI mail/ledger reconcile to V2.2 SSOT; keep NOT_ACCEPTED until gates green | Claiming ACCEPTED from visual 22/22 |
| **User** | None required for V2.2 blockers | — |

## Gmail coordination (RUHI)

1. Cursor reads Gmail (readonly OK) at session start  
2. Durable updates → #188 comment + `GITHUB_ACTION_MAP_STATUS.csv`  
3. Broadcast mirror → `GMAIL_AGENT_DIGEST.md` + optional mail to warghade2012@gmail.com  
4. Never claim DONE from mail without Cloud Run proof  

Access requests list: `reports/coordination/AGENT_ACCESS_REQUESTS.md`

## Laptop path lock (2026-08-25)

- **Canonical clone:** `C:\Users\ADMIN\Genesis_System3\Genesis_System3` — see `docs/handoffs/CANONICAL_LAPTOP_REPO_PATH.md` and `.cursor/rules/canonical-laptop-repo-path.mdc`
- **Do not use:** `C:\System3\Genesis_System3` (broken Git archive), parent `C:\Users\ADMIN\Genesis_System3` (stale), `C:\Genesis_System3` root (not a clone)
- Linked worktrees on C/D/E share the primary `.git`; prefer new worktrees on **E:** when C: free < 10 GB
- Verify snapshot: `reports/latest/repo_path_audit/verify_summary.txt`
- **Master automation runbook:** `docs/handoffs/SYSTEM3_MASTER_AUTOMATION_RUNBOOK.md` (access PASS 2026-08-25; RUHI + GitHub/GCP dual lanes)
- Access confirm: `reports/latest/access_capability/ACCESS_VERIFY_CONFIRM.md`

## Cursor 2026-08-22T10:34:40Z serving + named-gate recapture

- Docs-only GitHub main: `f9a0fe6ce4e66ca2012c08a645a6bad0887a60cb` (PR #319 merged 2026-08-22T10:33:07Z). Path index / B002 / ChatGPT CSVs are on `main`.
- Runtime-affecting SHA and serving SHA: `3661b61b4543a6f45b0ecf48a56cd0f765716881` via fresh GET `/api/deploy/info` at 2026-08-22T10:33:52Z.
- Cloud Run Auto Deploy `32567500703` promoted that SHA (step 12 success) then failed step 18. Named gate artifact uploaded (step 19): `system3-scheduler-health-gate-175` id `9474562356` digest `sha256:8697d030fbadda4baaea3be0a3af5424716f1f6c4f71666c287fc4f4e84976e0`.
- Gate: `transport_class=OK`, `failed_predicates=["observability.alert_severity_none"]`. Collector `genesis-system3-scheduler-collector-47n7j` was `prior_succeeded_execution`.
- Next owner is ChatGPT for RUHI-022: `*/5` vs `30 * * * *`. Cursor will not change `scheduler_contract.py` or Cloud Scheduler.
- Do not merge #286. Do not edit `.cursor/rules/governance-watchdog.mdc` (PR #317). Do not treat this failed deploy event as Dhan-verifier trigger.

## Cursor 2026-08-22T10:25:00Z GitHub path lock

Gmail is now available to Cursor and is used as a **mirror only**. Durable paths ChatGPT must read:

- `docs/handoffs/CURSOR_TO_CHATGPT_PATH_INDEX.md`
- `docs/handoffs/RUHI_B002_CURSOR_STATUS.md`
- `reports/coordination/ruhi_task_ledger.csv`
- `docs/RUHI_RULE_V2.md`

PR #318 is merged as `3661b61b4543a6f45b0ecf48a56cd0f765716881`. Serving SHA for that commit was later recaptured at 2026-08-22T10:33:52Z.

## Cursor 2026-08-22T10:16:10Z recapture

- Current GitHub main SHA: `d3119d669b7bcb871c8dc7b94eabcc44363f8e65` (PR #316 merge)
- Fresh `/api/deploy/info` serving SHA matches that exact main SHA
- Broker API this session: `connected=true`, secret version metadata `298`, LIVE=false, orders=false. This is not 4/4 chain acceptance.
- Scheduler health this session: HTTP 200, `healthy=false`, `alert_severity=critical`, reason `scheduler contract mismatch: genesis-system3-dhan-token-rotate-daily`
- Live rotate-daily schedule is `*/5 * * * *` Asia/Kolkata; `dashboard/backend/scheduler_contract.py` still expects `30 * * * *`. ChatGPT owns that contradiction; Cursor did not change the contract.
- Cursor lane: PR #318 scheduler-health named gate. Do not merge stale PR #286.

## Current verified shared baseline

- Repository: `psw2025-cmd/Genesis_System3`
- Current GitHub main SHA at this Cursor recapture: `d3119d669b7bcb871c8dc7b94eabcc44363f8e65`
- Historical handoff-creation SHA (2026-08-20): `99e36562856acce545dcf912860c389008b00306`
- PR #299 is merged and its code has been reported as serving by the latest Cursor Issue #188 loop.
- Latest Cursor loop also reports broker `connected=false`; therefore production is NOT accepted even though exact-main serving is aligned.
- LIVE trading and orders remain disabled.
- Claude has adopted the coordination concept and reports several prepared patches/tools, but some remain in Claude-local paths and are not authoritative until landed/rebased on current main.
- Cursor reported local permanent rule/handoff paths, but those paths were not present on GitHub main when this handoff was created. This PR fixes that durability gap.

## Why RUHI v2 is required

Existing emails contain useful technical findings but do not enforce a measurable delivery contract. The user cannot easily see:

- which exact tasks were promised previously;
- whether those tasks were truly completed;
- what proof class was used;
- which tasks remain blocked and why;
- which exact tasks each agent commits to next.

The rolling CSV ledger fixes this by making task IDs, owner, status, evidence, dependencies and next actions durable and machine-readable.

## Batch B001 execution order

### Lane A — Production/Broker/UI (Cursor primary)

1. RUHI-004 exact-main vs serving recapture.
2. RUHI-005 safe broker recovery/root cause.
3. RUHI-006 first post-PR295 scheduled rotation proof at 07:30 IST.
4. RUHI-007 phase-correct semantic UI proof.
5. RUHI-008 all-tab production browser capture.
6. RUHI-017 full supported market-data/option coverage proof.
7. RUHI-018 true chain-age/freshness remediation.

### Lane B — Local-origin/Paper-trade forensic (Cursor primary)

1. RUHI-010 local history forensic for paper trades.
2. RUHI-011 local roots/branches/unpushed inventory.
3. RUHI-012 historical DB/report paper-record evidence.
4. RUHI-013 local → GitHub → GCP migration-loss diff.
5. RUHI-015 current paper persistence proof.
6. RUHI-016 production dashboard paper-row proof.

### Lane C — Independent forensic (Claude primary)

1. RUHI-014 current-main end-to-end paper pipeline trace.
2. RUHI-020 RC-3/T11 stale disabled-path proof cleanup/rebase handoff.
3. Cross-check RUHI-018 chain-age findings without duplicating Cursor implementation.
4. Convert any local-only Claude patch claim into a current-main-applicable micro-handoff with tests and exact files.

### Lane D — Control/acceptance (ChatGPT primary)

1. RUHI-001 canonical rule.
2. RUHI-002 rolling CSV ledger.
3. RUHI-003 durable live handoff.
4. RUHI-009 user-facing dashboard proof matrix after Cursor browser capture.
5. RUHI-019 current-main review/landing path for QC false-green if still present.
6. Reconcile contradictions between email, GitHub and live evidence before accepting any DONE state.

## Mandatory next-mail format

Every RUHI mail from every agent must include:

```text
RULE_VERSION=RUHI_RULE_V2
BATCH_ID=B001
CURRENT_MAIN_SHA=<sha>
SERVING_SHA=<sha or N/A>
MARKET_PHASE=<OPEN/CLOSED/PREOPEN/etc>

PREVIOUS_BATCH_COMMITMENT:
<task IDs promised last time>

PREVIOUS_BATCH_RESULT:
<each task ID = DONE/PARTIAL/BLOCKED/SUPERSEDED/NOT_STARTED>

COMPLETED_WITH_PROOF:
<task ID | exact acceptance met | proof URL/artifact | timestamp | serving SHA>

NOT_COMPLETED:
<task ID | reason | remaining acceptance>

BLOCKERS_OR_CONFUSION:
<task ID | exact blocker | owner needed | micro repro/handoff>

HANDOFF_REQUIRED:
<from -> to | task ID | exact files/commands/UI path/evidence required>

NEXT_BATCH_COMMITMENT:
<next highest-priority executable tasks; default 20, carry unfinished commitments forward>

METRICS:
TOTAL_KNOWN=<n>
DONE=<n>
PARTIAL=<n>
BLOCKED=<n>
OPEN_EXECUTABLE=<n>
PREVIOUS_BATCH_COMPLETION_PERCENT=<calculated>
FRESH_UI_PROOF_TASKS=<n>
REGRESSIONS_REOPENED=<n>

USER_ACTION_REQUIRED=<NONE or exact unavoidable action>
```

## Completion rule

For any user-visible task, `DONE` requires production dashboard/browser proof on the exact serving SHA. API/CI/source evidence can support diagnosis but cannot replace the UI acceptance proof.

For paper trading, the final proof chain must be visible end-to-end:

`market data → scanner/ranker → signal decision → analyzer/paper order → persisted paper record → production dashboard row → P&L/position update`

No live order may be required to prove this chain.

## User-facing progress target

The user should be able to read one RUHI status and answer immediately:

- What did each agent actually finish?
- Where is the proof?
- What failed?
- Who owns each blocker?
- What are the next exact tasks?
- Did the last mail's promised tasks really complete?

If an update cannot answer those questions, it is not a valid RUHI progress update.
