# Cloud Runtime Check

- Generated UTC: `2026-08-04T04:02:20.514691Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
- Expected commit: `f4ff64368d0f5e6247022844533b0e41a7544633`
- Deployed commit: `unknown`

## Key facts
- `broker_connected`: `False`
- `scheduler_received`: `False`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `skipped_for_render_memory`

## Memory
- `before`: rss=`472.0`, pct=`98.3`, status=`HIGH`
- `after_portfolio`: rss=`472.0`, pct=`98.3`, status=`HIGH`
- `after_chain`: rss=`472.0`, pct=`98.3`, status=`HIGH`

## Alerts
- None

## Warnings
- **WARNING** `broker_not_connected` — broker status not connected: TOKEN_EXPIRED_OR_INVALID
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=NO_DHAN_DATA source=dhan
- **WARNING** `memory_before` — RSS high: 472.0MB
- **WARNING** `memory_after_portfolio` — RSS high: 472.0MB
- **WARNING** `memory_after_chain` — RSS high: 472.0MB

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`886.8`, attempts=`1`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`578.2`, attempts=`1`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`377.7`, attempts=`1`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`750.0`, attempts=`1`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`729.8`, attempts=`1`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`1376.6`, attempts=`1`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`311.2`, attempts=`1`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`594.7`, attempts=`1`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`659.6`, attempts=`1`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`401.0`, attempts=`1`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`370.3`, attempts=`1`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`575.3`, attempts=`1`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`309.8`, attempts=`1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
