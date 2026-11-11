import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

import asyncio
from dashboard.backend.app import get_market_live_board, get_chain

async def main():
    print("Testing get_chain('NIFTY')...")
    chain = await get_chain('NIFTY')
    print(f"NIFTY spot: {chain.get('spot')}, atm: {chain.get('atm_strike')}, chg: {chain.get('change')} ({chain.get('change_pct')}%), contracts: {len(chain.get('contracts', []))}")
    
    print("\nTesting get_market_live_board()...")
    board = await get_market_live_board()
    indices = board.get("indices", [])
    print(f"Indices count: {len(indices)}")
    for idx in indices:
        sym = idx.get("symbol")
        ltp = idx.get("spot") or idx.get("ltp")
        chg = idx.get("change")
        chg_pct = idx.get("change_pct")
        prev = idx.get("prev_close")
        print(f"  {sym}: ltp={ltp}, chg={chg} ({chg_pct}%), prev={prev}")

if __name__ == "__main__":
    asyncio.run(main())
