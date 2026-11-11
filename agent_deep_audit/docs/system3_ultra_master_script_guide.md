# System3 Ultra: Master Monitoring Script Guide

**Created**: 2025-11-29  
**Purpose**: Comprehensive monitoring and operations script for all System3 Ultra tasks

---

## 🎯 Quick Start

### Recommended: Use Menu-Driven Script

**Double-click or run**:
```cmd
system3_ultra_master_monitor.bat
```

This opens an interactive menu with all options.

---

## 📋 Available Scripts

### 1. Master Monitor (Menu-Driven) ⭐ RECOMMENDED
**File**: `system3_ultra_master_monitor.bat`  
**Purpose**: Interactive menu with all options  
**Time**: Varies by selection

### 2. Daily Quick Check
**File**: `system3_ultra_daily_quick.bat`  
**Purpose**: Quick 2-3 minute health check  
**Time**: 2-3 minutes  
**When**: Morning pre-market

### 3. Full Daily Check
**File**: `system3_ultra_daily_full.bat`  
**Purpose**: Complete after-market review  
**Time**: 10-15 minutes  
**When**: After market close

### 4. Original Simple Monitor
**File**: `monitor_ultra_system.bat`  
**Purpose**: Basic monitoring (original script)  
**Time**: 2-3 minutes

---

## 🎮 Menu Options (Master Monitor)

When you run `system3_ultra_master_monitor.bat`, you'll see:

```
1) Daily Quick Check (2-3 min) - Recommended for daily use
2) Full Daily Check (10-15 min) - Complete after-market review
3) Check Latest Decisions (Phase 31)
4) Check Shadow Trades
5) Check Promotion Status (Phase 33)
6) Compare Performance (Phase 32)
7) System Health Check
8) Run All Phases (31-38)
9) Exit
```

---

## 📖 What Each Option Does

### Option 1: Daily Quick Check
**Runs**:
- Phase 37: Policy & Risk Monitor
- Phase 38: Governance Summary
- Shadow Trades Check

**Output**: Quick health status  
**Time**: 2-3 minutes  
**When**: Morning pre-market

---

### Option 2: Full Daily Check
**Runs**:
- Phase 31: Ultra Decision Fusion
- Phase 32: Ultra vs Baseline Comparator
- Phase 35: Decision Auditor
- Phase 33: Promotion Planner
- Phase 37: Policy & Risk Monitor
- Phase 38: Governance Summary
- Shadow Trades Check

**Output**: Complete daily review  
**Time**: 10-15 minutes  
**When**: After market close

---

### Option 3: Check Latest Decisions
**Runs**:
- Phase 31: Ultra Decision Fusion
- Decision summary statistics

**Output**: Latest fused decisions with counts  
**Time**: 1-2 minutes  
**When**: Anytime to check signal status

---

### Option 4: Check Shadow Trades
**Runs**:
- Reads shadow trades file
- Shows count and recent trades

**Output**: Shadow trades status  
**Time**: < 1 minute  
**When**: Anytime to check shadow activity

---

### Option 5: Check Promotion Status
**Runs**:
- Phase 33: Promotion Planner
- Shows eligibility summary

**Output**: Promotion plan and eligibility  
**Time**: 1-2 minutes  
**When**: To review promotion readiness

---

### Option 6: Compare Performance
**Runs**:
- Phase 32: Ultra vs Baseline Comparator
- Shows comparison summary

**Output**: Performance comparison report  
**Time**: 1-2 minutes  
**When**: To compare Ultra vs baseline

---

### Option 7: System Health Check
**Runs**:
- Phase 35: Decision Auditor
- Phase 37: Policy & Risk Monitor
- Phase 38: Governance Summary
- File system check

**Output**: Complete health status  
**Time**: 3-5 minutes  
**When**: To verify system health

---

### Option 8: Run All Phases
**Runs**:
- All phases 31-38 sequentially

**Output**: Complete system status  
**Time**: 15-20 minutes  
**When**: Weekly comprehensive check

