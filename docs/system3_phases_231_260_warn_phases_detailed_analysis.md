# System3 Phases 231-260 - Detailed WARN Phases Analysis

**Date**: 2025-12-02  
**Analysis**: Micro-level breakdown of all 8 WARN phases

---

## 📊 OVERVIEW

**Total WARN Phases**: 8  
**Status**: ⚠️ All expected - waiting for data files  
**Will Show OK**: After autopilot generates data

---

## 🔍 PHASE-BY-PHASE DETAILED ANALYSIS

---

### **PHASE 238 - Virtual Orders Schema Guard** ⚠️ WARN

**Script**: `system3_virtual_orders_schema_check.py`  
**Current Status**: ⚠️ WARN  
**Reason**: File not found

#### **What It Checks**
- Validates schema of `storage/live/angel_virtual_orders.csv`
- Checks for required columns
- Validates data types
- Reports missing columns or data issues

#### **Required File**
```
Path: storage/live/angel_virtual_orders.csv
```

#### **Required Columns** (15 total)
```python
REQUIRED_COLS = [
    "ts",                    # Timestamp
    "underlying",            # NIFTY, BANKNIFTY, etc.
    "strike",                # Strike price
    "option_type",           # CE or PE
    "side",                  # BUY or SELL
    "expiry",                # Expiry date
    "ltp",                   # Last traded price
    "final_score",           # Final signal score
    "ai_score",              # AI component score
    "lots",                  # Number of lots
    "approved",              # Risk approval (bool)
    "adjusted_lots",         # Risk-adjusted lots
    "risk_reason",           # Risk decision reason
    "risk_flags_json",       # Risk flags (JSON string)
    "snapshot_id"            # Snapshot identifier
]
```

#### **Current Condition**
```python
if not VIRTUAL_ORDERS_CSV.exists():
    return {
        "status": "WARN",
        "details": "File not found (expected if no orders generated)"
    }
```

#### **What Creates This File**
- **Phase 237**: Virtual execution integrated in signal engine
- **When**: Every time autopilot generates BUY/SELL signals
- **Location**: `core/engine/system3_signal_engine.py` → `run_signal_engine()` → `log_virtual_orders()`

#### **When It Will Show OK**
- ✅ File exists
- ✅ All 15 required columns present
- ✅ Data types valid
- ✅ At least 1 row of data

#### **Expected Output When OK**
```python
{
    "phase": 238,
    "status": "OK",
    "details": "Schema check complete: X rows, 0 missing cols",
    "outputs": {
        "file_exists": True,
        "row_count": X,
        "missing_cols": []
    }
}
```

#### **Report Generated**
- **File**: `logs/execution/system3_virtual_orders_schema_report.md`
- **Content**: Schema validation results, row count, first/last timestamp

---

### **PHASE 239 - Virtual PnL Joiner** ⚠️ WARN

**Script**: `system3_virtual_trades_enrichment.py`  
**Current Status**: ⚠️ WARN  
**Reason**: Input files not found

#### **What It Does**
- Joins virtual orders with forward returns
- Computes PnL for each virtual trade
- Creates enriched CSV with PnL columns

#### **Required Input Files** (2 files)

**File 1**: `storage/live/angel_virtual_orders.csv`
- **Source**: Phase 237 (virtual execution)
- **Contains**: Virtual orders with scores, lots, approval status

**File 2**: `storage/live/angel_index_ai_signals_with_forward.csv`
- **Source**: Phase 221 (forward returns computation)
- **Contains**: Signals with forward return columns (`forward_ret_1`, `forward_ret_3`, `forward_ret_5`, etc.)

#### **Join Keys**
```python
join_keys = [
    "ts",           # Timestamp
    "underlying",   # NIFTY, BANKNIFTY, etc.
    "strike",       # Strike price
    "side",         # BUY or SELL
    "option_type",  # CE or PE
    "expiry"        # Expiry date
]
```

#### **Current Condition**
```python
if not VIRTUAL_ORDERS_CSV.exists():
    return {"status": "WARN", "details": "Virtual orders CSV not found"}

if not FORWARD_SIGNALS_CSV.exists():
    return {"status": "WARN", "details": "Forward signals CSV not found"}
```

#### **What Creates These Files**
- **Virtual Orders CSV**: Phase 237 (autopilot generates signals → virtual orders)
- **Forward Returns CSV**: Phase 221 (computes forward returns from historical signals)

