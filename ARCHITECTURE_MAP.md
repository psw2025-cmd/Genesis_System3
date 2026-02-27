# ARCHITECTURE_MAP.md

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPTION CHAIN AUTOMATION MASTER              │
│                    (option_chain_automation_master.py)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: DATA FETCHING                                         │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │ WebSocket        │      │ REST Fallback     │            │
│  │ (live_chain_ws)  │──────│ (live_chain_rest) │            │
│  └────────┬─────────┘      └────────┬─────────┘            │
│           │                          │                         │
│           └──────────┬───────────────┘                         │
│                      ▼                                         │
│              AngelOneBroker (broker.py)                         │
│                      │                                         │
│                      ▼                                         │
│         chain_data: Dict[str, pd.DataFrame]                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: QC VALIDATION                                        │
│  QCValidator (qc_validator.py)                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Checks:                                                  │  │
│  │ - min_contracts (per-underlying: SENSEX=30, etc.)       │  │
│  │ - data_completeness >= 70%                              │  │
│  │ - bid/ask validity                                      │  │
│  │ - IV sanity (0-3 range)                                 │  │
│  │ - spread quality                                        │  │
│  │ - strikes near ATM                                      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                      │                                         │
│                      ▼                                         │
│         qc_results: {underlying: (passed, failures)}          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: SIGNAL GENERATION                                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ IF QC_FAILED: Skip strategy, return NO_TRADE            │  │
│  │ IF QC_PASSED:                                           │  │
│  │   1. ML Predictions (ensemble_predictor)                │  │
│  │   2. Strategy Engine (strategy_engine.py)                │  │
│  │      - analyze_sentiment()                               │  │
│  │      - recommend_strategy()                             │  │
│  │        * Check: confidence >= 0.5 AND                  │  │
│  │                 liquidity_score >= 40                   │  │
│  │        * Check: bullish_score > 60 OR                   │  │
│  │                 bearish_score > 60 OR                    │  │
│  │                 (NEUTRAL AND liquidity_score > 70)      │  │
│  │      - decide() → TRADE or NO_TRADE                     │  │
│  │   3. Filter by confidence >= min_confidence (0.5)      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                      │                                         │
│                      ▼                                         │
│         signals: List[Dict] (TRADE or NO_TRADE)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 4: TRADE EXECUTION                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ IF sim_mode OR live_trade_enabled:                       │  │
│  │   Filter: signals where action == 'TRADE'                │  │
│  │   Check: current_positions < max_positions (5)           │  │
│  │   Execute: PaperExecutor.execute_trade()                │  │
│  │ ELSE:                                                    │  │
│  │   Skip execution (safety lock)                           │  │
│  └─────────────────────────────────────────────────────────┘  │
│                      │                                         │
│                      ▼                                         │
│         executed_trades: List[Dict]                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 5: PnL TRACKING                                          │
│  PaperExecutor.update_positions()                               │
│  PnLTracker.update()                                            │
│                      │                                         │
│                      ▼                                         │
│         positions_summary: Dict                                │
│         - total_unrealized_pnl                                 │
│         - total_realized_pnl                                  │
│         - open_count                                           │
│         - closed_positions                                     │
└─────────────────────────────────────────────────────────────────┘
```

## File Control Map

### Data Fetching
- **File**: `option_chain_automation_master.py`
- **Method**: `fetch_option_chain_data()`
- **Calls**: `_fetch_via_websocket()` → `LiveChainWebSocket` (`src/angel/live_chain_ws.py`)
- **Fallback**: `LiveChainREST` (`src/angel/live_chain_rest.py`) → `AngelOneBroker` (`core/brokers/angel_one/broker.py`)

### QC Validation
- **File**: `src/validation/qc_validator.py`
- **Class**: `QCValidator`
- **Method**: `validate_snapshot(df, underlying)`
- **Thresholds**:
  - `min_contracts`: Per-underlying (SENSEX=30, MIDCPNIFTY=40, FINNIFTY=45, NIFTY=50, BANKNIFTY=50)
  - `min_data_completeness`: 0.7 (70%)
  - `max_spread_pct`: 10.0%
  - ATM strikes: >= 10 (or >= 5 in sim_mode)

### Signal Generation
- **File**: `option_chain_automation_master.py`
- **Method**: `generate_signals(chain_data, qc_results)`
- **Flow**:
  1. Check QC → if failed, return NO_TRADE
  2. ML Predictions → `ensemble_predictor.predict_batch()`
  3. Strategy Engine → `strategy_engine.decide()`
- **Strategy Engine**: `src/selector/strategy_engine.py`
  - `analyze_sentiment()` → bullish_score, bearish_score
  - `recommend_strategy()` → Checks:
    - `confidence >= 0.5` AND `liquidity_score >= 40`
    - `bullish_score > 60` OR `bearish_score > 60` OR `(NEUTRAL AND liquidity_score > 70)`
  - Returns: `TRADE` or `NO_TRADE`

### Trade Execution
- **File**: `option_chain_automation_master.py`
- **Method**: `execute_trades(signals)`
- **Gating**:
  - `if not sim_mode and not live_trade_enabled: trade_signals = []` (LIVE safety lock)
  - `if current_positions >= max_positions: skip`
- **Executor**: `src/trading/paper_executor.py`
  - `PaperExecutor.execute_trade()` → Creates position
  - `PaperExecutor.update_positions()` → Updates PnL

### PnL Tracking
- **File**: `src/trading/pnl_tracker.py`
- **Class**: `PnLTracker`
- **Method**: `update(positions_summary, cycle_timestamp)`
- **Output**: `outputs/paper_pnl_summary.json` (NOT IMPLEMENTED YET)

## Decision Points (Where Trades Can Be Blocked)

1. **QC Validation** (`qc_validator.py:validate_snapshot()`)
   - Blocks if: `len(df) < min_contracts` OR `completeness < 70%` OR other checks fail
   - **Impact**: Skips strategy entirely, returns NO_TRADE

2. **ML Predictions** (`generate_signals()`)
   - Blocks if: `ensemble_predictor` fails or returns empty
   - **Impact**: Returns NO_TRADE with reason `PREDICTION_UNAVAILABLE`

3. **Strategy Engine** (`strategy_engine.py:recommend_strategy()`)
   - Blocks if: `confidence < 0.5` OR `liquidity_score < 40`
   - Blocks if: `sentiment != BULLISH/BEARISH` AND `liquidity_score < 70` (for NEUTRAL)
   - Blocks if: `bullish_score <= 60` AND `bearish_score <= 60` (for BULLISH/BEARISH)
   - **Impact**: Returns NO_TRADE

4. **Confidence Filter** (`generate_signals()`)
   - Blocks if: `confidence < min_confidence` (0.5)
   - **Impact**: Converts TRADE to NO_TRADE with reason `LOW_CONFIDENCE`

5. **LIVE Safety Lock** (`run_cycle()`)
   - Blocks if: `not sim_mode and not live_trade_enabled`
   - **Impact**: Filters out all TRADE signals, sets `trade_signals = []`

6. **Max Positions** (`execute_trades()`)
   - Blocks if: `current_positions >= max_positions` (5)
   - **Impact**: Skips execution

7. **Paper Executor** (`paper_executor.py:execute_trade()`)
   - Blocks if: `action != 'TRADE'` OR `max_positions reached` OR `contract not found`
   - **Impact**: Returns None (no position created)
