# Cloud Runtime Check

- Generated UTC: `2026-08-05T06:24:05.655413Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
- Expected commit: `abb67e4660ad6a1b0af8e636768b2d64a08d39ad`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `False`
- `scheduler_received`: `False`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `160`
- `portfolio_details_mode`: `None`

## Memory
- `before`: rss=`1409.5`, pct=`293.6`, status=`HIGH`
- `after_portfolio`: rss=`1409.5`, pct=`293.6`, status=`HIGH`
- `after_chain`: rss=`1409.5`, pct=`293.6`, status=`HIGH`

## Alerts
- None

## Warnings
- **WARNING** `endpoint_portfolio_unified` — portfolio_unified failed: 500 HTTPError: 500 attempts=1
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=abb67e4660ad
- **WARNING** `broker_not_connected` — broker status not connected: TOKEN_EXPIRED_OR_INVALID
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `memory_before` — RSS high: 1409.5MB
- **WARNING** `memory_after_portfolio` — RSS high: 1409.5MB
- **WARNING** `memory_after_chain` — RSS high: 1409.5MB

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`933.5`, attempts=`2`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`13350.2`, attempts=`1`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`12923.1`, attempts=`1`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`13566.9`, attempts=`1`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`525.1`, attempts=`1`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`1461.7`, attempts=`1`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`333.6`, attempts=`1`
- `portfolio_unified` `/api/portfolio/unified`: ok=`False`, status=`500`, latency_ms=`335.8`, attempts=`1`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`436.1`, attempts=`1`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`814.2`, attempts=`1`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`399.7`, attempts=`1`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`352.1`, attempts=`1`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`320.0`, attempts=`1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
