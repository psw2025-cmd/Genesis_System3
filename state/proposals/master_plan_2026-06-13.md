# MASTER PLAN — Genesis System3 World's Best AI Options Trading System
> Author: Claude (controller) | Date: 2026-06-13 | Based on: full codebase investigation + Gemini + Codex analysis
> Status: APPROVED — implementing in phases

---

## ROOT CAUSE ANALYSIS — Why Spearman ρ = 0.20

### The Fundamental Disconnect
Two independent systems were built but never connected:

```
OLD SYSTEM (448 engine files, Feb 2026):
  system3_signal_engine.py
    → greeks, trend, volatility, breakout, momentum, scoring engines
    → core/engine/ensemble_predictor.py (Ultra + RF models)
    → OUTPUT: per-option BUY_CE/BUY_PE/HOLD signals per strike
    → STORED: storage/live/dhan_index_ai_signals.csv

NEW SYSTEM (June 2026):
  GainRankEngine (gain_rank_engine.py)
    → 6-factor weighted scoring (OI 30%, IV 20%, vol 20%, PCR 15%, ATM 10%, mom 5%)
    → OUTPUT: underlying-level rankings (NIFTY > BANKNIFTY > FINNIFTY > etc.)
    → MarketResultValidator measures Spearman ρ vs actual NSE top movers

NEVER CONNECTED → ML signal strength not feeding into underlying ranking
```

### Why ρ = 0.20 Specifically
1. OI change was synthetic/flat — NOW FIXED (NSE provider + OI cache)
2. IV percentile needs 30+ days of history — MISSING
3. Volume baseline needs history — MISSING
4. Factor weights (initial estimates) never backtested — need calibration
5. ML model confidence NOT used as a ranking factor — biggest missing signal
6. NSE anti-bot blocking in codespace — production machine should work

---

## ARCHITECTURE TARGET — How the Systems Must Work Together

```
DAILY FLOW:
09:00 — Fetch option chain data (NSE API → Dhan Data API when subscribed)
        ↓
09:05 — system3_signal_engine.py runs → generates per-option signals
        Output: storage/live/dhan_index_ai_signals.csv
        ↓
09:10 — BRIDGE: aggregate_signals_by_underlying.py
        Reads signal CSV → computes per-underlying ML confidence score
        (avg BUY_CE probability per underlying = directional conviction)
        ↓
09:15 — GainRankEngine.rank_all() with:
        - Real OI from NSE (prev vs curr via market_cache.json)
        - Real IV data from option chain
        - Real volume from option chain
        - ML_confidence as NEW 7th factor (25% weight)
        → Ranked underlyings by predicted gain
        → Saved to state/gain_rank_history.json
        ↓
        TRADING DAY RUNS
        ↓
15:35 — MarketResultValidator: compare predictions vs NSE actual top movers
        → Spearman ρ calculated and stored
        → If ρ < 0.40 for 3 days → retrain_signal.json emitted
        ↓
15:40 — OI snapshot saved to market_cache.json (for next morning)
        ↓
15:45 — auto_retrain.py checks retrain_signal.json
        If signal exists → triggers dhan_blended_model_trainer.py → new models
        ↓
        Dashboard updated in real time
```

---

## PRIORITY ROADMAP — Fastest Path to ρ ≥ 0.70

### PHASE 1 — BRIDGE (builds immediately, biggest single improvement)
**Bridge the two systems.** Connect ML signal output to GainRankEngine as a 7th factor.

Files to create/modify:
- NEW: `src/ranking/ml_signal_aggregator.py` — reads signal CSV, computes per-underlying ML confidence
- MODIFY: `src/ranking/gain_rank_engine.py` — add 7th factor: ml_confidence (weight: start at 25%)
- MODIFY: `scripts/daily_gain_rank_and_validate.py` — call signal aggregator before ranking

Expected ρ improvement: 0.20 → 0.40-0.50 (ML models were trained on real option data)

### PHASE 2 — DATA FOUNDATION (required for ρ ≥ 0.60)
**Real option chain data for all factors.**

