# PIPELINE PROFILER - PHASE 369

**Generated:** 2025-12-10 07:51:56

## Executive Summary

This phase profiles the entire signal processing pipeline to identify performance
bottlenecks and resource usage patterns.

**Total Pipeline Size:** 2.47 MB  
**Estimated Processing Time:** 0.05s  
**Estimated Peak Memory:** 11 MB  
**Files Processed:** 2

## File-by-File Analysis


### angel_index_ai_signals_curated.csv

| Metric | Value |
|--------|-------|
| Size | 0.30 MB |
| Read Time | 0 ms |
| Throughput | 0.00 MB/s |


### angel_index_ai_signals_with_forward.csv

| Metric | Value |
|--------|-------|
| Size | 2.18 MB |
| Read Time | 45 ms |
| Throughput | 48.30 MB/s |

- [NOT FOUND] angel_index_ai_signals_deduped.csv
- [NOT FOUND] angel_index_ai_signals_with_forward_deduped.csv
## Memory Usage Estimate

| Component | Memory (MB) |
|-----------|----------|
| File Read | 7 |
| Processing | 3 |
| Overhead | 1 |
| **Total Peak** | **11** |

**Memory Classification:** [OK] Low (< 200 MB)

## [OK] No Critical Bottlenecks Detected

## Profiling Metrics Explanation

- **Size:** Actual file size on disk
- **Read Time:** Time to read entire file into memory
- **Throughput:** MB/s read rate (higher is better)
- **Estimated Memory:** Approximate peak memory during processing
- **Processing Time:** Estimated time for entire pipeline

## Optimization Recommendations

1. **Chunked Processing:** For files > 50 MB, consider processing in chunks
2. **Data Filtering:** Apply filters early to reduce data volume
3. **Parallel Processing:** Independent files can be processed in parallel
4. **Caching:** Cache frequently accessed data to reduce IO
5. **Compression:** Consider compressed storage for historical data

## Performance Targets

- Pipeline should complete in < 5 seconds
- Peak memory should stay < 500 MB
- Average IO throughput > 50 MB/s

---

**Status:** [OK] Profiling Complete (DRY-RUN)  
**Mode:** Read-only analysis  
**Next Profile:** After major code changes or data volume increases
