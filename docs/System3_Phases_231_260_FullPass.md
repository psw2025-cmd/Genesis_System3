System3 Phases 231–260 – Full-Pass Implementation Specification

AngelOne-only • DRY-RUN • Virtual Execution + Threshold Integration

This document defines concrete, implementation-ready specs for System3 Phases 231–260 in C:\Genesis_System3.

Assumptions:

Phases 1–230 are already implemented and passing diagnostics.

System is AngelOne-only (no Binance/crypto in this project).

System is currently DRY-RUN only (no real orders).

Existing files from earlier phases (already present):

storage/live/angel_index_ai_signals.csv

storage/live/angel_index_ai_signals_curated.csv

storage/live/angel_index_ai_signals_with_forward.csv

storage/live/angel_index_ai_signals_reconciled.csv

storage/meta/system3_threshold_candidates.json

logs/research/system3_signal_edge_report.md, etc.

The main goals of 231–260:

Use optimized thresholds (from phase 223) inside the live engine.

Add a complete virtual execution pipeline (plan orders, risk checks, virtual trades store).

Add PnL + diagnostics for virtual trades.

Provide a single diagnostics script for phases 231–260.

All changes must be DRY-RUN safe and AngelOne-only.

PHASE 231 – Threshold Loader & Registry

Objective: Provide a single, robust place to load BUY/SELL thresholds for each underlying.

Files:

New module: core/engine/threshold_loader.py

Existing meta file (may already exist): storage/meta/system3_threshold_candidates.json

Log: logs/research/system3_threshold_loader.log

Spec:

Implement function:

def load_thresholds(prefer_candidates: bool = True) -> dict:
    """
    Returns a dict:
    {
        "default": {"buy": float, "sell": float},
        "NIFTY":   {"buy": float, "sell": float},
        "BANKNIFTY": {...},
        "FINNIFTY": {...},
        "MIDCPNIFTY": {...},
        "SENSEX": {...}
    }
    """


Behavior:

If prefer_candidates is True:

Try to load storage/meta/system3_threshold_candidates.json.

Expected structure:

{
  "default": { "buy": 0.12, "sell": -0.10 },
  "NIFTY":   { "buy": 0.12, "sell": -0.10 },
  "BANKNIFTY": { ... }
}


If file missing, invalid, or missing some underlyings:

Log a WARN into logs/research/system3_threshold_loader.log.

Fill missing entries from a hardcoded default:

DEFAULT_THRESHOLDS = {"buy": 0.12, "sell": -0.10}


Return a fully-populated dict with all 5 indices + "default" key.

Must never crash:

On any error, log and return a dict with only default thresholds for all underlyings.

PHASE 232 – Live Engine Threshold Application

Objective: Use the thresholds from Phase 231 inside the live signal engine.

Files:

Modify: core/engine/system3_signal_engine.py

Log (reuse existing engine logs).

Spec:

At engine initialization (or at the start of each main run cycle):

Import and call:

from core.engine.threshold_loader import load_thresholds
thresholds_by_underlying = load_thresholds(prefer_candidates=True)


When converting raw scores to BUY/SELL/HOLD per row:

For each row with underlying:

t = thresholds_by_underlying.get(row['underlying'], thresholds_by_underlying['default'])
buy_thr = t['buy']
sell_thr = t['sell']


Apply:

If final_score >= buy_thr → BUY

Else if final_score <= sell_thr → SELL

Else → HOLD

Log a single summary line at the start of session:

Example:

Loaded thresholds: default(buy=0.12, sell=-0.10), NIFTY(0.13/-0.11), BANKNIFTY(0.14/-0.12), ...


If threshold loader fails (returns only default), engine still runs with default thresholds.

PHASE 233 – Virtual Order Models

Objective: Define structured Python models for planned orders and risk decisions.

Files:

New: core/execution/order_models.py

Spec:

Define dataclasses (or simple NamedTuple / pydantic-style, but no external package):

