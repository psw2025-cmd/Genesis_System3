# Dhan Broker Setup — Local Laptop Authority

Broker credentials belong only in the approved local secure-secret mechanism on the authorized Windows laptop. Do not commit, paste, email, upload, log, or print access tokens, PINs, TOTP seeds, private keys, or credential payloads.

Resolution order is local secure vault first, then an explicitly configured local environment mapping. Missing credentials fail closed.

Broker acceptance requires a fresh exact-current-main laptop session proving `/ui` connected status, matching same-session API metadata without secret values, and fresh semantic contracts for NIFTY, BANKNIFTY, FINNIFTY and MIDCPNIFTY.

Safety: `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`, real broker order count zero.
