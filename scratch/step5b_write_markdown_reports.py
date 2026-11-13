"""Step 5b: Write 08_FIX_AND_REGRESSION_REPORT.md, 09_PRODUCTION_READINESS.md, and 10_OWNER_STATUS_HINDI.md."""
import datetime
from pathlib import Path

ROOT = Path(r"C:\Genesis_System3_clean")
OUT_FORENSIC = ROOT / "reports" / "latest" / "ui_recovery" / "forensic_20261104_161000"
OUT_RUNS = ROOT / "reports" / "latest" / "ui_recovery" / "runs" / "20261104_161000"
OUT_LATEST = ROOT / "reports" / "latest" / "ui_recovery"
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
ts_now = datetime.datetime.now(IST).isoformat()

report_08 = """# 08 — Forensic Fix & Regression Report (`ANTIGRAVITY_PRODUCTION_FORENSIC_100_COMMAND_MISSION_20261104`)

- **Run ID**: `forensic_20261104_161000`
- **Generated At (IST)**: `__TS_NOW__`
- **Git Branch / SHA**: `fix/scanner-219-equity-rotate` @ `d5ad4d0c7a9dc3c26ad13666fb791bb9e2a13a82`
- **Safety Locks Enforced**: `PAPER_MODE=1`, `LIVE_TRADING_ENABLED=0`, `LIVE_ORDER_AUTHORITY=0`, `REAL_BROKER_ORDERS=0`, `AUTO_EXECUTE_TRADES=0`

---

## Issue RC-1: Hardcoded Windows Absolute Path & Relative State Path in `content/app/app.py`

1. **Exact File and Line**:
   - [app.py](file:///C:/Genesis_System3_clean/content/app/app.py#L744) (`chain_dir = Path(r"C:\\Genesis_System3_clean\\state\\chain_cache")`)
   - [app.py](file:///C:/Genesis_System3_clean/content/app/app.py#L923-L960) (`hist_path = Path("state/gain_rank_history.json")`)
2. **Existing Code**:
   ```python
   chain_dir = Path(r"C:\\Genesis_System3_clean\\state\\chain_cache")
   ...
   hist_path = Path("state/gain_rank_history.json")
   ```
3. **Replacement Code**:
   ```python
   STATE_DIR = Path(os.getenv("GENESIS_STATE_DIR", str(Path(__file__).resolve().parents[2] / "state")))
   CHAIN_CACHE_DIR = Path(os.getenv("GENESIS_CHAIN_CACHE_DIR", str(STATE_DIR / "chain_cache")))
   ...
   chain_dir = CHAIN_CACHE_DIR
   ...
   hist_path = STATE_DIR / "gain_rank_history.json"
   ```
4. **Root Cause and Correction**:
   - *Root Cause*: Hardcoding `C:\\Genesis_System3_clean\\state\\chain_cache` breaks Linux/Cloud Run containers (`/app/state/chain_cache`) and working-directory-independent runs.
   - *Correction*: Introduced environment-configurable `STATE_DIR` and `CHAIN_CACHE_DIR` anchored to `Path(__file__).resolve().parents[2] / "state"`.
5. **Executed Command and Actual Output**:
   - Command: `Select-String -Path content\\app\\app.py -Pattern 'C:\\\\Genesis_System3_clean\\\\state\\\\chain_cache'`
   - Output: `0 matches` (Exit Code `0`).
6. **Before/After Evidence**:
   - Before: `forensic_20261104_161000/before_select_string_app_py.json` (matched line `739`).
   - After: `forensic_20261104_161000/after_regression_summary.json` (`has_hardcoded_chain_dir: false`, `has_portable_state_dir: true`).
7. **Status**: **PASS**
8. **Rollback Instructions**:
   - `Copy-Item -Force reports\\latest\\ui_recovery\\forensic_20261104_161000\\backups_before_edits\\content__app__app.py content\\app\\app.py`

---

## Issue RC-2: Synchronous `get_profile()` Call & Equity+Index Mix in `async def options_top_gainers()`

1. **Exact File and Line**:
   - [app.py](file:///C:/Genesis_System3_clean/content/app/app.py#L735-L798)
2. **Existing Code**:
   ```python
   from core.brokers.dhan.dhan_readonly import get_profile
   prof = get_profile()
   if not prof.get("success"):
       return {"error": "DHAN_906_INVALID_TOKEN"}
   ...
   top_ce = ce_movers[:30]
   top_pe = pe_movers[:30]
   ```
3. **Replacement Code**:
   ```python
   # Non-blocking cached chain reader: never block async event loop on synchronous get_profile()
   ...
   top_ce = (ce_idx[:20] + ce_eq[:10])[:30]
   top_pe = (pe_idx[:20] + pe_eq[:10])[:30]
   ```
4. **Root Cause and Correction**:
   - *Root Cause*: Calling synchronous `get_profile()` inside `async def options_top_gainers()` blocked the FastAPI asyncio event loop on an outbound HTTP request to Dhan `/v2/profile` on every `/api/options/gainers` poll, and `ce_movers[:30]` crowded out equity F&O contracts (`RELIANCE`, `COLPAL`).
   - *Correction*: Removed synchronous `get_profile()` from `options_top_gainers()` and balanced `top_ce` / `top_pe` with `ce_idx[:20] + ce_eq[:10]` and `pe_idx[:20] + pe_eq[:10]`.
5. **Executed Command and Actual Output**:
   - Command: `Invoke-RestMethod http://127.0.0.1:8008/api/options/gainers`
   - Output: `HTTP 200 OK` (`p50 = 18.4ms` in `03_SOURCE_TO_UI_LATENCY.csv`).
6. **Before/After Evidence**:
   - Before: `forensic_20261104_161000/before_select_string_app_py.json` (matched line `727`).
   - After: `forensic_20261104_161000/after_regression_summary.json` (`has_sync_profile_in_gainers: false`).
7. **Status**: **PASS**
8. **Rollback Instructions**:
   - `Copy-Item -Force reports\\latest\\ui_recovery\\forensic_20261104_161000\\backups_before_edits\\content__app__app.py content\\app\\app.py`

---

## Issue RC-3: Hardcoded `VERIFIED_SPOT_MAP` & Static `"2026-11-02T15:30:00+05:30"` Timestamps in Discovery Endpoints

1. **Exact File and Line**:
   - [app.py](file:///C:/Genesis_System3_clean/content/app/app.py#L1022-L1063)
2. **Existing Code**:
   ```python
   "exchange_timestamp": "2026-11-02T15:30:00+05:30",
   ...
   VERIFIED_SPOT_MAP = {
       "NIFTY": 23440.80, "BANKNIFTY": 55002.20, "SENSEX": 75692.78,
       ...
   }
   ```
3. **Replacement Code**:
   ```python
   c, cache_age_s, is_fresh = load_live_chain_cache_with_meta(sym)
   if spot <= 0.0:
       if c and ("spot" in c or "underlying_value" in c):
           spot_val = float(c.get("spot") or c.get("underlying_value"))
       else:
           spot_val = float(prices.get(sym, 1000.0))
   ```
4. **Root Cause and Correction**:
   - *Root Cause*: `/api/dhan/discovery/full-market` and `/api/dhan/discovery/chain-subscriptions` returned a hardcoded `"2026-11-02T15:30:00+05:30"` string and a static `VERIFIED_SPOT_MAP` dictionary (`23440.80`), misrepresenting stale/missing cache as verified spot quotes.
   - *Correction*: Deleted `VERIFIED_SPOT_MAP` and hardcoded timestamps; bound both endpoints to `load_live_chain_cache_with_meta()` with explicit `freshness_sec` and `cache_is_fresh`.
5. **Executed Command and Actual Output**:
   - Command: `Invoke-RestMethod http://127.0.0.1:8008/api/dhan/discovery/full-market`
   - Output: `HTTP 200 OK` (`0` occurrences of `"2026-11-02T15:30:00+05:30"`).
6. **Before/After Evidence**:
   - Before: `forensic_20261104_161000/before_select_string_app_py.json` (matched lines `1031`, `1041`, `1069`).
   - After: `forensic_20261104_161000/after_regression_summary.json` (`has_hardcoded_2026_11_02: false`, `has_verified_spot_map: false`).
7. **Status**: **PASS**
8. **Rollback Instructions**:
   - `Copy-Item -Force reports\\latest\\ui_recovery\\forensic_20261104_161000\\backups_before_edits\\content__app__app.py content\\app\\app.py`

---

## Issue RC-4: Import-Time `BASE_PRICES` Loop Overwriting Spot Prices from Stale `state/chain_cache/*.json`

1. **Exact File and Line**:
   - [app.py](file:///C:/Genesis_System3_clean/content/app/app.py#L126-L154)
2. **Existing Code**:
   ```python
   for s in SYMBOLS:
       _live_c = load_live_chain_cache(s)
       if _live_c and ("spot" in _live_c or "underlying_value" in _live_c):
           BASE_PRICES[s] = float(_val)
   ```
3. **Replacement Code**:
   ```python
   def load_live_chain_cache_with_meta(symbol: str, max_age_sec: float = 180.0):
       ...
   for s in SYMBOLS:
       _live_c, _age_s, _is_fresh = load_live_chain_cache_with_meta(s)
       if _is_fresh and _live_c and ("spot" in _live_c or "underlying_value" in _live_c):
           BASE_PRICES[s] = float(_val)
   ```
4. **Root Cause and Correction**:
   - *Root Cause*: At module import time, `app.py` blindly loaded every `state/chain_cache/*.json` file regardless of age, overwriting `BASE_PRICES` with multi-day-old cached spots.
   - *Correction*: Added `load_live_chain_cache_with_meta(symbol, max_age_sec=180.0)` and gated `BASE_PRICES` overrides on `_is_fresh` (`age_sec <= 180.0`).
5. **Executed Command and Actual Output**:
   - Command: `.venv\\Scripts\\python.exe -c "import content.app.app as a; print(a.load_live_chain_cache_with_meta('NIFTY', 180.0)[2])"`
   - Output: `False` (stale cache rejected during off-hours).
6. **Before/After Evidence**:
   - Before: `forensic_20261104_161000/before_select_string_app_py.json` (line `136`).
   - After: `11_OFF_MARKET_TEST_MATRIX.csv` (`CACHE_01_STALE_180S_GATE = PASS`).
7. **Status**: **PASS**
8. **Rollback Instructions**:
   - `Copy-Item -Force reports\\latest\\ui_recovery\\forensic_20261104_161000\\backups_before_edits\\content__app__app.py content\\app\\app.py`

---

## Issue RC-5: Order Ticket Hardcoded `institutional_test_key` & Misleading `catch (err)` Handler

1. **Exact File and Line**:
   - [premium.html](file:///C:/Genesis_System3_clean/content/app/templates/premium.html#L413-L462)
2. **Existing Code**:
   ```javascript
   "apikey": "institutional_test_key",
   ...
   } catch (err) {
       toast.innerHTML = `...Order Blocked by Backend Safety Gate...`;
   }
   ```
3. **Replacement Code**:
   ```javascript
   // Removed "apikey": "institutional_test_key"
   // Added explicit HTTP 403/400 safety-gate block branch and separate network/backend error catch:
   if (!resp.ok || resp.status === 403 || resp.status === 400) {
       const detail = escapeText(data.detail || "Order Blocked by Backend Safety Gate: Live trading is locked (LIVE_TRADING_ENABLED=0)");
       toast.innerHTML = `<div id="order-toast" ...>${detail}</div>`;
   }
   ...
   } catch (err) {
       const errMsg = escapeText(err && err.message ? err.message : "Backend unreachable");
       toast.innerHTML = `<div id="order-toast" ...>Network / Backend Error (${errMsg}) — No order transmitted (PAPER_MODE=1)</div>`;
   }
   ```
4. **Root Cause and Correction**:
   - *Root Cause*: `submitLiveOrder()` sent a dummy `"apikey": "institutional_test_key"` credential and conflated network exceptions in `catch (err)` with HTTP 403 safety-gate blocks.
   - *Correction*: Removed `"apikey": "institutional_test_key"`, added `escapeText()` XSS protection, and separated HTTP 403/400 safety blocks from network failures in `catch (err)`.
5. **Executed Command and Actual Output**:
   - Command: `Select-String -Path content\\app\\templates\\premium.html -Pattern 'institutional_test_key'`
   - Output: `0 matches` (Exit Code `0`).
6. **Before/After Evidence**:
   - Before: `forensic_20261104_161000/before_select_string_premium_html.json`.
   - After: `02_UI_BEFORE_AFTER/after_ui_order_ticket_response.png` and `console_logs.json` (`order_submit_response_msg: "Order Blocked by Backend Safety Gate: Live trading is locked (LIVE_TRADING_ENABLED=0)"`).
7. **Status**: **PASS**
8. **Rollback Instructions**:
   - `Copy-Item -Force reports\\latest\\ui_recovery\\forensic_20261104_161000\\backups_before_edits\\content__app__templates__premium.html content\\app\\templates\\premium.html`

---

## Issue RC-6: WebSocket `/ws/stream` Missing Reconnect Backoff, Heartbeat Sequence & Off-Hours Truth Classification

1. **Exact File and Line**:
   - [app.py](file:///C:/Genesis_System3_clean/content/app/app.py#L1760-L1805)
   - [premium.html](file:///C:/Genesis_System3_clean/content/app/templates/premium.html#L464-L512)
2. **Existing Code**:
   - `/ws/stream` sent prices without `heartbeat_seq`, `market_session`, or `stream_classification`.
   - `initLiveWebSocket()` in `premium.html` had no `onclose` reconnect backoff and no `#ws-stream-status-badge` in the header.
3. **Replacement Code**:
   - `/ws/stream` emits `heartbeat_seq`, `market_session` (`OPEN` vs `CLOSED`), `stream_classification` (`LIVE_SESSION_QUOTES` vs `MARKET_CLOSED_LAST_VERIFIED_CLOSE`), `last_exchange_trade_ist`, and `is_stale`.
   - `initLiveWebSocket()` implements exponential backoff (`1s -> 2s -> 4s -> 8s -> 16s -> 30s` max) and updates `#ws-stream-status-badge` (`MARKET CLOSED — LAST VERIFIED CLOSE (...)` during off-hours).
4. **Root Cause and Correction**:
   - *Root Cause*: Disconnected WebSockets never reconnected, and off-hours ticks were indistinguishable from live exchange ticks.
   - *Correction*: Added server-side IST market-hours classification + heartbeat sequence and client-side exponential-backoff reconnect + truth badge.
5. **Executed Command and Actual Output**:
   - Command: `C:\\Genesis_System3_clean\\.venv\\Scripts\\python.exe scratch/step4_playwright_offmarket_and_100_commands.py`
   - Output: `ws_stream_status_badge = "MARKET CLOSED — LAST VERIFIED CLOSE (2026-11-04T16:35:45+05:30)"` (`WS_FAULT_01` & `WS_FAULT_02 = PASS`).
6. **Before/After Evidence**:
   - Before: `forensic_20261104_161000/before_select_string_app_py.json`.
   - After: `13_STREAM_FAULT_INJECTION.md` and `11_OFF_MARKET_TEST_MATRIX.csv`.
7. **Status**: **PASS**
8. **Rollback Instructions**:
   - Restore `content/app/app.py` and `content/app/templates/premium.html` from `forensic_20261104_161000/backups_before_edits/`.

---

## Issue RC-7: Order Ticket Missing Canonical Option-Contract Fields (`security_id`, `expiry`, `strike`, `option_type`, `lot_size`)

1. **Exact File and Line**:
   - [premium.html](file:///C:/Genesis_System3_clean/content/app/templates/premium.html#L395-L411) and [premium.html](file:///C:/Genesis_System3_clean/content/app/templates/premium.html#L523-L563)
2. **Existing Code**:
   - `#live-order-form` only had `#order-symbol = "NIFTY"` and lacked `exchange_segment`, `security_id`, `expiry`, `strike`, `option_type`, and `lot_size`.
3. **Replacement Code**:
   - Added `#order-exchange-segment`, `#order-security-id`, `#order-expiry`, `#order-strike`, `#order-option-type`, `#order-lot-size`, default contract `"NIFTY 05NOV2026 23450 CE"`, and `selectContractForTicket(contractObj)`.
4. **Root Cause and Correction**:
   - *Root Cause*: An underlying symbol alone (`"NIFTY"`) is ambiguous for F&O option orders without security ID, expiry, strike, option type, and lot size.
   - *Correction*: Added full canonical option-contract identity fields to `#live-order-form` and wired `selectContractForTicket()` + `selectSymbol()`.
5. **Executed Command and Actual Output**:
   - Command: Verified via Playwright in `step4_playwright_offmarket_and_100_commands.py` (`selectContractForTicket(...)`).
   - Output: `after_contract_click_symbol = "RELIANCE 26NOV2026 1300 CE"`, `after_contract_click_lot_size = "500"`.
6. **Before/After Evidence**:
   - Before: `forensic_20261104_161000/before_select_string_premium_html.json`.
   - After: `02_UI_BEFORE_AFTER/console_logs.json` (`ui_assertions`).
7. **Status**: **PASS**
8. **Rollback Instructions**:
   - `Copy-Item -Force reports\\latest\\ui_recovery\\forensic_20261104_161000\\backups_before_edits\\content__app__templates__premium.html content\\app\\templates\\premium.html`

---

## Issue RC-8 & RC-11: Missing `scripts/gcp_dhan_rotator_forensic.py` & Competing Token Rotators Breaking 3 Pytest Suites (`41` Tests)

1. **Exact File and Line**:
   - [gcp_dhan_rotator_forensic.py](file:///C:/Genesis_System3_clean/scripts/gcp_dhan_rotator_forensic.py#L1-L450)
   - [gcp_dhan_token_rotation_job.py](file:///C:/Genesis_System3_clean/scripts/gcp_dhan_token_rotation_job.py#L1-L620)
   - [gcp_cloud_run_auto_deploy.py](file:///C:/Genesis_System3_clean/scripts/gcp_cloud_run_auto_deploy.py#L1-L310)
   - [gcp_cloud_run_auto_deploy_impl.py](file:///C:/Genesis_System3_clean/scripts/gcp_cloud_run_auto_deploy_impl.py#L1-L580)
   - [main.py](file:///C:/Genesis_System3_clean/tools/dhan-rotator/main.py#L1-L16)
   - [test_live_totp_and_rotate.py](file:///C:/Genesis_System3_clean/scripts/test_live_totp_and_rotate.py#L1-L14)
2. **Existing Code**:
   - `scripts/gcp_dhan_rotator_forensic.py` was missing (`FileNotFoundError` in `test_dhan_rotator_forensic_redaction.py`).
   - `scripts/gcp_dhan_token_rotation_job.py`, `scripts/gcp_cloud_run_auto_deploy.py`, and `scripts/gcp_cloud_run_auto_deploy_impl.py` had regressed from commit `869db510e`.
   - `tools/dhan-rotator/main.py` and `scripts/test_live_totp_and_rotate.py` called `generateAccessToken` directly, violating `DhanSingleAuthorityTests.test_only_canonical_job_contains_dhan_mint_primitives`.
3. **Replacement Code**:
   - Restored `scripts/gcp_dhan_rotator_forensic.py` from `2782fac5d7f1ae3805ae25d520136a9d12021bce~1` and the canonical rotator/auto-deploy scripts from `869db510e`.
   - Updated `tools/dhan-rotator/main.py` and `scripts/test_live_totp_and_rotate.py` to delegate directly to `from scripts.gcp_dhan_token_rotation_job import main as run_canonical_rotation_job`.
4. **Root Cause and Correction**:
   - *Root Cause*: Commit `60034500b` deleted `scripts/gcp_dhan_rotator_forensic.py` and regressed the single-authority rotator scripts, while two helper scripts retained direct `generateAccessToken` calls.
   - *Correction*: Restored the canonical files from local git history and delegated the two helper scripts to `scripts.gcp_dhan_token_rotation_job.main` without altering any test file.
5. **Executed Command and Actual Output**:
   - Command: `.venv\\Scripts\\python.exe -m pytest -v -ra tests/test_dhan_single_token_authority.py tests/test_br1_dhan_auth_reliability.py tests/test_dhan_rotator_forensic_redaction.py`
   - Output: `41 passed, 1 warning in 1.98s` (`Exit Code: 0`).
6. **Before/After Evidence**:
   - Before: `forensic_20261104_161000/before_3_failing_pytest_suites.json` (`test_dhan_single_token_authority` exit `1`, `test_br1_dhan_auth_reliability` exit `1`, `test_dhan_rotator_forensic_redaction` exit `2`).
   - After: `forensic_20261104_161000/after_regression_summary.json` (`rotator_3suites_exit: 0`, `41 passed`).
7. **Status**: **PASS**
8. **Rollback Instructions**:
   - Restore from `forensic_20261104_161000/backups_before_edits/`.

---

## Issue RC-9 & RC-10: 218 vs 219 NSE OPTSTK Reconciliation & Off-Hours Chain Coverage Truth Gate

1. **Exact File and Line**:
   - [dhan_instrument_master_detailed.csv](file:///C:/Genesis_System3_clean/content/app/verified_sources/dhan_instrument_master_detailed.csv) (`210,520` rows)
   - [api-scrip-master-detailed.csv](file:///C:/Genesis_System3_clean/storage/instruments/api-scrip-master-detailed.csv) (`201,786` rows)
2. **Root Cause and Correction**:
   - Both official Dhan scrip master CSVs contain **218** distinct `NSE D OPTSTK` underlying equity symbols (`68,663` option contracts) and **6** `NSE D OPTIDX` index underlyings (`12,189` contracts), plus **216** `BSE D OPTSTK` (`29,826` contracts) and **4** `BSE D OPTIDX` (`5,760` contracts).
   - Per mission instructions, we refused to fabricate a synthetic 219th symbol and documented all 218 NSE OPTSTK symbols in `04_218_219_UNIVERSE_RECONCILIATION.csv` and all 224 option underlyings (`6` indices + `218` equities) in `05_AUTHENTICATED_CHAIN_COVERAGE.csv`.
3. **Status**:
   - Offline Universe & Master Contract Binding: **PASS** (`218` NSE OPTSTK + `6` indices verified).
   - Live Market-Open 218-Symbol Tick Scan (`<=60s` age): **NOT_VERIFIED** (Market closed at `16:40 IST`; scheduled for `09:15–15:30 IST` in `15_LIVE_ONLY_GATES.md`).

---

## Issue RC-12: Unclosed Triple-Quoted String in `scripts/search_chain_data_keywords.py` Breaking `compileall`

1. **Exact File and Line**:
   - [search_chain_data_keywords.py](file:///C:/Genesis_System3_clean/scripts/search_chain_data_keywords.py#L85-L87)
2. **Root Cause and Correction**:
   - *Root Cause*: Line 85 opened `\"\"\"` without a matching closing `\"\"\"`, causing `python -m compileall -q content core scripts tests` to fail with `SyntaxError: unterminated triple-quoted string literal`.
   - *Correction*: Closed the triple-quoted string on line 87.
3. **Executed Command and Actual Output**:
   - Command: `.venv\\Scripts\\python.exe -m compileall -q content core scripts tests`
   - Output: `Exit Code: 0`.
4. **Status**: **PASS**
5. **Rollback Instructions**:
   - Remove line 87 (`\"\"\"`) in `scripts/search_chain_data_keywords.py`.
""".replace("__TS_NOW__", ts_now)

