# Dhan Option Chain Schema Audit

Generated UTC: `2026-06-23T21:26:51.229872Z`
Status: **PASS**

## Files scanned
- `core/data/datasource_manager.py`
- `core/data/dhan_option_chain_parser.py`
- `dashboard/backend/app.py`
- `src/dhan/live_chain_rest.py`

## Files changed
- `core/data/dhan_option_chain_parser.py`
- `core/data/datasource_manager.py`

## Wrong mappings found
- none

## Correct mappings verified
- `oi`
- `previous_oi`
- `top_bid_price`
- `top_ask_price`
- `greeks.delta`
- `change_in_oi`
- `bid_ask_spread`

## Tests
- `tests/test_dhan_option_chain_parser.py`
- `tests/fixtures/dhan_option_chain_sample.json`
- pytest: PASS

## Remaining blockers
- none