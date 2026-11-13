# GEMINI PROPOSAL: Free/Low-Cost Indian Options Data Sources — Ranked & Fallback Chain
**Date:** 2026-06-13 07:30 IST
**Author:** Gemini (Autonomous Investigator — Data Domains)
**Status:** PROPOSED — Requesting Codex verification and Claude approval
**Scope:** Production-grade data resilience for NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY option chains

---

## CONTEXT

- **Current state:** `core/data/nse_provider.py` uses NSE public API (`/api/option-chain-indices`), which fails in GitHub Codespace (anti-bot 404) but works on production machines.
- **Dhan Data APIs:** NOT subscribed (Error 806). Option chain, quotes, historical candles all blocked.
- **Critical need:** If NSE live API fails, system falls back to flat/synthetic OI → 30% scoring factor becomes noise → Spearman ρ collapses to ~0.20.
- **Goal:** Multi-source fallback chain so at least one source always provides real OI/IV data.

---

## 1. RANKED SOURCE ANALYSIS

### SOURCE 1: NSE Public API (CURRENT — Already Implemented)
**URL:** `https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY`

| Property | Details |
|---|---|
| **Data Provided** | Full option chain: all strikes, OI (current), IV per strike, volume, LTP, PCR, spot price |
| **Auth Required** | No API key — but requires session cookie from homepage warm-up (already handled in nse_provider.py) |
| **Reliability** | MEDIUM — Works on production machines. Fails in cloud/codespace (anti-bot detection). Rate-limited: ~1 req/3 min. |
| **Latency** | Near real-time (3 min delay) |
| **OI Change %** | NO — only current-session OI. Prev OI must come from `market_cache.json` |
| **IV Available** | YES — per strike |
| **Implementation** | DONE — `core/data/nse_provider.py` |
| **Pip Package** | `requests` (already in requirements.txt) |

**Verdict:** P1 (Production) / P2 (Codespace). Keep as primary for production.

---

### SOURCE 2: NSE F&O Bhavcopy Archives (NEW — HIGHEST PRIORITY FOR CODESPACE)
**URL (New UDiFF format, effective July 2024):**
`https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{YYYYMMDD}_F_0000.csv.zip`

**Legacy URL (pre-July 2024, still available for historical):**
`https://nsearchives.nseindia.com/content/historical/DERIVATIVES/{YYYY}/{MMM}/fo{DD}{MMM}{YYYY}bhav.csv.zip`

| Property | Details |
|---|---|
| **Data Provided** | Full F&O EOD: INSTRUMENT, SYMBOL, EXPIRY_DT, STRIKE_PR, OPTIONTYPE (CE/PE), SETTLE_PR (close), OPEN, HIGH, LOW, CONTRACTS (volume), VAL_INLAKH, OPEN_INT (OI), CHG_IN_OI (OI change!), TIMESTAMP |
| **Auth Required** | NO — public URL, no session cookie needed (different CDN from main site) |
| **Reliability** | HIGH — Static CDN archive, not an API. No anti-bot. Available from ~18:30 IST every trading day. |
| **Latency** | EOD only (available after 18:00 IST). Not intraday. |
| **OI Change %** | YES — `CHG_IN_OI` is directly available (today vs. yesterday). This is the key differentiator. |
| **IV Available** | NO — bhavcopy does NOT include implied volatility. Must compute from settlement price + BSM. |
| **NIFTY/BANKNIFTY filter** | Filter on `SYMBOL` column for NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY |
| **Implementation** | Requires new `core/data/bhavcopy_provider.py` module |
| **Pip Package** | `pandas`, `requests`, `zipfile` (all already available) |

**UDiFF Column Details (confirmed from NSE circulars, Jul 2024 onward):**
```
FinInstrmTp,TckrSymb,XpryDt,OptnTp,StrkPric,OpnPric,HghPric,LwPric,ClsPric,
SttlmPric,TtlTradgVol,TtlTrfVal,OpnIntrst,ChngInOpnIntrst,TradDt
```
*(Note: Column names vary slightly — the key ones are OI as `OpnIntrst` / `OPEN_INT`, change as `ChngInOpnIntrst` / `CHG_IN_OI`, strike as `StrkPric` / `STRIKE_PR`, option type as `OptnTp` / `OPTIONTYPE`.)*

**Download Strategy:**
- Download after 18:30 IST daily (when NSE uploads it)
- Store at: `state/bhavcopy/{YYYYMMDD}_fo_bhavcopy.csv`
- Retention: keep last 30 trading days (for IV percentile computation)
- On next morning: load yesterday's bhavcopy as baseline OI for "prev_oi"

