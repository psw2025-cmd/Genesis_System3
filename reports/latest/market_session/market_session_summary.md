# Market Session Truth — Phase 7

**Generated:** 2026-07-02 16:27 IST

| Field | Value |
|---|---|
| Date | 2026-07-02 (Thursday) |
| Trading day | Yes |
| Weekend | No |
| NSE holiday | No |
| Market hours (IST) | 09:15–15:30 |
| Current session | **POST_MARKET_CLOSED** |
| Paper lifecycle allowed now | **No** |

## Why not allowed right now

Market closed for the day — current time (16:27 IST) is past the 15:30 IST close. Market **was** genuinely open earlier today (confirmed via `/api/health` showing `market_status: open` and broker connected, observed during roughly the 12:00–16:25 IST window of this session), but backend instability during that window (see `api_health_summary.md`) prevented reliably capturing a complete paper lifecycle proof before close.

## Next market-day command

Tomorrow, 2026-07-03 (Friday, confirmed trading day), between 09:15–15:30 IST:

```
python core/engine/system3_phase82_job_scheduler.py --job-id paper_lifecycle_proof
```

Or wait for the scheduled runs (09:30 / 12:00 / 14:00 IST) and check `reports/latest/analyzer_paper_lifecycle_proof/`.
