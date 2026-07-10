# Cloud Runtime Check

- Generated UTC: `2026-07-10T09:04:53.335415Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `975f1821bff93a54f0a3e9aeff8a30cd6f2293cf`
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
- `deploy_info` `/api/deploy/info`: ok=`False`, status=`401`, latency_ms=`84.4`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`64.6`
- `memory_before` `/api/memory`: ok=`False`, status=`401`, latency_ms=`144.0`
- `broker_status` `/api/broker/status`: ok=`False`, status=`401`, latency_ms=`67.3`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`False`, status=`401`, latency_ms=`76.1`
- `broker_deps` `/api/broker/deps`: ok=`False`, status=`401`, latency_ms=`63.6`
- `scheduler_health` `/api/scheduler/health`: ok=`False`, status=`401`, latency_ms=`67.7`
- `portfolio_unified` `/api/portfolio/unified`: ok=`False`, status=`401`, latency_ms=`61.9`
- `memory_after_portfolio` `/api/memory`: ok=`False`, status=`401`, latency_ms=`71.3`
- `chain_nifty` `/api/chain/NIFTY`: ok=`False`, status=`401`, latency_ms=`292.4`
- `memory_after_chain` `/api/memory`: ok=`False`, status=`401`, latency_ms=`60.8`
- `underlyings` `/api/underlyings`: ok=`False`, status=`401`, latency_ms=`64.0`
- `state` `/api/state`: ok=`False`, status=`401`, latency_ms=`63.1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
