# Cloud Runtime Check

- Generated UTC: `2026-07-10T18:16:50.619446Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `3d64cbe318a485920b1704f5fad728e8aeccbe20`
- Deployed commit: `unknown`

## Key facts
- `broker_connected`: `False`
- `scheduler_received`: `False`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `160`
- `portfolio_details_mode`: `skipped_for_render_memory`

## Memory
- `before`: rss=`None`, pct=`None`, status=`None`
- `after_portfolio`: rss=`369.2`, pct=`20.5`, status=`OK`
- `after_chain`: rss=`369.2`, pct=`20.5`, status=`OK`

## Alerts
- None

## Warnings
- **WARNING** `endpoint_deploy_info` — deploy_info failed: 502 HTTPError: 502
- **WARNING** `endpoint_health` — health failed: 502 HTTPError: 502
- **WARNING** `endpoint_memory_before` — memory_before failed: 502 HTTPError: 502
- **WARNING** `endpoint_broker_status` — broker_status failed: 502 HTTPError: 502
- **WARNING** `endpoint_broker_dhan_status` — broker_dhan_status failed: 502 HTTPError: 502
- **WARNING** `broker_not_connected` — broker status not connected: None
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`False`, status=`502`, latency_ms=`193.5`
- `health` `/api/health`: ok=`False`, status=`502`, latency_ms=`285.9`
- `memory_before` `/api/memory`: ok=`False`, status=`502`, latency_ms=`127.2`
- `broker_status` `/api/broker/status`: ok=`False`, status=`502`, latency_ms=`147.0`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`False`, status=`502`, latency_ms=`124.0`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`889.9`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`173.7`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`6404.1`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`171.2`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`199.8`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`344.9`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`133.6`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`137.1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
