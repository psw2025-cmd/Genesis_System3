# Inspector audit response — money gates vs engineering (proof)

**Cloud revision at audit:** `genesis-system3-web-00062-6xz`  
**API snapshot:** `reports/latest/full_dashboard_api_audit/cloud_api_snapshot.json`  
**Live trading:** remains **OFF** (`LIVE_TRADING_ENABLED=0`). Do not enable.

## Two different verdicts (do not conflate)

| Bucket | Meaning | Status |
|---|---|---|
| **A. Live-money gates** | Correct safety blockers before real orders | **BLOCKED by design** — not an excuse for broken UI |
| **B. Engineering failures** | Tabs/APIs that must work in paper/analyzer today | **Fixed in this change set** (ship + re-prove) |

### A — Live money (correctly blocked — with API proof)

From `/api/live-trading/gate` on Cloud:

- `gate_open=false` / `LIVE_TRADING_BLOCKED`
- Fail: `human_approved`, `validation_days` (1 need ≥10), `ml_accuracy_rho` (0.200 need ≥0.70)
- Pass: `env_live_disabled`, `kill_switch_off`, `max_loss_configured`

These numbers are **real gate math**, not a substitute for fixing broken tabs. More paper days alone do **not** fix Genesis Brain hang, empty Alerts, MC 403 UX, BN chain warm, or corrupted Performance evidence.

### B — Engineering findings → fixes (this ship)

| Finding | Root cause | Fix |
|---|---|---|
| Genesis Brain stuck loading | `Promise.all` + no timeouts | `allSettled` + 10s timeout per call |
| Truth Control all BLOCKED while Broker OK | Stampede `/api/chain/*`; closed snapshots rejected via `stale!==true` | Batch APIs; accept `MARKET_CLOSED_DHAN_SNAPSHOT` |
| TopBar DEGRADED flicker | Sticky `NETWORK_ERROR` after recover | `markSuccess` clears `apiStatus` |
| Signals MC 403 | Moneycontrol blocks scrape; board defaulted to MC | Default board **Dhan**; MC labeled reference; alert on fail |
| Alerts empty | File-only alerts; `/api/agent/issues` stub `[]` | Synthesize operational alerts + real issues |
| Performance `candidates_sample` = .py paths | Orchestrator file-scan dumped to UI | Sanitize `/api/backtest/results` operator payload |
| BN/MID TopBar `--` after hours | Micro-loop 4s closed OC timeout → cold cache | Micro-loop closed fetch timeout **22s** |
| Broker shows real holdings | Read-only Dhan funds/holdings (expected) | Keep live orders OFF; Broker tab is proof of read path |

### Proven before ship (Cloud API)

- Broker `connected=true`, funds OK (~₹13,917 available), holdings path live
- Batch chains: NIFTY + FINNIFTY snapshots OK; BANKNIFTY + MIDCPNIFTY `CHAIN_CACHE_WARMING` (target of longer warm)
- Moneycontrol: `SCRAPE_FAILED` HTTP 403 (reference only)
- Alerts: `count=0` **before** synth fix
- Live gate: blocked as above

### Success criteria after deploy

1. Genesis Brain shows content or partial errors — **never** infinite “loading…”
2. Alerts tab shows MC scrape / chain-cold / live-gate info (not blank)
3. Signals default Dhan board with rows when Dhan market-top available
4. Performance backtest JSON has **no** `.py`/docs paths in operator summary
5. Truth Control broker/funds/holdings layers PASS when broker connected
6. Live gate still `LIVE_TRADING_BLOCKED` — **no** live enablement
