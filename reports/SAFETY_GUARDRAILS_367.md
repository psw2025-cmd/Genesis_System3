# SAFETY GUARDRAIL RECOMMENDATIONS - PHASE 367

**Generated:** 2025-12-10 07:51:56

## Executive Summary

This phase analyzes system state and recommends safety guardrails to prevent losses.
**Status:** Analysis only - recommendations do NOT enforce changes.

## System State

| Metric | Value | Status |
|--------|-------|--------|
| Health Score | 50.0/100 | [GOOD] |
| Quality Score | 50.0/100 | [GOOD] |
| Volatility | medium | [NORMAL] |
| Conflict Load | 30.00% | [LOW] |
| Data Freshness | 1.00/1.0 | [GOOD] |


## Recommendations (2 active)

[WARN] **1 CRITICAL recommendations** require immediate attention

### [CRITICAL] REDUCE_TRADE_FREQUENCY [CRITICAL]

**Reason:** Health score low (50.0)  
**Action:** Reduce signal acceptance rate to 50%  
**Safety Level:** aggressive

### [HIGH] INCREASE_CONFIDENCE_THRESHOLD [HIGH]

**Reason:** Data quality degraded (50.0)  
**Action:** Increase minimum confidence to 0.70  
**Safety Level:** moderate

## Safety Rules

These hard-coded safety rules are ALWAYS enforced:

1. [OK] **LIVE_TRADING_ENABLED** = false (cannot be changed)
2. [OK] **USE_ANGELONE_LIVE_EXECUTION** = false (cannot be changed)
3. [OK] **DRY-RUN MODE** = enabled (all trades simulated only)
4. [OK] **POSITION LIMITS** enforced in execution layer
5. [OK] **LOSS LIMITS** enforced in execution layer

## Important Notes

- This phase **recommends** guardrails but does NOT enforce them
- Hard-coded safety rules in execution layer cannot be bypassed
- Always verify guardrail recommendations against live market conditions
- System is designed to fail-safe (DRY-RUN mode default)

---

**Status:** [OK] Analysis Complete (DRY-RUN)  
**Safety Mode:** DRY-RUN (no live orders possible)  
**Last Updated:** 2025-12-10 07:51:56