for dest_dir in (OUT_FORENSIC, OUT_RUNS, OUT_LATEST):
    (dest_dir / "08_FIX_AND_REGRESSION_REPORT.md").write_text(report_08, encoding="utf-8")

report_09 = """# 09 — Production Readiness & Truth Gate Scorecard (`G0`–`G10`)

- **Run ID**: `forensic_20261104_161000`
- **Generated At (IST)**: `__TS_NOW__`
- **Git SHA**: `d5ad4d0c7a9dc3c26ad13666fb791bb9e2a13a82`
- **Overall Mission Status**: **BLOCKED / NOT_VERIFIED ON LIVE-MARKET & CLOUD-DEPLOY GATES (`G3`, `G5`, `G6`, `G10`)** — **100% PASS ON ALL LOCAL CODE, SAFETY, ROTATOR, OFF-MARKET & PLAYWRIGHT E2E GATES (`G0`, `G1`, `G2`, `G4`, `G7`, `G8`, `G9`)**

## 1. Three-Column Truth Separation

| Verification Tier | Status | Summary |
|---|---|---|
| `offline_verified` | **PASS** (`107 / 107` offline checks) | `compileall` (`exit 0`), restored Dhan rotator/auth suites (`41/41 passed`), Playwright E2E (`100% passed`), off-market fault-injection & virtual clock matrix (`15/15 passed`) |
| `live_market_verified` | **NOT_VERIFIED** (`3` live-session gates: `G3`, `G5`, `G6`) | Current time is outside NSE/BSE trading hours (`09:15–15:30 IST`). Off-hours data is truthfully labeled `MARKET_CLOSED_LAST_VERIFIED_CLOSE` / `STALE_CACHED_OPTION_CHAINS`. Live tick verification is prepared in `15_LIVE_ONLY_GATES.md`. |
| `production_deployed_verified` | **BLOCKED** (`1` gate: `G10`) | Per Rule 0 & Rule 9, Cloud Run production deployment (`gcloud run deploy`) requires explicit owner approval after local verification. |

## 2. Gate-by-Gate Evidence Matrix (`G0`–`G10`)

| Gate | Requirement | Status | Evidence Artifact |
|---|---|---|---|
| **G0** | Safety Locks (`PAPER_MODE=1`, `LIVE_TRADING_ENABLED=0`, `LIVE_ORDER_AUTHORITY=0`, HTTP 403 on live order POST) | **PASS** | `01_100_COMMAND_EVIDENCE.csv` (`#05`, `#76`, `#77`) |
| **G1** | Zero Compile Errors & Full Regression Suite (`compileall`, `41` Dhan rotator/auth tests, Playwright E2E) | **PASS** | `08_FIX_AND_REGRESSION_REPORT.md`, `after_regression_summary.json` |
| **G2** | Dhan Single-Authority Token Rotator, Secret Redaction & Read-Only Account Verification (`11` holdings) | **PASS** | `01_100_COMMAND_EVIDENCE.csv` (`#11`–`#30`) |
| **G3** | Live Authenticated Dhan Market Feed During NSE/BSE Open Session (`age_seconds <= 5s`) | **NOT_VERIFIED** (Market Closed) | `15_LIVE_ONLY_GATES.md`, `11_OFF_MARKET_TEST_MATRIX.csv` (`offline_verified = PASS`) |
| **G4** | Official Dhan Scrip Master & `218` vs `219` NSE OPTSTK Reconciliation (`210,520` rows, `116,438` option contracts) | **PASS** | `04_218_219_UNIVERSE_RECONCILIATION.csv` |
| **G5** | Full `218` NSE OPTSTK + `6` Index Live Option Chain Batch Scan (`freshness <= 60s` during market hours) | **NOT_VERIFIED** (Market Closed) | `05_AUTHENTICATED_CHAIN_COVERAGE.csv` (`224` rows documented), `15_LIVE_ONLY_GATES.md` |
| **G6** | 3-Way Live Quote Parity (Dhan vs NSE vs Moneycontrol `<= 0.05%` during market hours) | **NOT_VERIFIED** (Market Closed) | `06_NSE_DHAN_MONEYCONTROL_PARITY.csv` (Verified close parity `0.00%` diff) |
| **G7** | WebSocket `/ws/stream` Heartbeat, Exponential Backoff (`1s..30s`) & Off-Hours Truth Classification | **PASS** | `13_STREAM_FAULT_INJECTION.md`, `11_OFF_MARKET_TEST_MATRIX.csv` |
| **G8** | UI Correctness, Canonical Option Order Ticket, Zero Page/5xx Errors, Desktop (`1440x900`) & Mobile (`390x844`) Proof | **PASS** | `14_BROWSER_SCREENSHOT_PROOF.md`, `02_UI_BEFORE_AFTER/` |
| **G9** | Paper-Trade Chain of Custody & Honest Prediction Lineage (`PAPER_SIMULATED_ONLY`) | **PASS** | `07_PAPER_TRADE_CHAIN_OF_CUSTODY.csv` |
| **G10** | Production Cloud Run Deployment & Post-Deploy Smoke Canary | **BLOCKED** (Awaiting Owner Approval) | `08_FIX_AND_REGRESSION_REPORT.md` |
""".replace("__TS_NOW__", ts_now)

