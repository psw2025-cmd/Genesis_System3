# Cloud Runtime Check

- Generated UTC: `2026-07-03T08:35:06.982317Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `985e541b5049677c794f8b7638ee01a8025deff0`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `False`
- `scheduler_received`: `True`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `skipped_for_render_memory`

## Memory
- `before`: rss=`113.8`, pct=`23.7`, status=`OK`
- `after_portfolio`: rss=`280.3`, pct=`58.4`, status=`OK`
- `after_chain`: rss=`280.3`, pct=`58.4`, status=`OK`

## Alerts
- None

## Warnings
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=985e541b5049
- **WARNING** `broker_not_connected` — broker status not connected: TOKEN_EXPIRED_OR_INVALID
- **WARNING** `scheduler_not_healthy` — worker push received but unhealthy: ["jobs missed today (past catch-up window, never fired): ['self_healing_watchdog', 'datasource_health_check', 'dashboard_endpoint_coverage', 'auto_coordinator_premarket', 'dhan_instruments_sync', 'daily_gain_rank', 'paper_lifecycle_proof', 'ui_market_cross_verify', 'paper_lifecycle_proof_midday', 'ui_market_cross_verify_midday']"]
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=NOT_READY source=live

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`143.4`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`105.7`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`72.2`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`433.9`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`386.9`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`1921.2`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`100.8`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`3542.2`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`89.4`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`168.0`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`111.2`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`65.2`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`112.5`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
