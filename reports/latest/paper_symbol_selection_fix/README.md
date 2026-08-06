# Paper symbol selection fix — proof

## Live bug (Cloud, 2026-08-06 market open)

| Source | Contract | Side | Why |
|---|---|---|---|
| Paper open POS_0002 | NIFTY 24600 | **PE** | strategy=`OI_FLOW_PAPER` (OI change rank) |
| Dhan Market Top #1 | NIFTY 24700 | **CE** | +18.15% pure gain_pct |
| Dhan Market Top #2-8 | NIFTY 24500-24850 | **CE** | +15% to +17% gainers |

Paper was selecting by **OI flow**, not highest market gain → wrong PE while CE was the real mover.

## Fix

- `cloud_paper_engine._pick_signal`: primary rank = **Dhan LTP % gain** (OI only tie-break)
- `_pick_from_market_top`: map scanner `market_top_table` onto live chain strike/side
- `step(..., market_top=)`: prefer scanner-confirmed gainer; rotate legacy `OI_FLOW_PAPER` when top gainer differs (≥10% gain, chg>-5%)
- Paper loop + `/api/paper/tick` pass market top rows

## Local unit proof

```
PICKED NIFTY24700CE MARKET_TOP_GAIN_PCT dhan_market_top_rank_gain_pct=18.15
PROOF_OK
```

Live trading remains OFF. Paper only.