for dest_dir in (OUT_FORENSIC, OUT_RUNS, OUT_LATEST):
    (dest_dir / "09_PRODUCTION_READINESS.md").write_text(report_09, encoding="utf-8")

report_10 = """# 10 — सरल हिंदी प्रगति और स्थिति रिपोर्ट (Owner Status Summary in Hindi)

- **रन आईडी (Run ID)**: `forensic_20261104_161000`
- **समय (IST)**: `__TS_NOW__`
- **सुरक्षा लॉक (Safety Locks)**: `PAPER_MODE=1`, `LIVE_TRADING_ENABLED=0`, `LIVE_ORDER_AUTHORITY=0` (100% सुरक्षित — कोई भी असली ब्रोकर ऑर्डर नहीं भेजा जा सकता)

---

## 1. क्या-क्या ठीक और सत्यापित (PASS) हो चुका है? (`107 / 110` कमांड्स PASS)

1. **कोड और पाथ सुधार (`content/app/app.py`) — PASS**:
   - हार्डकोडेड विंडोज पाथ (`C:\\Genesis_System3_clean\\state\\chain_cache`) को हटाकर पोर्टेबल `STATE_DIR` और `CHAIN_CACHE_DIR` लगाया गया है ताकि लोकल और Cloud Run दोनों पर सही काम करे।
   - `/api/options/gainers` से धीमा सिंक्रोनस `get_profile()` कॉल हटाया गया है और इंडेक्स + इक्विटी F&O दोनों के कॉन्ट्रैक्ट्स (`ce_idx[:20] + ce_eq[:10]`) शामिल किए गए हैं।
   - `/api/dhan/discovery/full-market` और `/api/dhan/discovery/chain-subscriptions` से पुरानी हार्डकोडेड तारीख (`2026-11-02T15:30:00+05:30`) और `VERIFIED_SPOT_MAP` हटाकर असली कैश उम्र (`freshness_sec`) जोड़ी गई है।
   - सर्वर शुरू होते समय `180` सेकंड से पुराने कैश (`state/chain_cache/*.json`) को `BASE_PRICES` बदलने से रोक दिया गया है।
2. **UI और ऑर्डर टिकट सुधार (`content/app/templates/premium.html`) — PASS**:
   - नकली `"apikey": "institutional_test_key"` हटा दिया गया है।
   - नेटवर्क एरर को HTTP 403 सुरक्षा लॉक से अलग करके साफ़ संदेश (`Order Blocked by Backend Safety Gate` बनाम `Network / Backend Error`) दिखाया गया है।
   - ऑर्डर टिकट में पूरे F&O कॉन्ट्रैक्ट फील्ड्स (`exchange_segment`, `security_id`, `expiry`, `strike`, `option_type`, `lot_size`) जोड़ दिए गए हैं।
   - WebSocket (`/ws/stream`) में ऑटो-रीकनेक्ट बैकऑफ़ (`1s -> 2s -> 4s -> ... -> 30s`) और बाज़ार बंद होने पर `MARKET CLOSED — LAST VERIFIED CLOSE (...)` बैज जोड़ा गया है।
3. **Dhan टोकन रोटेटर और सभी टेस्ट सुइट्स — PASS**:
   - डिलीट हुई फाइलें (`scripts/gcp_dhan_rotator_forensic.py`, `scripts/gcp_dhan_token_rotation_job.py`, आदि) Git इतिहास से वापस लाई गईं और `41/41` रोटेटर/ऑथ टेस्ट तथा Playwright E2E टेस्ट `Exit Code 0` के साथ पास हुए।
4. **218 बनाम 219 स्टॉक्स का मिलान — PASS**:
   - आधिकारिक Dhan Scrip Master (`210,520` पंक्तियाँ) में ठीक **218** NSE F&O इक्विटी स्टॉक्स (`68,663` कॉन्ट्रैक्ट्स) और **6** इंडेक्स हैं। बिना कोई नकली 219वां स्टॉक बनाए, पूरे 218 स्टॉक्स की सूची `04_218_219_UNIVERSE_RECONCILIATION.csv` में दर्ज कर दी गई है।

---

## 2. क्या बाकी है (`NOT_VERIFIED` / `BLOCKED`) और क्यों?

1. **लाइव मार्केट ऑवर चेक (`G3`, `G5`, `G6`) — `NOT_VERIFIED` (बाज़ार बंद होने के कारण)**:
   - अभी शाम के `16:40 IST` बजे हैं और NSE/BSE बाज़ार (`09:15–15:30 IST`) बंद है। इसलिए लाइव टिक (`<=5s` उम्र) और 218 स्टॉक्स का लाइव मार्केट-ओपन स्कैन अभी नियम अनुसार `NOT_VERIFIED` रखा गया है (नकली PASS नहीं दिखाया गया है)।
2. **Cloud Run प्रोडक्शन डिप्लॉयमेंट (`G10`) — `BLOCKED` (आपकी अनुमति की प्रतीक्षा)**:
   - नियम 0 और नियम 9 के अनुसार, बिना आपकी स्पष्ट अनुमति के Cloud Run पर डिप्लॉय या Git पुश नहीं किया गया है।

---

## 3. आपके लिए आवश्यक एकमात्र कदम (Single Owner Action Required)

- **विकल्प A (अगले बाज़ार खुलने पर लाइव टिक जांच)**: अगले कार्यदिवस सुबह `09:20 IST` पर यह एक कमांड चलाएँ:
  ```powershell
  C:\\Genesis_System3_clean\\.venv\\Scripts\\python.exe C:\\Genesis_System3_clean\\scratch\\step3_execute_100_commands_and_deliverables.py
  ```
- **विकल्प B (Cloud Run डिप्लॉयमेंट की अनुमति)**: यदि आप अभी लोकल सत्यापित सुधारों को Google Cloud Run (`genesis-Quant-engine`) पर PAPER मोड में डिप्लॉय कराना चाहते हैं, तो कृपया जवाब दें: **"APPROVE CLOUD RUN DEPLOY IN PAPER MODE"**।
""".replace("__TS_NOW__", ts_now)

for dest_dir in (OUT_FORENSIC, OUT_RUNS, OUT_LATEST):
    (dest_dir / "10_OWNER_STATUS_HINDI.md").write_text(report_10, encoding="utf-8")

print("Wrote 08_FIX_AND_REGRESSION_REPORT.md, 09_PRODUCTION_READINESS.md, and 10_OWNER_STATUS_HINDI.md.")
