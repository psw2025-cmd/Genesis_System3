# System3 Ultra Phases 31-38: Test Commands

**Date**: 2025-11-29  
**Purpose**: Commands to test all phases 31-38 sequentially

---

## Prerequisites

1. Activate your virtual environment:
   ```powershell
   (venv) PS C:\Genesis_System3> 
   ```

2. Ensure required input files exist:
   - `storage/live/angel_index_ai_signals.csv` (for Phase 31)
   - `storage/reports_ultra/phase21_risk_evaluations.csv` (optional, for Phase 31)
   - `storage/reports_ultra/phase30_calibration_results.csv` (optional, for Phase 31)

---

## Option 1: Run All Tests Automatically

```powershell
(venv) PS C:\Genesis_System3> python test_phases_31_38.py
```

This will:
- Test all phases sequentially
- Check dependencies
- Verify output files
- Print a summary

---

## Option 2: Test Each Phase Individually

### Phase 31: Ultra Decision Fusion
```powershell
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase31_ultra_fusion
(venv) PS C:\Genesis_System3> type storage\ultra\phase31_ultra_fused_decisions.csv | Select-Object -First 10
```

**Expected Outputs**:
- `storage/ultra/phase31_ultra_fused_decisions.csv`
- `storage/ultra/phase31_ultra_fused_decisions_summary.json`

**Verification**:
- Check that CSV has columns: timestamp, underlying, strike, side, final_action, final_size, final_risk_flag
- Check distribution of final_action (mostly HOLD/AVOID, maybe few BUYs)

---

### Phase 32: Ultra vs Baseline Comparator
```powershell
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase32_ultra_vs_baseline
(venv) PS C:\Genesis_System3> type storage\ultra\phase32_ultra_vs_baseline_summary.md
```

**Expected Outputs**:
- `storage/ultra/phase32_ultra_vs_baseline_comparison.csv`
- `storage/ultra/phase32_ultra_vs_baseline_summary.md`

**Verification**:
- Check that summary MD contains comparison tables
- Verify baseline vs Ultra metrics are computed

---

### Phase 33: Ultra Promotion Planner
```powershell
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase33_promotion_planner
(venv) PS C:\Genesis_System3> type storage\ultra\phase33_promotion_plan.md
```

**Expected Outputs**:
- `storage/ultra/phase33_promotion_plan.json`
- `storage/ultra/phase33_promotion_plan.md`

**Verification**:
- Check that plan clearly marks eligible/not_eligible per underlying
- Verify "SUGGESTIONS ONLY" warnings are present
- Confirm no configs were modified

---

### Phase 34: Ultra Live Shadow Comparison
```powershell
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase34_ultra_shadow_exec
(venv) PS C:\Genesis_System3> type storage\live\angel_index_ai_ultra_trades_shadow.csv | Select-Object -First 10
```

**Expected Outputs**:
- `storage/live/angel_index_ai_ultra_trades_shadow.csv`

**Verification**:
- Check that CSV exists (may be empty if no BUY actions with SAFE risk)
- Verify column `reason` is always `ULTRA_SHADOW`
- Confirm shadow trades are logged but not executed

---

### Phase 35: Ultra Decision Auditor
```powershell
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase35_ultra_auditor
(venv) PS C:\Genesis_System3> type storage\ultra\phase35_decision_audit_report.md
```

**Expected Outputs**:
- `storage/ultra/phase35_decision_audit.csv`
- `storage/ultra/phase35_decision_audit_report.md`

**Verification**:
- Check counts of OK/WARN/BLOCK
- Verify no auto-config changes
- Check that serious issues are clearly listed

---

### Phase 36: Ultra Continuous Learning Cycle (CULL)
```powershell
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase36_cull_orchestrator
(venv) PS C:\Genesis_System3> type storage\ultra\phase36_cull_execution_log.md
```

**Expected Outputs**:
- `storage/ultra/phase36_cull_execution_log.md`

**Verification**:
- Check that each sub-phase is logged with START/END status
- Verify any failures are marked clearly
- Confirm no config files were changed

---

### Phase 37: Ultra Policy & Risk Monitor
```powershell
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase37_policy_risk_monitor
(venv) PS C:\Genesis_System3> type storage\ultra\phase37_policy_risk_dashboard.md
```

**Expected Outputs**:
- `storage/ultra/phase37_policy_risk_dashboard.md`

**Verification**:
- Check that dashboard is clear and human-readable
- Verify current safety settings are shown
- Check shadow trade statistics
- Confirm WARN/BLOCK issues are summarized

---

### Phase 38: Ultra Governance Summary
```powershell
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase38_governance_summary
(venv) PS C:\Genesis_System3> type storage\ultra\phase38_governance_summary.md
```

**Expected Outputs**:
- `storage/ultra/phase38_governance_summary.md`

**Verification**:
- Check that summary contains all sections (Performance, Risk, Promotion Readiness, Open Issues)
- Verify final GO/NO-GO recommendation is clear
- Confirm no automatic promotion occurred

---

## Phase Dependencies

```
Phase 31 (no dependencies)
    ├── Phase 32 (requires 31)
    │   └── Phase 33 (requires 32)
    ├── Phase 34 (requires 31)
    └── Phase 35 (requires 31)
        ├── Phase 36 (requires 32, 33, 35)
        └── Phase 37 (requires 35)
            └── Phase 38 (requires 32, 33, 35, 37)
```

**Recommended Test Order**:
1. Phase 31 (foundation)
2. Phase 32 (depends on 31)
3. Phase 33 (depends on 32)
4. Phase 34 (depends on 31)
5. Phase 35 (depends on 31)
6. Phase 36 (depends on 32, 33, 35)
7. Phase 37 (depends on 35)
8. Phase 38 (depends on 32, 33, 35, 37)

---

## Quick Verification Checklist

After running all phases, verify:

- [ ] Phase 31: `phase31_ultra_fused_decisions.csv` exists with expected columns
- [ ] Phase 32: `phase32_ultra_vs_baseline_summary.md` contains comparison tables
- [ ] Phase 33: `phase33_promotion_plan.md` shows eligibility per underlying
- [ ] Phase 34: `angel_index_ai_ultra_trades_shadow.csv` exists (may be empty)
- [ ] Phase 35: `phase35_decision_audit_report.md` shows OK/WARN/BLOCK counts
- [ ] Phase 36: `phase36_cull_execution_log.md` shows all steps executed
- [ ] Phase 37: `phase37_policy_risk_dashboard.md` shows safety settings
- [ ] Phase 38: `phase38_governance_summary.md` shows final recommendation

---

## Troubleshooting

### Phase 31 fails: "No live signals found"
- **Solution**: Ensure `storage/live/angel_index_ai_signals.csv` exists
- **Workaround**: Run menu option 11 to generate signals first

### Phase 32 fails: "No Ultra decisions found"
- **Solution**: Run Phase 31 first

### Phase 33 fails: "No comparison data found"
- **Solution**: Run Phase 32 first

### Phase 35 fails: "No Ultra decisions found"
- **Solution**: Run Phase 31 first

### Phase 36 fails: Import errors
- **Solution**: Ensure all required modules exist (real data extractor, blended builder, etc.)

### Phase 38 fails: "No promotion plan available"
- **Solution**: Run Phases 32, 33, 35, and 37 first

---

## Expected Test Results

When all phases pass:
- All output files created in `storage/ultra/`
- Shadow trades logged to `storage/live/angel_index_ai_ultra_trades_shadow.csv`
- No baseline files modified
- No configs changed
- All safety guarantees maintained

