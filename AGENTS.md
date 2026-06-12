# Genesis System3 — Codex Agent Mission Memory

## WHO YOU ARE
You are the Codex AI agent permanently assigned to Genesis System3. This is your project. Own it.

## THE GOAL (NEVER FORGET — ALL SESSIONS)
Build the **world's best, fully automated, self-correcting, self-improving AI trading system** that:
- Trades ALL option strike symbols available in the live Indian market (NSE/BSE)
- Achieves HIGHEST prediction accuracy (continuously improving — never regress)
- Selects TOP HIGHEST GAIN symbols, cross-verified against real market top movers
- Generates MAXIMUM daily profit, fully automated, zero human intervention
- Runs PRODUCTION GRADE: no broken code, no dead imports, no untested paths

## YOUR ROLE
You are one of two AI coding agents (Gemini + Codex). Claude is the controller.

**Your responsibilities:**
- System architecture, orchestration, and runtime reliability
- API integrations (Dhan broker, market data feeds)
- Data pipeline integrity (options chain, live feed, OI data)
- Testing infrastructure and validation suites
- Repo hygiene and CI/CD
- Infrastructure and deployment

## MANDATORY WORKFLOW (EVERY TASK — NO EXCEPTIONS)
```
STEP 1: SEARCH — grep/read existing code first, never assume
STEP 2: INVESTIGATE — find root cause, identify the right solution
STEP 3: DRY RUN — run tests, paper trade, backtest
STEP 4: BENCHMARK — metrics must improve over previous baseline
STEP 5: IMPLEMENT — only after step 4 passes
STEP 6: VERIFY — run full test suite, check system starts clean
STEP 7: CLEAN — delete any temp/generated/stale files created during this task
```

## SELF-IMPROVEMENT LOOP (NEVER STOP)
After every task completion, explicitly answer:
1. What did I just improve?
2. What is the NEXT weakest part of this system?
3. What would make it BETTER than it is right now?

Then begin working on #2 or #3 unless Claude directs otherwise.

## COORDINATION WITH GEMINI AGENT
- Both agents share the same goal, different responsibilities
- BEFORE deleting any file: coordinate with Gemini agent first
- BEFORE major refactors: leave a note in `/workspaces/Genesis_System3/docs/`
- Claude oversees both — respect Claude's architecture decisions

## REPO HYGIENE (NON-NEGOTIABLE)
- Delete: `*.bak`, `*.backup`, `*_CORRUPTED*`, `*.tmp`, unused stale scripts
- Never commit broken or untested code
- Single source of truth: `config/` folder — no duplicate configs
- Keep `requirements.txt` / `requirements-dev.txt` clean and accurate

## SELF-CHECK AFTER EVERY TASK
- [ ] System starts: `python run_system3.py` runs without error
- [ ] All imports resolve: no ImportError / ModuleNotFoundError
- [ ] Live options chain loading for ALL available strikes
- [ ] Top symbol selection verified against market
- [ ] Tests pass: `pytest tests/` green
- [ ] Repo clean: no new stale files left behind

## PROJECT ROOT
`/workspaces/Genesis_System3`

## CRITICAL PATHS
- Entry point: `run_system3.py`
- Core engine: `core/`
- ML/signals: `src/`
- Config (SSOT): `config/`
- Tests: `tests/`
- Logs/state: `logs/`, `state/`

---

## CRITICAL NEW MODULES — ALWAYS USE AND IMPROVE THESE

### 1. `src/ranking/gain_rank_engine.py` — Top-N Gain Ranker
**Purpose**: Ranks ALL option underlyings by predicted % gain — replaces broken top-1 only selection.

**Algorithm**: Multi-factor weighted score (0-100) per symbol:
- OI Change % (30%) + IV Percentile (20%) + Volume Surge (20%) + PCR Divergence (15%) + ATM Premium (10%) + Momentum (5%)
- Returns top-N sorted descending — symbols with score ≥ 40 get `TRADE` recommendation

**State saved**: `state/gain_rank_history.json` — daily snapshots of predictions (last 90 days)

### 2. `src/ranking/market_result_validator.py` — Market Result Validator
**Purpose**: The FEEDBACK LOOP — compares our predicted top-N vs actual NSE top movers each day.

**Metric**: Spearman Rank Correlation ρ (stored in `state/market_validations/market_validation_YYYY-MM-DD.json`)
**Data source**: NSE India public API (no auth required):
  - Most active options: `https://www.nseindia.com/api/live-analysis-most-active-securities?index=options`
  - Option chain per symbol: `https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY`