#### **Computation Logic**
```python
# For each forward return column (forward_ret_1, forward_ret_3, etc.)
for col in forward_cols:
    pnl_col = col.replace("forward_ret", "pnl").replace("ret", "pnl")
    merged[pnl_col] = merged[col] * merged["lots"]
```

#### **Output File**
```
Path: storage/live/angel_virtual_orders_with_pnl.csv
```

#### **New Columns Added**
- `pnl_1`: PnL for 1-minute forward return
- `pnl_3`: PnL for 3-minute forward return
- `pnl_5`: PnL for 5-minute forward return
- (etc., based on available forward return columns)

#### **When It Will Show OK**
- ✅ Both input files exist
- ✅ Join keys match
- ✅ At least 1 matched row
- ✅ Output file created successfully

#### **Expected Output When OK**
```python
{
    "phase": 239,
    "status": "OK",
    "details": "Enriched X orders: Y matched, Z unmatched",
    "outputs": {
        "total_orders": X,
        "matched": Y,
        "unmatched": Z,
        "output_file": "storage/live/angel_virtual_orders_with_pnl.csv"
    }
}
```

#### **Log File**
- **File**: `logs/research/system3_virtual_trades_enrichment.log`
- **Content**: Matching statistics, errors if any

---

### **PHASE 240 - Virtual PnL Daily Report** ⚠️ WARN

**Script**: `system3_virtual_trades_summary.py`  
**Current Status**: ⚠️ WARN  
**Reason**: Input file not found

#### **What It Does**
- Generates daily PnL summaries
- Per-underlying breakdowns
- Win rate calculations
- Overall statistics

#### **Required Input File**
```
Path: storage/live/angel_virtual_orders_with_pnl.csv
```

#### **Required Columns**
- `ts`: Timestamp (for date extraction)
- `underlying`: Symbol name
- `side`: BUY or SELL
- `pnl_1`, `pnl_3`, `pnl_5`: PnL columns (at least one)

#### **Current Condition**
```python
if not INPUT_CSV.exists():
    return {
        "status": "WARN",
        "details": "No virtual trades available (file not found)"
    }

if df.empty:
    return {
        "status": "WARN",
        "details": "File is empty"
    }
```

#### **Computation Logic**

**1. Overall Summary**
```python
total_trades = len(df)
wins = len(df[df[pnl_col] > 0])
losses = len(df[df[pnl_col] < 0])
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
total_pnl = df[pnl_col].sum()
avg_pnl = df[pnl_col].mean()
```

**2. Per-Day Summary**
```python
# Group by date extracted from ts
for date, group in df.groupby("date"):
    daily_trades = len(group)
    daily_wins = len(group[group[pnl_col] > 0])
    daily_losses = len(group[group[pnl_col] < 0])
    daily_win_rate = (daily_wins / daily_trades * 100)
    daily_pnl = group[pnl_col].sum()
```

**3. Per-Underlying Summary**
```python
# Group by underlying
for underlying, group in df.groupby("underlying"):
    und_trades = len(group)
    und_wins = len(group[group[pnl_col] > 0])
    und_losses = len(group[group[pnl_col] < 0])
    und_win_rate = (und_wins / und_trades * 100)
    und_pnl = group[pnl_col].sum()
```

#### **Output Report**
```
Path: logs/research/system3_virtual_trades_pnl_report.md
```

#### **Report Content**
- Overall summary table (total trades, wins, losses, win rate, total PnL, avg PnL)
- Per-day summary table
- Per-underlying summary table

#### **When It Will Show OK**
- ✅ Input file exists
- ✅ File has data (not empty)
- ✅ PnL column found (pnl_1, pnl_3, or pnl_5)
- ✅ Report generated successfully

#### **Expected Output When OK**
```python
{
    "phase": 240,
    "status": "OK",
    "details": "Generated report: X trades, Y% win rate",
    "outputs": {
        "total_trades": X,
        "win_rate": Y,
        "report_file": "logs/research/system3_virtual_trades_pnl_report.md"
    }
}
```

---

### **PHASE 241 - Virtual Trade Diagnostics** ⚠️ WARN

**Script**: `system3_virtual_trades_diagnostics.py`  
**Current Status**: ⚠️ WARN  
**Reason**: Input file not found

#### **What It Does**
- Sanity checks virtual trades
- Detects anomalies
- Computes correlations
- Validates data quality

#### **Required Input File**
```
Path: storage/live/angel_virtual_orders_with_pnl.csv
```

#### **Checks Performed**

