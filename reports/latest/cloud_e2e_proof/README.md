# Cloud E2E Proof

- Base: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
- Expected epoch: `20260803_e2e_full_cloud_40`
- Observed epoch: `20260803_e2e_full_cloud_40`
- Overall: **PASS** (10/10)
- Live trading: OFF

## Checks

- `provenance_epoch`: **PASS** — `{"expected": "20260803_e2e_full_cloud_40", "got": "20260803_e2e_full_cloud_40", "http": 200}`
- `provenance_badges`: **PASS** — `{"schema": 1, "sidebar_sha256": "5e2aafa9c916e29125690ab09c5bbe68cbc1c7115cfeb220d9c689b251806dd3", "sim_live_required": true, "live_trading_enabled": false, "cloud_build_badge": true, "session_snapshot_ui": true, "build`
- `ui_html_assets`: **PASS** — `{"http": 200, "has_js": true, "snippet": "<!doctype html>\n<html lang=\"en\" class=\"dark\">\n<head>\n  <meta charset=\"UTF-8\" />\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n  <title`
- `health_ok`: **PASS** — `{"http": 200, "broker": "connected", "market": "closed", "live_allowed": false}`
- `chain_NIFTY`: **PASS** — `{"http": 200, "spot": 24774.3, "contracts": 160, "status": "MARKET_CLOSED_DHAN_SNAPSHOT", "source_priority": "dhan_last_verified_snapshot", "age_s": 66.9}`
- `chain_BANKNIFTY`: **PASS** — `{"http": 200, "spot": 58247.95, "contracts": 160, "status": "MARKET_CLOSED_DHAN_SNAPSHOT", "source_priority": "dhan_last_verified_snapshot", "age_s": 47.1}`
- `chain_FINNIFTY`: **PASS** — `{"http": 200, "spot": 26984.45, "contracts": 160, "status": "MARKET_CLOSED_DHAN_SNAPSHOT", "source_priority": "dhan_last_verified_snapshot", "age_s": 27.3}`
- `chain_MIDCPNIFTY`: **PASS** — `{"http": 200, "spot": 14898.15, "contracts": 160, "status": "MARKET_CLOSED_DHAN_SNAPSHOT", "source_priority": "dhan_last_verified_snapshot", "age_s": 7.4}`
- `market_top`: **PASS** — `{"http": 200, "rows": 25, "status": "ok", "stream_mode": "ultra_micro", "sample": ["DIVISLAB CE 3383.871", "DIVISLAB CE 3281.8182", "LTM CE 745.2229"]}`
- `auth_status`: **PASS** — `{"required": true, "configured": true, "authenticated": true, "mode": "session_cookie_or_header"}`

## User visual confirmation

1. Hard refresh: `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?v=20260803_e2e_full_cloud_40`
2. TopBar must show green **CLOUD BUILD** badge ending with `e2e_full_cloud_40`
3. Trade tab: Market Top + Option Chain rows (snapshot after hours / live in session)

