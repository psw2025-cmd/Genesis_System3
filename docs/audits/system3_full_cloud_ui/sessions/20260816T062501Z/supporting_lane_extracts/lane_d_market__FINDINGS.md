# Lane D — Dhan market data forensic

**Worktree:** `C:\System3\Genesis_System3_audit_main_c763ecf`  
**SHA:** `c763ecf048478842688373cf674eb56a7dc04aa9`  
**Mode:** READ-ONLY code forensic (no functional changes)  
**Related:** GitHub Issue #188 — broker-data/UI universe parity

---

## 1. Executive verdict

Market data is **Dhan-centric REST + in-process paced cache**, not a full broker WebSocket feed. Live option-chain acquisition is serialized (~3.4s gap) and owned by `index_chain_micro_loop` for a **hardcoded index subset**. Full OPTSTK discovery exists from `security_id_list.csv`, but paced streaming / Market Top / signal engine do **not** cover the full master. India VIX is on the index LTP board only (no option chain). Dashboard `/ws/stream` fans out **cache**, not DhanHQ marketfeed WS.

---

## 2. Call-site map (authoritative paths)

| Concern | Primary path(s) | Role |
|--------|-----------------|------|
| Option chain fetch | `core/data/datasource_manager.py` → `fetch_option_chain` / `get_option_chain` | Sole paced Dhan OC owner for API/UI (process-wide lock + min gap) |
| Chain API / UI | `dashboard/backend/app.py` `GET /api/chain/{underlying}`, `/api/batch/chains` | Prefer `_PUSHED_CHAIN_CACHE` → TTL → last-resort live fetch |
| Discovery / expiries | `dashboard/backend/routers/chain.py` | `/api/underlyings`, `/api/expiries/{u}`, `/api/chain-expiry/{u}` from security master |
| Adapter | `dashboard/backend/chain_adapter.py` (via DSM) | API-shaped chain payloads |
| Index / VIX LTP | `core/brokers/dhan/market_ltp.py` | REST `marketfeed/ltp|ohlc|quote` + SDK fallbacks |
| Live board | `dashboard/backend/app.py` market live board builder | `build_index_board` + `paced_chain_cache` spot fallback |
| Equity FO universe | `core/brokers/dhan/equity_fo_universe.py` | OPTSTK underlyings from `security_id_list.csv` |
| Instruments master | `core/data/instruments_cache.py`, `instruments_master.py`, `core/brokers/dhan/instruments.py` | JSON/CSV master load + option/index lookup |
| Equity scanner | `dashboard/backend/equity_option_scanner.py` | Priority/momentum subset + `state/chain_cache/{SYM}.json` |
| Dashboard WS | `dashboard/backend/app.py` `/ws/stream` | Cache fan-out only; **never** calls live Dhan OC |
| DhanHQ WS (disabled) | `src/dhan/live_chain_ws.py` | Instantiates → `RuntimeError` |
| Preflight / token | `core/brokers/dhan/preflight.py`, `token_manager.py`, `cloud_token_provider.py` | Auth before broker calls (not market payload) |

Legacy / secondary callers (REST runners, proofs, soak): `scripts/smart_live_chain_runner.py`, `scripts/run_live_chain.py`, `src/dhan/live_chain_rest.py`, `scripts/websocket_tick_health_proof.py` — many still mention WS but production dashboard path is paced REST + cache.

---

## 3. Option universe / security master

### SSOT files

1. **Runtime preferred:** `storage/instruments/OpenAPIScripMaster.json` (from sync)
2. **CDN sync CSV:** detailed Dhan master via `scripts/sync_dhan_instruments_master.py` (documented 08:35 IST)
3. **Bundled fallback:** repo-root `security_id_list.csv`

Load order is implemented in `core/data/instruments_cache.py`.

### Universe builders

- **Equity F&O (OPTSTK):** `load_equity_fo_universe()` reads `security_id_list.csv`, returns full underlying list + `PRIORITY_EQUITY_FO` / `HIGH_MOMENTUM_EQUITY_FO` scan subsets.
- **Index F&O set:** `INDEX_FO_SYMBOLS = {NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX, BANKEX}`.
- **UI discovery:** `build_underlyings_payload()` merges indices + all equity OPTSTK → `source: dhan_security_master` (or `missing_security_master`).

### Hardcoded security IDs (not full master)

`DataSourceManager._DHAN_SECURITY_IDS` and `market_ltp.INDEX_SECURITY_IDS`:

