# Render DhanHQ SDK Fix Proof

## Decision
Keep dhanhq==2.2.0.

## Root cause
Two data modules used old SDK construction:

- dhanhq(client_id, token)

DhanHQ 2.2.0 runtime expects:

- DhanContext(client_id, access_token)
- dhanhq(ctx)

## Files patched
- core/data/datasource_manager.py
- core/data/history_fetcher.py

## Validation proof
Docker Render-like runtime passed:

- Python 3.11.15
- dhanhq_version: 2.2.0
- dhanhq_2_2_imports: OK
- dhan_client_creation: OK dhanhq
- pandas_import: OK 2.3.3
- patched_runtime_module_imports: OK

## Safety
No live trading settings changed.
No credentials changed.
No .env files changed.
