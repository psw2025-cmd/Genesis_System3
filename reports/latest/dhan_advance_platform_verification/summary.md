# Dhan Advance Platform Verification Audit

- Generated UTC: 2026-06-27T21:34:40.931935Z
- Dhan Advance Platform exact name: NOT_OFFICIAL_EXACT_NAME
- DhanHQ API v2: OFFICIAL_SUPPORTED
- Dhan Cloud: OFFICIAL_SUPPORTED
- Strategy hosting under Dhan Cloud: OFFICIAL_SUPPORTED
- Dhan Cloud strategy templates: OFFICIAL_SUPPORTED as strategy-code starting templates
- React/TypeScript frontend dashboard templates: NOT_VERIFIED
- System3 migration recommendation: DO_NOT_MIGRATE_NOW
- Current System3 mode: Analyzer/Paper only
- Official claim coverage: 88.89%
- System3 current endpoint match: 100.0%
- Safety verdict: PASS_ANALYZER_PAPER_ONLY
- Market-closed verdict: MARKET_CLOSED_EXPECTED

## Unsupported Claims

- Frontend dashboard templates or React/TypeScript templates

## Official Sources

- https://docs.dhanhq.co/
- https://docs.dhanhq.co/cloud/
- https://dhanhq.co/docs/v2/
- C:\System3\Genesis_System3\dhan-api-docs.md

## Recommendation

Do not migrate to or use the name `Dhan Advance Platform`.
Continue System3 as a DhanHQ API v2 integration in Analyzer/Paper mode.
Evaluate Dhan Cloud separately later only after System3 Analyzer/Paper proof is stable.
Do not enable live trading or order writes in this branch.

## Safety

- mode: PAPER
- broker mode: ANALYZER
- live_trading_enabled: False
- order_placement_allowed: False
- frontend_header: react
