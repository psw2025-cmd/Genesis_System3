# System3 Option Strike Visibility Audit

Generated UTC: `2026-10-29T10:19:30.207213+00:00`

## Summary

- **Signal source**: `api:https://genesis-system3-web-802404398783.asia-south1.run.app/api/gain_rank`
- **Option master source**: `security_id_list.csv`
- **Rows**: `4`
- **Paper trade allowed**: `0`
- **Blocked**: `4`

## Visibility Rows

| Underlying | Type | Score | CE/PE | Eligible | Expiry | Strike | Token | LTP | Spread % | Paper Allowed | Blocker Reason |
|---|---|---:|---|---:|---|---|---|---:|---:|---:|---|
| `NIFTY` | `INDEX` | `61.09` | `UNKNOWN` | `True` | `` | `` | `543323` | `125.0` | `0.8` | `False` | `CE_PE_SIDE_NOT_PROVEN;EXPIRY_NOT_FOUND;STRIKE_NOT_FOUND` |
| `FINNIFTY` | `INDEX` | `59.89` | `UNKNOWN` | `True` | `2026-06-30 14:30:00` | `22050.00000` | `35013` | `125.0` | `0.8` | `False` | `CE_PE_SIDE_NOT_PROVEN` |
| `MIDCPNIFTY` | `INDEX` | `35.32` | `UNKNOWN` | `True` | `2026-07-28 14:30:00` | `9400.00000` | `35018` | `125.0` | `0.8` | `False` | `CE_PE_SIDE_NOT_PROVEN` |
| `BANKNIFTY` | `INDEX` | `31.71` | `UNKNOWN` | `True` | `2026-06-30 14:30:00` | `65400.00000` | `35000` | `125.0` | `0.8` | `False` | `CE_PE_SIDE_NOT_PROVEN` |

## Verdict Rule

No row is paper-trade-ready unless option eligibility, expiry, strike, token/security id, quote, and liquidity assumptions are proven.
