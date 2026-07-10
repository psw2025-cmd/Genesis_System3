# Cloud Runtime Check

- Generated UTC: `2026-07-10T09:08:15.126164Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `793d83f594411b5f70ef55197b3896c2e7642a8a`
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
- `deploy_info` `/api/deploy/info`: ok=`False`, status=`502`, latency_ms=`164.3`
- `health` `/api/health`: ok=`False`, status=`502`, latency_ms=`141.1`
- `memory_before` `/api/memory`: ok=`False`, status=`502`, latency_ms=`120.8`
- `broker_status` `/api/broker/status`: ok=`False`, status=`502`, latency_ms=`107.8`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`False`, status=`502`, latency_ms=`110.5`
- `broker_deps` `/api/broker/deps`: ok=`False`, status=`502`, latency_ms=`117.6`
- `scheduler_health` `/api/scheduler/health`: ok=`False`, status=`502`, latency_ms=`125.3`
- `portfolio_unified` `/api/portfolio/unified`: ok=`False`, status=`502`, latency_ms=`262.2`
- `memory_after_portfolio` `/api/memory`: ok=`False`, status=`502`, latency_ms=`102.5`
- `chain_nifty` `/api/chain/NIFTY`: ok=`False`, status=`502`, latency_ms=`100.2`
- `memory_after_chain` `/api/memory`: ok=`False`, status=`502`, latency_ms=`90.6`
- `underlyings` `/api/underlyings`: ok=`False`, status=`502`, latency_ms=`108.6`
- `state` `/api/state`: ok=`False`, status=`502`, latency_ms=`113.4`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