**1. Lots Validation**
```python
if "lots" in df.columns:
    invalid_lots = len(df[df["lots"] <= 0])
    if invalid_lots > 0:
        anomalies.append(f"{invalid_lots} trades with lots <= 0")
```

**2. Underlying Validation**
```python
valid_underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
if "underlying" in df.columns:
    unknown = df[~df["underlying"].isin(valid_underlyings)]
    if len(unknown) > 0:
        anomalies.append(f"{len(unknown)} trades with unknown underlyings")
```

**3. Outlier Detection**
```python
# Check for PnL outliers (>3 standard deviations)
for col in pnl_cols:
    mean_pnl = df[col].mean()
    std_pnl = df[col].std()
    if std_pnl > 0:
        outliers = df[abs(df[col] - mean_pnl) > 3 * std_pnl]
        outlier_count += len(outliers)
```

**4. Correlation Check**
```python
# Correlation between final_score and PnL
if "final_score" in df.columns and pnl_cols:
    correlation = df["final_score"].corr(df[pnl_col])
```

#### **Current Condition**
```python
if not INPUT_CSV.exists():
    return {
        "status": "WARN",
        "details": "Input file not found"
    }

if df.empty:
    return {
        "status": "WARN",
        "details": "File is empty"
    }
```

#### **Output Report**
```
Path: logs/research/system3_virtual_trades_diagnostics.md
```

#### **Report Content**
- List of anomalies detected
- Outlier count
- Correlation between final_score and PnL
- Data quality summary

#### **When It Will Show OK**
- ✅ Input file exists
- ✅ File has data
- ✅ No anomalies detected (or anomalies logged)
- ✅ Report generated successfully

#### **Expected Output When OK**
```python
{
    "phase": 241,
    "status": "OK",
    "details": "Diagnostics complete: 0 anomalies, correlation=X.XXX",
    "outputs": {
        "anomalies": 0,
        "correlation": X.XXX,
        "report_file": "logs/research/system3_virtual_trades_diagnostics.md"
    }
}
```

---

### **PHASE 244 - Score-to-Trade Attribution** ⚠️ WARN

**Script**: `system3_score_to_trade_attribution.py`  
**Current Status**: ⚠️ WARN  
**Reason**: Input files not found

#### **What It Does**
- Analyzes which score components drive trades
- Computes average component values per trade
- Correlates components with PnL
- Reports feature importance for trading

#### **Required Input Files** (2 files)

**File 1**: `storage/live/angel_virtual_orders_with_pnl.csv`
- **Contains**: Virtual trades with PnL

**File 2**: `storage/live/angel_index_ai_signals.csv`
- **Contains**: Original signals with all score components

#### **Join Logic**
```python
join_keys = ["ts", "underlying", "strike", "side", "option_type", "expiry"]
merged = orders_df.merge(signals_df, on=join_keys, how="left")
```

#### **Score Components Analyzed**
```python
score_cols = [
    "final_score",      # Combined final score
    "ai_score",         # AI model score
    "greeks_score",     # Greeks component
    "trend_score",      # Trend component
    "volatility_score", # Volatility component
    "momentum_score",   # Momentum component
    "breakout_score"    # Breakout component
]
```

#### **Current Condition**
```python
if not VIRTUAL_ORDERS_CSV.exists() or not SIGNALS_CSV.exists():
    return {
        "status": "WARN",
        "details": "Input files not found"
    }
```

#### **Analysis Performed**

**1. Average Component Values**
```python
for col in available_score_cols:
    avg_val = merged[col].mean()
    # Report average value per component
```

**2. Correlation with PnL**
```python
if pnl_col:
    for col in available_score_cols:
        corr = merged[col].corr(merged[pnl_col])
        # Report correlation between component and PnL
```

#### **Output Report**
```
Path: logs/research/system3_score_to_trade_attribution.md
```

#### **Report Content**
- Table: Average value per score component
- Correlation table: Component correlation with PnL
- Analysis of which components drive profitable trades

#### **When It Will Show OK**
- ✅ Both input files exist
- ✅ Join keys match
- ✅ Score component columns found
- ✅ At least 1 matched row
- ✅ Report generated successfully

#### **Expected Output When OK**
```python
{
    "phase": 244,
    "status": "OK",
    "details": "Attribution report generated: X components",
    "outputs": {
        "components_analyzed": X,
        "report_file": "logs/research/system3_score_to_trade_attribution.md"
    }
}
```

---

### **PHASE 245 - Symbol Participation Summary** ⚠️ WARN

