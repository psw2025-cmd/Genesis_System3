# Market-Hours Repro Plan

**Required:** NSE session Mon–Fri 09:15–15:30 IST (prefer 09:30–15:00 core).

1. Record AUDIT_REQUEST_START; confirm `/api/deploy/info` serving SHA.
2. Prove broker connected; live=false.
3. For NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY: contracts>0, CE/PE, LTP/OI, source strip, fetched_at age.
4. Equity option sample (≥10 underlyings): chain rows + discovery count vs master.
5. India VIX on live_board freshness.
6. Concurrent 4-chain fetch must not yield CHAIN_FETCH_TIMEOUT.
7. 22-tab browser lifecycle on serving SHA; no WAITING that is unexplained by session.
8. 60-minute stability: no unexplained blank chain/tab; log 429 clusters.
9. Re-check serving SHA end.

Until then: label live-tick claims `MARKET_HOURS_VALIDATION_REQUIRED`.
