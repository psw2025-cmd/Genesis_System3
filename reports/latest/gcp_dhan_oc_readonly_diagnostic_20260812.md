# GCP Dhan Option-Chain Read-Only Diagnostic — 2026-08-12

## Scope

Read-only verification of the deployed `genesis-system3-web` Cloud Run service. No deployment, secret rotation, order placement, live-trading enablement, or production mutation was performed by this diagnostic branch.

Deployed application source under test: `575d75b47a51173bcc5e23d0b10e3aa7f52a7b84` (Cloud Run run-75 deployment source). The repository later received documentation-only commit `f5a85ba505bf63c2b7aad50804fa43005811c33c`; the diagnostic branch remains isolated from `main`.

## UI/deployment baseline

Run `31584906616` (run 75) previously proved the deployed source/revision identity and completed the public PAPER dashboard proof with 22 tabs at desktop and mobile sizes (44 screenshots total). LIVE trading remained disabled.

## Current broker/state proof

Correct-order probe from diagnostic run `31589272386`, repeated by run `31589499358`:

- `/api/broker/status`: `connected=true`
- token source: `GCP_SECRET_MANAGER_DYNAMIC`
- `live_trading_enabled=false`
- `order_placement_allowed=false`
- broker latency observed: 34–38 ms
- `/api/state` fetched after broker refresh: `broker_connected=true`
- `/api/state` mode: `PAPER`

Conclusion: run-75's earlier `/api/state=false` versus `/api/broker/status=true` result was an endpoint-order/staleness artifact, not a reproduced persistent broker-state contradiction.

## Required index-chain proof

Read-only probes after market close returned verified Dhan snapshots for all required indices:

| Symbol | Status | Contracts | Positive spot | Observed latency |
|---|---|---:|---|---:|
| NIFTY | `MARKET_CLOSED_DHAN_SNAPSHOT` | 160 | yes | 782–810 ms |
| BANKNIFTY | `MARKET_CLOSED_DHAN_SNAPSHOT` | 160 | yes | 791–1108 ms |
| FINNIFTY | `MARKET_CLOSED_DHAN_SNAPSHOT` | 160 | yes | 1080–1436 ms |
| MIDCPNIFTY | `MARKET_CLOSED_DHAN_SNAPSHOT` | 160 | yes | 780–1101 ms |

Conclusion: the four required chain endpoints are not in a permanent empty/outage state. The earlier run-75 `dhan_only_no_rows` state was not reproduced after market close.

## Scanner reproducibility

The same endpoint produced contradictory latency outcomes under repeated read-only probes:

1. Diagnostic run `31589272386`: `/api/scanner/top_contract_gainers` returned HTTP 200 in **799 ms**, with `status=eod_snapshot`.
2. Diagnostic run `31589499358`: the same endpoint returned **0 bytes and timed out after 35.002 s** (`curl rc=28`; measured 35.013 s).
3. Immediately before the timeout in run `31589499358`, all four required chain endpoints completed in 0.782–1.436 s with 160 contracts and positive spot.
4. An exact timestamp-filtered Cloud Logging query from the probe start found zero new whitelisted `[DSM]` option-chain fetch/error messages during the timeout window.

Conclusion: scanner latency is intermittent and is not explained by a persistent Dhan-chain outage. The evidence is consistent with an internal wait/serialization/cache-refresh path and requires source-level remediation plus a market-open recheck before readiness claims.

## Source findings relevant to next patch

- `dashboard/backend/contract_gain_scanner.py` fetches the four index segments through a `ThreadPoolExecutor`.
- `core/data/datasource_manager.py` still has a process-global Dhan option-chain lock and process-global minimum gap (`_DHAN_OC_MIN_GAP_S = 3.4`).
- `dashboard/backend/app.py` also has a single-worker / single-lock Dhan chain helper for direct chain API traffic.
- Current Dhan v2 Option Chain documentation describes the restriction as one **unique request** every 3 seconds and permits different underlying/expiry requests concurrently. The current process-global interpretation is therefore stricter than the documented API rule.
- `scripts/gcp_runtime_evidence.py` currently treats `spot is not None` as `spot_available`; this can count `spot: 0` as available. Future evidence should require a strictly positive spot.
- `scripts/gcp_runtime_evidence.py` currently probes `/api/state` before `/api/broker/status`; future evidence should refresh broker truth first or re-fetch state after the broker probe.

## Safety/readiness verdict

- UI deployment proof: **PASS**
- Public PAPER/read-only posture: **PASS**
- LIVE trading: **OFF / locked**
- Broker read-only connectivity: **PASS**
- Four required market-closed Dhan snapshots: **PASS**
- Top-contract-gainers scanner reliability: **FAIL — intermittent 35 s timeout reproduced**
- Market-open Dhan option-chain reliability: **NOT RE-VERIFIED in this post-close diagnostic**
- Trade-ready / production-grade claim: **NOT ALLOWED**

## Next safe action

Implement and test a targeted scanner/data-source concurrency fix on a non-deploying branch, preserving same-key Dhan throttling while removing unnecessary cross-underlying serialization; add timeout/concurrency regression tests and evidence-order/positive-spot checks. Re-run during market hours before any merge/deployment decision.
