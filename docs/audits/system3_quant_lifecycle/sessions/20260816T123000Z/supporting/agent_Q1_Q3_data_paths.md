# Genesis System3 Market-Data Audit

Audit date: 2026-08-16  
Trees inspected:

- `C:\System3\Genesis_System3`
- `C:\System3\Genesis_System3_broker_permfix`

No secret values were inspected or reproduced.

## Executive verdict

| Area | Classification | Finding |
|---|---|---|
| Dhan instrument master | PARTIAL | Correct daily CDN sync exists. Cloud evidence is fresh, but the main worktree’s local master is stale. Normalization defaults to derivatives only. |
| Index option chains | PARTIAL | Real Dhan REST option-chain path is implemented and previously produced valid rows, Greeks, OI and bid/ask. Current broker/token health is unstable and the path is rate-sensitive. |
| Equity option chains | PARTIAL | Security-ID resolution exists, but production streaming/scanning defaults primarily to four indices. Full OPTSTK coverage is not continuously fetched. |
| Spot indices/VIX | PARTIAL | Dhan marketfeed quote/OHLC/LTP implementation exists. The live-board route is present in `Genesis_System3_broker_permfix`, but absent from the current main app. |
| Cash equities | PARTIAL | The worktree can quote up to 40 broker holdings. There is no full NSE/BSE cash-market ingestion path. |
| Futures | NOT_WIRED | Futures appear in instrument master and bhavcopy, but no production futures quote/chain/history consumer path was found. |
| Live OHLC/volume | PARTIAL | Available through marketfeed/option chain, but no comprehensive durable time-series capture. |
| Greeks | WORKING when Dhan chain works | Parsed from official Dhan option-chain legs. |
| Dhan broker WebSocket | UNSUPPORTED | Dashboard WebSocket redistributes cached REST data; it is not a Dhan marketfeed WebSocket. |
| Index historical candles | NOT_WIRED | Dhan/yfinance fetcher exists but is effectively orphaned from UI/model/backtest. |
| Historical CE/PE candles | EMPTY | Real Dhan download pipeline exists, but contract list, raw data, dataset and proof artifacts are absent. |
| NSE FO bhavcopy | PARTIAL/STALE | Downloader and scheduled post-market consumer exist, but main ranking path no longer consumes bhavcopy and freshness is unproven. |
| Data-source failover | NOT_WIRED | Manager lists seven sources, but all non-Dhan `_try_*` methods are no-op shims. |
| Rate-limit resilience | RATE_LIMITED | Preventive pacing exists, but no explicit Dhan 429/`Retry-After` handling. Cloud evidence recorded eight HTTP 429 responses. |

---

# Q1 — Data fetch paths

## 1. Market master/reference data

**Status: PARTIAL**

| Property | Actual implementation |
|---|---|
| Source | Dhan official scrip-master CDN |
| Endpoints | `https://images.dhan.co/api-data/api-scrip-master-detailed.csv`; fallback compact CSV |
| Fetcher | `C:\System3\Genesis_System3\scripts\sync_dhan_instruments_master.py:36-40,56-63,81-117` |
| Frequency | Weekdays 08:35 IST: `config\system3_job_scheduler.json:60-72` |
| Timeout | 120 seconds |
| Retry/fallback | Detailed download once; compact is attempted only when invoked with `--force`. No exponential backoff or 429 handling. |
| Cache/storage | `storage\instruments\api-scrip-master-detailed.csv`, `OpenAPIScripMaster.json`, `master_meta.json` |
| Consumers | Instrument lookup, option symbol resolution, equity F&O universe, `/instruments`, historical contract builder |
| Fields | Security ID, symbol, underlying, expiry, strike, lot size, instrument type, exchange segment, tick size |
| Coverage caveat | `dataframe_from_dhan_csv()` defaults to `derivatives_only=True`, filtering `SEGMENT == D`: `core\data\instruments_master.py:71-83`. Cash instruments are therefore not in the normal runtime JSON. |

Freshness evidence:

- Main local metadata: 219,686 source rows, 125,096 normalized rows, last sync `2026-07-21`: `storage\instruments\master_meta.json:2-11` — **STALE locally**.
- Cloud snapshot: 210,446 source rows, 119,552 runtime rows, synced `2026-08-15T21:44:51Z`: `reports\latest\full_cloud_ui_forensic_scratch\live_api\chains\api_instruments_health:1` — **WORKING in sampled cloud runtime**.

