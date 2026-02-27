# System3 – Phases 131–200 Ultra Master Angel Plan
Master implementation + cursor-agent instructions (AngelOne-only, DRY-RUN safe)

File name (recommended):
`docs/system3_phases_131_200_ultra_master_angel.md`

Root project folder:
`C:\Genesis_System3`

> This document is written for Cursor / AI agent to implement all remaining
> System3 Ultra Master phases 131–200 in a **safe**, **AngelOne-only**,
> **DRY-RUN-only** way, fully compatible with the existing System3 codebase.


------------------------------------------------------------
GLOBAL RULES (MUST FOLLOW FOR ALL PHASES)
------------------------------------------------------------

1) Broker scope
   - ONLY AngelOne is allowed.
   - Do NOT import or reference Binance, crypto, or any other broker.
   - If you need broker-related info, always use the existing AngelOne layers
     already in `core/engine` and `core/models/angel_one`.

2) DRY-RUN safety
   - Absolutely NO REAL ORDER placement.
   - All trade-related phases must:
     - Read from **dry-run ledgers**, signals, or plans only.
     - Write to simulation or analysis outputs only.
   - Never send anything to SmartAPI that places, modifies, or cancels an order.

3) Baseline & Ultra protection
   - Baseline folders must not be modified:
     - `core/models/angel_one/`
     - Existing baseline phases 1–130
   - All new work for phases 131–200 must be in **new files only**:
     - `core/engine/system3_phaseXXX_*.py`
     - `storage/ultra/phaseXXX_*` (for outputs)
     - `docs/system3_phaseXXX_*` (for docs)

4) Naming convention
   - Python file for phase N:
     `core/engine/system3_phaseNNN_<short_name>.py`
   - Main entry function inside each file:
     `def run_phaseNNN_<short_name>(...)`
   - CLI entry at bottom of each file:
     ```python
     if __name__ == "__main__":
         run_phaseNNN_<short_name>()
     ```

5) Logging & storage
   - Use `storage/ultra/phaseNNN_*` for outputs:
     - CSV / JSON / MD
   - Use the existing `logs/` folder for log output if needed.
   - Prefer pandas + CSV/Parquet for tabular data; JSON for configs; MD/TXT for reports.

6) Config loading pattern
   - Use the existing config loaders where possible:
     - `config/system3_ultra_config.json` (if exists)
     - `storage/config/*` for thresholds / safety / risk
   - If a new config is needed:
     - Create JSON in `storage/config/phaseNNN_<name>_config.json`
     - Always provide safe defaults if file missing.

7) Error handling
   - Each `run_phaseNNN_*` must:
     - Catch exceptions
     - Log to console in a clean format
     - Never crash run_system3 or system3_ultra menu
   - On error: write a short MD report in `storage/ultra/phaseNNN_error_report.md`.

8) Menu integration
   - Do NOT modify existing menus in this document.
   - Menu integration will be handled separately in `system3_ultra.py` once
     all files are created and verified.

9) Idempotency
   - Each phase run MUST be safe to re-run many times.
   - Re-running must NOT corrupt data or create inconsistent state.
   - Overwrites are allowed only for outputs in `storage/ultra/phaseNNN_*`.

10) Reuse existing schemas
    - Use existing ledger schema from phases 101–130 where applicable.
    - Use the same PnL and trade-plan structures:
      - 22-column ledger
      - existing DRY_RUN execution format


============================================================
PHASE GROUP 131–135 – MASTER SESSION BOOTSTRAP (ANGEL-ONLY)
============================================================

GOAL: Build a “Master Angel Session” skeleton that can:
- Read configs
- Check system health
- Validate safety
- Prepare a DRY-RUN session plan
- Produce a human-readable summary

All WITHOUT placing real orders.

---------------------------------
Phase 131 – Master Session Config
---------------------------------

File:
- `core/engine/system3_phase131_master_session_config.py`

Function:
- `run_phase131_master_session_config(mode: str = "ANGEL_ONLY")`

Inputs:
- Reads base ultra config (if exists):
  - `storage/config/system3_ultra_master_config.json` (optional)
- If missing, create with safe defaults.

Outputs:
- JSON: `storage/config/system3_master_session_config.json`
- MD:   `storage/ultra/phase131_master_session_config_report.md`

Logic:
1. Start with safe defaults:
   - `"broker": "ANGEL_ONE"`
   - `"live_trading_enabled": false`
   - `"max_daily_trades": 10`
   - `"max_trades_per_underlying": 3`
   - `"max_loss_percent": 1.0`
   - `"dry_run": true`
