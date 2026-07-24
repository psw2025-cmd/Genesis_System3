# System3 Option Strike Visibility Audit

Generated UTC: `2026-07-24T03:53:41.373542+00:00`

## Summary

- **Signal source**: `api:http://127.0.0.1:8000/api/gain_rank`
- **Option master source**: `security_id_list.csv`
- **Rows**: `4`
- **Paper trade allowed**: `0`
- **Blocked**: `4`

## Visibility Rows

| Underlying | Type | Score | CE/PE | Eligible | Expiry | Strike | Token | LTP | Spread % | Paper Allowed | Blocker Reason |
|---|---|---:|---|---:|---|---|---|---:|---:|---:|---|
| `NIFTY` | `INDEX` | `76.93` | `UNKNOWN` | `False` | `` | `` | `` | `None` | `None` | `False` | `OPTION_ELIGIBILITY_NOT_PROVEN;CE_PE_SIDE_NOT_PROVEN;EXPIRY_NOT_FOUND;STRIKE_NOT_FOUND;TOKEN_SECURITY_ID_NOT_FOUND;LTP_NOT_AVAILABLE` |
| `BANKNIFTY` | `INDEX` | `66.04` | `UNKNOWN` | `False` | `` | `` | `` | `None` | `None` | `False` | `OPTION_ELIGIBILITY_NOT_PROVEN;CE_PE_SIDE_NOT_PROVEN;EXPIRY_NOT_FOUND;STRIKE_NOT_FOUND;TOKEN_SECURITY_ID_NOT_FOUND;LTP_NOT_AVAILABLE` |
| `MIDCPNIFTY` | `INDEX` | `61.7` | `UNKNOWN` | `False` | `` | `` | `` | `None` | `None` | `False` | `OPTION_ELIGIBILITY_NOT_PROVEN;CE_PE_SIDE_NOT_PROVEN;EXPIRY_NOT_FOUND;STRIKE_NOT_FOUND;TOKEN_SECURITY_ID_NOT_FOUND;LTP_NOT_AVAILABLE` |
| `FINNIFTY` | `INDEX` | `34.58` | `UNKNOWN` | `False` | `` | `` | `` | `None` | `None` | `False` | `OPTION_ELIGIBILITY_NOT_PROVEN;CE_PE_SIDE_NOT_PROVEN;EXPIRY_NOT_FOUND;STRIKE_NOT_FOUND;TOKEN_SECURITY_ID_NOT_FOUND;LTP_NOT_AVAILABLE` |

## Verdict Rule

No row is paper-trade-ready unless option eligibility, expiry, strike, token/security id, quote, and liquidity assumptions are proven.