Reference resolution:

- Option security ID, symbol, expiry and lot size lookup:  
  `core\brokers\dhan\nse_option_symbol.py:219-309`.
- Full OPTSTK universe reads the bundled `security_id_list.csv`, not necessarily the latest synced master:  
  `core\brokers\dhan\equity_fo_universe.py:17-18,75-143`.
- Hardcoded index IDs: NIFTY 13, BANKNIFTY 25, FINNIFTY 27, MIDCPNIFTY 442, SENSEX 51:  
  `core\data\datasource_manager.py:45-63`.

## 2. Index spot, VIX and cash quotes

**Status: PARTIAL / branch-dependent**

### Dhan marketfeed path

| Property | Actual implementation |
|---|---|
| Source | Dhan REST marketfeed |
| Endpoints | `/v2/marketfeed/ohlc`, `/quote`, `/ltp` |
| Fetcher | `core\brokers\dhan\market_ltp.py:16-18,138-183` |
| Symbols | NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX, India VIX |
| Fields | LTP, open, high, low, close, net change, percentage change |
| Timeout | 8 seconds per REST attempt |
| Fallback order | OHLC → quote → LTP → SDK methods |
| Retry | String security IDs followed by integer IDs; no backoff or `Retry-After` handling |
| Durable storage | None in this module |
| Consumers | Index ribbon and broker position LTP enrichment, where wired |

Important wiring split:

- Current main `dashboard\backend\app.py` has **no** `/api/market/live_board` route and no caller of `build_index_board()`; therefore index/VIX quote board is **NOT_WIRED on current main**.
- `C:\System3\Genesis_System3_broker_permfix\dashboard\backend\app.py:1068-1184` wires `/api/market/live_board`, with a 3-second cache and 12-second outer timeout.
- That worktree also refreshes at most 40 holdings through `NSE_EQ`: lines 1111-1148.
- Worktree frontend consumes it at `dashboard\frontend\src\hooks\useData.ts:303-327`.

Cash-market limitation:

- Only broker holdings are enriched.
- No full NSE/BSE equity universe quote collector was found.
- BSE cash and broad NSE cash OHLC/history are not wired.

## 3. Derivatives option-chain path

**Status: PARTIAL, previously working, currently operationally unstable**

| Property | Actual implementation |
|---|---|
| Source | Dhan option-chain REST/SDK |
| API | SDK `expiry_list()` then `option_chain()` / `get_option_chain()` |
| Caller | `core\data\datasource_manager.py:193-213,283-364` |
| Parser | `core\data\dhan_option_chain_parser.py:34-69,72-163` |
| API/UI | `dashboard\backend\app.py:3678-3724`; adapter at `dashboard\backend\chain_adapter.py:60-156` |
| Frequency | Index micro-loop round-robin every 3.5 seconds open, 20 seconds closed: `app.py:5363-5399` |
| API hard limit | Process-wide minimum 3.4 seconds between option-chain calls: `datasource_manager.py:21-35` |
| In-memory cache | DSM 5 seconds; app chain TTL 20 seconds |
| Pushed-cache freshness | 45 seconds open, 1 hour closed; stale serving up to 180 seconds open or 24 hours closed |
| Timeout | API request path 25 seconds open, 8 seconds closed; micro-loop allows 28 seconds |
| Retry | One bounded retry after another 3.4-second delay |
| 429 handling | No explicit 429/body classifier, exponential backoff or `Retry-After` support |
| Durable storage | `state\chain_cache\{SYMBOL}.json`; local/session durable only, ephemeral on ordinary Cloud Run filesystem |
| Consumers | Option Chain UI, Market Top scanner, paper engine, GainRank, charts/Greeks UI |

Fields parsed from official Dhan legs:

- Security ID
- LTP and previous close
- OI and previous OI
- OI change
- Volume and previous volume
- Top bid/ask price and quantity
- IV
- Delta, gamma, theta, vega

Evidence: `core\data\dhan_option_chain_parser.py:34-69`.

Coverage:

- Continuously warmed: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY.
- SENSEX is supported by DSM but absent from current main `_INDEX_STREAM_SYMBOLS`: `app.py:1811`.
- Equity OPTSTK IDs can be resolved dynamically, but market-top equity enrichment defaults off: `app.py:5433-5444`.
- Full master-wide option streaming is therefore **NOT_WIRED**.