from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class PlannedOrder:
    ts: str
    underlying: str
    strike: float
    option_type: str   # "CE" or "PE"
    side: str          # "BUY" or "SELL"
    expiry: str
    ltp: float
    final_score: float
    ai_score: float
    lots: int
    reason: str
    snapshot_id: Optional[int] = None

@dataclass
class RiskDecision:
    approved: bool
    adjusted_lots: int
    reason: str
    risk_flags: Dict[str, str]


These are pure Python models, no broker or API dependencies.

PHASE 234 – Live Trading Config (Flags & Limits)

Objective: Provide a central JSON config for trading flags and risk limits.

Files:

New: config/live_trade_config.json

New: core/config/live_trade_config_loader.py

Spec:

Create config/live_trade_config.json with at least:

{
  "LIVE_TRADING_ENABLED": false,
  "USE_ANGELONE_LIVE_EXECUTION": false,
  "MAX_DAILY_LOSS": 5000,
  "MAX_OPEN_POSITIONS": 3,
  "MAX_LOTS_PER_TRADE": 1,
  "AUTO_SQUARE_OFF_TIME": "15:20",
  "SYMBOL_WHITELIST": ["NIFTY", "BANKNIFTY"],
  "MIN_SCORE_FOR_TRADE": 0.12
}


Important: Both flags must stay false by default.

core/config/live_trade_config_loader.py:

Implement:

import json
import os

def load_live_trade_config() -> dict:
    # load JSON, apply defaults, never crash


On missing/invalid config:

Log a WARN and return safe defaults with LIVE_TRADING_ENABLED = False.

PHASE 235 – Risk Guard Core

Objective: Central risk checks for virtual orders (no real API).

Files:

New: core/execution/risk_guard.py

Log: logs/risk/system3_risk_guard.log

Spec:

Functions:

from typing import List, Tuple
from .order_models import PlannedOrder, RiskDecision

def check_per_trade_limits(order: PlannedOrder, risk_config: dict) -> RiskDecision:
    ...

def check_daily_limits(orders: List[PlannedOrder],
                       current_pnl: float,
                       open_positions_count: int,
                       risk_config: dict) -> Tuple[List[RiskDecision], dict]:
    """
    Returns list of RiskDecision (aligned to orders)
    and a summary dict of risk metrics.
    """

def apply_global_safety_flags(orders: List[PlannedOrder],
                              risk_config: dict,
                              live_trade_config: dict) -> List[RiskDecision]:
    ...


Logic (example, can be simple but must exist):

If order.underlying not in SYMBOL_WHITELIST → approved=False.

If order.final_score < MIN_SCORE_FOR_TRADE → approved=False.

If planned lots > MAX_LOTS_PER_TRADE → reduce to max, mark reason.

If current_pnl <= -MAX_DAILY_LOSS → reject all, flag “MAX_DAILY_LOSS_REACHED”.

All decisions and risk flags must be logged (short summary) into logs/risk/system3_risk_guard.log.

Risk guard must never crash; on error, return approved=False with reason "RISK_GUARD_ERROR".

PHASE 236 – Virtual Execution Engine

Objective: Convert signals + thresholds into virtual orders and log them.

Files:

New: core/execution/live_execution_engine.py

Store: storage/live/angel_virtual_orders.csv

Log: logs/execution/system3_virtual_execution.log

Spec:

Functions:

import pandas as pd
from typing import List
from .order_models import PlannedOrder
from .risk_guard import check_per_trade_limits, check_daily_limits, apply_global_safety_flags

def plan_orders_from_signals(signals_df: pd.DataFrame,
                             thresholds_by_underlying: dict,
                             live_trade_config: dict) -> List[PlannedOrder]:
    ...

def run_risk_checks_on_orders(planned_orders: List[PlannedOrder],
                              risk_config: dict,
                              current_pnl: float,
                              open_positions_count: int) -> List[RiskDecision]:
    ...

def log_virtual_orders(planned_orders: List[PlannedOrder],
                       risk_decisions: List[RiskDecision],
                       csv_path: str = "storage/live/angel_virtual_orders.csv") -> None:
    ...