---

## 🚀 Usage Examples

### Daily Morning Routine
```cmd
system3_ultra_daily_quick.bat
```
Or run master monitor and select option 1.

### After Market Close
```cmd
system3_ultra_daily_full.bat
```
Or run master monitor and select option 2.

### Interactive Menu
```cmd
system3_ultra_master_monitor.bat
```
Then select from menu options 1-9.

### Command Line (Direct PowerShell)
```powershell
# Daily quick check
powershell -ExecutionPolicy Bypass -File .\system3_ultra_master_monitor.ps1 -Mode daily

# Full daily check
powershell -ExecutionPolicy Bypass -File .\system3_ultra_master_monitor.ps1 -Mode full

# Menu mode
powershell -ExecutionPolicy Bypass -File .\system3_ultra_master_monitor.ps1 -Mode menu
```

---

## 📊 Output Files

All scripts generate output files in `storage\ultra\`:

- `phase31_ultra_fused_decisions.csv` - Fused decisions
- `phase32_ultra_vs_baseline_summary.md` - Comparison report
- `phase33_promotion_plan.md` - Promotion plan
- `phase35_decision_audit_report.md` - Audit report
- `phase37_policy_risk_dashboard.md` - Policy dashboard
- `phase38_governance_summary.md` - Governance summary

---

## ⚙️ Features

### Automatic Virtual Environment Activation
- Scripts automatically activate venv if not already active
- No manual activation needed

### Color-Coded Output
- ✅ Green: Success messages
- ℹ️ White: Information
- ⚠️ Yellow: Warnings
- ❌ Red: Errors
- 🔵 Cyan: Headers

### Error Handling
- Checks for virtual environment
- Verifies file existence
- Provides helpful error messages

### Interactive Menu
- Easy navigation
- Clear descriptions
- Returns to menu after each operation

---

## 📅 Recommended Schedule

### Daily (Morning)
- **Script**: `system3_ultra_daily_quick.bat` or Option 1
- **Time**: 2-3 minutes
- **Purpose**: Quick health check

### Daily (After Market Close)
- **Script**: `system3_ultra_daily_full.bat` or Option 2
- **Time**: 10-15 minutes
- **Purpose**: Complete review

### Weekly
- **Script**: Master monitor, Option 8
- **Time**: 15-20 minutes
- **Purpose**: Comprehensive check

### As Needed
- **Script**: Master monitor, Options 3-7
- **Time**: 1-5 minutes each
- **Purpose**: Specific checks

---

## 🔧 Troubleshooting

### "Execution Policy" Error
**Solution**: Use the `.bat` files (they handle this automatically)

### "Virtual Environment Not Found"
**Solution**: Make sure you're in `C:\Genesis_System3` directory

### "Python Module Not Found"
**Solution**: Script should auto-activate venv, but if not:
```cmd
venv\Scripts\activate
```

### Menu Not Showing
**Solution**: Run the `.bat` file instead of `.ps1` directly

---

## 📝 Quick Reference

| Task | Script | Option | Time |
|------|--------|--------|------|
| Daily Quick | `system3_ultra_daily_quick.bat` | 1 | 2-3 min |
| Daily Full | `system3_ultra_daily_full.bat` | 2 | 10-15 min |
| Check Decisions | Master Monitor | 3 | 1-2 min |
| Check Shadow | Master Monitor | 4 | < 1 min |
| Check Promotion | Master Monitor | 5 | 1-2 min |
| Compare Perf | Master Monitor | 6 | 1-2 min |
| Health Check | Master Monitor | 7 | 3-5 min |
| All Phases | Master Monitor | 8 | 15-20 min |

---

## ✅ Status

**All scripts created and ready to use!**

- ✅ Master monitor script with menu
- ✅ Daily quick check script
- ✅ Daily full check script
- ✅ Batch file wrappers
- ✅ Comprehensive documentation

**Start using**: Double-click `system3_ultra_master_monitor.bat`

---

**Last Updated**: 2025-11-29

