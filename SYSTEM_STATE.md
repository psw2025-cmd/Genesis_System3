# SYSTEM_STATE.md — Single Source of Truth
> **ALL AGENTS MUST READ THIS FILE FIRST before making any changes.**
> Last updated: 2026-06-13 21:00 IST | Updated by: Claude (controller)

---

## RULE: Before Any Change
1. Read this file completely
2. Check `CHANGE_LOG.md` for recent changes by other agents
3. Make your change
4. Append your change to `CHANGE_LOG.md` (name + what + why + timestamp)
5. Update this file if system state changed

---

## BROKER
- **ACTIVE:** DhanHQ ONLY
- **Client ID:** ...3741
- **SDK:** dhanhq 2.2.0
- **Status:** CONNECTED ✅ (verified 2026-06-12)
- **Balance:** ₹17.53

### Dhan API Subscription Status (CRITICAL — read before implementing data features)
| API Category | Status | Notes |
|---|---|---|
| Account APIs (funds, positions, holdings, orders, trades, ledger) | ✅ SUBSCRIBED | All working |
| Security Master (232K instruments) | ✅ SUBSCRIBED | Downloads via fetch_security_list() |
| Margin Calculator | ✅ SUBSCRIBED | Returns 0 for this account type |
| **Option Chain (expiry list, OI, IV, Greeks)** | ❌ NOT SUBSCRIBED | Error 806 — needs Data APIs plan |
| **Quote Data (real-time LTP, bid/ask, depth)** | ❌ NOT SUBSCRIBED | Error 806 |
| **OHLC Data (real-time)** | ❌ NOT SUBSCRIBED | Error 806 |
| **Historical Candles (daily/intraday)** | ❌ NOT SUBSCRIBED | Error DH-902 |
| **WebSocket Market Feed** | ❌ NOT SUBSCRIBED | Error 806 |

**Action needed:** User must subscribe to Dhan Data APIs at web.dhan.co → Profile → DhanHQ Trading APIs → Data APIs plan.

### Data Fallback (used until Data APIs subscribed)
- Option chain OI data: NSE public API `https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY`
- Most active options: `https://www.nseindia.com/api/live-analysis-most-active-securities?index=options`
- These work but have rate limits and require session cookies (handled in market_result_validator.py)

---

## TOKEN MANAGEMENT
- **Strategy:** generate_token(PIN + TOTP) — pure API, fully automated
- **Daemon:** Running daily at 08:30 AM (dhan_token_auto_refresh.py)
- **Watchdog:** Running every 30 min (dhan_watchdog_runner.py)
- **Startup check:** Runs on every terminal login via ~/.bashrc
- **Credentials:** DHAN_PIN ✅, DHAN_TOTP_SECRET ✅, DHAN_APP_ID ✅, DHAN_APP_SECRET ✅
- **Current token expires:** 2026-06-13 ~19:00 IST

---

