# Recommendation

Do not recommend migration to a platform named `Dhan Advance Platform` because the exact term was not verified in official Dhan/DhanHQ documentation.

Continue treating official DhanHQ API v2 documentation as the authority for orders, portfolio, funds/margins, historical data, option chains, WebSocket feeds, instrument master support, and trader risk controls.

System3 should remain in Analyzer/Paper mode for this branch. Any proof that reports `mode=LIVE`, `live_trading_enabled=true`, or `order_placement_allowed=true` is a critical failure.

Current safety verdict: PASS_ANALYZER_PAPER_ONLY.
Current market-closed verdict: MARKET_CLOSED_EXPECTED.