2. If `system3_ultra_master_config.json` exists, merge in overrides but:
   - NEVER allow `live_trading_enabled` to become true here.
3. Save final config to `system3_master_session_config.json`.
4. Write MD summary with:
   - Effective config
   - Any overrides applied
   - Safety flags state

Verification:
- If JSON missing initially → created with defaults.
- Re-run → merges and overwrites only that one JSON safely.
- MD clearly states `dry_run: true` and `live_trading_enabled: false`.


------------------------------------------
Phase 132 – Master Session Health Snapshot
------------------------------------------

File:
- `core/engine/system3_phase132_master_health_snapshot.py`

Function:
- `run_phase132_master_health_snapshot()`

Inputs:
- Reads:
  - `storage/config/system3_master_session_config.json`
  - Existing health/info from:
    - `core/engine/angel_health_check.py` (if exists)
    - Or run a light inline AngelOne capability check using existing APIs in safe mode.

Outputs:
- JSON: `storage/ultra/phase132_master_health_snapshot.json`
- MD:   `storage/ultra/phase132_master_health_snapshot.md`

Logic:
1. Load master config (phase 131).
2. Gather minimal health info:
   - Python version
   - venv status (detect via sys.executable)
   - AngelOne connectivity: try a **SAFE** call (like get profile or holdings) but DO NOT place orders.
3. Classify status:
   - `"broker_status": "OK" | "WARN" | "ERROR"`
   - `"env_status": "OK" | "WARN" | "ERROR"`
4. Write JSON with full snapshot.
5. Write MD with:
   - Table of health checks
   - Summary line: `MASTER_HEALTH_STATUS = OK/WARN/ERROR`

Verification:
- Running without broker credentials: should not crash, but mark broker_status = "WARN" or "ERROR".
- JSON must always exist after phase run.


----------------------------------------
Phase 133 – Master Safety & Kill-Switch
----------------------------------------

File:
- `core/engine/system3_phase133_master_safety_guard.py`

Function:
- `run_phase133_master_safety_guard()`

Inputs:
- `storage/config/system3_master_session_config.json`
- `storage/ultra/phase132_master_health_snapshot.json`
- Any existing safety config from:
  - `storage/config/system3_safety_config.json` (optional)

Outputs:
- JSON: `storage/config/system3_master_safety_state.json`
- MD:   `storage/ultra/phase133_master_safety_report.md`

Logic:
1. Read config + health snapshot.
2. Compute safety flags:
   - `kill_switch_active`: true if any critical check failed.
   - `live_trading_allowed`: must remain false in this phase.
   - `max_risk_percent_per_day`: from config or default 1.0.
3. If `kill_switch_active` → future live trading (if ever enabled) should be blocked.
4. Save safety state JSON.
5. MD report:
   - Safety flags
   - Reasons for kill-switch
   - Explicit line: `LIVE_TRADING_ALLOWED: FALSE (MASTER MODE)`

Verification:
- Even if configs try to set live_trading_enabled true, this phase MUST clamp to false.
- Re-run yields consistent safety JSON.


-----------------------------------
Phase 134 – Master DRY-RUN Session Plan
-----------------------------------

File:
- `core/engine/system3_phase134_master_session_plan.py`

Function:
- `run_phase134_master_session_plan()`

Inputs:
- `system3_master_session_config.json`
- `system3_master_safety_state.json`
- Ultra thresholds from prior phases (if available)

Outputs:
- JSON: `storage/ultra/phase134_master_session_plan.json`
- MD:   `storage/ultra/phase134_master_session_plan.md`

Logic:
1. Read config + safety state.
2. If `kill_switch_active` → create plan with `"status": "ABORTED"`.
3. If safe:
   - Build session-level limits:
     - number of cycles
     - max indices to watch
     - DRY-RUN only
4. For each underlying (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX):
   - Mark `enabled` or `disabled` based on config (default all enabled).
5. Save JSON with structure:
   ```json
   {
     "status": "READY",
     "dry_run": true,
     "underlyings": {
       "NIFTY": {"enabled": true, ... },
       ...
     },
     "max_trades_per_underlying": 3,
     "max_daily_trades": 10
   }
   ```
6. MD summary with table of underlyings and limits.

Verification:
- Plan must always have `"dry_run": true`.
- If kill switch active → `"status": "ABORTED"`.