| Symbol | ID | Notes |
|--------|----|-------|
| NIFTY | 13 | Index OC + LTP |
| BANKNIFTY | 25 | |
| INDIAVIX | 26 | **LTP board only** (not in DSM OC map) |
| FINNIFTY | 27 | |
| MIDCPNIFTY | 442 | |
| SENSEX | 51 | Segment forced `IDX_I` |

Equity OC security IDs are resolved dynamically from master when symbol is OPTSTK.

---

## 4. Paced chain cache (`paced_chain_cache`)

### In-memory (process-local)

| Structure | Location | Durability |
|-----------|----------|------------|
| `_PUSHED_CHAIN_CACHE` | `dashboard/backend/app.py` | **EPHEMERAL** — lost on Cloud Run instance recycle |
| `_cache_get` / `_cache_set` TTL keys `chain_{SYM}`, `batch_chains_v1`, scanner keys | same | **EPHEMERAL** |
| Source label `"paced_chain_cache"` | market live board fallback when marketfeed LTP missing | Uses pushed/TTL chain spots |

### Owner loop

`index_chain_micro_loop()`:

- Symbols: `_INDEX_STREAM_SYMBOLS = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX")`
- Round-robin; sleep **3.5s** open / **20s** closed
- Writes `_PUSHED_CHAIN_CACHE[sym]` + `_cache_set(f"chain_{sym}", …)`
- Comment: DSM enforces ~3.4s OC gap; UI/WS must not fan-out live OC

`market_top_micro_loop()` ranks from paced snapshots only (`stream_mode: index_chain_cache` / `ultra_micro_cache`).

### On-disk snapshots (session / host durable, not multi-instance SSOT)

| Path | Use | Durability class |
|------|-----|------------------|
| `state/chain_cache/{SYM}.json` | Last-session / closed-market serve; equity scanner | **SESSION_DURABLE** (local FS; Cloud Run ephemeral disk unless mounted) |
| `state/option_chain_cache.json` | ML/router readers | **SESSION_DURABLE** |
| `storage/live/option_chain_cache.json` | Alternate live path | **SESSION_DURABLE** |
| Market Top state file (app `_MARKET_TOP_STATE_FILE`) | Background ranked table | **SESSION_DURABLE** |

**Classification summary for paced chain:** production UI truth during market hours is **EPHEMERAL in-memory**, with **SESSION_DURABLE** JSON fallbacks — **not PRODUCTION_DURABLE** (no GCS/Postgres lineage of every OC snapshot).

---

## 5. 429 / rate-limit handling

### Dhan option-chain (provider side)

- Process-wide `_DHAN_OC_LOCK` + `_DHAN_OC_MIN_GAP_S` (default **3.4**, env `DHAN_OC_MIN_GAP_S`).
- Explicit goal: prevent Market Top + WS + UI stampede → empty/`NO_DHAN_DATA`.
- Stale serve: `_chain_from_push_cache` returns last-good within stale windows with message about paced refresh (avoids empty rate-limit responses).
- **No dedicated HTTP-429 parser** in DSM for Dhan OC responses; pacing is preventive.

### Dashboard HTTP 429 (client → API)

`compat_rate_limit_and_timing` middleware:

- GET/HEAD/OPTIONS exempt from bucket
- Broker/batch/health paths exempt when authenticated
- Else 180/min anonymous or 1200/min authed → HTTP **429** + `Retry-After: 60`
- Intent: never 429 broker reads into false DISCONNECTED/TOKEN ERROR

Cloud/deploy probes also retry 429/5xx (`tools/cloud_runtime_check.py`, mutation-policy tests). That is **infra**, not Dhan marketfeed backoff.

---

## 6. Index coverage

| Symbol | Paced OC stream | `/api/underlyings` | LTP board (`DEFAULT_INDEX_BOARD`) | DSM hardcoded OC |
|--------|-----------------|--------------------|-----------------------------------|------------------|
| NIFTY | Yes | Yes | Yes | Yes |
| BANKNIFTY | Yes | Yes | Yes | Yes |
| FINNIFTY | Yes | Yes | Yes | Yes |
| MIDCPNIFTY | Yes | Yes | Yes | Yes |
| SENSEX | Yes | Yes | Via board list (not in DEFAULT_INDEX_BOARD tuple; included in app live-board loop) | Yes |
| BANKEX | No stream | In INDEX_FO_SYMBOLS | No dedicated LTP ID in `INDEX_SECURITY_IDS` | No |
| INDIAVIX | No OC | N/A | Yes (ID 26) | No |

