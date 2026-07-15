# Cloud Runtime Check

- Generated UTC: `2026-07-15T09:14:37.594109Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `286e40cb2733f3296ea80ffbd6953d84f9ff12b2`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `False`
- `scheduler_received`: `False`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `skipped_for_render_memory`

## Memory
- `before`: rss=`361.1`, pct=`20.1`, status=`OK`
- `after_portfolio`: rss=`405.3`, pct=`22.5`, status=`OK`
- `after_chain`: rss=`405.3`, pct=`22.5`, status=`OK`

## Alerts
- None

## Warnings
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=286e40cb2733
- **WARNING** `broker_not_connected` — broker status not connected: TOKEN_EXPIRED_OR_INVALID
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=NO_DHAN_DATA source=dhan

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`243.7`, attempts=`1`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`154.6`, attempts=`1`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`146.6`, attempts=`1`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`531.0`, attempts=`1`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`460.1`, attempts=`1`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`888.1`, attempts=`1`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`315.8`, attempts=`1`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`6211.6`, attempts=`1`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`148.7`, attempts=`1`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`642.9`, attempts=`1`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`147.0`, attempts=`1`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`145.9`, attempts=`1`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`121.7`, attempts=`1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