**Script**: `system3_symbol_participation_summary.py`  
**Current Status**: ⚠️ WARN  
**Reason**: Input file not found

#### **What It Does**
- Summarizes trade participation by underlying
- Counts BUY vs SELL per symbol
- Breaks down by expiry
- Shows trading activity distribution

#### **Required Input File**
```
Path: storage/live/angel_virtual_orders.csv
```

#### **Required Columns**
- `underlying`: Symbol name (NIFTY, BANKNIFTY, etc.)
- `side`: BUY or SELL
- `expiry`: Expiry date

#### **Current Condition**
```python
if not INPUT_CSV.exists():
    return {
        "status": "WARN",
        "details": "Input file not found"
    }

if df.empty:
    return {
        "status": "WARN",
        "details": "File is empty"
    }
```

#### **Analysis Performed**

**1. Per-Underlying Summary**
```python
for underlying, group in df.groupby("underlying"):
    total = len(group)
    buy_count = len(group[group["side"] == "BUY"])
    sell_count = len(group[group["side"] == "SELL"])
```

**2. Per-Expiry Summary**
```python
for expiry, group in df.groupby("expiry"):
    total_trades = len(group)
```

#### **Output Report**
```
Path: logs/research/system3_symbol_participation_summary.md
```

#### **Report Content**
- **Per-Underlying Table**: Symbol | Total Trades | BUY | SELL
- **Per-Expiry Table**: Expiry | Total Trades

#### **When It Will Show OK**
- ✅ Input file exists
- ✅ File has data
- ✅ Required columns present
- ✅ Report generated successfully

#### **Expected Output When OK**
```python
{
    "phase": 245,
    "status": "OK",
    "details": "Participation summary generated: X trades",
    "outputs": {
        "total_trades": X,
        "report_file": "logs/research/system3_symbol_participation_summary.md"
    }
}
```

---

### **PHASE 246 - Trade Density vs Volatility Regime** ⚠️ WARN

**Script**: `system3_trade_density_vs_regime.py`  
**Current Status**: ⚠️ WARN  
**Reason**: Input files not found

#### **What It Does**
- Maps trades to volatility regimes
- Analyzes trade density per regime
- Compares win rate and PnL by regime
- Identifies optimal trading conditions

#### **Required Input Files** (2 files)

**File 1**: `storage/live/angel_virtual_orders.csv`
- **Contains**: Virtual trades

**File 2**: `storage/meta/system3_vol_regimes.csv`
- **Source**: Phase 217 (volatility regime detection)
- **Contains**: Date, underlying, regime (LOW/NORMAL/HIGH)

#### **Join Logic**
```python
# Extract date from timestamp
orders_df["date"] = pd.to_datetime(orders_df["ts"], errors="coerce").dt.date

# Join on date + underlying
merged = orders_df.merge(regimes_df, on=["date", "underlying"], how="left")
```

#### **Current Condition**
```python
if not ORDERS_CSV.exists():
    return {
        "status": "WARN",
        "details": "Orders CSV not found"
    }
```

#### **Analysis Performed**

**1. Trade Count by Regime**
```python
if "regime" in merged.columns:
    for regime, group in merged.groupby("regime"):
        trade_count = len(group)
        # Report trades per regime
```

**2. Win Rate by Regime** (if PnL available)
```python
if pnl_col:
    for regime, group in merged.groupby("regime"):
        wins = len(group[group[pnl_col] > 0])
        win_rate = (wins / len(group) * 100)
        avg_pnl = group[pnl_col].mean()
```

#### **Output Report**
```
Path: logs/research/system3_trade_density_vs_regime.md
```

#### **Report Content**
- **Table**: Regime | Trade Count | Win Rate | Avg PnL
- Analysis of which regimes generate most trades
- Performance comparison across regimes

#### **When It Will Show OK**
- ✅ Orders CSV exists
- ✅ Regimes CSV exists (or handled gracefully)
- ✅ At least 1 trade with regime data
- ✅ Report generated successfully

#### **Expected Output When OK**
```python
{
    "phase": 246,
    "status": "OK",
    "details": "Trade density report generated",
    "outputs": {
        "report_file": "logs/research/system3_trade_density_vs_regime.md"
    }
}
```

---

### **PHASE 247 - Edge-by-Score-Bucket Tracker** ⚠️ WARN

**Script**: `system3_edge_by_score_bucket_tracker.py`  
**Current Status**: ⚠️ WARN  
**Reason**: Input file not found

