# Cloud Runtime Check

- Generated UTC: `2026-07-03T11:00:11.283120Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `1fdb140833afed9a47a67ee76c69658b51acfb68`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `True`
- `scheduler_received`: `True`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `skipped_for_render_memory`

## Memory
- `before`: rss=`399.1`, pct=`83.2`, status=`WARN`
- `after_portfolio`: rss=`399.1`, pct=`83.2`, status=`WARN`
- `after_chain`: rss=`399.1`, pct=`83.2`, status=`WARN`

## Alerts
- None

## Warnings
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=1fdb140833af
- **WARNING** `scheduler_not_healthy` — worker push received but unhealthy: ["jobs missed today (past catch-up window, never fired): ['self_healing_watchdog', 'datasource_health_check', 'dashboard_endpoint_coverage', 'auto_coordinator_premarket', 'dhan_instruments_sync', 'daily_gain_rank', 'paper_lifecycle_proof', 'ui_market_cross_verify', 'paper_lifecycle_proof_midday', 'ui_market_cross_verify_midday', 'paper_lifecycle_proof_afternoon', '[REDACTED]', 'daily_gain_validate', 'dashboard_browser_proof']"]
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=MARKET_CLOSED source=closed

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`368.2`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`155.8`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`146.2`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`453.4`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`452.7`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`1742.7`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`121.7`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`2783.4`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`132.8`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`194.9`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`117.6`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`130.3`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`110.5`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