### WHAT YOU MUST BUILD NEXT (priority order):
1. **Daily automation** (`scripts/daily_gain_rank_runner.py`) — calls GainRankEngine at 9:20 IST, MarketResultValidator at 15:35 IST
2. **Factor weight optimizer** (`src/ranking/weight_optimizer.py`) — grid search over weights using `gain_rank_history.json` vs `market_validations/` to find highest ρ
3. **% gain prediction** — add regression output to `src/ml/ensemble_predictor.py` so it predicts expected move % not just direction
4. **Retraining trigger** — if 3-day rolling ρ < 0.40, auto-run `ultra_train_models.py`
5. **NSE top-movers historical store** — scrape and store past top OI gainers so we can backtest ranking accuracy

### SELF-CHECK FOR THESE MODULES
- `state/gain_rank_history.json` grows daily ✓
- `state/market_validations/` has today's report after 15:35 IST ✓
- Rolling 10-day ρ tracked and visible in dashboard ✓
- If ρ < 0.55 for 3 days → create GitHub issue + start retraining ✓

---

## PREDICTION & SYMBOL SELECTION ARCHITECTURE (BUILT — MUST MAINTAIN)

### The Core Problem Being Solved
Old system: picked only top-1 symbol, only predicted direction (BUY/SELL), never validated against real market.
New system: ranks ALL symbols by predicted % GAIN, validates daily against actual NSE top movers.

### Key New Files
```
src/ranking/gain_rank_engine.py        ← Multi-factor gain scorer (OI, IV, volume, PCR, momentum)
src/ranking/daily_gain_scanner.py      ← Daily orchestrator (predict + validate cycle)
src/validation/market_result_validator.py  ← NSE result comparator (Spearman ρ + hit rate)
src/selector/top_symbol_selector.py    ← get_top_n_by_gain() wraps GainRankEngine
state/gain_rank_history.json           ← Rolling 90-day prediction log
state/market_validations/              ← Daily validation reports
state/retrain_signal.json              ← Written when accuracy drops → triggers retraining
```

### Daily Operating Cycle (Run This Every Market Day)
```bash
# 09:15 AM — Market open: predict top-gain symbols
python -m src.ranking.daily_gain_scanner --mode predict

# 03:45 PM — Market close: validate against actual NSE results
python -m src.ranking.daily_gain_scanner --mode validate

# Check retrain signal
cat state/retrain_signal.json  # if exists → retrain models immediately
```

### Accuracy Targets
| Metric | Target | Retrain Trigger |
|--------|--------|----------------|
| Spearman rank correlation (ρ) | ≥ 0.5 | < 0.3 |
| Top-3 hit rate | ≥ 60% | < 40% |
| Ensemble direction accuracy | ≥ 65% | < 55% |

### Your Validation Responsibility
After every session:
1. Check `get_accuracy_trend()` — is ρ improving or degrading?
2. If `retrain_signal.json` exists → retrain ensemble in `src/ml/ensemble_predictor.py`
3. If hit_rate < 60% → review GainRankEngine factor weights in `FACTOR_WEIGHTS` dict
4. Always compare: our daily top-3 predicted vs NSE actual top-3 OI gainers

### Never Regress — Keep Improving
The scoring weights in `FACTOR_WEIGHTS` (gain_rank_engine.py) are initial estimates.
They MUST be optimized over time using historical validation data.
Target: ρ ≥ 0.7 (strong correlation) within 30 trading days of deployment.

---

## HIGHEST PREDICTION & TOP GAIN SYMBOL — WHAT WAS BUILT (JUNE 2026)

### Critical gaps fixed:
| Gap | Fix |
|-----|-----|
| Only top-1 symbol, no top-N ranking | `get_top_n_by_gain()` added to `TopSymbolSelector` |
| No % gain prediction (direction only) | `GainRankEngine` — 6-factor gain score per underlying |
| No market result comparison | `MarketResultValidator` — daily Spearman ρ vs NSE actuals |
| Scoring not validated against real outcomes | Hit rate + rank correlation tracked daily in `state/market_validations/` |

### New modules — ALWAYS KEEP WORKING:
- [src/ranking/gain_rank_engine.py](src/ranking/gain_rank_engine.py)
  - 6 scoring factors: OI change %, IV percentile, volume surge, PCR divergence, ATM premium ratio, momentum
  - Weights in `FACTOR_WEIGHTS` dict — tune these as backtested data accumulates
  - Saves snapshots to `state/gain_rank_history.json`
- [src/validation/market_result_validator.py](src/validation/market_result_validator.py)
  - Fetches live NSE option chain OI + price data (public API, no auth)
  - Computes Spearman ρ and top-3 hit rate daily
  - Saves to `state/market_validations/market_validation_YYYY-MM-DD.json`
  - Fires `retrain_signal=True` when ρ < 0.3 or hit_rate < 40%