#### **What It Does**
- Tracks edge (profitability) by score buckets
- Maintains ongoing performance metrics
- Identifies optimal score ranges
- Updates historical tracking CSV

#### **Required Input File**
```
Path: storage/live/angel_virtual_orders_with_pnl.csv
```

#### **Required Columns**
- `final_score`: Final signal score
- `pnl_1`, `pnl_3`, `pnl_5`: PnL columns (at least one)

#### **Current Condition**
```python
if not INPUT_CSV.exists():
    return {
        "phase": 247,
        "status": "WARN",
        "details": "Input file not found"
    }

if df.empty or "final_score" not in df.columns:
    return {
        "phase": 247,
        "status": "WARN",
        "details": "No data or missing final_score"
    }
```

#### **Score Buckets Defined**
```python
buckets = [
    "(-inf, 0.0)",    # Negative scores
    "[0.0, 0.1)",     # Low positive scores
    "[0.1, 0.2)",     # Medium-low scores
    "[0.2, 0.3)",     # Medium-high scores
    "[0.3, inf)"      # High scores
]
```

#### **Computation Logic**
```python
# Create buckets
df["score_bucket"] = pd.cut(
    df["final_score"],
    bins=[-float('inf'), 0.0, 0.1, 0.2, 0.3, float('inf')],
    labels=["(-inf, 0.0)", "[0.0, 0.1)", "[0.1, 0.2)", "[0.2, 0.3)", "[0.3, inf)"]
)

# Aggregate by bucket
for bucket, group in df.groupby("score_bucket"):
    trades = len(group)
    wins = len(group[group[pnl_col] > 0])
    win_rate = (wins / trades * 100) if trades > 0 else 0
    avg_pnl = group[pnl_col].mean()
```

#### **Output File**
```
Path: storage/meta/system3_edge_by_score_bucket.csv
```

#### **Output Columns**
- `bucket`: Score bucket range
- `trades`: Number of trades in bucket
- `wins`: Number of winning trades
- `win_rate`: Win rate percentage
- `avg_pnl`: Average PnL per trade

#### **Append Logic**
```python
# Load existing history or create new
if OUTPUT_CSV.exists():
    existing_df = pd.read_csv(OUTPUT_CSV)
    bucket_df = pd.concat([existing_df, bucket_df], ignore_index=True)
else:
    bucket_df = new_df

bucket_df.to_csv(OUTPUT_CSV, index=False)
```

#### **When It Will Show OK**
- ✅ Input file exists
- ✅ File has data
- ✅ `final_score` column present
- ✅ PnL column found
- ✅ Buckets computed successfully
- ✅ Output CSV created/updated

#### **Expected Output When OK**
```python
{
    "phase": 247,
    "status": "OK",
    "details": "Edge tracked: X buckets",
    "outputs": {
        "buckets": X,
        "output_file": "storage/meta/system3_edge_by_score_bucket.csv"
    }
}
```

#### **Log File**
- **File**: `logs/research/system3_edge_by_score_bucket.log`
- **Content**: Tracking updates, bucket statistics

---

## 📊 DATA DEPENDENCY CHAIN

### **Phase Execution Order**

```
Phase 237 (Virtual Execution)
    ↓
Creates: storage/live/angel_virtual_orders.csv
    ↓
Phase 238 (Schema Check) → ✅ OK
Phase 245 (Participation) → ✅ OK
    ↓
Phase 221 (Forward Returns) [Already implemented]
    ↓
Creates: storage/live/angel_index_ai_signals_with_forward.csv
    ↓
Phase 239 (PnL Joiner)
    ↓
Creates: storage/live/angel_virtual_orders_with_pnl.csv
    ↓
Phase 240 (PnL Summary) → ✅ OK
Phase 241 (Diagnostics) → ✅ OK
Phase 244 (Attribution) → ✅ OK
Phase 247 (Edge Tracker) → ✅ OK
    ↓
Phase 217 (Vol Regimes) [Already implemented]
    ↓
Creates: storage/meta/system3_vol_regimes.csv
    ↓
Phase 246 (Trade Density) → ✅ OK
```

---

## 🔄 TRANSITION FROM WARN TO OK

### **Step-by-Step Process**

**Step 1: Run Autopilot**
```bash
python system3_live_day_autopilot.py
```
- Generates signals with BUY/SELL
- Phase 237 creates virtual orders
- **Result**: `angel_virtual_orders.csv` created

**Step 2: Phases Show OK**
- ✅ Phase 238: Schema check passes
- ✅ Phase 245: Participation summary generated

