# System3 Option Strike Visibility Audit

Generated UTC: `2026-07-03T18:04:50.495453+00:00`

## Summary

- **Signal source**: `no-signal-source-found`
- **Option master source**: `security_id_list.csv`
- **Rows**: `1`
- **Paper trade allowed**: `0`
- **Blocked**: `1`

## Visibility Rows

| Underlying | Type | Score | CE/PE | Eligible | Expiry | Strike | Token | LTP | Spread % | Paper Allowed | Blocker Reason |
|---|---|---:|---|---:|---|---|---|---:|---:|---:|---|
| `NO_SIGNAL_FOUND` | `UNKNOWN` | `None` | `UNKNOWN` | `False` | `` | `` | `` | `None` | `None` | `False` | `NO_SIGNAL_SOURCE_FOUND_OR_NO_SIGNAL_ROWS` |

## Verdict Rule

No row is paper-trade-ready unless option eligibility, expiry, strike, token/security id, quote, and liquidity assumptions are proven.