Prior cloud evidence from 2026-08-06 showed 160-contract Dhan snapshots for five indices, but this is historical proof, not current live proof:  
`reports\latest\dashboard_visible_issue_tracker\summary.json:98,202-213`.

## 4. Futures

**Status: NOT_WIRED**

- Futures rows are retained by the derivative instrument master.
- NSE FO bhavcopy stores futures alongside options.
- No dedicated live futures marketfeed collector, futures API endpoint, futures feature pipeline, or historical futures consumer was found.
- `DataSourceManager.fetch_option_chain()` is option-specific.

## 5. Dashboard WebSocket

**Status: PARTIAL / not broker WebSocket**

- `/ws/stream` pushes cached chains, chain spots, Market Top and heartbeat data.
- It does not subscribe to Dhan’s marketfeed WebSocket.
- Backend REST micro-loops own the actual market retrieval.
- Therefore a UI “WS LIVE” indicator means dashboard cache fan-out, not exchange/broker tick streaming.

## 6. API/UI chain fallback

**Status: PARTIAL with stale-data risk**

Current API preference:

1. Fresh pushed cache.
2. Stale-but-usable pushed cache.
3. Local TTL.
4. Live paced Dhan fetch.
5. `state\chain_cache\{symbol}.json`.
6. `outputs\chain_raw_live.csv`.
7. Empty result.

Evidence: `dashboard\backend\app.py:3678-3724,3822-3907,3960-4162`.

CSV fallback is explicitly marked `STALE_CSV_FALLBACK`, which is correct, but it still supplies market fields after Dhan failure.

---

# Q2 — Data quality

## Field-quality matrix

| Field | Source and status |
|---|---|
| Security ID | WORKING from Dhan master and option-chain legs |
| Symbol/underlying | WORKING, though normalizer may derive underlying from symbol text |
| Expiry | WORKING via `expiry_list`; calendar fallback is risky |
| CE/PE | WORKING from Dhan leg type/master symbol |
| Lot size | WORKING from master; defaults may be used when lookup fails |
| LTP | WORKING when Dhan marketfeed/chain succeeds |
| OHLC | PARTIAL; marketfeed board only, no durable capture |
| Volume | WORKING for option-chain legs and bhavcopy |
| Bid/ask | WORKING for option-chain top-of-book only |
| OI | WORKING for option chain and bhavcopy |
| Previous OI | WORKING from Dhan leg where supplied |
| Greeks | WORKING from Dhan chain; absent in bhavcopy |
| Futures fields | NOT_WIRED |
| Market depth beyond top bid/ask | UNSUPPORTED in normalized path |

## Critical quality defects

### 1. Advertised fallback chain is non-functional

`DataSourceManager.fetch_option_chain()` lists Dhan, NSE, nsepython, bhavcopy, jugaad, yfinance and synthetic at lines 230-238. However:

- `_try_nse()`
- `_try_nsepython()`
- `_try_bhavcopy()`
- `_try_jugaad()`
- `_try_yfinance()`
- `_try_synthetic()`

all return `(None, None)`: `datasource_manager.py:504-524`.

Classification: **NOT_WIRED**.

### 2. Health check does not test market data

Full `health_check()` calls `dhan.get_holdings()`, not option chain, marketfeed or historical data: `datasource_manager.py:526-536`.

The quick health check calls the no-op NSE/bhavcopy shims:  
`scripts\datasource_health_check.py:50-87`.

Classification: **PARTIAL / misleading health signal**.

### 3. Broken NSE validator fallback

`src\validation\market_result_validator.py:193-220` imports `fetch_option_chain_json` from `core.data.nse_session`, but that module only defines disabled stubs and does not define `fetch_option_chain_json`: `core\data\nse_session.py:1-15`.

Classification: **NOT_WIRED**.

### 4. Ranking OI state is stale or missing

- `state\market_cache.json` was last updated 2026-06-13 and contains zero OI totals.
- `state\dhan_oi_cache.json` is absent.
- `state\iv_history.json` contains only 2026-06-13.
- `state\gain_rank_history.json` ends on 2026-06-13.

Classification: **STALE**.

Also, `daily_gain_rank_and_validate.py:114` references `dsm.last_error`, but `DataSourceManager` does not define that attribute. A failed chain can therefore cause an exception instead of a clean blocked proof.

### 5. Instrument master freshness differs by runtime