**Step 3: Forward Returns Computed**
- Phase 221 (already runs) computes forward returns
- **Result**: `angel_index_ai_signals_with_forward.csv` updated

**Step 4: PnL Enrichment**
- Phase 239 joins orders with forward returns
- **Result**: `angel_virtual_orders_with_pnl.csv` created

**Step 5: All Phases Show OK**
- ✅ Phase 240: PnL summary generated
- ✅ Phase 241: Diagnostics complete
- ✅ Phase 244: Attribution report generated
- ✅ Phase 247: Edge tracking updated

**Step 6: Vol Regime Analysis**
- Phase 217 (already runs) detects regimes
- Phase 246 joins trades with regimes
- **Result**: Trade density report generated

---

## 📁 FILE CREATION TIMELINE

### **After 1 Autopilot Snapshot**
- ✅ `angel_virtual_orders.csv` (if BUY/SELL signals generated)
- ⏳ `angel_virtual_orders_with_pnl.csv` (needs forward returns)

### **After Forward Returns Computed**
- ✅ `angel_virtual_orders_with_pnl.csv` (Phase 239)
- ✅ All PnL reports available

### **After Multiple Snapshots**
- ✅ `system3_edge_by_score_bucket.csv` (accumulated)
- ✅ `system3_threshold_history.csv` (accumulated)

---

## 🎯 SPECIFIC CONDITIONS FOR OK STATUS

### **Phase 238 - Schema Check**
```python
Conditions:
✅ File exists: storage/live/angel_virtual_orders.csv
✅ File not empty (len(df) > 0)
✅ All 15 required columns present
✅ No data type errors

Will show OK when: File created by Phase 237
```

### **Phase 239 - PnL Joiner**
```python
Conditions:
✅ File 1 exists: storage/live/angel_virtual_orders.csv
✅ File 2 exists: storage/live/angel_index_ai_signals_with_forward.csv
✅ Join keys match (ts, underlying, strike, side, option_type, expiry)
✅ At least 1 matched row
✅ Output file created successfully

Will show OK when: Both files exist and have matching rows
```

### **Phase 240 - PnL Summary**
```python
Conditions:
✅ File exists: storage/live/angel_virtual_orders_with_pnl.csv
✅ File not empty
✅ PnL column found (pnl_1, pnl_3, or pnl_5)
✅ Report generated successfully

Will show OK when: Enriched orders file exists (from Phase 239)
```

### **Phase 241 - Diagnostics**
```python
Conditions:
✅ File exists: storage/live/angel_virtual_orders_with_pnl.csv
✅ File not empty
✅ Required columns present (lots, underlying, final_score, pnl)
✅ Report generated successfully

Will show OK when: Enriched orders file exists (from Phase 239)
```

### **Phase 244 - Attribution**
```python
Conditions:
✅ File 1 exists: storage/live/angel_virtual_orders_with_pnl.csv
✅ File 2 exists: storage/live/angel_index_ai_signals.csv
✅ Join keys match
✅ Score component columns found
✅ At least 1 matched row

Will show OK when: Both files exist and have matching rows
```

### **Phase 245 - Participation**
```python
Conditions:
✅ File exists: storage/live/angel_virtual_orders.csv
✅ File not empty
✅ Required columns present (underlying, side, expiry)
✅ Report generated successfully

Will show OK when: Virtual orders file exists (from Phase 237)
```

### **Phase 246 - Trade Density**
```python
Conditions:
✅ File 1 exists: storage/live/angel_virtual_orders.csv
✅ File 2 exists: storage/meta/system3_vol_regimes.csv (optional)
✅ Date extraction successful
✅ Report generated successfully

Will show OK when: Orders file exists (regimes file optional)
```

### **Phase 247 - Edge Tracker**
```python
Conditions:
✅ File exists: storage/live/angel_virtual_orders_with_pnl.csv
✅ File not empty
✅ final_score column present
✅ PnL column found
✅ Buckets computed successfully
✅ Output CSV created/updated

Will show OK when: Enriched orders file exists (from Phase 239)
```

---

## 🔍 DETAILED FILE REQUIREMENTS

### **File 1: angel_virtual_orders.csv**
**Created By**: Phase 237 (Virtual Execution)  
**Location**: `storage/live/angel_virtual_orders.csv`  
**Required For**: Phases 238, 239, 244, 245, 246

