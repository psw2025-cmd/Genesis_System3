# Comprehensive Dashboard E2E Test Report

**Generated:** 2026-02-10T06:59:28.146419

## Summary

- **Total Tabs:** 11
- **Tabs Passed:** 10
- **Tabs Failed:** 1
- **Total APIs Tested:** 36
- **APIs Passed:** 34
- **APIs Failed:** 2
- **Overall Status:** PASS

## Tab Results

### [PASS] Overview

- **Status:** PASS
- **Endpoints Passed:** 3
- **Endpoints Failed:** 0

**Endpoints:**

- [OK] `GET /api/state` - SSOT State
- [OK] `GET /api/health` - Health Check
- [OK] `GET /api/perf` - Performance Metrics

### [PASS] Chain Analytics

- **Status:** PASS
- **Endpoints Passed:** 3
- **Endpoints Failed:** 0

**Endpoints:**

- [OK] `GET /api/chain/NIFTY` - NIFTY Chain
- [OK] `GET /api/chain/BANKNIFTY` - BANKNIFTY Chain
- [OK] `GET /api/chain/FINNIFTY` - FINNIFTY Chain

### [PASS] Signals

- **Status:** PASS
- **Endpoints Passed:** 3
- **Endpoints Failed:** 0

**Endpoints:**

- [OK] `GET /api/state` - SSOT State (signals)
- [OK] `GET /api/signal/top` - Top Signal
- [OK] `GET /api/qc` - QC Status

### [PASS] Paper Trading

- **Status:** PASS
- **Endpoints Passed:** 3
- **Endpoints Failed:** 0

**Endpoints:**

- [OK] `GET /api/state` - SSOT State (positions)
- [OK] `GET /api/positions` - Positions
- [OK] `GET /api/pnl` - PnL Data

### [PASS] Alerts

- **Status:** PASS
- **Endpoints Passed:** 3
- **Endpoints Failed:** 0

**Endpoints:**

- [OK] `GET /api/state` - SSOT State (alerts)
- [OK] `GET /api/alerts/recent` - Recent Alerts
- [OK] `GET /api/alerts/unread` - Unread Count

### [PASS] Risk Dashboard

- **Status:** PASS
- **Endpoints Passed:** 3
- **Endpoints Failed:** 0

**Endpoints:**

- [OK] `GET /api/state` - SSOT State (risk)
- [OK] `GET /api/risk/portfolio` - Portfolio Risk
- [OK] `POST /api/risk/check-limits` - Check Risk Limits

### [PASS] Advanced Charts

- **Status:** PASS
- **Endpoints Passed:** 4
- **Endpoints Failed:** 0

**Endpoints:**

- [OK] `GET /api/charting/heatmap/NIFTY?metric=oi` - Heatmap (OI)
- [OK] `GET /api/charting/iv-surface/NIFTY` - IV Surface
- [OK] `GET /api/charting/greeks/NIFTY?greek=delta` - Greeks Chart
- [OK] `GET /api/charting/pcr/NIFTY` - PCR Chart

### [PASS] ML Performance

- **Status:** PASS
- **Endpoints Passed:** 3
- **Endpoints Failed:** 0

**Endpoints:**

- [OK] `GET /api/state` - SSOT State (model)
- [OK] `GET /api/ml/performance` - ML Performance
- [OK] `GET /api/ml/compare` - Model Comparison

### [PASS] Model Behavior

- **Status:** PASS
- **Endpoints Passed:** 3
- **Endpoints Failed:** 0

**Endpoints:**

- [OK] `GET /api/logs/tail?lines=50` - Runtime Logs
- [OK] `GET /api/audit/secrets` - Security Audit
- [OK] `GET /api/qc` - QC Status

### [PASS] Control Plane

- **Status:** PASS
- **Endpoints Passed:** 4
- **Endpoints Failed:** 0

**Endpoints:**

- [OK] `GET /api/learning/status` - Learning Status
- [OK] `GET /api/learning/insights` - Learning Insights
- [OK] `GET /api/forensic/report` - Forensic Report
- [OK] `GET /api/validation/status` - Validation Status

### [FAIL] Agent Console

- **Status:** FAIL
- **Endpoints Passed:** 2
- **Endpoints Failed:** 2

**Endpoints:**

- [FAIL] `GET /api/agent/status` - Agent Status
  - Error: {'detail': 'Not Found'}
- [OK] `GET /api/agent/memory` - Agent Memory
- [FAIL] `GET /api/agent/issues` - Detected Issues
  - Error: {'error': 'Request timeout'}
- [OK] `GET /api/agent/upgrade-plan` - Upgrade Plan

## Errors

- Agent Console - /api/agent/status: Unknown error
- Agent Console - /api/agent/issues: Request timeout


## Detailed Results

See JSON report: `comprehensive_e2e_test_20260210_065928.json`

---
**Test completed at:** 2026-02-10T06:59:28.146655
