# Q1 — Data Fetch Master Checklist

**Evidence classes:** CURRENT_GITHUB_MAIN + LIVE_API + prior forensic lanes E/F (PR #242)  
**Live broker:** connected / `dhan-access-token` v259 (asia-south1)

## Category matrix

| Category | Dataset | Source | Caller (primary) | Storage | Class |
|----------|---------|--------|------------------|---------|-------|
| A Master | Dhan security master | Dhan CDN / `fetch_security_list` | `scripts/sync_dhan_instruments_master.py`, `core/brokers/dhan/instruments.py` | `storage/instruments/…` | **PARTIAL** (rebuildable; Cloud Run durability caution) |
| A Master | Bundled fallback CSV | Repo | instruments cache | `security_id_list.csv` | **WORKING** (fallback) |
| B Spot | Index LTP / spots | Dhan LTP/OHLC REST + fallbacks | `core/brokers/dhan/market_ltp.py`, batch market-data | EPHEMERAL cache | **PARTIAL** |
| B Spot | India VIX | Provider-dependent | datasource chain | varies | **PARTIAL / UNKNOWN** per day |
| C Deriv | Option chain | Dhan OC (paced) → NSE/nsepython/bhavcopy/… | `core/data/datasource_manager.py` (7-source) | `_PUSHED_CHAIN_CACHE`, optional `state/chain_cache` | **PARTIAL** (806 risk on Dhan Data APIs) |
| C Deriv | Equity FO universe | Instruments + filters | `equity_fo_universe` / chain routers | derived | **PARTIAL** (Issue #188 gap historically) |
| D Fields | LTP/OHLC/quote | `market_ltp.py` | broker/UI batch | EPHEMERAL | **PARTIAL** |
| D Fields | OI / OI change | NSE/bhavcopy UDiFF `OpnIntrst`/`ChngInOpnIntrst` | `nse_provider`, bhavcopy parser | `storage/bhavcopy/`, `state/market_cache.json` | **PARTIAL** |
| D Fields | Full Greeks from Dhan | Often unsubscribed | — | — | **UNSUPPORTED / PARTIAL** (derived/proxy elsewhere) |
| E Hist | EOD bhavcopy | NSE FO UDiFF | `scripts/bhavcopy_downloader.py` (18:30 IST) | `storage/bhavcopy/` | **PARTIAL** (days-scale cache) |
| E Hist | Intraday 1m–1h lake | — | — | — | **MISSING / NOT_WIRED** as institutional lake |
| E Hist | Daily validations | Validator | `scripts/daily_gain_rank_and_validate.py` | `state/market_validations/`, gain_rank history | **PARTIAL** |

## Required fields per path (condensed)

| Path | Freq | Cache | Rate limit | Retry/backoff | Consumers |
|------|------|-------|------------|---------------|-----------|
| Instruments sync | ~08:35 IST (scheduled docs) | file + memory | provider limits | script-level | chain, FO universe, models resolve |
| Option chain | paced ~3.4s gap | push/TTL cache | FE rate-limit handling; Dhan 429 separate defect | paced + FE slower poll | UI Option Chain, ranking inputs |
| Bhavcopy | 18:30 IST | disk files | NSE download | downloader | signal engine, OI features, training |
| LTP/OHLC | on demand / poll | short TTL | concurrency risk | status probe bounded | TopBar, market-data batch |
| Datasource health | ~08:00 IST | `state/datasource_health.json` | probe | — | System Health UI/API |

## Live API notes (captured this session)
- `/api/gain_rank`: status present; rankings payload non-empty when file exists
- `/api/system_health`: token + datasource_health + jobs keys present
- `/api/accuracy_trend`: trend/avg_ρ/retrain_needed fields present

## Defects to track into Q2
- Dhan Data API **806** → fallback chain; risk of **source mismatch / synthetic leakage** if mislabeled
- Cloud Run **ephemeral** disk → history not PRODUCTION_DURABLE unless GCS
- Greeks completeness **NOT_PROVEN** for full strike surface

## Q1 overall: **PARTIAL**