-------------------------------------------
Phase 135 – Master Session Human Summary MD
-------------------------------------------

File:
- `core/engine/system3_phase135_master_session_summary.py`

Function:
- `run_phase135_master_session_summary()`

Inputs:
- Outputs from phases 131–134:
  - master config
  - health snapshot
  - safety state
  - session plan

Outputs:
- MD: `storage/ultra/phase135_master_session_summary.md`

Logic:
1. Load all JSONs.
2. Summarize into 4 sections:
   - Config
   - Health
   - Safety
   - Plan
3. Add final line clearly:
   - `MASTER_SESSION_READY: YES/NO`
   - `DRY_RUN_ONLY: YES`
   - `BROKER: ANGEL_ONE`
4. No JSON outputs (MD only).

Verification:
- Easy to read manually before market.
- Re-running updates only this MD.


====================================================
PHASE GROUP 136–140 – ANGEL SYMBOLS, EXPIRY, STRIKES
====================================================

GOAL: Build a clean Angel-only symbol universe and risk metadata layer.

-----------------------------------
Phase 136 – Angel Symbol Universe
-----------------------------------

File:
- `core/engine/system3_phase136_angel_symbol_universe.py`

Function:
- `run_phase136_angel_symbol_universe()`

Inputs:
- NONE (hard-coded list of supported Angel index symbols):
  - NIFTY
  - BANKNIFTY
  - FINNIFTY
  - MIDCPNIFTY
  - SENSEX

Outputs:
- CSV: `storage/ultra/phase136_angel_symbol_universe.csv`
- JSON: `storage/ultra/phase136_angel_symbol_universe.json`

Logic:
1. Create dataframe with columns:
   - `underlying`
   - `angel_symbol`
   - `segment` (e.g., "NSEFO")
   - `enabled` (default true)
2. Save CSV+JSON.
3. No broker calls; static metadata only.

Verification:
- Re-run must overwrite CSV/JSON safely.


---------------------------------
Phase 137 – Expiry & Calendar Map
---------------------------------

File:
- `core/engine/system3_phase137_expiry_calendar_map.py`

Function:
- `run_phase137_expiry_calendar_map()`

Inputs:
- `phase136` universe
- Optionally an AngelOne safe method to fetch expiries (if available in dry API).

Outputs:
- CSV: `storage/ultra/phase137_expiry_calendar_map.csv`

Logic:
1. For each underlying:
   - If live expiry fetch is possible from existing code (safe calls), use it.
   - Else approximate next 4 weekly/monthly expiries as dates only (no API).
2. Columns:
   - `underlying`
   - `expiry_date`
   - `type` (WEEKLY/MONTHLY)
   - `priority` (1=nearest, etc)
3. Save CSV.

Verification:
- Should not crash if no live expiry API; just approximate from today’s date.


------------------------------------
Phase 138 – Angel Risk Tier Assignment
------------------------------------

File:
- `core/engine/system3_phase138_risk_tier_assignment.py`

Function:
- `run_phase138_risk_tier_assignment()`

Inputs:
- `phase136` universe
- Optionally volatility/ATR estimates from earlier phases (if available).

Outputs:
- CSV: `storage/ultra/phase138_risk_tiers.csv`

Logic:
1. For each underlying, assign a tier:
   - Example:
     - BANKNIFTY, MIDCPNIFTY → "HIGH"
     - NIFTY, FINNIFTY → "MEDIUM"
     - SENSEX → "LOW"
2. Add columns:
   - `underlying`
   - `risk_tier` ("LOW"/"MEDIUM"/"HIGH")
   - `max_trades` (e.g., 2 for HIGH, 3 for MEDIUM, 4 for LOW)
   - `max_lot_per_trade` (1 for now)
3. Save CSV.

Verification:
- Tiers are deterministic and do not depend on external calls.


-----------------------------------------
Phase 139 – Lot Size & Margin Estimation
-----------------------------------------

File:
- `core/engine/system3_phase139_lot_margin_estimator.py`

Function:
- `run_phase139_lot_margin_estimator()`

Inputs:
- `phase136` universe
- Known lot sizes (hard-coded as constants) for each underlying.

Outputs:
- CSV: `storage/ultra/phase139_lot_margin.csv`

Logic:
1. Use known or approximated lot sizes for each index.
2. Estimate “typical” margin for 1 lot (simple constant per index).
3. Columns:
   - `underlying`
   - `lot_size`
   - `est_margin_per_lot`
   - `base_capital_unit` (e.g. 1 lot * est_margin).
