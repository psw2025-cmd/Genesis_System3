# Cloud Runtime Check

- Generated UTC: `2026-07-03T11:46:41.678482Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `19e3208364f4711b7212662bd260a47c0e14ba46`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `True`
- `scheduler_received`: `True`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `skipped_for_render_memory`

## Memory
- `before`: rss=`113.1`, pct=`23.6`, status=`OK`
- `after_portfolio`: rss=`273.0`, pct=`56.9`, status=`OK`
- `after_chain`: rss=`273.0`, pct=`56.9`, status=`OK`

## Alerts
- None

## Warnings
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=19e3208364f4
- **WARNING** `scheduler_not_healthy` — worker push received but unhealthy: ["jobs missed today (past catch-up window, never fired): ['self_healing_watchdog', 'datasource_health_check', 'dashboard_endpoint_coverage', 'auto_coordinator_premarket', 'dhan_instruments_sync', 'daily_gain_rank', 'paper_lifecycle_proof', 'ui_market_cross_verify', 'paper_lifecycle_proof_midday', 'ui_market_cross_verify_midday', 'paper_lifecycle_proof_afternoon', '[REDACTED]', 'daily_gain_validate', 'dashboard_browser_proof']"]
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=MARKET_CLOSED source=closed

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`335.8`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`179.9`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`174.6`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`600.6`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`498.9`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`1696.9`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`291.7`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`3755.2`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`137.6`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`210.4`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`159.8`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`135.3`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`153.6`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
