# Cloud Runtime Check

- Generated UTC: `2026-07-06T10:29:04.817766Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `0148588fa2db552c2236f99c2959cf44b54432c1`
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
- **WARNING** `endpoint_deploy_info` — deploy_info failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `endpoint_health` — health failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `endpoint_memory_before` — memory_before failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `endpoint_broker_status` — broker_status failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `endpoint_broker_dhan_status` — broker_dhan_status failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `endpoint_broker_deps` — broker_deps failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `endpoint_scheduler_health` — scheduler_health failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `endpoint_portfolio_unified` — portfolio_unified failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `endpoint_memory_after_portfolio` — memory_after_portfolio failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `endpoint_chain_nifty` — chain_nifty failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `endpoint_memory_after_chain` — memory_after_chain failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `endpoint_underlyings` — underlyings failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `endpoint_state` — state failed: None URLError: <urlopen error [Errno -5] No address associated with hostname>
- **WARNING** `broker_not_connected` — broker status not connected: None
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=None source=None

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`False`, status=`None`, latency_ms=`22.4`
- `health` `/api/health`: ok=`False`, status=`None`, latency_ms=`1.2`
- `memory_before` `/api/memory`: ok=`False`, status=`None`, latency_ms=`1.2`
- `broker_status` `/api/broker/status`: ok=`False`, status=`None`, latency_ms=`1.1`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`False`, status=`None`, latency_ms=`1.1`
- `broker_deps` `/api/broker/deps`: ok=`False`, status=`None`, latency_ms=`1.2`
- `scheduler_health` `/api/scheduler/health`: ok=`False`, status=`None`, latency_ms=`1.2`
- `portfolio_unified` `/api/portfolio/unified`: ok=`False`, status=`None`, latency_ms=`1.2`
- `memory_after_portfolio` `/api/memory`: ok=`False`, status=`None`, latency_ms=`1.1`
- `chain_nifty` `/api/chain/NIFTY`: ok=`False`, status=`None`, latency_ms=`1.2`
- `memory_after_chain` `/api/memory`: ok=`False`, status=`None`, latency_ms=`1.2`
- `underlyings` `/api/underlyings`: ok=`False`, status=`None`, latency_ms=`1.2`
- `state` `/api/state`: ok=`False`, status=`None`, latency_ms=`1.2`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
