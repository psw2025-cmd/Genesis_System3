import asyncio
import json
import sys
from pathlib import Path

# Add C:\content\app to path
sys.path.insert(0, r"C:\content\app")
from app import app, evidence_store, SYMBOLS, STRIKES, list_routes, ui, market_overview, get_evidence

async def main():
    print("Testing C:\\content\\app\\app.py directly...")
    
    # 1. Total routes count from app.routes
    get_routes = [r for r in app.routes if hasattr(r, 'methods') and 'GET' in r.methods]
    print(f"Total GET routes: {len(get_routes)}")
    assert len(get_routes) >= 500, f"Expected >= 500 GET routes, got {len(get_routes)}"

    # 2. Evidence store count
    print(f"Evidence store count: {len(evidence_store)}")
    assert len(evidence_store) >= 1300, f"Expected >= 1300 evidence entries, got {len(evidence_store)}"
    first_ev = evidence_store[0]
    print(f"Evidence sample: {first_ev['symbol']} at {first_ev['price']}, hash: {first_ev['hash'][:12]}...")
    assert "symbol" in first_ev and "price" in first_ev and "timestamp" in first_ev and "hash" in first_ev

    # 3. /api/routes handler
    routes_resp = await list_routes()
    print(f"/api/routes returned: total={routes_resp['total']}, real={routes_resp['real']}, routes_len={len(routes_resp['routes'])}")
    assert routes_resp['total'] >= 500
    assert routes_resp['real'] is True
    assert len(routes_resp['routes']) >= 500
    assert routes_resp['routes'][0]['status'] == "ONLINE"

    # 4. /ui handler
    ui_resp = await ui()
    html = ui_resp.body.decode('utf-8')
    print(f"/ui response status: {ui_resp.status_code}, html length: {len(html)}")
    assert ui_resp.status_code == 200
    assert len(html) > 500
    assert "GENESIS" in html
    assert "Auto-Found @app.get" in html

    # 5. /api/market handler
    market_resp = await market_overview()
    quotes = market_resp['data']['quotes']
    print(f"/api/market quotes: {len(quotes)}, real={market_resp['real']}, hash={market_resp['hash'][:12]}")
    assert len(quotes) >= 48
    assert market_resp['real'] is True
    assert "hash" in market_resp

    # 6. /api/evidence handler
    ev_resp = await get_evidence(limit=50)
    entries = ev_resp['data']['entries']
    total_in_store = ev_resp['data']['total_in_store']
    print(f"/api/evidence entries returned: {len(entries)}, total in store: {total_in_store}")
    assert len(entries) == 50
    assert total_in_store >= 1300

    # 7. Check option routes presence
    opt_routes = [r.path for r in get_routes if r.path.startswith("/api/option-chain")]
    print(f"Option chain routes: {len(opt_routes)} (e.g. {opt_routes[0]} to {opt_routes[-1]})")
    assert len(opt_routes) >= 100

    # 8. Check symbol routes presence
    market_sym_routes = [r.path for r in get_routes if r.path.startswith("/api/market/")]
    print(f"Market symbol routes: {len(market_sym_routes)}")
    assert len(market_sym_routes) >= 48

    # 9. Check scanner routes presence
    scanner_routes = [r.path for r in get_routes if r.path.startswith("/api/scanner")]
    print(f"Scanner routes: {len(scanner_routes)}")
    assert len(scanner_routes) >= 50

    print("\n>>> ALL IN-PROCESS FASTAPI ASSERTIONS PASSED! <<<")

if __name__ == "__main__":
    asyncio.run(main())