plan_orders_from_signals:

Input signals_df is for one snapshot or more, containing at least:

ts, underlying, strike, side (“BUY”/“SELL”), option_type (“CE”/“PE”), expiry, ltp, final_score, ai_score.

For each row with side ∈ {BUY, SELL}:

Build a PlannedOrder with lots=1 (or simple logic from config).

Ignore HOLD rows.

log_virtual_orders:

Append to storage/live/angel_virtual_orders.csv with columns:

ts, underlying, strike, option_type, side, expiry,
ltp, final_score, ai_score, lots, approved, adjusted_lots,
risk_reason, risk_flags_json, snapshot_id


Create file with header if missing.

Must handle file lock / IO errors gracefully: log WARN and continue.

All of this is virtual only:

No AngelOne SmartAPI imports here.

No network calls inside this module.

PHASE 237 – Wiring Virtual Execution into Live Loop

Objective: Call the virtual engine from the main System3 live loop.

Files:

Modify: main live script(s), e.g.:

system3_live_day_autopilot.py (or whichever file drives snapshots)

or core loop inside core/engine/system3_signal_engine.py

Reuse: load_thresholds, load_live_trade_config, live_execution_engine.

Spec:

After a snapshot’s signals are computed and written to angel_index_ai_signals.csv:

Build a DataFrame for that snapshot only (e.g. the last 30 rows you just generated).

Call:

from core.engine.threshold_loader import load_thresholds
from core.config.live_trade_config_loader import load_live_trade_config
from core.execution.live_execution_engine import (
    plan_orders_from_signals,
    run_risk_checks_on_orders,
    log_virtual_orders,
)

thresholds = load_thresholds(prefer_candidates=True)
live_cfg = load_live_trade_config()
planned_orders = plan_orders_from_signals(snapshot_df, thresholds, live_cfg)

# current_pnl and open_positions_count can be 0 for now (Phase 237),
# later phases can enhance.
risk_decisions = run_risk_checks_on_orders(planned_orders, live_cfg, 0.0, 0)

log_virtual_orders(planned_orders, risk_decisions)


Error handling:

Wrap this entire block in try/except:

On exception → log stacktrace to logs/execution/system3_virtual_execution.log.

Do not crash the autopilot loop.

This path must run even while LIVE_TRADING_ENABLED = false.
It is pure virtual trade logging.

PHASE 238 – Virtual Orders Store & Schema Guard

Objective: Ensure angel_virtual_orders.csv is consistent and well-formed.

Files:

New utility script: system3_virtual_orders_schema_check.py

Log: logs/execution/system3_virtual_orders_schema_report.md

Spec:

Script behavior:

Open storage/live/angel_virtual_orders.csv if it exists.

Validate columns:

REQUIRED_COLS = [
    "ts", "underlying", "strike", "option_type", "side", "expiry",
    "ltp", "final_score", "ai_score", "lots", "approved",
    "adjusted_lots", "risk_reason", "risk_flags_json", "snapshot_id"
]


If file missing → write a short report (WARN: file not found) and exit OK.

For existing file:

Check:

All REQUIRED_COLS present.

No obvious type corruption (e.g., non-numeric in lots where possible).

Write markdown summary to logs/execution/system3_virtual_orders_schema_report.md:

Row count.

First/last timestamp.

Any missing columns.

Must be callable safely from diagnostics script.

PHASE 239 – Virtual PnL Joiner (Forward Returns)

Objective: Join virtual trades with forward returns to measure edge.

Files:

New script: system3_virtual_trades_enrichment.py

Inputs:

storage/live/angel_virtual_orders.csv

storage/live/angel_index_ai_signals_with_forward.csv

Output:

storage/live/angel_virtual_orders_with_pnl.csv

Log:

logs/research/system3_virtual_trades_enrichment.log

Spec:

Matching logic:

Read both CSVs.

Join on keys:

ts

underlying

strike

side

option_type

expiry

From angel_index_ai_signals_with_forward.csv expect columns like:

forward_ret_1, forward_ret_3, forward_ret_5 (example names from Phase 221).