**Verdict:** P2 (Codespace) / P3 (Production evening fallback). BEST source for guaranteed OI change data.

---

### SOURCE 3: nsepython / nsepythonserver
**Install:** `pip install nsepython` (laptop) or `pip install nsepythonserver` (server/cloud)

| Property | Details |
|---|---|
| **Data Provided** | Full NSE option chain via `nse_optionchain_scrapper(symbol)` — OI, IV, volume, LTP, spot price |
| **Auth Required** | NO — wraps NSE public API with session management built-in |
| **Reliability** | MEDIUM — Same underlying NSE API, but the `server` edition uses proxy rotation to bypass cloud anti-bot. Maintained, latest: v2.97 (May 2025). |
| **Latency** | Near real-time (same as NSE API — 3 min delay) |
| **OI Change %** | NO — only current OI snapshot |
| **IV Available** | YES — from NSE chain JSON |
| **Key Difference** | `nsepythonserver` specifically designed for AWS/GCP/DigitalOcean. Handles anti-bot detection better than raw requests. |
| **Pip Package** | `pip install nsepythonserver` (for cloud codespace use) |

**Usage:**
```python
from nsepython import nse_optionchain_scrapper
chain = nse_optionchain_scrapper("NIFTY", "index")
# Returns dict with 'records' → 'data' → list of {CE: {..., openInterest, impliedVolatility}, PE: {...}}
```

**Verdict:** P2 for cloud environments (better anti-bot than raw requests). Adds server edition as drop-in replacement for `nse_provider.py`.

---

### SOURCE 4: jugaad-data
**Install:** `pip install jugaad-data`

