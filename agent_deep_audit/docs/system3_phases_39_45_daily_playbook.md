# System3 Ultra Phases 39-45: Daily Playbook

**Date**: 2025-11-29  
**Purpose**: Step-by-step daily operational playbook

---

## 📅 Daily Playbook

### Morning (Pre-Market) - 5 Minutes

**Step 1**: Run Quick Health Check
```cmd
system3_ultra_daily_quick.bat
```

**Step 2**: Review Outputs
- Check `storage/ultra/phase37_policy_risk_dashboard.md`
- Check `storage/ultra/phase38_governance_summary.md`
- Verify no errors

**Step 3**: Check Environment (Optional)
```cmd
python -m core.engine.system3_phase43_env_guard
```

---

### During Market Hours - Optional

**Option A**: Run Shadow Campaign
```cmd
run_system3.py → Option 102
```

**Or**:
```cmd
python -m core.engine.system3_phase39_shadow_campaign
```

**Note**: Campaign runs in loops (configurable). Can be interrupted with Ctrl+C.

---

### After Market Close - 15 Minutes

**Step 1**: Run Full Daily Check
```cmd
system3_ultra_daily_full.bat
```

**Step 2**: Review All Outputs
- Phase 31: Fused decisions
- Phase 32: Comparison summary
- Phase 35: Audit report (check for WARN/BLOCK)
- Phase 33: Promotion plan
- Phase 37: Policy dashboard
- Phase 38: Governance summary

**Step 3**: Check Shadow Trades
```cmd
type storage\live\dhan_index_ai_ultra_trades_shadow.csv
```

**Step 4**: Run Daily All-In-One (Optional)
```cmd
system3_ultra_daily_all.bat
```
- Creates snapshot automatically
- Runs all health checks

---

## 📅 Weekly Playbook

### Once Per Week (Recommended: Friday After Market)

**Step 1**: Run Weekly Governance Pack
```cmd
run_system3.py → Option 103
```

**Or**:
```cmd
python -m core.engine.system3_phase40_weekly_governance_pack
```

**Step 2**: Review Weekly Pack
- Location: `storage/ultra/weekly_packs/YYYYWW/`
- Review: `weekly_governance_pack.md`
- Check: `weekly_governance_pack_meta.json`

**Step 3**: Evaluate Promotion Readiness
- Review promotion plan (Phase 33)
- Check eligible underlyings
- Review metrics and recommendations

**Step 4**: Decision Point
- **If promoting**: Follow promotion workflow (below)
- **If not**: Continue monitoring

---

## 🔒 Promotion Workflow (When Ready)

### Prerequisites Checklist

- [ ] Weekly pack reviewed
- [ ] Promotion plan shows eligible underlyings
- [ ] Performance metrics acceptable
- [ ] Manual approval decision made

---

### Step 1: Create Snapshot (REQUIRED)

**Run**:
```cmd
run_system3.py → Option 105
```

**Or**:
```cmd
python -m core.engine.system3_phase42_snapshot_manager create
```

**Verify**:
```cmd
python -m core.engine.system3_phase42_snapshot_manager list
```

**Output**: `storage/snapshots/YYYYMMDD_HHMMSS/`

**⚠️ CRITICAL**: Snapshot is REQUIRED before any promotion.

---

### Step 2: Create Promotion Flag (If Approving)

**Create file manually**:
```
storage/config/ultra_promotion_flag.txt
```

**Content** (exact, case-sensitive):
```
ALLOW_ULTRA_PROMOTION_STAGING
```

**⚠️ WARNING**: Only create if you explicitly want to stage promotion.

---

### Step 3: Run Promotion Executor

**Run**:
```cmd
run_system3.py → Option 104
```

**Or**:
```cmd
python -m core.engine.system3_phase41_promotion_executor
```

**What Happens**:
- Checks flag file (must exist with keyword)
- Checks promotion plan (must have eligible underlyings)
- Checks snapshot (must exist)
- Copies Ultra models to staging directory
- **NEVER touches baseline**

**Output**: `storage/ultra/phase41_promotion_staging_report.md`

**Staging Location**: `core/models/dhan_ultra_staging/`

---

### Step 4: Review Staging Report

**Check**:
```cmd
type storage\ultra\phase41_promotion_staging_report.md
```

**Verify**:
- Which underlyings were staged
- Source paths
- Snapshot used
- Flag file status

---

### Step 5: Final Manual Promotion (If Approved)

**⚠️ MANUAL ACTION REQUIRED**

If you decide to promote staged models to baseline:

1. **Review staging report thoroughly**
2. **Test staged models** (if desired)
3. **Manual copy** from staging to baseline:
   ```cmd
   # Example (DO NOT RUN WITHOUT REVIEW):
   # copy core\models\dhan_ultra_staging\FINNIFTY_model.pkl core\models\dhan\FINNIFTY_model.pkl
   ```
4. **Document the promotion** (manual note)

**⚠️ CRITICAL**: This is a manual step. No automatic baseline changes occur.

---

## 🛡️ Safety Reminders

### Before Any Promotion

- ✅ Snapshot created (Phase 42)
- ✅ Promotion plan reviewed (Phase 33)
- ✅ Weekly pack reviewed (Phase 40)
- ✅ Manual approval decision made
- ✅ Flag file created (if approving)
- ✅ Staging completed (Phase 41)
- ✅ Staging report reviewed
- ✅ Final manual promotion (if approved)

### Daily Safety

- ✅ Run health checks daily
- ✅ Review audit results
- ✅ Check for WARN/BLOCK decisions
- ✅ Monitor shadow trades
- ✅ Review governance summary

### Weekly Safety

- ✅ Run weekly pack
- ✅ Review week-over-week performance
- ✅ Evaluate promotion readiness
- ✅ Plan next steps

---

## 🚨 Emergency Procedures

### If Something Goes Wrong

1. **Check Logs**:
   ```cmd
   type storage\logs_ultra\system3_phases_39_45.log
   ```

2. **Check Latest Snapshot**:
   ```cmd
   python -m core.engine.system3_phase42_snapshot_manager list
   ```

3. **Rollback Instructions** (if needed):
   - Latest snapshot: `storage/snapshots/YYYYMMDD_HHMMSS/`
   - Manually copy files from snapshot to baseline locations
   - **No automatic rollback** - manual action required

---

## 📊 Monitoring Checklist

### Daily
- [ ] Morning quick check completed
- [ ] After-market full check completed
- [ ] Audit results reviewed (no WARN/BLOCK)
- [ ] Governance summary reviewed
- [ ] Shadow trades checked

### Weekly
- [ ] Weekly pack generated
- [ ] Weekly pack reviewed
- [ ] Promotion eligibility checked
- [ ] Performance metrics reviewed

### Monthly
- [ ] All weekly packs reviewed
- [ ] System performance evaluated
- [ ] Promotion decisions made (if ready)
- [ ] Future improvements planned

---

## 🎯 Quick Reference

### Daily Commands
```cmd
# Morning
system3_ultra_daily_quick.bat

# After Market
system3_ultra_daily_full.bat

# All-In-One
system3_ultra_daily_all.bat
```

### Weekly Commands
```cmd
# Weekly Pack
python -m core.engine.system3_phase40_weekly_governance_pack
```

### Promotion Commands
```cmd
# Create Snapshot
python -m core.engine.system3_phase42_snapshot_manager create

# List Snapshots
python -m core.engine.system3_phase42_snapshot_manager list

# Stage Promotion (after flag + snapshot)
python -m core.engine.system3_phase41_promotion_executor
```

---

**Last Updated**: 2025-11-29  
**Status**: ✅ **READY FOR DAILY USE**

