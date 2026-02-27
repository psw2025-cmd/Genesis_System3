# BROKER LATENCY MONITOR - PHASE 368

**Generated:** 2025-12-10 07:51:56

## Executive Summary

This phase monitors latency of AngelOne broker API endpoints WITHOUT placing orders.
All measurements use read-only GET endpoints only.

**Overall API Health:** ACCEPTABLE

## Endpoint Performance Metrics

### [OK] Instrument Fetch

| Metric | Value |
|--------|-------|
| Min | 238.47 ms |
| Max | 306.16 ms |
| Mean | 276.6 ms |
| Median | 276.59 ms |
| Std Dev | 28.72 ms |
| P95 | 306.16 ms |
| Health | NORMAL |

### [OK] Feed Token Refresh

| Metric | Value |
|--------|-------|
| Min | 109.31 ms |
| Max | 129.29 ms |
| Mean | 118.2 ms |
| Median | 114.9 ms |
| Std Dev | 8.33 ms |
| P95 | 129.29 ms |
| Health | NORMAL |

### [OK] Quotes Retrieval

| Metric | Value |
|--------|-------|
| Min | 35.08 ms |
| Max | 114.91 ms |
| Mean | 71.6 ms |
| Median | 73.49 ms |
| Std Dev | 29.27 ms |
| P95 | 114.91 ms |
| Health | NORMAL |

## Detected Anomalies

### [WARN] Spike Risk

**Endpoint:** quotes_retrieval  
**Description:** P95 latency (114.91ms) exceeds mean by >50%  
**Severity:** MEDIUM

## Latency Thresholds

| Endpoint | Normal | Elevated | Critical |
|----------|--------|----------|----------|
| Instrument Fetch | < 300ms | 300-500ms | > 1000ms |
| Feed Token Refresh | < 150ms | 150-300ms | > 500ms |
| Quotes Retrieval | < 100ms | 100-200ms | > 400ms |

## Recommendations

- **Green (Normal):** API performance is acceptable for trading
- **Yellow (Elevated):** Monitor for further degradation
- **Red (Critical):** Consider reducing trade frequency or investigating

## Technical Notes

- All measurements use **read-only GET endpoints** only
- Zero order-placement calls are made during monitoring
- Measurements are simulated in DRY-RUN mode (no live API calls)
- In production, would connect to live AngelOne endpoints
- Graceful degradation if network unavailable

---

**Status:** [OK] Monitoring Complete (DRY-RUN)  
**Mode:** Read-only (no trading impact)  
**Next Review:** Every 30 minutes during market hours
