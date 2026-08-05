# Cloud Runtime Check

- Generated UTC: `2026-08-05T04:01:28.702676Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
- Expected commit: `49bae332ff5072aa50b0c38f307b1306834e233a`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `False`
- `scheduler_received`: `False`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `None`

## Memory
- `before`: rss=`1398.8`, pct=`291.4`, status=`HIGH`
- `after_portfolio`: rss=`1398.8`, pct=`291.4`, status=`HIGH`
- `after_chain`: rss=`1398.8`, pct=`291.4`, status=`HIGH`

## Alerts
- None

## Warnings
- **WARNING** `endpoint_portfolio_unified` — portfolio_unified failed: 500 HTTPError: 500 attempts=1
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=49bae332ff50
- **WARNING** `broker_not_connected` — broker status not connected: TOKEN_EXPIRED_OR_INVALID
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=NO_DHAN_DATA source=dhan
- **WARNING** `memory_before` — RSS high: 1398.8MB
- **WARNING** `memory_after_portfolio` — RSS high: 1398.8MB
- **WARNING** `memory_after_chain` — RSS high: 1398.8MB

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`17961.1`, attempts=`2`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`13344.5`, attempts=`1`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`13239.5`, attempts=`1`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`13466.9`, attempts=`1`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`515.9`, attempts=`1`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`1670.4`, attempts=`1`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`333.9`, attempts=`1`
- `portfolio_unified` `/api/portfolio/unified`: ok=`False`, status=`500`, latency_ms=`325.9`, attempts=`1`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`429.3`, attempts=`1`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`426.0`, attempts=`1`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`431.6`, attempts=`1`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`328.9`, attempts=`1`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`340.8`, attempts=`1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
