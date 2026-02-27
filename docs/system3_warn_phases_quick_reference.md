# System3 WARN Phases - Quick Reference

**Last Updated**: 2025-12-02  
**Current Status**: 8 phases showing WARN (all expected)

---

## 🎯 QUICK STATUS CHECK

### **Missing Files** (as of now)
- ❌ `storage/live/angel_virtual_orders.csv` - **NOT FOUND**
- ❌ `storage/live/angel_virtual_orders_with_pnl.csv` - **NOT FOUND**
- ✅ `storage/live/angel_index_ai_signals_with_forward.csv` - **EXISTS** (from Phase 221)

---

## 📋 ALL 8 WARN PHASES AT A GLANCE

| # | Phase | Script | Needs File | Created By | Status |
|---|-------|--------|------------|------------|--------|
| **238** | Schema Guard | `system3_virtual_orders_schema_check.py` | `angel_virtual_orders.csv` | Phase 237 | ⚠️ WARN |
| **239** | PnL Joiner | `system3_virtual_trades_enrichment.py` | `angel_virtual_orders.csv` + `angel_index_ai_signals_with_forward.csv` | Phase 237 + 221 | ⚠️ WARN |
| **240** | PnL Summary | `system3_virtual_trades_summary.py` | `angel_virtual_orders_with_pnl.csv` | Phase 239 | ⚠️ WARN |
| **241** | Diagnostics | `system3_virtual_trades_diagnostics.py` | `angel_virtual_orders_with_pnl.csv` | Phase 239 | ⚠️ WARN |
| **244** | Attribution | `system3_score_to_trade_attribution.py` | `angel_virtual_orders_with_pnl.csv` + `angel_index_ai_signals.csv` | Phase 239 + 237 | ⚠️ WARN |
| **245** | Participation | `system3_symbol_participation_summary.py` | `angel_virtual_orders.csv` | Phase 237 | ⚠️ WARN |
| **246** | Trade Density | `system3_trade_density_vs_regime.py` | `angel_virtual_orders.csv` + `system3_vol_regimes.csv` | Phase 237 + 217 | ⚠️ WARN |
| **247** | Edge Tracker | `system3_edge_by_score_bucket_tracker.py` | `angel_virtual_orders_with_pnl.csv` | Phase 239 | ⚠️ WARN |

---

## 🔄 RESOLUTION FLOW

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Run Autopilot                                        │
│ Command: python system3_live_day_autopilot.py                │
│ Result: Generates BUY/SELL signals                           │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 237: Virtual Execution                                 │
│ Creates: storage/live/angel_virtual_orders.csv               │
│ Fixes: Phases 238, 245 → ✅ OK                               │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Run Phase 239 (PnL Joiner)                          │
│ Command: python system3_virtual_trades_enrichment.py         │
│ Reads: angel_virtual_orders.csv +                           │
│        angel_index_ai_signals_with_forward.csv               │
│ Creates: storage/live/angel_virtual_orders_with_pnl.csv     │
│ Fixes: Phases 240, 241, 244, 247 → ✅ OK                     │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Run Phase 217 (Vol Regimes) - Optional              │
│ Creates: storage/meta/system3_vol_regimes.csv                │
│ Fixes: Phase 246 → ✅ OK                                     │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ RESULT: All 8 phases → ✅ OK                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 FILE DEPENDENCY TREE

```
angel_virtual_orders.csv (Phase 237)
├── Phase 238: Schema Check ✅
├── Phase 245: Participation ✅
└── Phase 239: PnL Joiner
    └── angel_virtual_orders_with_pnl.csv
        ├── Phase 240: PnL Summary ✅
        ├── Phase 241: Diagnostics ✅
        ├── Phase 244: Attribution ✅
        └── Phase 247: Edge Tracker ✅

angel_index_ai_signals_with_forward.csv (Phase 221)
└── Phase 239: PnL Joiner (join key)

system3_vol_regimes.csv (Phase 217)
└── Phase 246: Trade Density ✅
```

---

## 🔍 DETAILED BREAKDOWN

### **Phase 238 - Schema Guard**
- **File**: `storage/live/angel_virtual_orders.csv`
- **Checks**: 15 required columns, data types, row count
- **Output**: `logs/execution/system3_virtual_orders_schema_report.md`
- **Will OK**: When file exists with valid schema

### **Phase 239 - PnL Joiner**
- **Input Files**: 
  - `storage/live/angel_virtual_orders.csv`
  - `storage/live/angel_index_ai_signals_with_forward.csv` ✅ (exists)
- **Join Keys**: `ts`, `underlying`, `strike`, `side`, `option_type`, `expiry`
- **Output**: `storage/live/angel_virtual_orders_with_pnl.csv`
- **Adds Columns**: `pnl_1`, `pnl_3`, `pnl_5` (from forward returns)
- **Will OK**: When both input files exist and have matching rows