4. Save CSV.

Verification:
- This is only an approximate metadata layer; must not use real broker margin APIs.


----------------------------------------------
Phase 140 – Capital Guard & One-Lot Guardrail
----------------------------------------------

File:
- `core/engine/system3_phase140_capital_guardrail.py`

Function:
- `run_phase140_capital_guardrail(total_test_capital: float = 50000.0)`

Inputs:
- `phase139` lot/margin CSV
- Total test capital parameter (default 50k INR).

Outputs:
- CSV: `storage/ultra/phase140_capital_guardrail.csv`
- MD:  `storage/ultra/phase140_capital_guardrail.md`

Logic:
1. Compute for each index whether 1 lot fits into test capital safely.
2. Derive:
   - `max_lots_allowed` (0 or 1 given your goal “1 lot only”).
   - `capital_usage_percent` for 1 lot.
3. Enforce:
   - For production test, always clamp to at most 1 lot.
4. MD summary:
   - Show which underlyings are allowed for 1-lot test.
   - Explicit list: “ONE-LOT ONLY TEST MODE ACTIVE”.

Verification:
- Must never recommend more than 1 lot per trade for your chosen mode.
- Re-run just refreshes metadata.


==========================================================
PHASE GROUP 141–145 – FILL QUALITY, SLIPPAGE, SPREAD METRICS
==========================================================

GOAL: Build DRY-RUN evaluation tools for execution quality (no real orders).

-------------------------------------------
Phase 141 – Spread & Liquidity Estimation
-------------------------------------------

File:
- `core/engine/system3_phase141_spread_liquidity_estimator.py`

Function:
- `run_phase141_spread_liquidity_estimator()`

Inputs:
- Existing snapshot CSVs from live signals
  (same ones used by prior phases, location already defined in System3).

Outputs:
- CSV: `storage/ultra/phase141_spread_liquidity_metrics.csv`

Logic:
1. For each option leg in recent snapshots:
   - Use best bid/ask (if available) to estimate spread.
   - If only LTP is available, approximate a synthetic spread.
2. Columns:
   - `timestamp`
   - `underlying`
   - `strike`
   - `side`
   - `ltp`
   - `spread_estimate`
   - `liquidity_score` (simple heuristic 0–1).
3. Save CSV.

Verification:
- Should handle missing bid/ask gracefully.


--------------------------------------------
Phase 142 – DRY-RUN Slippage Calculator (Ledger)
--------------------------------------------

File:
- `core/engine/system3_phase142_slippage_calculator.py`

Function:
- `run_phase142_slippage_calculator()`

Inputs:
- DRY-RUN ledger from earlier phases (22 columns CSV).
- Spread metrics from phase 141.

Outputs:
- CSV: `storage/ultra/phase142_slippage_results.csv`
- MD:  `storage/ultra/phase142_slippage_summary.md`

Logic:
1. Join DRY-RUN fills with spread/liquidity metrics.
2. Estimate “ideal fill” vs simulated fill:
   - `slippage_amount`
   - `slippage_percent`
3. Summarize by underlying:
   - average slippage
   - worst case
4. MD report summarizing per-underlying slippage.

Verification:
- Works even if only a few dummy trades exist.


----------------------------------------------
Phase 143 – Execution Quality & Fill Heatmap
----------------------------------------------

File:
- `core/engine/system3_phase143_execution_quality.py`

Function:
- `run_phase143_execution_quality()`

Inputs:
- Output from phase 142.

Outputs:
- CSV: `storage/ultra/phase143_execution_quality.csv`
- MD:  `storage/ultra/phase143_execution_quality.md`

Logic:
1. Classify each trade’s execution quality:
   - GOOD, OK, POOR based on slippage thresholds.
2. Compute metrics:
   - `good_fill_rate`
   - `poor_fill_rate`
   - per underlyings.
3. MD summary with simple ASCII “heatmap” style table.

Verification:
- No new external data; pure post-processing.


----------------------------------------------
Phase 144 – DRY-RUN PnL vs Execution Scenario
----------------------------------------------

File:
- `core/engine/system3_phase144_pnl_vs_execution_scenario.py`

Function:
- `run_phase144_pnl_vs_execution_scenario()`

Inputs:
- Original DRY-RUN ledger
- Slippage results (phase 142)
- Execution quality (phase 143)

