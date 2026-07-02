# Analyzer Signal Proof — Phase 9

**Generated:** 2026-07-02 17:28 IST
**Mechanism proven:** ✅ Yes | **Latest signal fresh:** ❌ No (19 days stale)

## Evidence

`GET /api/gain_rank` returns real, structured predictions with genuine fields (not fabricated):

| Rank | Underlying | Gain Score | Expected Move % | Recommendation |
|---|---|---|---|---|
| 1 | NIFTY | 76.93 | 0.032 | TRADE |
| 2 | BANKNIFTY | 66.04 | 0.099 | TRADE |
| 3 | MIDCPNIFTY | 61.70 | 0.147 | TRADE |
| 4 | FINNIFTY | 34.58 | 0.031 | SKIP |

But `latest.date: "2026-06-13"` — **19 days stale**.

## Honest finding

The analyzer/ranking mechanism itself is real and functional. The staleness is a direct consequence of the scheduler bug this session already found and fixed (Phase 2-4): `daily_gain_rank` (09:15 IST) hasn't successfully fired in weeks because of the silent missed-window bug.

**Expected to self-heal**: once the catch-up-policy scheduler fix (this session's PR) is deployed, `daily_gain_rank` should fire again at its next 09:15 IST window (tomorrow, 2026-07-03) or via catch-up if a restart lands within its 30-minute window. Not verified live in this session — market closed before a fresh firing could be confirmed against the deployed fix.
