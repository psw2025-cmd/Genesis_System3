# Cloud Runtime Check

- Generated UTC: `2026-07-10T15:54:21.798957Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `c40c9fd0ee7afb6e58326b87aa08f369b837ed34`
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
- **WARNING** `endpoint_deploy_info` — deploy_info failed: 502 HTTPError: 502
- **WARNING** `endpoint_health` — health failed: 502 HTTPError: 502
- **WARNING** `endpoint_memory_before` — memory_before failed: 502 HTTPError: 502
- **WARNING** `endpoint_broker_status` — broker_status failed: 502 HTTPError: 502
- **WARNING** `endpoint_broker_dhan_status` — broker_dhan_status failed: 502 HTTPError: 502
- **WARNING** `endpoint_broker_deps` — broker_deps failed: 502 HTTPError: 502
- **WARNING** `endpoint_scheduler_health` — scheduler_health failed: 502 HTTPError: 502
- **WARNING** `endpoint_portfolio_unified` — portfolio_unified failed: 502 HTTPError: 502
- **WARNING** `endpoint_memory_after_portfolio` — memory_after_portfolio failed: 502 HTTPError: 502
- **WARNING** `endpoint_chain_nifty` — chain_nifty failed: 502 HTTPError: 502
- **WARNING** `endpoint_memory_after_chain` — memory_after_chain failed: 502 HTTPError: 502
- **WARNING** `endpoint_underlyings` — underlyings failed: 502 HTTPError: 502
- **WARNING** `endpoint_state` — state failed: 502 HTTPError: 502
- **WARNING** `broker_not_connected` — broker status not connected: None
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=None source=None

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`False`, status=`502`, latency_ms=`206.5`
- `health` `/api/health`: ok=`False`, status=`502`, latency_ms=`109.0`
- `memory_before` `/api/memory`: ok=`False`, status=`502`, latency_ms=`93.4`
- `broker_status` `/api/broker/status`: ok=`False`, status=`502`, latency_ms=`111.4`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`False`, status=`502`, latency_ms=`95.8`
- `broker_deps` `/api/broker/deps`: ok=`False`, status=`502`, latency_ms=`64.7`
- `scheduler_health` `/api/scheduler/health`: ok=`False`, status=`502`, latency_ms=`73.5`
- `portfolio_unified` `/api/portfolio/unified`: ok=`False`, status=`502`, latency_ms=`67.3`
- `memory_after_portfolio` `/api/memory`: ok=`False`, status=`502`, latency_ms=`96.0`
- `chain_nifty` `/api/chain/NIFTY`: ok=`False`, status=`502`, latency_ms=`71.6`
- `memory_after_chain` `/api/memory`: ok=`False`, status=`502`, latency_ms=`72.5`
- `underlyings` `/api/underlyings`: ok=`False`, status=`502`, latency_ms=`73.9`
- `state` `/api/state`: ok=`False`, status=`502`, latency_ms=`85.9`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
