# Production UI market-data proof policy

For authoritative GCP production, backend/API/CI success is diagnostic evidence only. Market-data completeness is PASS only when the actual serving Cloud Run UI visibly proves the expected broker-backed universe, selectable underlyings/expiries, complete option-chain rows, source/freshness truth, and safe degraded behavior.

The post-deploy `GCP Market Data UI Parity Proof` workflow is a hard evidence gate for the option-chain surface. Issue #188 remains open until its broader NSE/BSE/equity/index/chart checklist and 60 continuous market-session minutes are also UI-proven.

Safety is invariant: PAPER/analyzer only; LIVE and automatic order execution remain OFF.