- Local main master: stale since 2026-07-21.
- Cloud evidence: fresh on 2026-08-15.

Classification: **PARTIAL**, not globally WORKING.

### 6. Rate limiting

Preventive controls:

- 3.4-second process-wide Dhan option-chain spacing.
- Single-thread option-chain executor.
- 20-second app cache.
- Frontend chain polls reduced to 30–60 seconds.
- Last-good payload retention on HTTP 429.

Missing controls:

- No explicit Dhan 429 parser.
- No `Retry-After` handling.
- No exponential backoff/jitter in DSM.
- Retry is unconditional and limited to one call.

Cloud evidence recorded eight HTTP 429s in approximately two hours, including `/api/batch/chains` and `/ws/stream`:  
`reports\latest\full_cloud_ui_forensic_scratch\lane_c_gcp\07_logs_summary.json:2-38`.

Classification: **RATE_LIMITED**.

## Dhan Error 806

Dhan Error 806 means the Data API entitlement is absent/expired for option-chain, quote or historical APIs.

Findings:

- Code does not explicitly classify or remediate Error 806.
- Old state documentation says Data APIs were subscribed through 2026-07-23, which is expired relative to this audit date.
- Later August evidence proves option-chain data worked on 2026-08-06, so “currently unsubscribed” cannot be concluded solely from that old date.
- Current broker/token failures are predominantly `TOKEN_EXPIRED_OR_INVALID`, not proven Error 806.
- If 806 appears now, option chain, quote/OHLC and historical Dhan paths should be classified **UNSUPPORTED** until subscription renewal.

Current entitlement status: **UNKNOWN**.  
Current authentication/runtime status: **unstable**.

---

# Q3 — Historical data

## 1. Index historical candles

**Status: NOT_WIRED**

| Property | Implementation |
|---|---|
| Source | Dhan historical/intraday SDK; yfinance daily fallback |
| Caller | `core\data\history_fetcher.py:52-154` |
| Instruments | Hardcoded indices only |
| Intervals | 1, 5, 15, 25, 60 minutes and daily |
| Fields | Timestamp, OHLC, volume |
| Timeout/backoff | SDK-controlled; no explicit timeout, retry or 429 handling |
| Cache | None |
| Durable storage | Only if manually called through `data_router.fetch_and_store_history()` |
| Consumers | No active UI/model/backtest caller found |

Despite the module comment mentioning “index options,” it requests `instrument_type="INDEX"` with index security IDs. It does not fetch option-contract history.

The `/chart/{symbol}` route does not call this fetcher. It only reads pre-existing CSVs from `outputs` or `state`:  
`dashboard\backend\app.py:8409-8422`.

## 2. Historical CE/PE candles

**Status: EMPTY / NOT_WIRED**

| Property | Implementation |
|---|---|
| Endpoint | `https://api.dhan.co/v2/charts/historical` |
| Pipeline | `scripts\options_ce_pe_history_pipeline.py` |
| Contract source | `state\options_history\contracts.csv` |
| Fields | OHLC, volume, OI, strike, expiry, CE/PE, security ID |
| Timeout | 45 seconds |
| Pacing | 3.25 seconds per contract |
| 429 handling | HTTP errors recorded, but no backoff or retry |
| Raw storage | `state\options_history\raw\...` |
| Dataset | `state\options_history\dataset\ce_pe_dataset.csv` |
| Model | `state\models\options_ce_pe_model.joblib` |
| Frequency | Not present in scheduler |
| Consumers | Dataset builder and local model trainer only |

Actual state:

- `state\options_history\contracts.csv` absent.
- `reports\latest\options_contract_builder\summary.json` absent.
- `reports\latest\options_ml_training\summary.json` absent.
- No evidence of raw CE/PE candles or trained model.

The contract builder exists at `scripts\build_options_history_contracts.py:101-174`, but is not scheduled.

## 3. NSE FO bhavcopy EOD history

**Status: PARTIAL / freshness UNKNOWN-to-STALE**

| Property | Implementation |
|---|---|
| Source | NSE archive ZIP |
| Endpoints | New UDiFF archive and legacy derivatives archive |
| Fetcher | `scripts\bhavcopy_downloader.py:40-45,83-148` |
| Frequency | Weekdays 18:30 IST |
| Timeout | 8-second NSE warm-up; 30-second archive request |
| Pacing | 2 seconds between backfill dates |
| 429 handling | None; switches URL format only |
| Storage | `storage\bhavcopy\YYYYMMDD_fo_bhavcopy.csv` |
| Fields | Futures/options OHLC, volume, OI, OI change, underlying price |
| Consumer | `scripts\run_signal_engine_from_bhavcopy.py`, scheduled 18:45 |

