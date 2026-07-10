# Cloud Runtime Check

- Generated UTC: `2026-07-10T16:46:53.345166Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `fd096f185a8f82b16ec1d9702ddbf2cea85056a5`
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
- `deploy_info` `/api/deploy/info`: ok=`False`, status=`401`, latency_ms=`208.0`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`336.4`
- `memory_before` `/api/memory`: ok=`False`, status=`401`, latency_ms=`167.3`
- `broker_status` `/api/broker/status`: ok=`False`, status=`401`, latency_ms=`155.5`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`False`, status=`401`, latency_ms=`222.9`
- `broker_deps` `/api/broker/deps`: ok=`False`, status=`401`, latency_ms=`320.1`
- `scheduler_health` `/api/scheduler/health`: ok=`False`, status=`401`, latency_ms=`118.6`
- `portfolio_unified` `/api/portfolio/unified`: ok=`False`, status=`401`, latency_ms=`142.4`
- `memory_after_portfolio` `/api/memory`: ok=`False`, status=`401`, latency_ms=`292.6`
- `chain_nifty` `/api/chain/NIFTY`: ok=`False`, status=`401`, latency_ms=`162.7`
- `memory_after_chain` `/api/memory`: ok=`False`, status=`401`, latency_ms=`283.0`
- `underlyings` `/api/underlyings`: ok=`False`, status=`401`, latency_ms=`188.1`
- `state` `/api/state`: ok=`False`, status=`401`, latency_ms=`329.5`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
