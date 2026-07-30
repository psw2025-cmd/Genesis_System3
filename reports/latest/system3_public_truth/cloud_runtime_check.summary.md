# Cloud Runtime Check

- Generated UTC: `2026-07-30T04:01:01.414712Z`
- Verdict: **WARN**
- Base URL: `http://127.0.0.1:8000`
- Expected commit: `a4adb00e180df16d8207b591594bc71820b14e0e`
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
- **WARNING** `endpoint_deploy_info` — deploy_info failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `endpoint_health` — health failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `endpoint_memory_before` — memory_before failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `endpoint_broker_status` — broker_status failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `endpoint_broker_dhan_status` — broker_dhan_status failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `endpoint_broker_deps` — broker_deps failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `endpoint_scheduler_health` — scheduler_health failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `endpoint_portfolio_unified` — portfolio_unified failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `endpoint_memory_after_portfolio` — memory_after_portfolio failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `endpoint_chain_nifty` — chain_nifty failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `endpoint_memory_after_chain` — memory_after_chain failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `endpoint_underlyings` — underlyings failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `endpoint_state` — state failed: 0 URLError: <urlopen error [Errno 111] Connection refused> attempts=4
- **WARNING** `broker_not_connected` — broker status not connected: None
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=None source=None

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`False`, status=`0`, latency_ms=`0.4`, attempts=`4`
- `health` `/api/health`: ok=`False`, status=`0`, latency_ms=`0.5`, attempts=`4`
- `memory_before` `/api/memory`: ok=`False`, status=`0`, latency_ms=`0.4`, attempts=`4`
- `broker_status` `/api/broker/status`: ok=`False`, status=`0`, latency_ms=`0.4`, attempts=`4`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`False`, status=`0`, latency_ms=`0.3`, attempts=`4`
- `broker_deps` `/api/broker/deps`: ok=`False`, status=`0`, latency_ms=`0.3`, attempts=`4`
- `scheduler_health` `/api/scheduler/health`: ok=`False`, status=`0`, latency_ms=`0.4`, attempts=`4`
- `portfolio_unified` `/api/portfolio/unified`: ok=`False`, status=`0`, latency_ms=`0.3`, attempts=`4`
- `memory_after_portfolio` `/api/memory`: ok=`False`, status=`0`, latency_ms=`0.4`, attempts=`4`
- `chain_nifty` `/api/chain/NIFTY`: ok=`False`, status=`0`, latency_ms=`0.3`, attempts=`4`
- `memory_after_chain` `/api/memory`: ok=`False`, status=`0`, latency_ms=`0.3`, attempts=`4`
- `underlyings` `/api/underlyings`: ok=`False`, status=`0`, latency_ms=`0.3`, attempts=`4`
- `state` `/api/state`: ok=`False`, status=`0`, latency_ms=`0.3`, attempts=`4`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