Limitations:

- Downloader validates `OPTIDX`, but modern UDiFF option rows may use `IDO`; file is still saved, so this mostly corrupts the diagnostic `opt=` flag.
- Signal runner filters only four indices: `run_signal_engine_from_bhavcopy.py:34-35,46-54`.
- It does not cover SENSEX, equities or futures.
- Main `DataSourceManager._try_bhavcopy()` is a no-op, so bhavcopy is not an operational live fallback.
- No current on-disk freshness proof was found.

## 4. Backtesting

**Status: EMPTY / NOT_WIRED**

- `/backtest` explicitly returns `available: false`: `dashboard\backend\app.py:8526-8528`.
- Replay tooling consumes option-chain snapshots/CSV, not a verified multi-timeframe historical candle lake.
- There is no durable, scheduled 1m-to-daily market-history store for broad NSE/BSE instruments.
- No corporate-action-adjusted equity history, continuous futures series, expired-option history catalog, partitioning or retention policy was found.

---

# Actual production call graph

```text
Dhan scrip-master CDN
  -> sync_dhan_instruments_master.py
  -> storage/instruments/*.csv + OpenAPIScripMaster.json
  -> instruments_cache.py
  -> option symbol/security-ID lookup
  -> option chain / UI discovery / optional history contract builder

Dhan expiry_list + option_chain
  -> DataSourceManager
  -> dhan_option_chain_parser
  -> chain_adapter
  -> app in-memory pushed/TTL cache
  -> /api/chain + /api/batch/chains + dashboard WS
  -> Option Chain UI / Market Top / paper engine / GainRank

Dhan marketfeed OHLC/quote/LTP
  -> market_ltp.py
  -> live_board and holdings enrichment only in broker_permfix worktree
  -> index/VIX ribbon and broker holdings

NSE FO archive
  -> bhavcopy_downloader.py
  -> storage/bhavcopy
  -> run_signal_engine_from_bhavcopy.py
  -> storage/live/dhan_index_ai_signals.csv
  -> ML-confidence reader

Dhan charts/historical
  -> options_ce_pe_history_pipeline.py
  -> currently blocked by absent contracts/data
```

## Bottom line

The only substantially implemented real-time market-data pipeline is the paced Dhan option-chain REST path. It is useful but narrow, rate-sensitive, locally cached, and operationally dependent on token/subscription health.

Genesis System3 does not currently have:

- Full NSE/BSE cash coverage.
- A production futures data pipeline.
- Dhan broker WebSocket ingestion.
- Full OPTSTK continuous coverage.
- A durable historical market-data lake.
- Working multi-source failover.
- Populated CE/PE historical training data.
- A wired real-candle backtest path.

**Finalizing report structure**

I’m organizing the final report according to subagent guidelines. It needs absolute paths and a structured Markdown format. I’ll make sure to differentiate between main and worktree, and there shouldn’t be any code edits. Tables will include all requested columns, like scopes, timestamps, verdicts, architecture call graphs, and major paths. For instance, I'll specify different statuses and details about polling intervals for each endpoint involved in the report. This will ensure clarity and organization!
**Clarifying cash equities and instruments**

I’m outlining the details on cash equities, confirming there are only holdings up to 40 in the worktree and no market-wide cash ingestion. The instrument master is set to 'derivatives_only' by default, which I’m marking as PARTIAL. For the options chain, I'm noting the Dhan expiry list and option chain as WORKING/PARTIAL due to runtime authorization and rate limits, while caches will be utilized. In future references, I’ll need to address parser values and the overall state quality, which seems stale.
**Reviewing historical data fetching**

I'm evaluating the historical data fetching aspects, noting that the history_fetcher indexes for Dhan and yfinance are marked as NOT_WIRED, lacking persistence apart from the data_router. The supported intervals are 1, 5, 15, 25, 60, and D, but the source claims options while actually focusing on indices. The options historical pipeline endpoint doesn't seem to return expected contract reports, indicating EMPTY/NOT_WIRED status and missing a scheduler. I'll classify the bhavcopy state as STALE/PARTIAL, reflecting on potential local cache issues.