- User subscribes Dhan Data APIs OR NSE session cookies fixed for production
- Historical IV tracker: store daily IV per underlying in state/iv_history.json (30 days = IV percentile works)
- Historical volume tracker: store daily volume baseline in state/vol_history.json
- Once real data flows: all 6 original factors become real (not synthetic)

Expected ρ improvement: 0.40 → 0.60 (all 6 factors now real data)

### PHASE 3 — RETRAIN CONSUMER (closes the feedback loop)
**Make the system self-improving.**

- NEW: `scripts/auto_retrain.py` — checks retrain_signal.json, triggers dhan_blended_model_trainer_v2.py
- Add to scheduler as `auto_retrain` job running at 16:00 IST weekdays
- After retraining: new models deployed to core/models/dhan_ultra/, signal engine picks them up

Expected ρ improvement: after 2-3 retrain cycles → 0.60 → 0.70+

### PHASE 4 — MASTER ORCHESTRATOR (production grade)
**Single entry point that runs everything in order.**

- NEW: `scripts/genesis_orchestrator.py` — replaces fragmented scripts
- Runs: token check → data fetch → signal engine → bridge → ranking → validation → retrain check
- Scheduled at 09:00 (pre-market) and 15:30 (post-market) via system3_job_scheduler

### PHASE 5 — FACTOR WEIGHT CALIBRATION (maximum accuracy)
**Use real Spearman ρ data to tune weights.**

- After 5+ days of real ρ data: run correlation analysis on which factors predict gain best
- Use scipy.optimize or grid search to find optimal FACTOR_WEIGHTS
- Target: weights reflect actual predictive power, not initial estimates

Expected ρ improvement: 0.70 → 0.80+ (weights tuned to real market data)

### PHASE 6 — DASHBOARD + REGRESSION HEAD
- Add Spearman ρ trend chart, gain rank table, retrain status, token health to dashboard
- Add regression output to ensemble_predictor (predict % gain, not just direction)
- Expand to more underlyings (currently NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY/SENSEX)

---

## DOMAIN FINDINGS

### Prediction Accuracy
- Current: ρ = 0.20 (below random — factor weights are wrong without real data)
- ML models claim 99.1% accuracy but predict per-strike signals, NOT underlying rankings
- Bridge (Phase 1) is the highest-leverage single change available

### Highest Gain Ranking
- GainRankEngine architecture is sound — 6 factors are the right signals
- Factor weights need real data for validation (IV percentile needs 30 days)
- Missing: ML model conviction as a 7th factor (most important missing piece)

### Market Data
- NSE public API works in production (anti-bot is browser-session based, real machine should work)
- Dhan Data APIs (Error 806) need user subscription — unlocks all data
- Historical data: build IV and volume history trackers to enable percentile scoring

### Models
- Ultra models (core/models/dhan_ultra/) are trained Feb 2026 — 4 months stale
- 99.1% accuracy on classification (BUY_CE/BUY_PE/HOLD) — needs retrain on recent data
- Retrain consumer missing — Phase 3 closes this gap

### Dashboard
- Currently shows nothing about new system health
- Minimum needed: Spearman ρ trend, today's gain rank, token status, retrain alert

---

## SUCCESS METRICS PER PHASE

| Phase | Metric | Target |
|-------|--------|--------|
| Phase 1 (Bridge) | Spearman ρ | ≥ 0.40 |
| Phase 2 (Data) | Spearman ρ | ≥ 0.60 |
| Phase 3 (Retrain) | Spearman ρ after 3 retrains | ≥ 0.70 |
| Phase 4 (Orchestrator) | System uptime | 100% automated |
| Phase 5 (Calibration) | Spearman ρ | ≥ 0.80 |
| Phase 6 (Dashboard+Regression) | Full visibility, % gain output | Production grade |

---

## IMMEDIATE IMPLEMENTATION ORDER (today)
1. `src/ranking/ml_signal_aggregator.py` — read signal CSV, output per-underlying ML confidence
2. Update `src/ranking/gain_rank_engine.py` — add ml_confidence as 7th factor
3. Update `scripts/daily_gain_rank_and_validate.py` — call aggregator at 09:15
4. `scripts/auto_retrain.py` — retrain signal consumer
5. Add auto_retrain job to scheduler config