`DEFAULT_UNDERLYINGS` in app still defaults to **four** indices (`NIFTY…MIDCPNIFTY`) until startup bridge overwrites from master — see Issue #188 gaps.

---

## 7. India VIX

- Mapped in `market_ltp.INDEX_SECURITY_IDS["INDIAVIX"] = "26"`, label `"India VIX"`.
- Included in `DEFAULT_INDEX_BOARD` and app live-board symbol loop.
- Fallback source can be `paced_chain_cache` **only if** a chain row exists (normally VIX has no OC push) — so VIX depends primarily on **dhan_marketfeed**.
- Tests: `tests/test_dhan_market_ltp.py` assert VIX ID and paced fallback for indices.

---

## 8. WebSocket use

| Layer | Status |
|-------|--------|
| DhanHQ live marketfeed WS (`src/dhan/live_chain_ws.py`) | **DISABLED** — `RuntimeError` on construct |
| Dashboard `/ws/stream` | **ACTIVE** — UI push of state, Market Top, chain spots/NIFTY chain from **cache**, heartbeats |
| Proof gate `WEBSOCKET_TICK_HEALTH_PROVEN` | REST poll ≤10s allowed for analyzer; true Dhan WS required for live execution claims |
| Advance platform audit | Notes official DhanHQ WS exists; System3 may not show live ticks when market closed |

**Verdict:** “WS LIVE” in UI means **dashboard fan-out**, not broker tick stream. Aligns with Issue #188 architecture lock #6 (reconnect/resubscribe) — **not implemented** for DhanHQ WS.

---

## 9. Issue #188 — universe parity gaps (from code)

Issue title: *P0: Broker-data/UI parity — indices, equities, full option chains, live charts*.

### Gaps evidenced at `c763ecf`

1. **Hardcoded paced stream** — only 5 index symbols; full OPTSTK (~140) not paced.
2. **Hardcoded DSM index IDs** — equity IDs from master, but index board/OC IDs are static maps.
3. **Scan priority subsets** — `PRIORITY_EQUITY_FO` + `HIGH_MOMENTUM_EQUITY_FO` intentionally smaller than full master (`equity_fo_universe.py` comments).
4. **Signal engine index filter** — `scripts/run_signal_engine_from_bhavcopy.py` `INDEX_SYMBOLS` = 4 indices (no SENSEX/equity).
5. **Trainer underlyings** — `dhan_blended_model_trainer_v2.py` hardcodes 5 indices.
6. **Tools/gates** — `SYSTEM3_REQUIRED_UNDERLYINGS` default `NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY`; many audits only probe `/api/chain/NIFTY` (+ few peers).
7. **DhanHQ WS + full chart continuity** — disabled / not proven (Issue #188 categories).
8. **Discovery vs streaming asymmetry** — `/api/underlyings` can list full master while Market Top / micro-loop only score paced index chains (`include_equity: False` on cache-built Market Top).

Partial mitigation: `routers/chain.py` + tests `test_optionchain_ui_universe_contract.py` assert underlyings derived from broker security master for **discovery** — but discovery ≠ full live chain coverage.

---

## 10. Storage durability classification (market data)

| Artifact | Class | Notes |
|----------|-------|-------|
| `_PUSHED_CHAIN_CACHE`, API TTL caches | **EPHEMERAL** | Per process |
| `state/chain_cache/*.json` | **SESSION_DURABLE** | Local; Cloud Run disk not durable across revisions unless volume |
| `storage/live/option_chain_cache.json` | **SESSION_DURABLE** | |
| `security_id_list.csv` / synced master | **REPO_OR_SYNC_DURABLE** | Bundled + daily sync; not versioned Parquet lake |
| `storage/instruments/OpenAPIScripMaster.json` | **SESSION_DURABLE** (runtime) | Rebuildable from sync |
| Dhan live quotes | **EPHEMERAL_REMOTE** | No local immutable partition store |
| Blueprint Parquet nightly ingest | **MISSING** vs blueprint |

---

## 11. Success criteria for closing Lane D vs Issue #188

- Proof matrix: expected vs API vs UI counts for NSE/BSE cash, indices, OPTIDX, OPTSTK, multi-expiry chains.
- Paced or batched OC coverage for full supported derivative universe (or explicit coverage-defect labels).
- Source + freshness on every UI payload; no unlabeled stale/demo.
- Dhan rate-limit backoff + circuit breaker proven under load.
- DhanHQ WS reconnect proof **or** permanent labeled REST-only contract.
