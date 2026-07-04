# Cloud Runtime Check

- Generated UTC: `2026-07-03T17:46:53.654103Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `4f44d1945f676813beb098ae4282983f861a33a5`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `True`
- `scheduler_received`: `True`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `skipped_for_render_memory`

## Memory
- `before`: rss=`398.5`, pct=`83.0`, status=`WARN`
- `after_portfolio`: rss=`398.5`, pct=`83.0`, status=`WARN`
- `after_chain`: rss=`398.5`, pct=`83.0`, status=`WARN`

## Alerts
- None

## Warnings
- **WARNING** `endpoint_broker_dhan_status` — broker_dhan_status failed: 503 HTTPError: 503
- **WARNING** `endpoint_broker_deps` — broker_deps failed: 503 HTTPError: 503
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=4f44d1945f67
- **WARNING** `scheduler_not_healthy` — worker push received but unhealthy: ["jobs missed today (past catch-up window, never fired): ['self_healing_watchdog', 'datasource_health_check', 'dashboard_endpoint_coverage', 'auto_coordinator_premarket', 'dhan_instruments_sync', 'daily_gain_rank', 'paper_lifecycle_proof', 'ui_market_cross_verify', 'paper_lifecycle_proof_midday', 'ui_market_cross_verify_midday', 'paper_lifecycle_proof_afternoon', '[REDACTED]', 'daily_gain_validate', 'daily_gain_trend', 'daily_prediction_benchmark', 'dashboard_browser_proof', 'system3_post_market_pipeline', 'paper_day_proof_pack', 'auto_retrain', 'auto_coordinator_post_market']"]
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=MARKET_CLOSED source=closed

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`353.1`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`147.2`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`130.6`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`479.9`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`False`, status=`503`, latency_ms=`391.5`
- `broker_deps` `/api/broker/deps`: ok=`False`, status=`503`, latency_ms=`561.7`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`180.8`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`4412.5`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`127.8`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`189.9`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`138.7`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`118.1`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`118.7`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
