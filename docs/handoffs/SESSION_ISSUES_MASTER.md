# SESSION ISSUES MASTER — read every agent session BEFORE editing

**Marker:** `SYSTEM3_SESSION_ISSUES_MASTER_V2026_08_25`  
**Authority:** Live GitHub `main` + Cloud Run `/api/deploy_info` beat this file’s SHAs when they diverge — refresh SHAs in-session.  
**Primary clone:** `C:\Users\ADMIN\Genesis_System3\Genesis_System3`  

## Live status (overwrite-only — NO duplicate dated logs)

| File | Role |
|---|---|
| `reports/coordination/TRACKING_CHECKLIST.md` | **LIVE checklist** — replaced every tracker run |
| `reports/coordination/TRACKING_CHECKLIST.json` | Machine status + proofs |
| `reports/coordination/session_issues_master.csv` | CSV twin (overwrite) |
| `reports/latest/tracking/TRACKING_CHECKLIST.md` | Mirror of coordination (overwrite) |

**Refresh command:**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\ADMIN\Genesis_System3\Genesis_System3\scripts\run_pending_tracker_refresh.ps1
```

**Scheduler:** `config/system3_job_scheduler.json` job `pending_tracker_refresh` (hourly). Optional Windows task: `scripts/register_pending_tracker_task.ps1`.

**Hard rule:** Do **not** create `PENDING_*_YYYYMMDD.csv` / dated tracking logs for routine refreshes. Only replace the canonical files above.

This markdown file keeps **catalog + solutions**. Live OPEN/DONE counts always come from `TRACKING_CHECKLIST.md`.

**UI snaps (optional proof archive):** `reports/latest/ui_snaps_*/INDEX.md`  
**Runbook:** `docs/handoffs/SYSTEM3_MASTER_AUTOMATION_RUNBOOK.md` §0A + §10 + §11  

## Mandatory loop (never skip)

```text
1) Read TRACKING_CHECKLIST.md (live) + THIS catalog + runbook §0A
2) git fetch; record origin/main vs /api/deploy_info
3) Pick highest OPEN/IN_PROGRESS P0
4) Implement → PR → deploy → exact serving SHA
5) Re-run pending tracker (overwrite checklist)
6) Re-snap affected UI tabs
7) If still wrong → INVESTIGATE → fix again (do not mark DONE)
```

**PASS rule:** Issue is DONE only with browser/API proof on **exact serving SHA**. Local-only edits ≠ DONE.

**Hard bans:** LIVE orders OFF until gates 7/7; never dilute Spearman/expectancy; never work `C:\System3\Genesis_System3`.

---

## Full issue catalog (solutions — status is live in TRACKING_CHECKLIST)

| ID | Pri | Status | Title | Solution path | Verify by snap/API |
|---|---|---|---|---|---|
| PEND-001 | P0 | OPEN | Serving SHA lag (`719566d` behind `main`) | MRI Auto Deploy / Cloud Build | `/api/deploy_info` == `origin/main` |
| PEND-002 | P0 | OPEN | Scheduler health UNHEALTHY | MRI Scheduler→IAM→named gate | `/api/scheduler/health` healthy=true |
| PEND-003 | P1 | WATCH | Broker AUTH_OK (v319) | Watch rotate; no laptop mint | `/?tab=broker` Session OK |
| PEND-004 | P0 | IN_PROGRESS | Stale chain badge false-green | Age>60s → STALE; never LIVE/OK | `/?tab=chain` badge |
| PEND-005 | P0 | IN_PROGRESS | Default view not ATM | Default VISIBLE = ±10 ATM | chain scroll on ATM |
| PEND-006 | P0 | IN_PROGRESS | Missing LTP Chg % | Render `change_percent` | chain headers |
| PEND-007 | P0 | IN_PROGRESS | Missing Buildup | Price+OI rule labels | chain headers |
| PEND-008 | P0 | IN_PROGRESS | Missing OI%/Vol% | Render pct fields / derive | chain headers |
| PEND-009 | P0 | IN_PROGRESS | Missing Greeks columns | Render delta/gamma/theta/vega | chain headers |
| PEND-010 | P1 | OPEN | Equity options security_id | Scrip master map | Trade equity panel vs Dhan |
| PEND-011 | P1 | IN_PROGRESS | `/api/holdings` `/api/funds` 404 | Alias to broker holdings/funds | HTTP 200 |
| PEND-012 | P1 | OPEN | Charts 404 | Implement or mark MISSING | `/?tab=charts` |
| PEND-013 | P1 | OPEN | multibagger/predictions/backtest 404 | Wire or honest MISSING | APIs |
| PEND-014 | P0 | OPEN | Paper positions file missing | Cloud persistence path | `/?tab=paper` open>0 or honest |
| PEND-015 | P0 | OPEN | Paper P&L synthetic Feb only | Same-day paper lifecycle | paper P&L date today |
| PEND-016 | P0 | OPEN | `/api/paper/*` subroutes 404 | Implement or UI aggregate-only | HTTP |
| PEND-017 | P0 | OPEN | Paper lifecycle gate FAIL | Market-hours proof job | `/api/auto_gates` |
| PEND-018 | P0 | OPEN | Expectancy negative | Better signals; no gate weaken | auto_gates |
| PEND-019 | P0 | OPEN | Spearman ρ 0.30 < 0.70 | Retrain/validate loop | ml/performance |
| PEND-020 | P0 | OPEN | ML predictions = 0 | Prediction writer | performance tab |
| PEND-021 | P0 | OPEN | Signal file not found / 429 | Persist scanner + rate limit | `/?tab=signals` |
| PEND-022 | P1 | OPEN | `/api/positions` empty file | Align paper+broker paths | positions API |
| PEND-023 | P0 | OPEN | Tick health gate FAIL | Faster refresh / WS proof | auto_gates |
| PEND-024 | P0 | OPEN | Option visibility gate FAIL | ATM window + audit | auto_gates |
| PEND-025 | P1 | WATCH | API key public_readonly | User decide enforce vs doc | auth/status |
| PEND-026 | P1 | OPEN | No RUHI board on UI | Read-only progress board | UI |
| PEND-027 | P2 | OPEN | Claude memory stale | User refresh memory | — |
| PEND-028 | P1 | OPEN | Gates 2/7 | Close blockers; LIVE OFF | auto_gates |
| PEND-029 | P1 | OPEN | Full Dhan parity FAIL | Close 004–012 then snap vs Dhan | chain vs dhan.co |
| PEND-030 | P2 | OPEN | Wrong Cursor path | User open primary clone | git toplevel |
| PEND-031 | P0 | OPEN | Multibagger 0 candidates | Research pipeline | `/?tab=multibagger` |
| PEND-032 | P1 | OPEN | Manual Dhan book not linked to paper | Keep broker read-only; paper separate | broker vs paper snaps |

---

## Implementation batch now (this session)

1. **PEND-004…009** — OptionChain UI Dhan columns + ATM default + stale honesty → **CODE LANDED locally** (needs PR→deploy→re-snap on serving SHA)
2. **PEND-011** — `/api/holdings` + `/api/funds` aliases → **CODE LANDED locally**
3. Re-snap `/?tab=chain` + `/?tab=trade` **after deploy** (local-only ≠ DONE)
4. Mark DONE only after serving SHA proof

### Local code proof (not live yet)

| ID | Change |
|---|---|
| PEND-004 | Age >60s in market hours → STALE / DEGRADED badge; amber status line |
| PEND-005 | Default VISIBLE = ±10 ATM (was ALL) |
| PEND-006–009 | Headers: OI% Vol% LTP% Buildup Δ Γ Θ Vega both CE/PE |
| PEND-011 | `app.py` `/api/holdings` + `/api/funds` → broker read-only |

**Still OPEN after this batch:** paper (014–017), ML (018–020), signals (021), scheduler (002), deploy lag (001), multibagger (031), charts (012), etc.  

## Need from user

1. Cursor folder = primary clone only (PEND-030)  
2. Refresh Claude project memory (PEND-027)  
3. API key policy (PEND-025)  
4. Keep LIVE OFF; keep Dhan open for parity confirms  

## Next after this batch

Paper persistence (014–017) → signals (021) → scheduler (002) → deploy lag (001) → ML gates (018–020).
