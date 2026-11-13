# 15 — Live-Only Market Gates (`NOT_VERIFIED` Outside NSE/BSE Trading Hours)

- **Generated At (IST)**: `2026-11-04T16:36:14.661862+05:30`
- **Current Market Session**: `CLOSED` (NSE/BSE regular session is `09:15–15:30 IST` Monday–Friday)
- **Truth Gate Policy**: Per Addendum E Section E.6, off-market replay and mocked tests prove code correctness (`offline_verified = PASS`), but NEVER substitute for live market open ticks (`live_market_verified = NOT_VERIFIED`).

## 1. Gates Pending Next Market-Open Window (`09:15–15:30 IST`)

| Gate | Description | Off-Hours Prep Status | Live Market Status | Exact Command for Next Market Open (`09:20 IST`) |
|---|---|---|---|---|
| **G3** | Live Authenticated Dhan Market Feed (`age_seconds <= 5s`) | **PREPARED** (`offline_verified = PASS`) | **NOT_VERIFIED** (Market Closed) | `Invoke-RestMethod http://127.0.0.1:8008/api/market/verified-summary` |
| **G5** | Full 218 Equity Options Live Batch Chain Scan (`freshness <= 60s`) | **PREPARED** (`218` NSE OPTSTK inventory verified in `04_218_219_UNIVERSE_RECONCILIATION.csv`) | **NOT_VERIFIED** (Market Closed) | `Invoke-RestMethod http://127.0.0.1:8008/api/dhan/discovery/full-market` |
| **G6** | Live NSE / Dhan / Moneycontrol 3-Way Tick Parity (`<= 0.05%` spread) | **PREPARED** (`06_NSE_DHAN_MONEYCONTROL_PARITY.csv` close parity verified) | **NOT_VERIFIED** (Market Closed) | `C:\Genesis_System3_clean\.venv\Scripts\python.exe scratch/step3_execute_100_commands_and_deliverables.py` |
