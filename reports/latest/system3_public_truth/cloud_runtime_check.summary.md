# Cloud Runtime Check

- Generated UTC: `2026-07-14T10:09:18.286588Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `9519d8920b6a7ef1ab1a314f3be828f813773946`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `True`
- `scheduler_received`: `False`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `160`
- `portfolio_details_mode`: `None`

## Memory
- `before`: rss=`884.7`, pct=`49.1`, status=`OK`
- `after_portfolio`: rss=`252.1`, pct=`14.0`, status=`OK`
- `after_chain`: rss=`252.1`, pct=`14.0`, status=`OK`

## Alerts
- None

## Warnings
- **WARNING** `endpoint_portfolio_unified` — portfolio_unified failed: 502 HTTPError: 502 attempts=4
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=9519d8920b6a
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `memory_before` — RSS high: 884.7MB

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`13056.6`, attempts=`1`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`350.2`, attempts=`1`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`457.6`, attempts=`1`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`5438.1`, attempts=`1`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`13471.2`, attempts=`1`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`3271.6`, attempts=`1`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`4644.0`, attempts=`1`
- `portfolio_unified` `/api/portfolio/unified`: ok=`False`, status=`502`, latency_ms=`129.3`, attempts=`4`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`123.1`, attempts=`2`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`377.8`, attempts=`1`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`137.9`, attempts=`1`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`110.9`, attempts=`1`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`146.0`, attempts=`1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
