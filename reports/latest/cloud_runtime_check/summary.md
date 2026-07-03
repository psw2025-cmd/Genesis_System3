# Cloud Runtime Check

- Generated UTC: `2026-07-03T10:53:53.726706Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `b12b8f4502cb90769c9d7a40c92abe323feade3b`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `True`
- `scheduler_received`: `True`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `skipped_for_render_memory`

## Memory
- `before`: rss=`397.3`, pct=`82.8`, status=`WARN`
- `after_portfolio`: rss=`397.3`, pct=`82.8`, status=`WARN`
- `after_chain`: rss=`397.3`, pct=`82.8`, status=`WARN`

## Alerts
- None

## Warnings
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=b12b8f4502cb
- **WARNING** `scheduler_not_healthy` — worker push received but unhealthy: ["jobs missed today (past catch-up window, never fired): ['self_healing_watchdog', 'datasource_health_check', 'dashboard_endpoint_coverage', 'auto_coordinator_premarket', 'dhan_instruments_sync', 'daily_gain_rank', 'paper_lifecycle_proof', 'ui_market_cross_verify', 'paper_lifecycle_proof_midday', 'ui_market_cross_verify_midday', 'paper_lifecycle_proof_afternoon', 'daily_gain_validate', 'daily_gain_trend', 'dashboard_browser_proof', 'paper_day_proof_pack', 'auto_coordinator_post_market']"]
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=MARKET_CLOSED source=closed

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`215.9`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`240.8`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`243.5`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`556.0`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`476.7`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`1999.0`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`173.4`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`2966.7`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`142.7`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`214.7`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`148.1`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`201.5`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`166.5`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
