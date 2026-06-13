# SYSTEM3 – PHASES 101–130  
## Dhan Full Auto Layer – Mode 1 (Indian Market Only)

Root folder:

- `C:\Genesis_System3`

Python venv:

- `C:\Genesis_System3\venv\Scripts\python.exe`

Entry scripts already used:

- `run_system3.py`
- `system3_ultra.py`

This plan adds **Dhan LIVE trading automation** (Mode 1 only), in a **safe, layered, fully-configurable** way.

Very important:

- **Baseline & Ultra existing behaviour MUST NOT change by default.**
- **All new modules are additive.**
- **Real trading only activates when explicit flags are turned ON in config.**
- Initial real tests: **1 lot per trade** only.

---

## GLOBAL RULES FOR CURSOR AGENT (MUST FOLLOW)

1. **Never overwrite existing files** without explicit instruction below.  
   - If editing an existing file, follow the exact section described and **do not change anything else**.

2. **All new code for phases 101–130 goes into:**
   - `core/engine` (phase modules)
   - `core/broker` (Angel wrappers, if needed)
   - `config` (configs & switches)
   - `storage/live` (runtime CSV/JSON logs)
   - `logs` (runtime logs) – if needed
   - `docs` (documentation only)

3. **Phase module naming convention:**

   For each phase NNN:

   - Python module path:  
     `core/engine/system3_phaseNNN_<short_name>.py`
   - Each module must expose a **single main function**:

     ```python
     def run_phaseNNN(**kwargs) -> dict:
         ...
     ```

   - Return dict must always contain:

     ```python
     {
         "phase": 101,
         "status": "OK" or "ERROR",
         "details": "short human-readable summary",
         "outputs": { ... },      # phase-specific
         "errors": [],            # list of error strings
     }
     ```