## ACTIVE MODULES & STATUS
| Module | File | Status |
|---|---|---|
| GainRankEngine | src/ranking/gain_rank_engine.py | Built, 7-factor scoring, ML confidence bridge wired |
| NSE Provider | core/data/nse_provider.py | Shared session + OI cache; staleness guards + expiry-day guard |
| DataSourceManager | core/data/datasource_manager.py | NEW — 7-source fallback (P0-P6), auto-fallback, health check |
| Bhavcopy Store | storage/bhavcopy/ | NEW — 5 days cached (20260608–20260612), 7MB/day, real OI change |
| Bhavcopy Downloader | scripts/bhavcopy_downloader.py | NEW — daily at 18:30 IST, auto-download NSE FO archive |
| Datasource Health Check | scripts/datasource_health_check.py | NEW — daily at 08:00 IST, saves state/datasource_health.json |
| OI Cache | state/market_cache.json | Persists OI; date field + 3-day staleness + expiry-day guards |
| MarketResultValidator | src/ranking/market_result_validator.py | SHIM → src/validation/ (canonical) |
| TopSymbolSelector | src/selector/top_symbol_selector.py | Modified to use GainRankEngine |
| Daily Runner | scripts/daily_gain_rank_and_validate.py | Scheduled ✅, expiry-day guard added |
| ML Signal Aggregator | src/ranking/ml_signal_aggregator.py | Bridges signal CSV to GainRankEngine 7th factor |
| Auto Retrain | scripts/auto_retrain.py | Reads retrain_signal.json, triggers trainer at 16:00 |
| Job Scheduler Config | config/system3_job_scheduler.json | 7 jobs: + bhavcopy_download (18:30) + datasource_health_check (08:00) |
| Token Manager | core/brokers/dhan/token_manager.py | Live, 3-strategy refresh |
| Token Daemon | scripts/dhan_token_auto_refresh.py | Running (check PID with pgrep) |
| Watchdog | scripts/dhan_watchdog_runner.py | Running (check PID with pgrep) |
| Pre-flight Check | core/brokers/dhan/preflight.py | Ready for integration |
| Dhan Read-Only | core/brokers/dhan/dhan_readonly.py | Connected ✅ |
| Factor Weight Calibrator | scripts/calibrate_factor_weights.py | NEW — grid search, auto-updates at 5+ validation days |
| IV History | state/iv_history.json | NEW — rolling 5-day ATM straddle IV proxy per symbol |

---

## PENDING TASKS (priority order)
1. **[USER ACTION]** Subscribe to Dhan Data APIs → unlocks option chain, quotes, historical candles
2. ~~**[CODE]** Schedule daily_gain_rank_and_validate.py in orchestrator at 09:15 + 15:35~~ ✅ DONE
3. ~~**[CODE]** Wire real live option chain data into GainRankEngine (currently synthetic)~~ ✅ DONE (NSE first, CSV fallback, synthetic last)
4. ~~**[CODE]** Persist OI between sessions (prev_oi vs curr_oi) for accurate OI change scoring~~ ✅ DONE (market_cache.json via nse_provider.py)
5. ~~**[CODE]** Add focused tests: bhavcopy parser, OI cache staleness, DataSourceManager fallback~~ ✅ DONE (31/31 passing)
6. ~~**[CODE]** Build auto-retraining trigger from retrain_signal.json~~ ✅ DONE
7. ~~**[CODE]** Multi-source data resilience — DataSourceManager with auto-fallback~~ ✅ DONE
8. ~~**[CODE]** Tune FACTOR_WEIGHTS in gain_rank_engine.py after 5+ days of Spearman ρ data~~ ✅ DONE (conservative update applied; calibrate_factor_weights.py auto-tunes at 5+ days)
9. ~~**[CODE]** Add ensemble_predictor.py regression head for % gain prediction~~ ✅ DONE (heuristic head; real training when signal CSV available)
10. ~~**[CODE]** Dashboard: Spearman ρ trend chart, gain rank table, datasource health widget, retrain alert banner~~ ✅ DONE (3 new tabs: Rankings, Accuracy, System Health)
11. ~~**[CODE]** Unify dual validators (src/ranking/ vs src/validation/)~~ ✅ DONE (src/ranking/ is now a shim to canonical src/validation/)
12. ~~**[CODE]** Scheduler time-of-day enforcement~~ ✅ DONE (--daemon mode, 60s tick, IST, weekdays-only)
13. **[OPTIONAL USER ACTION]** Open free Finvasia/Shoonya account → real-time P3 source (no anti-bot, real Greeks)

---

## THE ONE DECISION LAW (read before any proposal or implementation)

**Only one thing decides what goes into core:**
Which solution produces the BEST result on ALL THREE metrics simultaneously:

| Metric | What it measures | Current value | Target |
|--------|-----------------|---------------|--------|
| Spearman ρ | Rank correlation — do our predicted top symbols match real NSE top movers? | **0.80** (1 day, session 5) | ≥ 0.80 on 5+ days |
| Top-N Hit Rate | Of our top-3 picks, how many appear in real market top-3? | 66.7% (1 day) | ≥ 70% |
| Daily Profit | Actual P&L from trading our top symbols (ANALYZER now, LIVE later) | N/A (analyzer) | Maximum |

**Rules that flow from this law:**
1. Any agent can propose any solution — opinions do not matter, measured results do
2. If two approaches are proposed, both must be tested on real data → better metric wins → goes to core
3. No change enters core without showing improvement in at least one metric without hurting others
4. If current approach gives ρ=0.20 and a new approach gives ρ=0.45 → new approach replaces old, no debate
5. If an agent argues "this is architecturally cleaner" but metrics are equal or worse → rejected
6. Always keep improving further — no solution is final, current best is always the floor not the ceiling
7. Phase priority: During ANALYZER phase, rank by (Spearman ρ + hit rate). Once LIVE, daily profit is the final arbiter.

**Consequence for agents:**
- Do not propose things you cannot measure
- Every proposal must state: "this will improve [metric] from X to Y, measured by [method]"
- Cross-verification between Gemini and Codex must include: "does this actually improve the 3 metrics?"

---

## ARCHITECTURE DECISIONS
- **No live order placement** — system is ANALYZER ONLY until explicitly enabled
- **Multi-source data fallback** — 7-source priority chain, system NEVER fails due to single source
- **NSE bhavcopy as ground truth** — `ChngInOpnIntrst` provides real OI change without two-session comparison
- **4-layer token safety** — L0 startup, L1 daily daemon, L2 watchdog, L3 preflight
- **Spearman ρ target ≥ 0.70** — retrain signal fires if ρ < 0.40 for 3 consecutive days
- **Angel/SmartAPI permanently removed** — migration completed 2026-06-12 (92 files, 359 content)

---

## AGENT ROLES AND AUTONOMOUS PROTOCOL

### Claude — Lead Investigator + Manager + Implementer
Claude is NOT a passive coordinator. Claude independently investigates, researches globally,
challenges agents, and only then implements. This is the correct protocol:

**STEP 0 — SELF AUDIT (every session, before dispatching agents)**
  - Read SYSTEM_STATE.md and CHANGE_LOG.md
  - Read current code for the problem area (not just agent summaries)
  - Form an independent view: what is the weakest point? what is the best global solution?
  - Search online/knowledge for world-class approaches to the same problem
  - Compare: is what we have actually world-best, or just "good enough"?

**STEP 1 — DISPATCH AGENTS IN PARALLEL (after forming own view)**
  - Run Gemini + Codex simultaneously on the same problem
  - Agents do NOT know Claude's view — they form their own independently
  - Claude's view + Gemini's view + Codex's view = 3 independent perspectives

