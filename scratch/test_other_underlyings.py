import sys
sys.path.insert(0, '.')
import asyncio
from dashboard.backend.app import _get_chain_uncached

async def test_all():
    for sym in ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'RELIANCE']:
        chain = await _get_chain_uncached(sym)
        print(f"[{sym}] status={chain.get('status')} contracts={len(chain.get('contracts', []))} spot={chain.get('spot')} iv_pct={chain.get('iv_percentile')} oi_chg={chain.get('oi_change')}")

asyncio.run(test_all())
