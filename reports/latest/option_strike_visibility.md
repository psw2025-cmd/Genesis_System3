# System3 Option Strike Visibility Audit

Generated UTC: `2026-08-29T18:20:55.119912+00:00`

## Summary

- **Signal source**: `baseline-index-signals`
- **Option master source**: `security_id_list.csv`
- **Rows**: `3`
- **Paper trade allowed**: `1`
- **Blocked**: `2`

## Visibility Rows

| Underlying | Type | Score | CE/PE | Eligible | Expiry | Strike | Token | LTP | Spread % | Paper Allowed | Blocker Reason |
|---|---|---:|---|---:|---|---|---|---:|---:|---:|---|
| `NIFTY` | `INDEX` | `0.85` | `CE` | `True` | `` | `` | `543323` | `125.0` | `0.8` | `False` | `EXPIRY_NOT_FOUND;STRIKE_NOT_FOUND` |
| `BANKNIFTY` | `INDEX` | `0.82` | `CE` | `True` | `2026-06-30 14:30:00` | `65400.00000` | `35000` | `125.0` | `0.8` | `True` | `PASS` |
| `RELIANCE` | `EQUITY` | `0.78` | `CE` | `False` | `` | `` | `` | `None` | `None` | `False` | `OPTION_ELIGIBILITY_NOT_PROVEN;EXPIRY_NOT_FOUND;STRIKE_NOT_FOUND;TOKEN_SECURITY_ID_NOT_FOUND;LTP_NOT_AVAILABLE` |

## Verdict Rule

No row is paper-trade-ready unless option eligibility, expiry, strike, token/security id, quote, and liquidity assumptions are proven.
