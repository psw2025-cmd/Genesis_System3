import sys
from pathlib import Path

# Add C:\content\app to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "content" / "app"))
from app import app, evidence_store, SYMBOLS, STRIKES
from starlette.testclient import TestClient

client = TestClient(app, raise_server_exceptions=False)

def test_genesis_500_routes():

    # 1. Total routes
    get_routes = [r for r in app.routes if hasattr(r, 'methods') and 'GET' in r.methods]
    print(f"Total GET routes: {len(get_routes)}")
    assert len(get_routes) >= 500, f"Expected >= 500 GET routes, got {len(get_routes)}"

    # 2. Evidence store count
    print(f"Evidence store count: {len(evidence_store)}")
    assert len(evidence_store) >= 1300, f"Expected >= 1300 evidence entries, got {len(evidence_store)}"

    # 3. /api/routes
    res_routes = client.get("/api/routes")
    data_routes = res_routes.json()
    print(f"/api/routes status: {res_routes.status_code}, total: {data_routes['total']}, real: {data_routes['real']}")
    assert res_routes.status_code == 200
    assert data_routes["total"] >= 500
    assert data_routes["real"] is True

    # 4. /ui
    res_ui = client.get("/ui")
    print(f"/ui status: {res_ui.status_code}, html len: {len(res_ui.text)}, contains GENESIS: {'GENESIS' in res_ui.text}")
    assert res_ui.status_code == 200
    assert "GENESIS" in res_ui.text
    assert "Auto-Found @app.get" in res_ui.text

    # 5. /api/market
    res_m = client.get("/api/market")
    data_m = res_m.json()
    print(f"/api/market quotes: {len(data_m['data']['quotes'])}, real: {data_m['real']}, hash: {data_m['hash'][:12]}")
    assert res_m.status_code == 200
    assert data_m["real"] is True
    assert len(data_m["data"]["quotes"]) >= 48

    # 6. /api/evidence
    res_ev = client.get("/api/evidence?limit=10")
    data_ev = res_ev.json()
    print(f"/api/evidence returned: {len(data_ev['data']['entries'])}, total_in_store: {data_ev['data']['total_in_store']}")
    assert res_ev.status_code == 200
    assert data_ev["data"]["total_in_store"] >= 1300

    # 7. Check option strike route
    res_opt = client.get("/api/option-chain/1250")
    assert res_opt.status_code == 200
    print(f"/api/option-chain/1250: {res_opt.json()['data']['ce_price']}")

    # 8. Check symbol market route
    res_sym = client.get("/api/market/RELIANCE")
    assert res_sym.status_code == 200
    print(f"/api/market/RELIANCE: {res_sym.json()['data']['price']}")

    # 9. Check exception handling auto-correct
    # Create dummy route that raises
    @app.get("/api/test_crash")
    async def crash():
        raise ValueError("Test forced failure for auto-correct handler")

    res_crash = client.get("/api/test_crash")
    data_crash = res_crash.json()
    print(f"Exception handler response: {data_crash}")
    assert data_crash["auto_corrected"] is True
    assert data_crash["real"] is True
    assert "hash" in data_crash

    print("\n>>> ALL TESTS & VERIFICATIONS PASSED SUCCESSFULLY! <<<")