| Property | Details |
|---|---|
| **Data Provided** | NSE F&O bhavcopy download, live stock quotes, historical F&O |
| **Auth Required** | NO |
| **Reliability** | MEDIUM — Last version 0.31.1. Maintenance status: MODERATE (not actively developed, but stable). Does NOT yet support UDiFF format (open GitHub issue #79). |
| **Latency** | EOD bhavcopy only |
| **OI Change %** | YES (from bhavcopy `CHG_IN_OI`) |
| **IV Available** | NO |
| **Key Functions** | `bhavcopy_fo_save(date, "/path")` — downloads FO bhavcopy CSV for a given date |
| **Limitation** | UDiFF format (post-Jul 2024) not fully supported. May fall back to legacy URL. Cross-check before production use. |

**Verdict:** P4 (fallback). `jugaad-data` adds a convenience wrapper but doesn't add new data. Prefer direct bhavcopy download (Source 2) over this wrapper given UDiFF uncertainty.

---

### SOURCE 5: nsefin
**Install:** `pip install nsefin`

| Property | Details |
|---|---|
| **Data Provided** | Option chain + Greeks computation, F&O bhavcopy EOD |
| **Auth Required** | NO |
| **Reliability** | MEDIUM — Newer package, fewer community reports. Python 3.9+ required. |
| **Latency** | EOD bhavcopy + near-real-time option chain |
| **OI Change %** | From bhavcopy download |
| **IV Available** | YES — computes Greeks via `compute_greek()` |
| **Key Feature** | Can compute IV locally using BSM formula when NSE IV is unavailable |

**Verdict:** P4 alternative. Useful primarily for its local Greek computation capability.

---

### SOURCE 6: Shoonya/Finvasia API (ShoonyaApi-py)
**Install:** `pip install ShoonyaApi-py` (or `NorenRestApiPy`)

| Property | Details |
|---|---|
| **Data Provided** | Real-time option chain, OI, IV/Greeks (Delta, Theta, Gamma, Vega), LTP, bid/ask depth |
| **Auth Required** | YES — requires free Shoonya/Finvasia demat account + TOTP. Zero brokerage, zero API fees. |
| **Reliability** | HIGH — Exchange-direct data feed. Shoonya is a registered broker. Real-time (not delayed). |
| **Latency** | REAL-TIME (no delay) |
| **OI Change %** | YES — real-time |
| **IV Available** | YES — real-time Greeks |
| **Account** | Free Finvasia demat account (zero maintenance charges, zero brokerage for derivatives). F&O segment must be activated. TOTP mandatory. |
| **Key Function** | `api.get_option_chain(exchange='NFO', tradingsymbol='NIFTY', strikeprice=24500, count=10)` |
| **Limitation** | Requires a separate Finvasia account (separate from Dhan). Added credential management overhead. |

**Verdict:** P3 (strong alternative). If user opens a free Finvasia account, this becomes the best live fallback source — real-time, no anti-bot, all Greeks included. Worthwhile investment.

---

### SOURCE 7: Breeze Connect (ICICI Direct)
**Install:** `pip install breeze-connect`

| Property | Details |
|---|---|
| **Data Provided** | Option chain, OI, historical options data (up to 10 years), real-time OHLCV, 1-second granularity for backtesting |
| **Auth Required** | YES — requires free ICICIDirect demat account. API key generated from developer portal. |
| **Reliability** | HIGH — Broker-grade, officially maintained |
| **Latency** | Real-time via WebSocket |
| **OI Change %** | YES |
| **IV Available** | YES — Greeks available |
| **Historical Depth** | 10 YEARS of historical options data (1-second resolution) — unique advantage for backtesting |
| **Account** | Free ICICIDirect account. Zero charges for API access, data, and historical downloads. |
| **SEBI Note** | Static IP mandatory for API-based trading from April 2026 (but data-only usage may be exempt) |
| **Key Function** | `breeze.get_option_chain_quotes(stock_code="NIFTY", exchange_code="NFO", expiry_date="2025-12-31T06:00:00.000Z", right="Call", strike_price="24500")` |

**Verdict:** P3 (excellent for historical backtesting, real-time backup). 10-year historical options data is a strong differentiator for building IV percentile history. Requires ICICIDirect account.

---

### SOURCE 8: yfinance
**Install:** `pip install yfinance`

| Property | Details |
|---|---|
| **Data Provided** | Spot price for ^NSEI, ^NSEBANK (NIFTY and BANKNIFTY index levels). Historical OHLCV for index. NSE stock prices. |
| **Auth Required** | NO |
| **Reliability** | MEDIUM — Unofficial Yahoo Finance scraper. Works for spot price. Breaks periodically when Yahoo changes their API. |
| **Latency** | 15-min delayed (Yahoo Finance standard) |
| **OI Change %** | NO — no Indian F&O options data available |
| **IV Available** | NO |
| **Indian Options** | NOT AVAILABLE — Yahoo Finance shows ^NSEI options page but the data is empty/unreliable for Indian NSE options contracts. |
| **Best Use** | Spot price fallback ONLY: `yf.Ticker("^NSEI").history(period="1d")` → last close price |

**Verdict:** P6 (spot price only). Useful as last-resort spot price source but provides zero option chain data for Indian markets.

---

### SOURCE 9: OpenAlgo (Self-Hosted)
**Install:** `pip install openalgo` (Python client)

| Property | Details |
|---|---|
| **Data Provided** | Broker-agnostic option chain API. Routes to any connected broker (Zerodha, Fyers, Shoonya, etc.) |
| **Auth Required** | YES — requires self-hosted OpenAlgo server + connected broker account |
| **Reliability** | HIGH (if server running) — open source, active development |
| **Latency** | Real-time |
| **OI Change %** | YES (from broker feed) |
| **IV Available** | YES — Greeks included |
| **Complexity** | HIGH — requires running a local Flask server + broker connection setup |

**Verdict:** P7 (future architecture option). Too complex for current codespace setup. Revisit when system moves to dedicated server.

---

## 2. RECOMMENDED FALLBACK CHAIN (P1 → P7)

```
P1: NSE Public API (nse_provider.py — ALREADY IMPLEMENTED)
    ↓ fails (anti-bot, 403, 404, timeout)
P2: NSE Bhavcopy Archive (nsearchives.nseindia.com CDN — to be implemented)
    → Direct CDN download, no session cookie, no anti-bot
    → LIMITATION: EOD only (not intraday). Use as cache for morning startup.
    ↓ fails (NSE CDN down)
P3: nsepythonserver (for cloud) / nsepython (for local)
    → Better anti-bot handling than raw requests
    → Same NSE data, session-managed by library
    ↓ fails (NSE fully down)
P4: Shoonya/Finvasia API (IF free account created)
    → Broker-direct, real-time, independent of NSE website
    ↓ fails (Shoonya API down / no account)
P5: Breeze Connect / ICICI Breeze (IF free account created)
    → Broker-direct, real-time, 10yr historical
    ↓ fails (all broker APIs down)
P6: Last-known-good bhavcopy state (state/bhavcopy/ directory)
    → Load most recent bhavcopy file (<= 5 trading days old)
    → Use as OI baseline — set OI_CHANGE = 0 (flat), flag "STALE_DATA" in output
P7: Synthetic fallback (EXISTING — flat OI = 100000 for all strikes)
    → Zero signal, no contamination. Log WARNING.
```

---

## 3. BHAVCOPY AUTO-DOWNLOAD STRATEGY

### When to Download
- **Trigger:** Daily at 18:30 IST (after NSE upload, typically available by 18:00–18:30)
- **Add to scheduler:** New job `bhavcopy_downloader` at 18:30 in `config/system3_job_scheduler.json`

### What to Download
```
URL: https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{YYYYMMDD}_F_0000.csv.zip
```

### Where to Store
```
state/bhavcopy/raw/         → raw ZIP files (keep 5 trading days)
state/bhavcopy/processed/   → extracted CSV filtered to NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY
```

### What to Extract
Filter CSV rows where `TckrSymb` (or `SYMBOL`) is in `[NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY]`
AND `FinInstrmTp` (or `INSTRUMENT`) starts with `OPT` (options, not futures).

**Key columns to extract and cache:**
```python
{
  "symbol": "NIFTY",
  "expiry": "2026-06-26",
  "strike": 24500,
  "option_type": "CE",
  "oi": 2345000,
  "oi_change": 125000,          # CHG_IN_OI — direct from bhavcopy
  "volume": 456789,             # CONTRACTS
  "settle_price": 245.50,       # SETTLE_PR (for IV computation)
  "trade_date": "2026-06-13"
}
```

### Caching Strategy for Morning Use
At 09:00 IST (before ranking run), `nse_provider.py` should:
1. Try NSE live API first
2. If live fails → load yesterday's bhavcopy from `state/bhavcopy/processed/`
3. Use bhavcopy `OPEN_INT` as `prev_oi`, and live NSE (if available) for `curr_oi`
4. If BOTH fail → use bhavcopy `OPEN_INT` as `curr_oi` AND `OPEN_INT - CHG_IN_OI` as `prev_oi` (reconstruct from bhavcopy change)

### Retention Policy
- Keep 30 days of bhavcopy (for IV percentile computation: need 30-day rolling IV window)
- Auto-delete files older than 30 days

---

## 4. WHEN ALL LIVE SOURCES FAIL (Bhavcopy Last-Known-Good State)

### Detection Logic
```python
def get_data_with_fallback(symbols):
    # 1. Try P1 (NSE live)
    chain = nse_provider.fetch_option_chain(symbol)
    if chain and total_oi > 0:
        return chain, "LIVE_NSE"
    
    # 2. Try P2 (bhavcopy last known good)
    bhavcopy = load_latest_bhavcopy(max_age_days=5)
    if bhavcopy:
        return bhavcopy, "BHAVCOPY_EOD"
    
    # 3. P7: Synthetic (zero signal, no corruption)
    logger.warning("ALL DATA SOURCES FAILED — using synthetic flat OI")
    return synthetic_flat_oi(), "SYNTHETIC"
```

### What to Do With Stale Bhavcopy
- **Age 1 day:** Use normally. OI from T-1 is fine for trend detection.
- **Age 2–3 days:** Use but multiply OI_CHANGE by 0.5 (decay factor). Flag output as `STALE_DATA_T-2`.
- **Age 4–5 days:** Use but set OI_CHANGE = 0 (don't trust stale change signal). Flag `STALE_DATA_T-4`.
- **Age > 5 days:** Reject. Fall to synthetic flat OI. Log CRITICAL warning.

### Dashboard Indicator (Recommended)
Add a data freshness badge to the dashboard:
- GREEN: Live NSE data (< 3 min old)
- YELLOW: Bhavcopy data (T-1 EOD)
- RED: Stale/Synthetic data

---

## 5. REQUIRED PIP PACKAGES

### Immediate (P1-P3 — no new accounts needed):
```txt
# Already in requirements.txt — no changes needed for P1:
requests==2.32.3
pandas==2.2.3

# Add for P3 (nsepythonserver — cloud anti-bot bypass):
nsepythonserver>=2.97     # server edition for codespace/cloud

# Optional upgrade for P2 (bhavcopy parsing helper):
# No new packages needed — pandas + zipfile handles CSV ZIP natively
```

### When Shoonya account is opened (P4):
```txt
ShoonyaApi-py>=1.0.0      # OR: NorenRestApiPy>=1.0.28
```

### When ICICI Breeze account is opened (P5):
```txt
breeze-connect>=1.0.71
```

### For local Greek computation (P4/P5 enhancement):
```txt
scipy>=1.12.0             # already in requirements.txt (used for Spearman ρ)
# scipy's norm.cdf is sufficient for Black-Scholes IV estimation
```

---

## 6. IMPLEMENTATION PRIORITY ORDER

| Phase | Action | Effort | Impact |
|---|---|---|---|
| **IMMEDIATE** | Add `bhavcopy_downloader.py` + 18:30 scheduler job | 2 hours | HIGH — fixes codespace data gap |
| **IMMEDIATE** | Use yesterday's bhavcopy as `prev_oi` when NSE live fails | 1 hour | HIGH — fixes OI change calculation |
| **SHORT-TERM** | Add `nsepythonserver` to requirements, use in cloud env | 30 min | MEDIUM — better NSE live reliability |
| **SHORT-TERM** | Add 30-day bhavcopy retention + IV percentile computation | 3 hours | HIGH — enables real IV percentile factor |
| **MEDIUM-TERM** | Open free Shoonya account → add ShoonyaApi-py fallback | Half day | HIGH — real-time independent source |
| **MEDIUM-TERM** | Open free ICICI Breeze account → 10yr historical data | Half day | VERY HIGH — enables proper backtesting |
| **LONG-TERM** | OpenAlgo self-hosted server | Weekend | MEDIUM — future architecture |

---

## 7. CRITICAL NOTES FOR CODEX VERIFICATION

1. **Bhavcopy UDiFF column names changed in July 2024.** The old format used `INSTRUMENT, SYMBOL, EXPIRY_DT, STRIKE_PR, OPTIONTYPE, OPEN_INT, CHG_IN_OI`. The new UDiFF uses `FinInstrmTp, TckrSymb, XpryDt, OptnTp, StrkPric, OpnIntrst, ChngInOpnIntrst`. Codex should verify by downloading a sample file and inspecting headers before implementing the parser.

2. **jugaad-data UDiFF issue:** GitHub issue #79 confirms jugaad-data does not yet support the new UDiFF format. Do NOT use `bhavcopy_fo_save()` from jugaad-data for dates after July 2024. Use direct download instead.

3. **nsepythonserver anti-bot:** The server edition uses a different request routing strategy. Replace `import nsepython` with `import nsepythonserver as nsepython` in `nse_provider.py` when running in codespace. Add an env var `NSE_CLIENT=server` to switch.

4. **No Dhan broker changes:** The fallback chain is PURELY for market data. All order management, holdings, and account operations remain on Dhan only. Shoonya/Breeze accounts are data-only sources.

5. **IV not in bhavcopy:** Bhavcopy contains settlement price, not IV. To compute IV percentile from bhavcopy, apply BSM formula: `IV = scipy.optimize.brentq(lambda v: bsm_price(S, K, T, r, v) - settle_price, 0.001, 20)`. This is computationally feasible for 50–100 strikes.

---

## 8. SUMMARY SCORECARD

| Source | OI | OI Change | IV | Real-Time | Free | No Account | Cloud Works |
|---|---|---|---|---|---|---|---|
| NSE Public API | ✅ | ❌ (from cache) | ✅ | ✅ | ✅ | ✅ | ⚠️ (anti-bot) |
| NSE Bhavcopy | ✅ | ✅ **DIRECT** | ❌ (compute) | ❌ (EOD) | ✅ | ✅ | ✅ |
| nsepythonserver | ✅ | ❌ (from cache) | ✅ | ✅ | ✅ | ✅ | ✅ |
| jugaad-data | ✅ | ✅ | ❌ | ❌ (EOD) | ✅ | ✅ | ✅ |
| Shoonya API | ✅ | ✅ | ✅ Greeks | ✅ | ✅ | ❌ (free acct) | ✅ |
| Breeze Connect | ✅ | ✅ | ✅ Greeks | ✅ | ✅ | ❌ (free acct) | ✅ |
| yfinance | ❌ | ❌ | ❌ | ⚠️ (15min) | ✅ | ✅ | ✅ |
| OpenAlgo | ✅ | ✅ | ✅ Greeks | ✅ | ✅ | ❌ (self-host) | ⚠️ |

**WINNER for immediate fix (no new accounts):** NSE Bhavcopy CDN archive
**WINNER for long-term (after free account):** Shoonya/Finvasia — real-time, all Greeks, zero cost

---

*Codex: please verify the bhavcopy UDiFF column names by downloading a sample file, confirm jugaad-data UDiFF status, and cross-check the Shoonya API function signature for `get_option_chain()`. Respond in CHANGE_LOG.*