**Schema**:
```csv
ts,underlying,strike,option_type,side,expiry,ltp,final_score,ai_score,lots,approved,adjusted_lots,risk_reason,risk_flags_json,snapshot_id
2025-12-02T09:15:00,NIFTY,23000,CE,BUY,30DEC2025,150.0,0.45,0.30,1,True,1,OK,{},1
```

**Minimum Data Required**:
- At least 1 row with BUY or SELL signal
- All 15 columns populated
- Valid data types

---

### **File 2: angel_index_ai_signals_with_forward.csv**
**Created By**: Phase 221 (Forward Returns)  
**Location**: `storage/live/angel_index_ai_signals_with_forward.csv`  
**Required For**: Phase 239

**Schema**:
```csv
ts,underlying,strike,side,option_type,expiry,...,forward_ret_1,forward_ret_3,forward_ret_5
2025-12-02T09:15:00,NIFTY,23000,CE,CE,30DEC2025,...,0.02,-0.01,0.05
```

**Required Columns**:
- Join keys: `ts`, `underlying`, `strike`, `side`, `option_type`, `expiry`
- Forward return columns: `forward_ret_1`, `forward_ret_3`, `forward_ret_5` (or similar)

**Minimum Data Required**:
- At least 1 row matching virtual orders
- Forward return columns populated

---

### **File 3: angel_virtual_orders_with_pnl.csv**
**Created By**: Phase 239 (PnL Joiner)  
**Location**: `storage/live/angel_virtual_orders_with_pnl.csv`  
**Required For**: Phases 240, 241, 244, 247

**Schema**:
```csv
ts,underlying,strike,option_type,side,expiry,ltp,final_score,ai_score,lots,approved,adjusted_lots,risk_reason,risk_flags_json,snapshot_id,pnl_1,pnl_3,pnl_5
2025-12-02T09:15:00,NIFTY,23000,CE,BUY,30DEC2025,150.0,0.45,0.30,1,True,1,OK,{},1,0.02,-0.01,0.05
```

**Required Columns**:
- All columns from `angel_virtual_orders.csv`
- Plus: `pnl_1`, `pnl_3`, `pnl_5` (or at least one PnL column)

**Minimum Data Required**:
- At least 1 row with PnL data
- Valid numeric PnL values

---

### **File 4: system3_vol_regimes.csv**
**Created By**: Phase 217 (Volatility Regime Detection)  
**Location**: `storage/meta/system3_vol_regimes.csv`  
**Required For**: Phase 246

**Schema**:
```csv
date,underlying,regime
2025-12-02,NIFTY,HIGH
2025-12-02,BANKNIFTY,MEDIUM
```

**Required Columns**:
- `date`: Date (YYYY-MM-DD)
- `underlying`: Symbol name
- `regime`: LOW, NORMAL, or HIGH

**Note**: This file is optional - Phase 246 will still run if it doesn't exist

---

## 📈 EXPECTED VALUES WHEN OK

### **Phase 238 - Schema Check**
```python
Expected Output:
{
    "status": "OK",
    "outputs": {
        "file_exists": True,
        "row_count": 50,  # Example: 50 virtual orders
        "missing_cols": []
    }
}
```

### **Phase 239 - PnL Joiner**
```python
Expected Output:
{
    "status": "OK",
    "outputs": {
        "total_orders": 50,
        "matched": 45,      # 45 orders matched with forward returns
        "unmatched": 5,     # 5 orders without forward returns
        "output_file": "storage/live/angel_virtual_orders_with_pnl.csv"
    }
}
```

### **Phase 240 - PnL Summary**
```python
Expected Output:
{
    "status": "OK",
    "outputs": {
        "total_trades": 45,
        "win_rate": 55.5,  # Example: 55.5% win rate
        "report_file": "logs/research/system3_virtual_trades_pnl_report.md"
    }
}
```

### **Phase 241 - Diagnostics**
```python
Expected Output:
{
    "status": "OK",
    "outputs": {
        "anomalies": 0,           # No data quality issues
        "correlation": 0.65,      # Example: 0.65 correlation between score and PnL
        "report_file": "logs/research/system3_virtual_trades_diagnostics.md"
    }
}
```

### **Phase 244 - Attribution**
```python
Expected Output:
{
    "status": "OK",
    "outputs": {
        "components_analyzed": 7,  # 7 score components
        "report_file": "logs/research/system3_score_to_trade_attribution.md"
    }
}
```

### **Phase 245 - Participation**
```python
Expected Output:
{
    "status": "OK",
    "outputs": {
        "total_trades": 50,
        "report_file": "logs/research/system3_symbol_participation_summary.md"
    }
}
```