4. **Config flags MUST centralize real-trade risk.**

   New config file:

   - `config/live_trade_config.py`

   Inside this file, define:

   ```python
   LIVE_TRADING_ENABLED = False        # must remain False by default
   MAX_LIVE_TRADES_PER_DAY = 10
   MAX_LIVE_TRADES_PER_UNDERLYING = 3
   MAX_RISK_PER_TRADE_RUPEES = 2000   # adjustable later
   DEFAULT_LOTS_PER_TRADE = 1

   # Allowed underlyings for live auto
   LIVE_ALLOWED_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]

   # Angel-specific
   ANGEL_PRODUCT_TYPE = "INTRADAY"    # or as per current DhanHQ usage
   ANGEL_ORDER_VARIETY = "NORMAL"
   ANGEL_ALLOWED_ORDER_TYPES = ["MARKET"]  # for phase 1 live trading


Cursor agent: create this file exactly once and do not modify other configs unless explicitly instructed.

All phases 101–130 MUST log to storage/live/ with clear filenames and never delete existing logs.

PHASE GROUP OVERVIEW

101–105: Live Trading Config & Local Order Ledger

106–110: Dhan Execution Wrapper & Dry-Run Mirroring

111–115: Live Signal → Trade → Order Flow

116–120: Intraday Session Brain & Kill-Switch

121–125: Post-Trade Logging, PnL & Outcome Bridges

126–130: Control Panel Integration & Safety Reports

Each phase below includes:

Goal

Files to create/update

Behaviour

Inputs & Outputs

Safety rules

Verification commands & expected outputs

PHASE 101 – Live Trading Config + Sanity Check

Goal: Central config layer for live trading (Mode 1 AngelOnly) + a check script Pritam can run before market.

Files

Create config/live_trade_config.py (as described in global rules, point 4).

Create core/engine/system3_phase101_live_trade_config_check.py

Behaviour

run_phase101() must:

Import config/live_trade_config.py.

Validate:

LIVE_TRADING_ENABLED is False by default.

Limits are positive integers.

Underlyings list is non-empty.

Summarize config into a dict and return status="OK" if all checks pass, else "ERROR".

Inputs

None (only reads config).

Outputs

Returns dict as per global rules.

Also write a small JSON snapshot to:

storage/live/phase101_live_trade_config_snapshot.json

Contents example:

{
  "timestamp": "2025-11-30T09:05:00",
  "LIVE_TRADING_ENABLED": false,
  "MAX_LIVE_TRADES_PER_DAY": 10,
  "MAX_LIVE_TRADES_PER_UNDERLYING": 3,
  "DEFAULT_LOTS_PER_TRADE": 1,
  "LIVE_ALLOWED_UNDERLYINGS": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"],
  "status": "OK"
}

Safety Rules

If LIVE_TRADING_ENABLED is True, the function must still return OK but include a warning in "details" and add an "errors" entry like "WARNING: LIVE_TRADING_ENABLED=True".

Verification command (Pritam)

From:

(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase101_live_trade_config_check


Expected on success:

Console prints one summary line:
Phase101: Live trading config check OK (LIVE_TRADING_ENABLED=False, ... )

JSON file created at storage/live/phase101_live_trade_config_snapshot.json.

PHASE 102 – Local Order Ledger Schema

Goal: Define the canonical local order ledger CSV that all live trades will write to.

Files

Create core/engine/system3_phase102_order_ledger_schema.py

Behaviour

run_phase102() must:

Ensure directory storage/live/ exists.

Ensure file:
storage/live/live_orders_ledger.csv exists with header only if not present.

Header columns:

local_order_id,
timestamp,
underlying,
symbol,
expiry,
strike,
option_type,
side,
lots,
qty,
entry_price,
target_price,
stop_loss_price,
status,
broker_order_id,
broker_status,
last_update_ts,
pnl_absolute,
pnl_percent,
exit_price,
exit_reason,
notes


Do not delete existing ledger; if exists, only verify header and create if absent.

Inputs

None.

Outputs

Ensured CSV file with header.

Return dict with status="OK" and "details" including file path.

Safety Rules

Never truncate or overwrite existing rows.

If header mismatch detected, append a log entry to:

logs/phase102_order_ledger_schema.log

and return status="ERROR" with explanation.

Verification command
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase102_order_ledger_schema


Expected:

storage/live/live_orders_ledger.csv exists with correct header.

Console: Phase102: Order ledger verified/created: storage/live/live_orders_ledger.csv

PHASE 103 – Dhan Low-Level Order Wrapper (Skeleton)

Goal: Abstract Dhan DhanHQ order placement into a dedicated module.

Files

Create core/broker/dhan_live_order_wrapper.py

Behaviour

Implement a class skeleton only, no real API logic inside yet:

class AngelLiveOrderWrapper:
    def __init__(self, smart_connect=None, logger=None):
        """
        smart_connect: existing SmartConnect session if available
        logger: optional logging function
        """
        ...

    def place_market_order(self, *, symbol, qty, side, product_type, variety) -> dict:
        """
        RETURNS: {
           "status": "OK" or "ERROR",
           "broker_order_id": "<id or None>",
           "error": "<error if any>",
        }
        """
        ...

    def cancel_order(self, broker_order_id: str) -> dict:
        ...

    def get_order_status(self, broker_order_id: str) -> dict:
        ...


Currently, bodies may:

Just return "status": "ERROR", "error": "NOT_IMPLEMENTED" or "DRY_RUN"; no real Angel API calls yet.

Inputs

None directly; no CLI script for this phase.

Outputs

A reusable wrapper class for later phases.

Safety Rules

NO actual DhanHQ calls in this phase.

This is only for structure.

Verification

No direct CLI. Verification will happen once used in Phase 106+.

PHASE 104 – Trade Plan → Local Order Construction

Goal: Take rows from existing trade plan CSV and construct local ledger orders.

Files

Create core/engine/system3_phase104_tradeplan_to_orders.py

Behaviour

run_phase104() must:

Read last N rows (e.g., 50) from:

storage/live/dhan_index_ai_trades_plan.csv

(this file already exists from current System3 trade planning).

For each row with status in ["NEW", "PENDING"]:

Map columns to the ledger schema used in Phase 102.

Generate a local_order_id using deterministic scheme:

"<underlying>_<strike>_<option_type>_<yyyymmddHHMMSS>_<random_suffix>"

Append any new orders into live_orders_ledger.csv with status="PLANNED" and broker_status="NOT_SENT".

Return dict with:

outputs["orders_created"] = <int>

outputs["ledger_path"] = "storage/live/live_orders_ledger.csv"

Inputs

storage/live/dhan_index_ai_trades_plan.csv

Outputs

Appended ledger rows.

Summary dict.

Safety Rules

No duplication: If a trade plan row is already represented in ledger (can be checked via combination of underlying+strike+side+timestamp), skip adding again.

Never set any broker_order_id here.

Verification command
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase104_tradeplan_to_orders


Expected:

Console: Phase104: X new planned orders appended to live ledger

Ledger updated with new PLANNED rows.

PHASE 105 – Ledger Integrity Checker

Goal: Check ledger sanity before any live execution.

Files

Create core/engine/system3_phase105_ledger_integrity_check.py

Behaviour

run_phase105() must:

Load live_orders_ledger.csv.

Verify:

All required columns exist.

No rows with:

negative qty

missing symbol/underlying/side

status is one of:

["PLANNED", "SENT", "PARTIAL", "FILLED", "CANCELLED", "REJECTED", "EXPIRED", "ERROR"]

broker_status is non-null only when status != "PLANNED".

If all good:

status="OK", details="Ledger integrity OK (N rows)"

If issues:

status="ERROR"

list problems in "errors" and write a log to:

logs/phase105_ledger_integrity_issues.log

Inputs

storage/live/live_orders_ledger.csv

Outputs

Validation dict.

Safety Rules

If ledger file missing:

Create empty header using Phase 102 logic internally.

Return status="ERROR" with details="Ledger missing; created empty header".

Verification command
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase105_ledger_integrity_check


Expected:

Clean install: Ledger integrity OK (0 rows) or small number.

Log file only created if issues.

PHASE 106 – Live Execution DRY-RUN Bridge

Goal: Wire ledger to existing DRY RUN executor without real Angel calls.

Files

Create core/engine/system3_phase106_dryrun_execution_bridge.py

Behaviour

run_phase106() must:

Read live_orders_ledger.csv.

Filter rows with status="PLANNED".

For each such row:

Call existing DRY RUN executor module (already in System3; name may be dhan_trade_executor_dryrun or similar – Cursor agent must inspect existing code and reuse).

Simulate fill (like current DRY RUN).

Update ledger row:

status="FILLED"

broker_status="DRY_RUN_FILLED"

entry_price set to simulated price.

last_update_ts updated.

Append a per-run log to:

logs/phase106_dryrun_execution.log

Inputs

storage/live/live_orders_ledger.csv

Existing DRY RUN functionality in System3.

Outputs

Updated ledger rows.

Dict with:

outputs["orders_processed"]

outputs["orders_filled_dryrun"]

Safety Rules

Absolutely no real Angel calls here.

Do not modify any rows with status not equal PLANNED.

Verification command
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase106_dryrun_execution_bridge


Expected:

When there are PLANNED orders, they transition to FILLED (DRY_RUN).

Ledger updated correctly.

PHASE 107 – Dhan LIVE Execution (ONE-LOT, GUARDED, OFF BY DEFAULT)

Goal: Actual real-order placement, but tightly guarded and controlled by config.

Files

Create core/engine/system3_phase107_live_execution_engine.py

Reuse core/broker/dhan_live_order_wrapper.py implemented in Phase 103.

Behaviour

run_phase107() must:

Import LIVE_TRADING_ENABLED, DEFAULT_LOTS_PER_TRADE, & risk limits from config/live_trade_config.py.

If LIVE_TRADING_ENABLED is False:

Return status="ERROR", details="LIVE_TRADING_ENABLED=False; aborting"

No changes to ledger.

If LIVE_TRADING_ENABLED is True:

Load live_orders_ledger.csv.

Filter candidate rows:

status="PLANNED"

underlying in LIVE_ALLOWED_UNDERLYINGS.

Enforce caps:

Do not process more than MAX_LIVE_TRADES_PER_DAY in total (count existing non-PLANNED rows for today).

Do not process more than MAX_LIVE_TRADES_PER_UNDERLYING per underlying.

For each candidate:

Build symbol, qty (lots * lot_size – Cursor must read existing code to get lot size or assume 1 for now and log warning).

Use AngelLiveOrderWrapper.place_market_order(...).

If result OK:

Update ledger: status="SENT", set broker_order_id, broker_status="SENT".

If ERROR:

status="ERROR", broker_status="FAILED", add note.

Write per-run log:

logs/phase107_live_execution_engine.log

Inputs

config/live_trade_config.py

storage/live/live_orders_ledger.csv

core/broker/dhan_live_order_wrapper.py (still likely DRY_RUN or stub).

Outputs

Updated ledger.

Dict summarizing:

orders_attempted

orders_sent

orders_failed

Safety Rules

This phase is where real trade risk exists. However:

For now, Cursor must keep AngelLiveOrderWrapper in DRY_RUN or mocked state unless explicitly instructed by Pritam in future.

run_phase107() must be written such that if the wrapper returns "status": "DRY_RUN" or "NOT_IMPLEMENTED", ledger is NOT modified to fully live states.

Pritam will later decide when to plug in real DhanHQ code.

Verification command
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase107_live_execution_engine


Expected (currently, with DRY_RUN wrapper):

status="ERROR" with message about LIVE_TRADING_ENABLED=False, OR

If turned True deliberately, still do DRY_RUN behaviour (no real broker hits yet).

PHASE 108 – Order Status Refresher

Goal: Pull order statuses from Angel (or simulated now) and update ledger.

Files

Create core/engine/system3_phase108_order_status_refresher.py

Behaviour

run_phase108() must:

Load live_orders_ledger.csv.

Find rows where status in ["SENT", "PARTIAL"].

For each:

Call AngelLiveOrderWrapper.get_order_status(broker_order_id).

Map broker status to ledger status:

COMPLETE → status="FILLED"

REJECTED → status="REJECTED"

CANCELLED → status="CANCELLED"

Others → status unchanged, update broker_status field textual.

Update last_update_ts.

Inputs

live_orders_ledger.csv

AngelLiveOrderWrapper

Outputs

Updated ledger.

Dict summarizing counts by final status.

Safety Rules

If wrapper is still DRY_RUN, implement a fallback:

No changes, just log "NOT_IMPLEMENTED" and return status="ERROR".

Verification command
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase108_order_status_refresher


Expected:

With DRY_RUN wrapper, you only see error/warning in logs.

Once real status logic is implemented later, statuses update.

PHASE 109 – Intraday Risk Guard (Hard Caps)

Goal: Before sending orders, enforce capital and drawdown limits.

Files

Create core/engine/system3_phase109_intraday_risk_guard.py

Behaviour

run_phase109() must:

Read live_orders_ledger.csv.

Calculate for the current trading day:

Number of live trades (non-PLANNED rows).

Approximate realized PnL from ledger fields where exit_reason is not null.

Compare vs config:

If daily trade count ≥ MAX_LIVE_TRADES_PER_DAY → return status="BLOCK".

If realized drawdown exceeds specified threshold (you can add new config like MAX_DAILY_DRAWDOWN_RUPEES) → status="BLOCK".

Inputs

live_orders_ledger.csv

config/live_trade_config.py (extended with drawdown if needed).

Outputs

Dict with:

status = "OK" or "BLOCK"

outputs["reason"]

outputs["trades_today"]

outputs["approx_realized_pnl"]

Safety Rules

This phase is pure check; no ledger modification.

It will be used inside the main session brain (Phase 116+).

Verification command
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase109_intraday_risk_guard


Expected:

For now, likely "OK" with small trades count (0 or few).

PHASE 110 – Stop-Loss & Exit Rule Builder (Static)

Goal: Build conservative SL/TP rules per trade from existing AI signals.

Files

Create core/engine/system3_phase110_exit_rule_builder.py

Behaviour

run_phase110() must:

Read dhan_index_ai_trades_plan.csv and live_orders_ledger.csv.

For any ledger row with status="PLANNED" and missing target_price / stop_loss_price:

Add default rules, e.g.:

target_price = entry_price * (1 + 0.02) (2% gain)

stop_loss_price = entry_price * (1 - 0.01) (1% loss)

If entry_price is not known yet, you can store relative rules in a separate JSON:

storage/live/phase110_exit_rules_pending.json

Return summary dict.

Safety Rules

Do not modify already filled exits.

Everything must be conservative (SL closer than TP).

Verification command
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase110_exit_rule_builder

NOTE

To keep within practical size, remaining phases are specified more compactly but still with enough micro detail for Cursor. They follow the same pattern: file path, run function, inputs/outputs, verification.

PHASE 111 – Live Signal Session Orchestrator (Skeleton)

File: core/engine/system3_phase111_live_session_brain.py

run_phase111():

Orchestrates phases: 101, 102, 104, 105, 109.

Returns combined status for a pre-execution check.

Inputs: none (calls other phases).

Output: dict with embedded child results.

Verify:

python -m core.engine.system3_phase111_live_session_brain

PHASE 112 – Session Loop Controller (One-Shot)

File: core/engine/system3_phase112_session_loop_controller.py

run_phase112(iterations: int = 1, sleep_seconds: int = 30):

For each iteration:

Call Phase 111.

If OK:

Call Phase 104 (build PLANNED), 105 (integrity), 109 (risk guard).

If risk guard OK:

Call Phase 106 (DRY_RUN) or 107 (LIVE) depending on config flag USE_LIVE_EXECUTION_ENGINE (new flag in live_trade_config.py).

Logs each cycle to logs/phase112_session_loop.log.

Inputs: ledger + trade plan.

Verification:

python -m core.engine.system3_phase112_session_loop_controller


(Cursor: default iterations=1, no infinite loop.)

PHASE 113 – Kill Switch Monitor

File: core/engine/system3_phase113_kill_switch_monitor.py

run_phase113():

Read optional kill file: storage/live/kill_switch.json.

If file exists and "kill": true, return status="KILL".

Else status="OK".

Used by Phase 112 to abort further execution if kill triggered.

Verify:

python -m core.engine.system3_phase113_kill_switch_monitor

PHASE 114 – Live Session Health Snapshot

File: core/engine/system3_phase114_live_session_health.py

run_phase114():

Summarize:

Number of PLANNED/SENT/FILLED trades for day.

Current risk guard status (call 109).

Kill switch status (call 113).

Write Markdown snapshot:

storage/live/phase114_live_session_health.md

Verify:

python -m core.engine.system3_phase114_live_session_health

PHASE 115 – Intraday Alert Summary (Text Only)

File: core/engine/system3_phase115_intraday_alert_summary.py

run_phase115():

Generate plain text summary for WhatsApp/Email integration later.

Write:

storage/live/phase115_intraday_alert_summary.txt

No sending; only content creation.

Verify:

python -m core.engine.system3_phase115_intraday_alert_summary

PHASE 116 – End-of-Session Auto Stop

File: core/engine/system3_phase116_end_session_auto_stop.py

run_phase116(market_close_time_str="15:30"):

If current local time > configured market close:

Write a note in kill_switch.json with "kill": true.

Return status.

Verify:

python -m core.engine.system3_phase116_end_session_auto_stop

PHASE 117 – Live → Learning Bridge

File: core/engine/system3_phase117_live_to_learning_bridge.py

Connect ledger & PnL to your Real Outcome files already used by phases 28–37.

run_phase117():

Take all trades that finished today (status FILLED with exit).

Append simplified rows to storage/learning/live_trade_outcomes.csv.

Verify:

python -m core.engine.system3_phase117_live_to_learning_bridge

PHASE 118 – Daily Live PnL Snapshot (Angel Only)

File: core/engine/system3_phase118_daily_live_pnl_snapshot.py

run_phase118():

Summarize daily PnL from ledger.

Write Markdown: storage/live/phase118_daily_pnl_snapshot.md.

Verify:

python -m core.engine.system3_phase118_daily_live_pnl_snapshot

PHASE 119 – Safety Audit for Live Trading

File: core/engine/system3_phase119_live_safety_audit.py

run_phase119():

Check:

LIVE_TRADING_ENABLED status.

Intraday risk guard result.

Kill switch state.

Trade count vs limits.

Write Markdown: storage/live/phase119_live_safety_audit.md.

Verify:

python -m core.engine.system3_phase119_live_safety_audit

PHASE 120 – End-of-Day Live Summary Pack

File: core/engine/system3_phase120_eod_live_summary_pack.py

run_phase120():

Combine outputs from 114, 118, 119 into one report:

storage/live/phase120_eod_live_summary_pack.md

Verify:

python -m core.engine.system3_phase120_eod_live_summary_pack

PHASES 121–125 – RESERVED FOR FUTURE ENHANCEMENTS

For now, Cursor must only create empty, minimal modules with run_phaseXXX() returning "status": "NOT_IMPLEMENTED" and no side effects:

core/engine/system3_phase121_*.py

core/engine/system3_phase122_*.py

...

core/engine/system3_phase125_*.py

Each:

def run_phase121(**kwargs) -> dict:
    return {
        "phase": 121,
        "status": "NOT_IMPLEMENTED",
        "details": "Reserved for future System3 live automation enhancements.",
        "outputs": {},
        "errors": []
    }


No CLI wiring required yet.

PHASES 126–130 – Control Panel & Menu Integration Stubs

Similarly, create:

core/engine/system3_phase126_control_panel_stub.py

...

core/engine/system3_phase130_control_panel_stub.py

Each run_phaseXXX() should:

Return "status": "STUB".

Not modify any files.

These will be wired later into system3_ultra.py menu once live trading is stable.

FINAL SECTION – WHAT PRITAM SHOULD RUN FOR VERIFICATION

Once Cursor agent implements all above:

Step 1 – Config & Ledger
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase101_live_trade_config_check
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase102_order_ledger_schema
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase105_ledger_integrity_check


Send me:

Console output of these three commands.

A copy of:

storage/live/phase101_live_trade_config_snapshot.json

storage/live/live_orders_ledger.csv (only header + few lines)

Step 2 – Trade Plan → Ledger → DRY RUN

With some AI trades available:

(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase104_tradeplan_to_orders
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase106_dryrun_execution_bridge
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase108_order_status_refresher


Send me:

Updated live_orders_ledger.csv (few rows).

Relevant log snippets from:

logs/phase106_dryrun_execution.log

Step 3 – Session Brain One-Shot
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase111_live_session_brain
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase112_session_loop_controller
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase114_live_session_health


Send me:

storage/live/phase114_live_session_health.md