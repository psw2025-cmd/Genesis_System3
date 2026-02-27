# System3 Ultra: Daily Routine Guide

**Date**: 2025-11-29  
**Purpose**: Daily and weekly operational routines for System3 Ultra

---

## 🌅 Morning Routine (Pre-Market)

### Quick Health Check (2-3 minutes)

**Run**:
```cmd
system3_ultra_daily_quick.bat
```

**What It Does**:
- Phase 37: Policy & Risk Monitor
- Phase 38: Governance Summary
- Shadow Trades Check

**Review**:
- Policy dashboard: `storage/ultra/phase37_policy_risk_dashboard.md`
- Governance summary: `storage/ultra/phase38_governance_summary.md`

**Time**: 2-3 minutes

---

## 📊 During Market Hours

### Optional: Shadow Campaign

**Run** (if desired):
```cmd
# Via menu
run_system3.py → Option 102

# Or directly
python -m core.engine.system3_phase39_shadow_campaign
```

**What It Does**:
- Runs Phase 31 (fusion) + Phase 34 (shadow) in loops
- Configurable loops and sleep intervals
- Generates daily summary

**Config**: `storage/config/ultra_shadow_campaign_config.json`
- Default: 60 loops, 30 seconds sleep

**Output**: `storage/ultra/phase39_shadow_campaign_summary_YYYYMMDD.md`

**Time**: Varies (depends on loops)

---

## 🌆 After Market Close

### Full Daily Check (10-15 minutes)

**Run**:
```cmd
system3_ultra_daily_full.bat
```

**What It Does**:
- Phase 31: Ultra Decision Fusion
- Phase 32: Ultra vs Baseline Comparator
- Phase 35: Decision Auditor
- Phase 33: Promotion Planner
- Phase 37: Policy Monitor
- Phase 38: Governance Summary
- Shadow Trades Check

**Review**:
- All output files in `storage/ultra/`
- Check for any WARN/BLOCK decisions
- Review promotion eligibility

**Time**: 10-15 minutes

---

## 📅 Weekly Routine

### Weekly Governance Pack

**Run** (once per week):
```cmd
# Via menu
run_system3.py → Option 103

# Or directly
python -m core.engine.system3_phase40_weekly_governance_pack
```

**What It Does**:
- Aggregates last 7 days of outputs
- Creates weekly pack in `storage/ultra/weekly_packs/YYYYWW/`
- Includes: comparison, audit, shadow, governance summaries

**Output**:
- `weekly_governance_pack.md`
- `weekly_governance_pack_meta.json`
- `weekly_governance_pack_files.txt`

**Time**: 1-2 minutes

---

## 🔒 Promotion Workflow (When Ready)

### Step 1: Review Promotion Plan

**Check**:
```cmd
type storage\ultra\phase33_promotion_plan.md
```

**Review**:
- Eligible underlyings
- Recommended changes
- Eligibility criteria

---

### Step 2: Create Snapshot (REQUIRED)

**Run**:
```cmd
# Via menu
run_system3.py → Option 105

# Or directly
python -m core.engine.system3_phase42_snapshot_manager create
```

**What It Does**:
- Creates snapshot of baseline models and configs
- Stores in `storage/snapshots/YYYYMMDD_HHMMSS/`
- **REQUIRED** before any promotion

**Time**: 1-2 minutes

---

### Step 3: Set Promotion Flag (If Approving)

**Create file**:
```
storage/config/ultra_promotion_flag.txt
```

**Content** (exact keyword):
```
ALLOW_ULTRA_PROMOTION_STAGING
```

**⚠️ WARNING**: Only create this file if you explicitly want to stage promotion.

---

### Step 4: Run Promotion Executor (Staging Only)

**Run**:
```cmd
# Via menu
run_system3.py → Option 104

# Or directly
python -m core.engine.system3_phase41_promotion_executor
```

**What It Does**:
- Checks flag file (must contain keyword)
- Checks promotion plan (must have eligible underlyings)
- Checks snapshot (must exist)
- Copies Ultra models to staging: `core/models/angel_one_ultra_staging/`
- **NEVER overwrites baseline**

**Output**: `storage/ultra/phase41_promotion_staging_report.md`

**Time**: 1-2 minutes

---

### Step 5: Manual Review & Final Promotion

**After staging**:
1. Review staging report
2. Test staged models (if desired)
3. **Manual decision**: Copy from staging to baseline (if approved)
4. **Manual action required**: No automatic baseline changes

---

## 🛡️ Safety Checklist

### Before Any Promotion

- [ ] Review promotion plan (Phase 33)
- [ ] Create snapshot (Phase 42)
- [ ] Review weekly pack (Phase 40)
- [ ] Set promotion flag (if approving)
- [ ] Run promotion executor (Phase 41) - staging only
- [ ] Manual review of staged models
- [ ] Manual final promotion (if approved)

### Daily Safety Checks

- [ ] Run daily quick check (morning)
- [ ] Review audit results (Phase 35)
- [ ] Check for WARN/BLOCK decisions
- [ ] Review governance summary (Phase 38)

### Weekly Safety Checks

- [ ] Run weekly governance pack (Phase 40)
- [ ] Review week-over-week performance
- [ ] Check promotion eligibility changes
- [ ] Review any issues or warnings

---

## 📋 Daily All-In-One Script

### Complete Health & Backup

**Run**:
```cmd
system3_ultra_daily_all.bat
```

**What It Does**:
- Phase 43: Environment & Broker Guard
- Phase 37: Policy & Risk Monitor
- Phase 38: Governance Summary
- Phase 42: Create Snapshot

**Optional**:
- Phase 39: Shadow Campaign (if `-RunCampaign` flag set)

**Time**: 5-10 minutes

**When**: Daily (recommended after market close)

---

## 🚨 Important Reminders

### Strict Rules

1. **No Baseline Changes Without**:
   - ✅ Snapshot (Phase 42)
   - ✅ Promotion plan (Phase 33)
   - ✅ Staging (Phase 41)
   - ✅ Manual confirmation

2. **No Auto-Execution**:
   - ✅ Shadow trades logged only
   - ✅ Never executed automatically
   - ✅ DRY RUN only

3. **No Auto-Promotion**:
   - ✅ Requires explicit flag file
   - ✅ Requires snapshot
   - ✅ Staging only (never baseline)

---

## 📊 Monitoring Schedule

### Daily
- **Morning**: Quick check (2-3 min)
- **After Market**: Full check (10-15 min)
- **Optional**: Shadow campaign during market

### Weekly
- **Once per week**: Weekly governance pack
- **Review**: Promotion eligibility
- **Decide**: Promotion staging (if ready)

### Monthly
- **Review**: All weekly packs
- **Evaluate**: System performance
- **Plan**: Future improvements

---

## 🎯 Quick Commands Reference

```cmd
# Daily Quick
system3_ultra_daily_quick.bat

# Daily Full
system3_ultra_daily_full.bat

# Daily All-In-One
system3_ultra_daily_all.bat

# Weekly Pack
python -m core.engine.system3_phase40_weekly_governance_pack

# Create Snapshot
python -m core.engine.system3_phase42_snapshot_manager create

# List Snapshots
python -m core.engine.system3_phase42_snapshot_manager list

# Promotion Staging (after flag + snapshot)
python -m core.engine.system3_phase41_promotion_executor

# Env Guard
python -m core.engine.system3_phase43_env_guard
```

---

**Last Updated**: 2025-11-29  
**Status**: ✅ **Ready for Daily Use**