### **Phase 246 - Trade Density**
```python
Expected Output:
{
    "status": "OK",
    "outputs": {
        "report_file": "logs/research/system3_trade_density_vs_regime.md"
    }
}
```

### **Phase 247 - Edge Tracker**
```python
Expected Output:
{
    "status": "OK",
    "outputs": {
        "buckets": 5,  # 5 score buckets
        "output_file": "storage/meta/system3_edge_by_score_bucket.csv"
    }
}
```

---

## 🔄 AUTOMATIC TRANSITION

### **When Autopilot Runs**

**Snapshot 1** (First BUY/SELL signal):
1. Phase 237 creates `angel_virtual_orders.csv` (1 row)
2. ✅ Phase 238: WARN → OK (file exists, schema valid)
3. ✅ Phase 245: WARN → OK (participation summary generated)
4. ⚠️ Phase 239: Still WARN (needs forward returns)
5. ⚠️ Phases 240-241, 244, 247: Still WARN (need enriched file)

**After Forward Returns Computed**:
1. Phase 221 updates `angel_index_ai_signals_with_forward.csv`
2. Phase 239 runs (manually or via autopilot integration)
3. ✅ Phase 239: WARN → OK (enriched file created)
4. ✅ Phase 240: WARN → OK (PnL summary generated)
5. ✅ Phase 241: WARN → OK (diagnostics complete)
6. ✅ Phase 244: WARN → OK (attribution report generated)
7. ✅ Phase 247: WARN → OK (edge tracking updated)

**After Vol Regime Detection**:
1. Phase 217 creates/updates `system3_vol_regimes.csv`
2. ✅ Phase 246: WARN → OK (trade density report generated)

---

## 📋 CHECKLIST TO RESOLVE ALL WARNS

### **To Make All 8 Phases Show OK**

- [ ] **Step 1**: Run autopilot to generate signals
  - Command: `python system3_live_day_autopilot.py`
  - Result: `angel_virtual_orders.csv` created
  - Phases fixed: 238, 245

- [ ] **Step 2**: Ensure forward returns are computed
  - Phase 221 should run automatically (or manually)
  - Result: `angel_index_ai_signals_with_forward.csv` updated
  - Phases fixed: 239 (can now run)

- [ ] **Step 3**: Run Phase 239 (PnL Joiner)
  - Command: `python system3_virtual_trades_enrichment.py`
  - Result: `angel_virtual_orders_with_pnl.csv` created
  - Phases fixed: 240, 241, 244, 247

- [ ] **Step 4**: Ensure vol regimes are detected
  - Phase 217 should run automatically (or manually)
  - Result: `system3_vol_regimes.csv` created/updated
  - Phases fixed: 246

---

## 🎯 SUMMARY

### **All 8 WARN Phases**

| Phase | File Needed | Created By | Will Show OK When |
|-------|-------------|------------|-------------------|
| **238** | `angel_virtual_orders.csv` | Phase 237 | File exists + valid schema |
| **239** | `angel_virtual_orders.csv` + `angel_index_ai_signals_with_forward.csv` | Phase 237 + Phase 221 | Both files exist + matching rows |
| **240** | `angel_virtual_orders_with_pnl.csv` | Phase 239 | File exists + has PnL data |
| **241** | `angel_virtual_orders_with_pnl.csv` | Phase 239 | File exists + has PnL data |
| **244** | `angel_virtual_orders_with_pnl.csv` + `angel_index_ai_signals.csv` | Phase 239 + Phase 237 | Both files exist + matching rows |
| **245** | `angel_virtual_orders.csv` | Phase 237 | File exists + has data |
| **246** | `angel_virtual_orders.csv` + `system3_vol_regimes.csv` | Phase 237 + Phase 217 | Orders file exists (regimes optional) |
| **247** | `angel_virtual_orders_with_pnl.csv` | Phase 239 | File exists + has score + PnL data |

### **Quick Resolution Path**

1. **Run Autopilot** → Creates `angel_virtual_orders.csv`
   - Fixes: Phases 238, 245

2. **Run Phase 239** → Creates `angel_virtual_orders_with_pnl.csv`
   - Fixes: Phases 240, 241, 244, 247

3. **Run Phase 217** (if not already) → Creates `system3_vol_regimes.csv`
   - Fixes: Phase 246

**Result**: All 8 phases will show ✅ OK

---

**Status**: ⚠️ **All WARN phases are EXPECTED and will resolve automatically when data is generated**

