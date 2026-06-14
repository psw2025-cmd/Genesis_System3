# fresh_data_automation_proof

Generated UTC: 2026-06-14T14:02:21.244232+00:00

- Status: `PASS_WITH_WARNINGS`
- Pass: `True`
- Auto repair allowed: `True`

## Blockers

- None

## Warnings

- `binance_crypto_data_candidates_not_proven`
- `external_yahoo_fallback_proof_missing`
- `dhan_broker_secrets_not_available_to_ci_data_live_probe_skipped`

## Next action

Run broker data proof only in secure runtime with Angel/Binance secrets; fallback data must remain labelled as fallback, not broker-live proof.
