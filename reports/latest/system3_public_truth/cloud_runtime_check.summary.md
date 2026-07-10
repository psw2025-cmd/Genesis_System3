# Cloud Runtime Check

- Generated UTC: `2026-07-10T11:48:18.656072Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `0e3ae264b708e12b707a66b6503721e42de9c4a9`
- Deployed commit: `unknown`

## Key facts
- `broker_connected`: `False`
- `scheduler_received`: `False`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `None`

## Memory
- `before`: rss=`None`, pct=`None`, status=`None`
- `after_portfolio`: rss=`None`, pct=`None`, status=`None`
- `after_chain`: rss=`None`, pct=`None`, status=`None`

## Alerts
- None

## Warnings
- **WARNING** `endpoint_deploy_info` — deploy_info failed: 401 HTTPError: 401
- **WARNING** `endpoint_memory_before` — memory_before failed: 401 HTTPError: 401
- **WARNING** `endpoint_broker_status` — broker_status failed: 401 HTTPError: 401
- **WARNING** `endpoint_broker_dhan_status` — broker_dhan_status failed: 401 HTTPError: 401
- **WARNING** `endpoint_broker_deps` — broker_deps failed: 401 HTTPError: 401
- **WARNING** `endpoint_scheduler_health` — scheduler_health failed: 401 HTTPError: 401
- **WARNING** `endpoint_portfolio_unified` — portfolio_unified failed: 401 HTTPError: 401
- **WARNING** `endpoint_memory_after_portfolio` — memory_after_portfolio failed: 401 HTTPError: 401
- **WARNING** `endpoint_chain_nifty` — chain_nifty failed: 401 HTTPError: 401
- **WARNING** `endpoint_memory_after_chain` — memory_after_chain failed: 401 HTTPError: 401
- **WARNING** `endpoint_underlyings` — underlyings failed: 401 HTTPError: 401
- **WARNING** `endpoint_state` — state failed: 401 HTTPError: 401
- **WARNING** `broker_not_connected` — broker status not connected: None
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=None source=None

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`False`, status=`401`, latency_ms=`148.9`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`167.7`
- `memory_before` `/api/memory`: ok=`False`, status=`401`, latency_ms=`264.5`
- `broker_status` `/api/broker/status`: ok=`False`, status=`401`, latency_ms=`183.0`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`False`, status=`401`, latency_ms=`145.2`
- `broker_deps` `/api/broker/deps`: ok=`False`, status=`401`, latency_ms=`111.7`
- `scheduler_health` `/api/scheduler/health`: ok=`False`, status=`401`, latency_ms=`115.3`
- `portfolio_unified` `/api/portfolio/unified`: ok=`False`, status=`401`, latency_ms=`132.5`
- `memory_after_portfolio` `/api/memory`: ok=`False`, status=`401`, latency_ms=`132.9`
- `chain_nifty` `/api/chain/NIFTY`: ok=`False`, status=`401`, latency_ms=`269.3`
- `memory_after_chain` `/api/memory`: ok=`False`, status=`401`, latency_ms=`278.4`
- `underlyings` `/api/underlyings`: ok=`False`, status=`401`, latency_ms=`154.9`
- `state` `/api/state`: ok=`False`, status=`401`, latency_ms=`125.6`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
