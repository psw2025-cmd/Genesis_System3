# Parallel Audit — chain_scanner

- Status: **BLOCKED**
- Blockers: `2`

## Findings
- Datasource manager contains Dhan chain path.
- Scanner includes index segment targets.

## Blockers
- Option-chain/scanner cannot pass until Dhan auth and live/closed-market Dhan chain rows are proven.
- Current user visual proof showed scanner segments 0/4 and enabled universe 0/4.

## Required fixes
- After broker auth proof, verify /api/chain/NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY with Dhan rows and spot > 0.
- Then verify /api/scanner/top_contract_gainers has real segment rows and CE/PE candidates.