Outputs:
- CSV: `storage/ultra/phase144_pnl_execution_scenarios.csv`
- MD:  `storage/ultra/phase144_pnl_execution_scenarios.md`

Logic:
1. For each trade, recompute hypothetical PnL under:
   - Ideal fill (no slippage)
   - Realistic slippage (from phase 142)
   - Worst-case allowed by spread
2. Compare:
   - `pnl_ideal`, `pnl_realistic`, `pnl_worst`
3. Summarize by underlying:
   - how much slippage reduces performance.
4. MD summarizing impact percentage.

Verification:
- Handles 0 or few trades gracefully (just prints “not enough data”).


----------------------------------------------
Phase 145 – One-Lot Test-Mode Health Report
----------------------------------------------

File:
- `core/engine/system3_phase145_one_lot_health_report.py`

Function:
- `run_phase145_one_lot_health_report()`

Inputs:
- Phases 140, 142, 143, 144 outputs.

Outputs:
- MD: `storage/ultra/phase145_one_lot_health_report.md`

Logic:
1. Summarize for 1-lot DRY-RUN testing:
   - Does 1-lot risk fit test capital comfortably?
   - Is slippage acceptable?
   - Are fills mostly GOOD/OK?
   - Are worst-case PnL scenarios within acceptable test drawdown?
2. Provide a YES/NO style conclusion per index:
   - `ONE_LOT_TEST_STATUS = SAFE / CAUTION / UNSAFE`.

Verification:
- Pure analysis; no data mutation.


==================================================
PHASE GROUP 146–155 – RESERVED META & EXTENSION LAYER
==================================================

NOTE:
- These phases are intentionally light and mostly meta/documentation helpers.
- They ensure there is NO future hole in phase numbering.
- They must not contain any risky logic or trading-related side effects.

Implement them as **simple, minimal utilities**:

146: Phase index catalog
- File: `system3_phase146_index_catalog.py`
- Output: MD + JSON listing all phases and their primary role.

147: Config inventory
- File: `system3_phase147_config_inventory.py`
- Output: MD listing all config JSON files and their purpose.

148: Storage inventory
- File: `system3_phase148_storage_inventory.py`
- Output: MD summarizing storage/ultra and storage/config files.

149: Log inventory
- File: `system3_phase149_log_inventory.py`
- Output: MD with last-modified times of major log files.

150: Phase dependency graph (static)
- File: `system3_phase150_dependency_graph.py`
- Output: JSON mapping each phase to its inputs/outputs (static mapping from hard-coded dict).

151–155: RESERVED STUBS
- Each file should exist and implement a `run_phaseXXX_stub()` which only writes an MD file:
  - `storage/ultra/phaseXXX_stub_report.md`
  - Content: “RESERVED FOR FUTURE USE – NO ACTIVE LOGIC”.

These ensure numbering is continuous without adding complexity.


===================================================
PHASE GROUP 156–170 – CAPITAL, RISK, STABILITY LOGIC
===================================================

These phases are analysis-only and operate on DRY-RUN & PnL data.

(You can keep the detailed definitions already given in previous plans. Only high-level notes here.)

Key requirements for all 156–170:
- No trading
- No broker API
- Only read PnL, ledgers, signals, thresholds, and write analysis.

Example structure per phase (156 shown; follow same pattern up to 170):

---------------------------------------------
Phase 156 – Capital Curve & Drawdown Analysis
---------------------------------------------

File:
- `core/engine/system3_phase156_capital_curve_analysis.py`

Function:
- `run_phase156_capital_curve_analysis()`

Inputs:
- DRY-RUN PnL log (from existing PnL simulator).
- Initial test capital input param (or default).

Outputs:
- CSV: `storage/ultra/phase156_capital_curve.csv`
- MD:  `storage/ultra/phase156_capital_curve_report.md`

Logic:
- Compute running capital over time using DRY-RUN PnL.
- Compute max drawdown, recovery periods.
- Summarize in MD report.

…

(Phases 157–170 follow similarly as previously defined: misfire breakdown, regime stability, threshold drift, error attribution, etc. Each reads from existing data and writes analysis only.)


==========================================================
PHASE GROUP 171–195 – RESILIENCE, BACKUP, HOLIDAY, SUMMARIES
==========================================================

All phases 171–195 are **non-trading meta/infra** modules:
- File backup
- Schema guards
- Holiday detection
- Retention policies
- Exception catalogs
- Long-run summaries

