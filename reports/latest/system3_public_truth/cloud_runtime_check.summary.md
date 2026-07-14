# Cloud Runtime Check

- Generated UTC: `2026-07-14T09:13:17.566162Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-backend.onrender.com`
- Expected commit: `893ca11f05bd64449633a91a147914fa1dd314b1`
- Deployed commit: `[REDACTED]`

## Key facts
- `broker_connected`: `False`
- `scheduler_received`: `False`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `skipped_for_render_memory`

## Memory
- `before`: rss=`361.1`, pct=`20.1`, status=`OK`
- `after_portfolio`: rss=`361.3`, pct=`20.1`, status=`OK`
- `after_chain`: rss=`361.3`, pct=`20.1`, status=`OK`

## Alerts
- None

## Warnings
- **WARNING** `deploy_commit_mismatch` — Render git_sha=[REDACTED] expected=893ca11f05bd
- **WARNING** `broker_not_connected` — broker status not connected: TOKEN_EXPIRED_OR_INVALID
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=NO_DHAN_DATA source=dhan

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`122.1`, attempts=`1`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`84.0`, attempts=`1`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`70.0`, attempts=`1`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`396.5`, attempts=`1`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`391.7`, attempts=`1`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`1385.8`, attempts=`1`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`120.9`, attempts=`1`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`8538.1`, attempts=`1`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`64.0`, attempts=`2`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`115.2`, attempts=`1`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`107.8`, attempts=`1`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`64.0`, attempts=`1`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`69.7`, attempts=`1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