### **Phase 240 - PnL Summary**
- **File**: `storage/live/angel_virtual_orders_with_pnl.csv`
- **Computes**: Overall win rate, per-day summary, per-underlying summary
- **Output**: `logs/research/system3_virtual_trades_pnl_report.md`
- **Will OK**: When enriched file exists with PnL data

### **Phase 241 - Diagnostics**
- **File**: `storage/live/angel_virtual_orders_with_pnl.csv`
- **Checks**: Invalid lots, unknown underlyings, outliers, correlation
- **Output**: `logs/research/system3_virtual_trades_diagnostics.md`
- **Will OK**: When enriched file exists with valid data

### **Phase 244 - Attribution**
- **Input Files**:
  - `storage/live/angel_virtual_orders_with_pnl.csv`
  - `storage/live/angel_index_ai_signals.csv`
- **Analyzes**: Which score components drive trades
- **Output**: `logs/research/system3_score_to_trade_attribution.md`
- **Will OK**: When both files exist and have matching rows

### **Phase 245 - Participation**
- **File**: `storage/live/angel_virtual_orders.csv`
- **Summarizes**: Trades per underlying, BUY vs SELL, per-expiry
- **Output**: `logs/research/system3_symbol_participation_summary.md`
- **Will OK**: When virtual orders file exists

### **Phase 246 - Trade Density**
- **Input Files**:
  - `storage/live/angel_virtual_orders.csv`
  - `storage/meta/system3_vol_regimes.csv` (optional)
- **Analyzes**: Trade density by volatility regime
- **Output**: `logs/research/system3_trade_density_vs_regime.md`
- **Will OK**: When orders file exists (regimes optional)

### **Phase 247 - Edge Tracker**
- **File**: `storage/live/angel_virtual_orders_with_pnl.csv`
- **Tracks**: Edge (profitability) by score buckets
- **Output**: `storage/meta/system3_edge_by_score_bucket.csv`
- **Buckets**: `(-inf, 0.0)`, `[0.0, 0.1)`, `[0.1, 0.2)`, `[0.2, 0.3)`, `[0.3, inf)`
- **Will OK**: When enriched file exists with score + PnL data

---

## ✅ EXPECTED VALUES WHEN OK

| Phase | Expected Output |
|-------|----------------|
| **238** | `"Schema check complete: X rows, 0 missing cols"` |
| **239** | `"Enriched X orders: Y matched, Z unmatched"` |
| **240** | `"Generated report: X trades, Y% win rate"` |
| **241** | `"Diagnostics complete: 0 anomalies, correlation=X.XXX"` |
| **244** | `"Attribution report generated: 7 components"` |
| **245** | `"Participation summary generated: X trades"` |
| **246** | `"Trade density report generated"` |
| **247** | `"Edge tracked: 5 buckets"` |

---

## 🚀 QUICK FIX COMMANDS

### **To Resolve All WARN Phases**

```bash
# Step 1: Run autopilot (generates signals + virtual orders)
python system3_live_day_autopilot.py

# Step 2: Run PnL joiner (creates enriched file)
python system3_virtual_trades_enrichment.py

# Step 3: Verify all phases OK
python system3_phase_231_260_diagnostics.py
```

### **Individual Phase Checks**

```bash
# Check Phase 238
python system3_virtual_orders_schema_check.py

# Check Phase 239
python system3_virtual_trades_enrichment.py

# Check Phase 240
python system3_virtual_trades_summary.py

# Check Phase 241
python system3_virtual_trades_diagnostics.py

# Check Phase 244
python system3_score_to_trade_attribution.py

# Check Phase 245
python system3_symbol_participation_summary.py

# Check Phase 246
python system3_trade_density_vs_regime.py

# Check Phase 247
python system3_edge_by_score_bucket_tracker.py
```

---

## 📊 CURRENT FILE STATUS

### **Required Files**
- ❌ `storage/live/angel_virtual_orders.csv` - **MISSING** (needs Phase 237)
- ❌ `storage/live/angel_virtual_orders_with_pnl.csv` - **MISSING** (needs Phase 239)
- ✅ `storage/live/angel_index_ai_signals_with_forward.csv` - **EXISTS** (Phase 221)
- ✅ `storage/live/angel_index_ai_signals.csv` - **EXISTS** (from autopilot)
- ❓ `storage/meta/system3_vol_regimes.csv` - **UNKNOWN** (needs Phase 217)

---

## 🎯 SUMMARY

**All 8 WARN phases are EXPECTED and BENIGN.**

They will automatically show ✅ OK when:
1. Autopilot generates BUY/SELL signals (Phase 237)
2. Virtual orders are created (`angel_virtual_orders.csv`)
3. PnL enrichment runs (Phase 239)
4. Enriched file is created (`angel_virtual_orders_with_pnl.csv`)

**No action needed** - these phases will resolve automatically during normal autopilot operation.

---

**For detailed analysis**: See `docs/system3_phases_231_260_warn_phases_detailed_analysis.md`

