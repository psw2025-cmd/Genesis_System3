# Options Big-Data Research Phase

Repository: `psw2025-cmd/Genesis_System3`  
Mode: analyzer/research only  
Live trading: disabled  
Model promotion: disabled

## Exact source scope

| Source | Maximum supported history | Resolution | Coverage | Limitation |
|---|---:|---|---|---|
| NSE F&O bhavcopy / UDiFF | Archive-dependent; requested from 2016-07-26 | End of day | All published F&O contracts, strikes and expiries in each daily file | No historical intraday bid/ask or order book |
| Dhan expired rolling options | 5 years | 1/5/15/25/60 minute | Index and stock options; OHLC, IV, volume, OI, strike and spot | ATM±10 only for near-expiry index options; ATM±3 for other contracts; 30-day request window |
| Dhan/NSE current option-chain snapshots | Forward collection | Snapshot/tick depending entitlement | Current listed contracts and live fields | Cannot be fabricated backward |
| Paid NSE historical order/trade data | Licensed period | Order/trade/tick | Full execution-grade market-event history | Paid licensed source; not bypassed by this phase |

The downloader reads the current Dhan detailed instrument master dynamically and includes `NSE_FNO` and `BSE_FNO` rows with `OPTIDX` or `OPTSTK`. Large data stays outside Git.

## Planning proof

A deterministic example with **140 stock-option underlyings plus 6 index-option underlyings** over `2021-07-26` through `2026-07-26` produces:

```text
underlyings:             146
stock underlyings:       140
index underlyings:         6
30-day date chunks:       61
planned Dhan requests: 409,920
```

This is a planning example. The real count must be regenerated from the current official instrument master at execution time.

## Storage contract

Large market data remains outside Git under the repository variable/environment variable `SYSTEM3_RESEARCH_DATA_ROOT`.

```text
<SYSTEM3_RESEARCH_DATA_ROOT>/
  reference/api-scrip-master-detailed.csv
  manifest.sqlite3
  nse_fo_eod/<year>/*.parquet
  dhan_rolling/<exchange>/<OPTIDX|OPTSTK>/<symbol>/<year>/*.parquet
reports/latest/options_bigdata_research/
  summary.json
  summary.md
  full_pipeline_summary.json
  training_metrics.json
  research_model.joblib
```

## One-command resumable execution

```powershell
python scripts/options_bigdata_full_pipeline.py `
  --data-root "D:\System3ResearchData" `
  --nse-start 2016-07-26 `
  --dhan-start 2021-07-26 `
  --end 2026-07-26 `
  --interval 1 `
  --batch-limit 500 `
  --exchanges NSE,BSE
```

Each repeated bounded run processes the **next unfinished** manifest objects. `--batch-limit 0` requests an unbounded run.

## Individual commands

```powershell
python scripts/options_bigdata_download.py plan --start 2021-07-26 --end 2026-07-26
python scripts/options_bigdata_download.py download-nse --start 2016-07-26 --end 2026-07-26 --limit 500
python scripts/options_bigdata_download.py download-dhan --start 2021-07-26 --end 2026-07-26 --limit 500
python scripts/options_bigdata_download.py verify --start 2021-07-26 --end 2026-07-26
python scripts/options_research_train_backtest.py --horizon-bars 30 --cost-bps 40 --top-k 3 --decision-time 10:00
python -m pytest -q tests/test_options_bigdata_download.py tests/test_options_bigdata_full_pipeline.py tests/test_options_research_train_backtest.py
```

## Feature and label proof

Features use only information timestamped at or before `t`:

1. 1/5/15-bar option returns.
2. 15-bar realized volatility.
3. 30-bar volume z-score.
4. One-bar OI and IV change.
5. Moneyness.
6. Expiry code and weekly/monthly flag.
7. Relative strike offset.
8. CE/PE, index/stock and NSE/BSE indicators.
9. Intraday time sine/cosine.

The target is net option return at strictly later `t + horizon`. The split uses chronological train/validation/test dates, verifies that future label timestamps do not cross fold boundaries, and inserts a trading-day embargo.

The ranked backtest selects:

- one fixed decision snapshot per day,
- one best contract per underlying,
- then top-K distinct underlyings,
- after an explicit round-trip cost deduction.

## Acceptance gates

```text
LIVE_TRADING_ENABLED                       = 0
SYSTEM3_LIVE_TRADING_ALLOWED               = 0
order placement calls                      = 0
failed manifest objects                    = 0
unreconciled expected NSE sessions         = 0
SHA-256 mismatches                         = 0
missing/unreadable/empty files             = 0
duplicate normalized rows                  = 0
invalid OHLC rows                          = 0
negative volume/OI rows                    = 0
chronological fold overlap                 = 0
future labels crossing fold boundary       = 0
frozen test days                           >= 500
frozen test trades                         >= 1,000
positive net expectancy after costs        required
median daily Spearman rho                  > 0
model promotion                            = false in this phase
```

## Current freeze status

```text
PHASE: OPTIONS_BIGDATA_RESEARCH
STATUS: PARTIAL
CODE_PATH: FEATURE BRANCH
FOCUSED_TESTS: 10/10 PASS LOCALLY
DETERMINISTIC_PLANNER: 409,920 REQUESTS PASS
ACTUAL_NEW_MARKET_FILES_DOWNLOADED: 0
ACTUAL_NEW_MARKET_ROWS_DOWNLOADED: 0
MODELS_TRAINED_ON_NEW_REAL_DATA: 0
BACKTESTS_RUN_ON_NEW_REAL_DATA: 0
BLOCKERS: VALID CURRENT DHAN TOKEN; EXTERNAL PERSISTENT DATA ROOT; LONG-RUN DATA TRANSFER
NEXT_PHASE_ALLOWED: NO
LIVE_TRADING: DISABLED
TRADE_READY: NO
```