For each virtual trade, compute:

pnl_1 = forward_ret_1 * lots

pnl_3 = forward_ret_3 * lots

etc. (if available).

Write enriched CSV:

storage/live/angel_virtual_orders_with_pnl.csv

Handle missing forward rows:

If no match → still keep the order, with NaN for forward returns.

Log counts:

total virtual trades

matched trades

unmatched trades

On missing inputs:

If either CSV missing → log WARN and exit gracefully.

PHASE 240 – Virtual PnL Daily Report

Objective: Produce daily PnL summaries by underlying and overall.

Files:

New script: system3_virtual_trades_summary.py

Input:

storage/live/angel_virtual_orders_with_pnl.csv

Output:

logs/research/system3_virtual_trades_pnl_report.md

Spec:

For each trading day and underlying:

Aggregate:

num_trades

num_wins (pnl_1 > 0)

num_losses (pnl_1 < 0)

win_rate

total_pnl_1

avg_pnl_1

Also compute overall totals.

Write markdown report with:

Per-day table.

Per-underlying table.

Overall summary.

If input file missing or empty:

Write a short report saying “no virtual trades available”.

No plots are required; text tables only.

PHASE 241 – Virtual Trade Diagnostics & Sanity Checks

Objective: Sanity-check virtual trades and edge.

Files:

New script: system3_virtual_trades_diagnostics.py

Output:

logs/research/system3_virtual_trades_diagnostics.md

Spec:

Use data from:

storage/live/angel_virtual_orders_with_pnl.csv

Check for:

Any trades violating basic rules:

lots <= 0

unknown underlyings

trades with extremely large absolute pnl (outliers).

Confirm that BUY trades tend to align with positive forward returns (basic correlation check).

Summarize:

Count of anomalies.

Simple correlation estimate between final_score and pnl_1.

Never crash on missing data; log WARN and exit.

PHASE 242 – Alert Hooks (Log-Only)

Objective: Prepare a minimal alert hook (log-only, no external calls).

Files:

New: core/monitoring/alert_hooks.py

Log: logs/monitoring/system3_alerts.log

Spec:

Functions:

def log_virtual_trade_alert(message: str) -> None:
    """
    For now, only append alert messages to system3_alerts.log.
    Future: WhatsApp/email integration.
    """


Integration:

In system3_virtual_trades_diagnostics.py, if:

daily loss (pnl_1) < -MAX_DAILY_LOSS, or

win_rate < some threshold (e.g., 40%)

Call log_virtual_trade_alert with a short summary.

No external APIs; file-log only.

PHASE 243 – Threshold Evolution Tracker

Objective: Track how thresholds change over time.

Files:

New script: system3_threshold_evolution_tracker.py

Input:

storage/meta/system3_threshold_candidates.json

Output:

storage/meta/system3_threshold_history.csv

Log:

logs/research/system3_threshold_evolution.log

Spec:

On each run:

Load current candidates JSON.

Append a new row into system3_threshold_history.csv:

run_ts, underlying, buy, sell


One row per underlying plus default.

Use current timestamp (now).

Handle missing JSON gracefully.

PHASE 244 – Score-to-Trade Attribution Report

Objective: Explain which score components drive most trades.

Files:

New script: system3_score_to_trade_attribution.py

Input:

storage/live/angel_virtual_orders_with_pnl.csv

storage/live/angel_index_ai_signals.csv (for score components)

Output:

logs/research/system3_score_to_trade_attribution.md

Spec:

Join virtual trades with underlying signal rows to get:

final_score, ai_score, greeks_score, trend_score, etc.

For trades in top final_score deciles:

Report:

average of each score component

win-rate per decile.

Write a human-readable markdown report.

PHASE 245 – Symbol Participation Summary

Objective: See how much each underlying participates in trades.

Files:

New script: system3_symbol_participation_summary.py

Input:

storage/live/angel_virtual_orders.csv

Output:

logs/research/system3_symbol_participation_summary.md

Spec:

For each underlying:

