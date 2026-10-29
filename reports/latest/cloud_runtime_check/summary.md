# Cloud Runtime Check

- Generated UTC: `2026-10-29T13:36:10.945682Z`
- Verdict: **WARN**
- Base URL: `https://genesis-system3-web-doq2wplepa-el.a.run.app`
- Expected commit: `unknown`
- Deployed commit: `[REDACTED] LIVE_TRADING_ENABLED=0 SYSTEM3_LIVE_TRADING_ALLOWED=0 AUTO_EXECUTE_TRADES=0 ANALYZE_MODE=1 SYSTEM3_MODE=ANALYZER`

## Key facts
- `broker_connected`: `True`
- `scheduler_received`: `False`
- `scheduler_healthy`: `False`
- `chain_nifty_contracts`: `0`
- `portfolio_details_mode`: `enabled`

## Memory
- `before`: rss=`512.9`, pct=`53.4`, status=`OK`
- `after_portfolio`: rss=`512.9`, pct=`53.4`, status=`OK`
- `after_chain`: rss=`512.9`, pct=`53.4`, status=`OK`

## Alerts
- None

## Warnings
- **WARNING** `scheduler_no_worker_push` — worker scheduler health has not been received
- **WARNING** `chain_nifty_empty` — NIFTY chain empty/status=NO_DHAN_DATA source=dhan
- **WARNING** `memory_before` — RSS high: 512.9MB
- **WARNING** `memory_after_portfolio` — RSS high: 512.9MB
- **WARNING** `memory_after_chain` — RSS high: 512.9MB

## Endpoint status
- `deploy_info` `/api/deploy/info`: ok=`True`, status=`200`, latency_ms=`136.2`, attempts=`1`
- `health` `/api/health`: ok=`True`, status=`200`, latency_ms=`66.2`, attempts=`1`
- `memory_before` `/api/memory`: ok=`True`, status=`200`, latency_ms=`45.0`, attempts=`1`
- `broker_status` `/api/broker/status`: ok=`True`, status=`200`, latency_ms=`3421.0`, attempts=`1`
- `broker_dhan_status` `/api/broker/dhan/status`: ok=`True`, status=`200`, latency_ms=`428.5`, attempts=`1`
- `broker_deps` `/api/broker/deps`: ok=`True`, status=`200`, latency_ms=`1082.2`, attempts=`1`
- `scheduler_health` `/api/scheduler/health`: ok=`True`, status=`200`, latency_ms=`84.5`, attempts=`1`
- `portfolio_unified` `/api/portfolio/unified`: ok=`True`, status=`200`, latency_ms=`12155.3`, attempts=`1`
- `memory_after_portfolio` `/api/memory`: ok=`True`, status=`200`, latency_ms=`2307.4`, attempts=`1`
- `chain_nifty` `/api/chain/NIFTY`: ok=`True`, status=`200`, latency_ms=`11122.9`, attempts=`1`
- `memory_after_chain` `/api/memory`: ok=`True`, status=`200`, latency_ms=`55.8`, attempts=`1`
- `underlyings` `/api/underlyings`: ok=`True`, status=`200`, latency_ms=`78.5`, attempts=`1`
- `state` `/api/state`: ok=`True`, status=`200`, latency_ms=`50.7`, attempts=`1`

## Safety
- This check does not call order placement, modification, cancellation, or live-trading enablement endpoints.
- Secret-looking keys/values are redacted before saving report files.