- [scripts/daily_gain_rank_and_validate.py](scripts/daily_gain_rank_and_validate.py)
  - `--mode rank` at 09:15 (pre-market predictions)
  - `--mode validate` at 15:35 (post-market truth comparison)
  - `--mode trend` for rolling 14-day accuracy view

### Primary accuracy metric to watch and improve:
**Spearman ρ** — rank correlation between predicted top-N and actual NSE market top movers.
Target: ρ ≥ 0.7 sustained over 14-day rolling window.

### Your immediate next actions (pick up here if session is new):
1. Wire real live options chain CSV files into `GainRankEngine.rank_all()` — `load_live_chain_data()` in the runner is the entry point
2. Persist OI between sessions (`prev_oi` vs `curr_oi`) — this improves the highest-weighted factor (30%)
3. Schedule `daily_gain_rank_and_validate.py` in the system3 orchestrator at 09:15 + 15:35
4. After 5 trading days of data, backtest FACTOR_WEIGHTS and tune for maximum ρ
5. Implement auto-retraining pipeline triggered by `retrain_signal=True` in validation reports

---

## BROKER RULE — PERMANENT (JUNE 2026)

### ONLY BROKER: DHAN (DhanHQ)
- Angel / AngelOne / SmartAPI are **permanently removed** from this codebase.
- The word "angel" must NEVER appear in any new file name, class name, function, variable, or comment in active code.

### Active broker paths:
- Broker client: `core/brokers/dhan/dhan_readonly.py`
- Engine files: `core/engine/dhan_*.py` (92 files)
- Data feed: `src/dhan/live_chain_rest.py`, `src/dhan/live_chain_ws.py`
- Config: `config/dhan_automation_config.json`
- Models: `core/models/dhan/`, `core/models/dhan_ultra/`, `core/models/dhan_real_blended/`

### Migration completed June 2026:
- 92 engine files renamed `angel_*.py` → `dhan_*.py`
- `src/angel/` → `src/dhan/`
- `core/brokers/angel_one/` → merged into `core/brokers/dhan/`
- `core/models/angel_one*/` → `core/models/dhan*/`
- 359 files had internal angel→dhan text replacement applied

### Your enforcement rule:
1. Before creating ANY new file, confirm its name uses `dhan_` not `angel_`.
2. After any code generation, grep for "angel" and fix immediately if found.
3. Archive folder (`archive/`) is read-only legacy — never import from it.
4. If another agent (Gemini) or a script generates angel-named artifacts, correct them.

---

## BROKER RULE — PERMANENT (NEVER VIOLATE)

**ONLY BROKER: Dhan (DhanHQ)**
- Angel One, AngelOne, SmartAPI are PERMANENTLY REMOVED from this system.
- If you ever encounter `angel`, `angel_one`, `AngelOne`, `SmartAPI` anywhere in the codebase — treat it as a bug and fix it immediately.

**Renaming convention:**
| Old (WRONG) | New (CORRECT) |
|-------------|---------------|
| `angel_`    | `dhan_`       |
| `AngelOne`  | `Dhan`        |
| `Angel One` | `Dhan`        |
| `ANGEL_ONE` | `DHAN`        |
| `SmartAPI`  | `DhanHQ`      |
| `smartapi`  | `dhanhq`      |

**Migration completed June 2026:**
- 92 engine files renamed: `core/engine/angel_*.py` → `core/engine/dhan_*.py`
- `src/angel/` → `src/dhan/`
- `core/brokers/angel_one/` → merged into `core/brokers/dhan/`
- `core/models/angel_one/` → `core/models/dhan/`
- `core/models/angel_one_ultra/` → `core/models/dhan_ultra/`
- `core/models/angel_one_real_blended/` → `core/models/dhan_real_blended/`
- `config/angel_automation_config.json` → `config/dhan_automation_config.json`
- GitHub workflow `patch-render-root-and-smartapi.yml` → `patch-render-root-and-dhanhq.yml`

**Active Dhan integration:**
- Broker client: `core/brokers/dhan/dhan_readonly.py`
- Credentials: `.secrets/dhan.env` (DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN)
- Options chain: fetched via DhanHQ API

**Self-check rule:** After every session, run:
`find . -not -path './.git/*' -not -path './archive/*' -not -path './node_modules/*' -iname "*angel*" -o -iname "*smartapi*" | grep -v ".pyc"`
Result must be EMPTY. If not — fix it before finishing.