Important rules:
- Never delete user data without explicit manual action.
- You may move or compress old logs/outputs only into clearly named backup folders:
  - `storage/backups/system3/`


==================================================
PHASE GROUP 196–200 – FINAL READINESS & HUMAN GATE
==================================================

These are the **most critical final safety & readiness phases.**
They must NEVER enable live trading; they only evaluate readiness.

----------------------------------------
Phase 196 – DRY-RUN Readiness Checklist
----------------------------------------

File:
- `core/engine/system3_phase196_dry_run_readiness.py`

Function:
- `run_phase196_dry_run_readiness()`

Inputs:
- All key config + safety JSONs
- Health/safety snapshots
- One-lot health (145)

Outputs:
- MD: `storage/ultra/phase196_dry_run_readiness_report.md`

Logic:
1. Verify:
   - DRY_RUN only
   - ANGEL_ONLY
   - Capital & lot-size rules obeyed
   - No kill-switch active
2. Provide explicit YES/NO for DRY-RUN readiness.

--------------------------------------
Phase 197 – Micro Capital Test Plan MD
--------------------------------------

File:
- `core/engine/system3_phase197_micro_capital_test_plan.py`

Function:
- `run_phase197_micro_capital_test_plan()`

Inputs:
- Capital guardrail (140)
- PnL & execution reports.

Outputs:
- MD: `storage/ultra/phase197_micro_capital_test_plan.md`

Logic:
- Build a concrete 1-lot-only test plan:
  - Max trades/day
  - Allowed underlyings
  - Stop conditions (max drawdown).

---------------------------------------------
Phase 198 – Human Gate Checklist (Manual Only)
---------------------------------------------

File:
- `core/engine/system3_phase198_human_gate_checklist.py`

Function:
- `run_phase198_human_gate_checklist()`

Inputs:
- 196/197 reports.

Outputs:
- MD: `storage/ultra/phase198_human_gate_checklist.md`

Logic:
- Generate human-readable checklist:
  - Items the user must confirm manually before any future live mode.
- No automation or flag toggling.

--------------------------------------------
Phase 199 – Live Mode Guard Stub (NO REAL LIVE)
--------------------------------------------

File:
- `core/engine/system3_phase199_live_mode_guard_stub.py`

Function:
- `run_phase199_live_mode_guard_stub()`

Inputs:
- None required (optional read of safety configs).

Outputs:
- MD: `storage/ultra/phase199_live_mode_guard_stub.md`

Logic:
- Explicitly state:
  - System3 is in DRY-RUN mode only.
  - No code path in phases 131–200 enables live trading.
- This is a formal guard/memo module for future yourself.

---------------------------------------------
Phase 200 – MASTER STATUS SNAPSHOT (Angel DRY-RUN)
---------------------------------------------

File:
- `core/engine/system3_phase200_master_status_snapshot.py`

Function:
- `run_phase200_master_status_snapshot()`

Inputs:
- Master config
- Safety state
- Health snapshot
- Key phase outputs (145, 156, 196).

Outputs:
- JSON: `storage/ultra/phase200_master_status_snapshot.json`
- MD:   `storage/ultra/phase200_master_status_snapshot.md`

Logic:
1. Consolidate final view:
   - DRY_RUN: true
   - BROKER: ANGEL_ONE
   - ONE_LOT_TEST: ACTIVE
   - LAST_KNOWN_STATUS: GOOD/WARN/ERROR
2. Save JSON + MD.
3. This is the “truth source” to read at the start of any session.

Verification:
- After running phase 200, user must easily see if system is safe and test-ready.


------------------------------------------------------------
FINAL INSTRUCTIONS TO CURSOR / AI AGENT
------------------------------------------------------------

1) Create all Python files listed above under:
   - `core/engine/system3_phaseNNN_*.py`

2) For each phase:
   - Implement `run_phaseNNN_*` as specified.
   - Implement CLI guard:
     ```python
     if __name__ == "__main__":
         run_phaseNNN_*()
     ```

3) Use ONLY:
   - AngelOne-related existing modules
   - Existing ledger and PnL structures
   - DRY-RUN data and simulated fills

4) Never:
   - Place live orders
   - Modify baseline models/engines
   - Write to any config that would enable live trading

5) After implementation:
   - Prepare a single MD summary:
     `docs/system3_phases_131_200_implementation_status.md`
   - For each phase: status OK/ERROR and short note.
