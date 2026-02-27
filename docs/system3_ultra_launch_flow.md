# System3 Ultra Control Panel - Launch Flow

**Date**: 2025-11-29  
**Version**: 1.0  
**Status**: Complete

---

## Overview

This document maps the complete operational flow from Pre-Market through Intraday, Post-Market, Weekly Review, and Ultra Experiments, with all menu options mapped.

---

## Pre-Market (Before Market Open)

### Recommended Sequence

1. **Environment Check** (Option 50 or 107)
   - `angel_env_consistency_checker` or `system3_phase43_env_guard`
   - Verify environment variables, packages, directories

2. **Pre-Market Diagnostic** (Option OP1 or 48)
   - `angel_market_warmup_scanner`
   - Validate models, configs, directories

3. **System Health Check** (Option 2 or 18)
   - `health_check` or `angel_watchdog_recovery`
   - Verify system health

4. **Safety Status** (Option S)
   - Check all safety switches

**Menu Options**: OP1, 2, 18, 48, 50, 107, S

---

## Live Session (Market Hours)

### Recommended Sequence

1. **Start Live Signal Generation** (Option OP2 or 11)
   - `angel_live_ai_signals`
   - Continuous signal generation loop

2. **Monitor Signals** (Option 44)
   - `angel_live_snapshot_reasoner`
   - Analyze latest signals

3. **Trade Decision** (Option OP3)
   - `angel_trade_decision`
   - Generate trade plans

4. **Intraday Monitoring** (Option 16)
   - `angel_intraday_pnl_monitor`
   - Monitor active trades

5. **Ultra Shadow Execution** (Option 97)
   - `system3_phase34_ultra_shadow_exec`
   - Shadow trade logging

**Menu Options**: OP2, OP3, 11, 16, 44, 97

---

## Post-Market (After Market Close)

### Recommended Sequence

1. **Outcome Logging** (Option 55)
   - `angel_unified_outcome_logger_v3`
   - Log real trade outcomes

2. **Post-Market Analysis** (Option OP4 or 57)
   - `angel_daily_learning_digest`
   - Daily learning summary

3. **Misfire Detection** (Option 56)
   - `angel_misfire_classifier_v2`
   - Classify misfires

4. **Daily Reports** (Option 40)
   - `angel_daily_auto_reports`
   - Generate all daily reports

5. **PnL Summary** (Option 15)
   - `angel_daily_pnl_summary`
   - Daily PnL summary

**Menu Options**: OP4, 15, 40, 55, 56, 57

---

## Weekly Review (End of Week)

### Recommended Sequence

1. **Weekly Governance Pack** (Option OP5 or 103)
   - `system3_phase40_weekly_governance_pack`
   - Aggregate weekly data

2. **Weekly Summary** (Option 41)
   - `angel_weekly_summary_report`
   - Weekly summary report

3. **Rolling Dashboard** (Option 37)
   - `angel_rolling_learning_dashboard`
   - 7-day rolling dashboard

4. **Governance Summary** (Option 101)
   - `system3_phase38_governance_summary`
   - Ultra governance summary

5. **Policy & Risk Monitor** (Option 100)
   - `system3_phase37_policy_risk_monitor`
   - Policy dashboard

**Menu Options**: OP5, 37, 41, 100, 101, 103

---

## Ultra Experiments (Anytime)

### Recommended Sequence

1. **Shadow Data Engine** (Option 73)
   - `ultra_shadow_data_engine`
   - Build shadow dataset

2. **Ultra Feature Engineering** (Option 74)
   - `ultra_feature_engineering`
   - Expand features

3. **Train Ultra Models** (Option 75)
   - `ultra_train_models`
   - Train Ultra models

4. **Ultra Phases 21-30** (Options 84-93)
   - Run risk-adaptive intelligence phases

5. **Ultra Phases 31-38** (Options 94-101)
   - Run integration & governance phases

6. **Ultra Comparison** (Option 95)
   - `system3_phase32_ultra_vs_baseline`
   - Compare Ultra vs baseline

7. **Promotion Planning** (Option 96)
   - `system3_phase33_promotion_planner`
   - Plan promotions (suggestions only)

**Menu Options**: 73-101

---

## Complete Daily Flow

### Morning (Pre-Market)
```
OP1 → 50 → S → 2
```

### Intraday (Live Session)
```
OP2 → OP3 → 16 → 44
```

### Afternoon (Post-Market)
```
55 → OP4 → 56 → 40 → 15
```

### Evening (Weekly Review - Friday)
```
OP5 → 41 → 37 → 101 → 100
```

---

## Complete Weekly Flow

### Monday
- Pre-Market: OP1, 50, S
- Live: OP2, OP3
- Post-Market: 55, OP4, 40

### Tuesday-Thursday
- Pre-Market: OP1 (quick)
- Live: OP2, OP3
- Post-Market: 55, OP4, 40

### Friday
- Pre-Market: OP1, 50, S
- Live: OP2, OP3
- Post-Market: 55, OP4, 40
- Weekly: OP5, 41, 37, 101, 100

---

## Ultra Experiment Flow

### Phase 1: Data Preparation
```
73 → 74 → 70
```

### Phase 2: Model Training
```
75 → 76 → 77
```

### Phase 3: Risk-Adaptive Intelligence
```
84 → 85 → 86 → 87 → 88 → 89 → 90 → 91 → 92 → 93
```

### Phase 4: Integration
```
94 → 95 → 96 → 97 → 98
```

### Phase 5: Governance
```
99 → 100 → 101
```

### Phase 6: Rollout
```
102 → 103 → 104 → 105 → 106 → 107
```

---

**Last Updated**: 2025-11-29  
**Status**: Complete

