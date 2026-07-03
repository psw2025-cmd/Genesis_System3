# Cloud Runtime Check

- Generated UTC: `2026-07-03T09:45:40.425985Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `90ce1c57641cab172353467e2b2721d274b76d0f`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `True`
- `scheduler_received`: `True`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `142`
- `portfolio_details_mode`: `skipped_for_render_memory`

## Memory
- `before`: rss=`398.1`, pct=`82.9`, status=`WARN`
- `after_portfolio`: rss=`398.1`, pct=`82.9`, status=`WARN`
- `after_chain`: rss=`398.1`, pct=`82.9`, status=`WARN`

## Alerts
- None

## Warnings
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=90ce1c57641c
- **WARNING** `scheduler_not_healthy` — worker push received but unhealthy: ["jobs missed today (past catch-up window, never fired): ['self_healing_watchdog', 'datasource_health_check', 'dashboard_endpoint_coverage', 'auto_coordinator_premarket', 'dhan_instruments_sync', 'daily_gain_rank', 'paper_lifecycle_proof', 'ui_market_cross_verify', 'paper_lifecycle_proof_midday', 'ui_market_cross_verify_midday', 'paper_lifecycle_proof_afternoon']"]

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`121.6`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`114.3`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`93.0`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`429.3`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`447.5`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`1935.4`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`84.1`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`3722.0`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`77.7`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`176.6`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`112.9`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`65.5`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`74.1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