Count num_trades, num_BUY, num_SELL.

For each expiry:

Basic count of trades.

Single markdown file summarizing.

PHASE 246 – Trade Density vs Volatility Regime

Objective: Compare trade counts vs vol regimes (Phase 217).

Files:

New script: system3_trade_density_vs_regime.py

Inputs:

storage/live/angel_virtual_orders.csv

storage/meta/system3_vol_regimes.csv

Output:

logs/research/system3_trade_density_vs_regime.md

Spec:

Map each trade’s date + underlying to a volatility regime (LOW/NORMAL/HIGH).

Compute:

Trades per regime.

Win-rate and average PnL per regime (if PnL enriched exists; else just counts).

Text-only report.

PHASE 247 – Edge-by-Score-Bucket Tracker

Objective: Maintain an ongoing table of edge per score bucket.

Files:

New script: system3_edge_by_score_bucket_tracker.py

Input:

storage/live/angel_virtual_orders_with_pnl.csv

Output:

storage/meta/system3_edge_by_score_bucket.csv

Log:

logs/research/system3_edge_by_score_bucket.log

Spec:

Define score buckets, e.g.:

(-inf, 0.0), [0.0, 0.1), [0.1, 0.2), [0.2, 0.3), [0.3, inf)

For each bucket:

Count trades.

Average PnL.

Win-rate.

Append/update CSV with bucket metrics.

PHASE 248 – Failure-Path Hardening

Objective: Ensure that new modules never crash the main loop.

Files:

Modify:

Any places where new scripts/functions are called from the main loop or daily runner.

Log:

Use existing logs, plus small additional WARN lines.

Spec:

Wherever you call:

system3_virtual_trades_enrichment.py

system3_virtual_trades_summary.py

system3_virtual_trades_diagnostics.py

etc.

Wrap them so that:

Exceptions are caught and logged as WARN.

Main system3_autorun_master and live loop keep running.

Confirm: no new functions raise unhandled exceptions in normal operation.

PHASE 249 – Phases 231–260 Diagnostics Script

Objective: Single diagnostics entry-point for 231–260.

Files:

New: system3_phase_231_260_diagnostics.py

Output:

docs/system3_phases_231_260_implementation_status.md

Spec:

Script should:

Import and run:

system3_virtual_orders_schema_check.py

system3_virtual_trades_enrichment.py (dry run with graceful behavior if data missing)

system3_virtual_trades_summary.py

system3_virtual_trades_diagnostics.py

system3_threshold_evolution_tracker.py

Other small scripts as needed (245–247).

Build a table:

Phase	Component / Script	Status (OK/WARN/ERROR)	Notes
231	Threshold loader	OK / WARN / ERROR	
...			

Also print a short summary to the console (like the 201–230 diagnostics):

How many OK / WARN / ERROR.

Path of the markdown status file.

PHASE 250–260 – Reserved for Future Expansion

For now, Phase 250–260 are logically covered by the above scripts and will be considered:

250: Threshold history & evolution (part of 243 + diagnostics)

251–260: Aggregate research diagnostics (rolled into 249)

No extra implementation required beyond what is already specified above.

Implementation & Validation Checklist

Implement all modules/scripts exactly as per paths above.

Ensure no live trading:

LIVE_TRADING_ENABLED = false

USE_ANGELONE_LIVE_EXECUTION = false

After implementation, run:

python system3_phase_231_260_diagnostics.py


Expect all phases OK or benign WARN (e.g., “no virtual trades yet”).

Confirm that:

storage/live/angel_virtual_orders.csv is created and updated during live DRY-RUN.

storage/live/angel_virtual_orders_with_pnl.csv is created once forward data exists.

logs/research/system3_virtual_trades_pnl_report.md and other reports are generated.

You can now:

Save this as docs/System3_Phases_231_260_FullPass.md in C:\Genesis_System3\docs.

Tell Cursor:

“Use docs/System3_Phases_231_260_FullPass.md and fully implement phases 231–260, then run python system3_phase_231_260_diagnostics.py and show me the summary.”