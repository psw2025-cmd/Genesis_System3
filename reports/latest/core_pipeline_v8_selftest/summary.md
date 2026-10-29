# Core Pipeline V8 Self-Test

Status: **PASS**

| Check | Result | Detail |
|---|---:|---|
| cash_equity_forecast_not_trade | PASS | Cash-only equity remains in forecast ledger and is blocked from trade with FORECAST_ONLY_CASH_EQUITY. |
| option_requires_real_dhan_quote | PASS | Option paper order requires a non-stale Dhan chain quote; non-Dhan files are blocked with NO_LIVE_OPTION_QUOTE. |
| paper_only_no_broker_order | PASS | Core Pipeline V8 writes JSON/CSV paper ledgers only and never calls broker order endpoints. |
| live_flags_safe | PASS | LIVE_TRADING_ENABLED=0 |