**STEP 2 — COMPARE ALL THREE (including Claude's own)**
  - If all 3 agree → strong signal, implement
  - If Claude's global research found something better than both agents → Claude's solution wins
  - If agents found something Claude missed → adopt and credit it
  - If 2 of 3 agree and 1 disagrees → investigate the disagreement, don't auto-dismiss

**STEP 3 — IMPLEMENT THE GLOBAL BEST**
  - Not the easiest solution, not what agents proposed by default
  - The objectively best solution — measured by: prediction accuracy, system reliability,
    data quality, production grade, zero manual steps
  - Write real proof after every implementation (actual output, not claimed output)

**STEP 4 — UPDATE ALL 3 MEMORY SYSTEMS**
  - Claude memory (/home/codespace/.claude/projects/.../memory/)
  - Gemini memory (GEMINI.md + ~/.gemini/GEMINI.md)
  - Codex memory (AGENTS.md)
  - SYSTEM_STATE.md + CHANGE_LOG.md

**Claude's standing duties (every session):**
- Runs agents via CLI: `gemini --skip-trust --yolo -p "..."` and `codex exec "..."`
- Updates SYSTEM_STATE.md after every significant change
- Arbitrates agent disagreements using own independent research as tiebreaker
- NEVER implements something just because an agent proposed it — always validates independently

### Gemini — Autonomous Investigator (Domains: Prediction, Gain Ranking, Market Data, Models, Dashboard)
- Investigates independently — forms own view before talking to Codex
- Writes proposals to: `state/proposals/gemini_proposal_YYYY-MM-DD.md`
- Requests Codex cross-verification via CHANGE_LOG.md
- Verifies Codex proposals independently (AGREE / DISAGREE / PARTIAL)
- Never implements without Claude approval on significant changes
- Memory: `GEMINI.md` + `~/.gemini/GEMINI.md`

### Codex — Autonomous Investigator (Domains: Architecture, Data Pipeline, API, Testing, Dashboard)
- Investigates independently — forms own view before talking to Gemini
- Writes proposals to: `state/proposals/codex_proposal_YYYY-MM-DD.md`
- Requests Gemini cross-verification via CHANGE_LOG.md
- Verifies Gemini proposals independently (AGREE / DISAGREE / PARTIAL)
- Never implements without Claude approval on significant changes
- Memory: `AGENTS.md`

### Cross-Verification Flow
```
Agent A investigates → writes proposal → logs in CHANGE_LOG requesting Agent B verify
Agent B reads proposal independently → writes AGREE/DISAGREE/PARTIAL in CHANGE_LOG
Claude reads both views → decides best solution → approves implementation
Implementing agent implements → other agent verifies result → Claude confirms
```

### Proposal Files
- `state/proposals/gemini_proposal_YYYY-MM-DD.md` — Gemini proposals
- `state/proposals/codex_proposal_YYYY-MM-DD.md` — Codex proposals
- Format: Problem | Recommended Solution | Alternatives Rejected | Success Metric

---

## PERPETUAL IMPROVEMENT LAW (permanent — never expires)

The system NEVER settles. Every session's best metric becomes the new minimum floor for the next session.

**Rule:** If today's Spearman ρ = 0.45, then next session's floor is 0.45.
Getting 0.44 next session = REGRESSION = unacceptable. Must be investigated and fixed immediately.

**How this works in practice:**
- Every session: read the last recorded metric values from state/market_validations/ and state/gain_rank_history.json
- That recorded value = the floor. Every change must beat it or at minimum not regress it.
- When a new all-time best is achieved → record it explicitly in CHANGE_LOG.md as "NEW BEST: ρ=X.XX"
- When a regression is detected → stop all other work, diagnose root cause, fix it first

**The 3 metric floors (updated as system improves):**
| Metric | First recorded value | Current floor | All-time best |
|--------|---------------------|---------------|---------------|
| Spearman ρ | 0.20 (2026-06-12) | **0.80** (2026-06-13 session 5) | **0.80** |
| Top-3 Hit Rate | 66.7% (2026-06-12) | 66.7% | 66.7% |
| Daily Profit | N/A (analyzer mode) | N/A | N/A |

**⚠ WARNING: ρ=0.80 measured on 1 validation day only — overfitting risk HIGH.**
Next session: must verify ρ holds on day 2 validation. If it drops, diagnose and fix first.
`scripts/calibrate_factor_weights.py` auto-tunes weights once 5+ validation days accumulate.

**This table must be updated every time a new best is recorded.**

**Agents must ask at the start of every session:**
"What were last session's metrics? What is the current floor? What can I do this session to push higher?"
Never ask "is the system good enough?" — it is never good enough. Always better.

**No final state exists.** ρ=0.80 achieved on 1 day — target is now 0.80+ confirmed on 5+ days, then 0.85, then 0.90.
The system is always improving. That is the permanent operating mode.
