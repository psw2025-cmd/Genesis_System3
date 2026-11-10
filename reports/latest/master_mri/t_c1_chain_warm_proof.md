# T-C1 chain warm implementation proof

captured_at_utc: 2026-08-20T03:54:10Z
branch: fix/chain-warm-backend
base_sha: 680944481ba71834fe59dfab5e937fd43afa6609
status: IMPLEMENTED_PENDING_LIVE_SMOKE

## Fix
- Cold-start burst: `_warm_required_index_chains_cold_start()` warms NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY with DSM 3.5s gap only.
- `batch_chains()` no longer caches payloads while any required symbol is CHAIN_CACHE_WARMING or empty.

## Tests
`python -m pytest tests/evals/test_eval_chain_warm_batch_readiness.py tests/test_br2_runtime_qc_observer_contract.py -q`
Result: 18 passed

## Deferred
Options Intel PCR field mismatch (`pcr` vs `pcr_oi`/`pcr_vol`) is NOT in this change.
