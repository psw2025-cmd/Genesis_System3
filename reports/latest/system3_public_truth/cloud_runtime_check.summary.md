# Cloud Runtime Check

- Generated UTC: `2026-07-10T12:47:58.615487Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `80ea1ef83ac321b10b05f886b091794961869a1e`
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
- **WARNING** `endpoint_memory_after_portfolio` — memory_after_portfolio failed: 429 HTTPError: 429
- **WARNING** `endpoint_chain_nifty` — chain_nifty failed: 429 HTTPError: 429
- **WARNING** `endpoint_memory_after_chain` — memory_after_chain failed: 429 HTTPError: 429
- **WARNING** `endpoint_underlyings` — underlyings failed: 401 HTTPError: 401
- **WARNING** `endpoint_state` — state failed: 401 HTTPError: 401
- **WARNING** `broker_not_connected` — broker status not connected: None
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=None source=None

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`False`, status=`401`, latency_ms=`192.7`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`122.7`
- `memory_before` `/api/memory`: ok=`False`, status=`401`, latency_ms=`324.6`
- `broker_status` `/api/broker/status`: ok=`False`, status=`401`, latency_ms=`127.0`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`False`, status=`401`, latency_ms=`176.6`
- `broker_deps` `/api/broker/deps`: ok=`False`, status=`401`, latency_ms=`134.8`
- `scheduler_health` `/api/scheduler/health`: ok=`False`, status=`401`, latency_ms=`143.4`
- `portfolio_unified` `/api/portfolio/unified`: ok=`False`, status=`401`, latency_ms=`138.5`
- `memory_after_portfolio` `/api/memory`: ok=`False`, status=`429`, latency_ms=`134.6`
- `chain_nifty` `/api/chain/NIFTY`: ok=`False`, status=`429`, latency_ms=`168.0`
- `memory_after_chain` `/api/memory`: ok=`False`, status=`429`, latency_ms=`343.9`
- `underlyings` `/api/underlyings`: ok=`False`, status=`401`, latency_ms=`127.4`
- `state` `/api/state`: ok=`False`, status=`401`, latency_ms=`162.5`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
