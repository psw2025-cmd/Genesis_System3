import json
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "http://127.0.0.1:8008"

def test_six_pillars():
    print(f"Executing 6-Pillar Full Command Center Audit against {BASE_URL}...")
    
    # 01. Market Coverage
    with urllib.request.urlopen(f"{BASE_URL}/api/market/inventory") as res:
        inv = json.loads(res.read().decode("utf-8"))["data"]
        print(f"[01 Coverage] Total Instruments: {inv['total_instruments']}, F&O: {inv['fo_contracts_count']}, Sectors: {inv['sectors_monitored']}")
        assert inv["total_instruments"] >= 2000
        assert inv["fo_contracts_count"] >= 1600

    with urllib.request.urlopen(f"{BASE_URL}/api/market/breadth") as res:
        br = json.loads(res.read().decode("utf-8"))["data"]
        print(f"[01 Coverage] Breadth: Adv={br['advances']}, Dec={br['declines']}, A/D Ratio={br['ad_ratio']}")
        assert br["advances"] > 1000 and br["declines"] > 1000

    with urllib.request.urlopen(f"{BASE_URL}/api/market/missing-symbols") as res:
        ms = json.loads(res.read().decode("utf-8"))["data"]
        assert ms["missing_count"] == 0

    # 02. Live Data Truth
    with urllib.request.urlopen(f"{BASE_URL}/api/route-health") as res:
        rh = json.loads(res.read().decode("utf-8"))["data"]
        print(f"[02 Truth] Route Health feeds count: {len(rh['routes'])}, overall: {rh['overall_health']}")
        assert len(rh["routes"]) >= 4

    with urllib.request.urlopen(f"{BASE_URL}/api/data/provenance") as res:
        dp = json.loads(res.read().decode("utf-8"))["data"]
        assert dp["hash_chain_verified"] is True

    with urllib.request.urlopen(f"{BASE_URL}/api/evidence?limit=10") as res:
        ev = json.loads(res.read().decode("utf-8"))["data"]
        print(f"[02 Truth] Evidence store total entries: {ev['total_in_store']}")
        assert ev["total_in_store"] >= 1300

    # 03. Options Intelligence
    with urllib.request.urlopen(f"{BASE_URL}/api/options/intelligence?symbol=RELIANCE") as res:
        oi = json.loads(res.read().decode("utf-8"))["data"]
        print(f"[03 Options] RELIANCE PCR={oi['pcr']}, IV={oi['iv']}%, Delta={oi['greeks']['delta']}")
        assert oi["pcr"] > 0
        assert "delta" in oi["greeks"] and "gamma" in oi["greeks"]

    with urllib.request.urlopen(f"{BASE_URL}/api/options/gainers") as res:
        og = json.loads(res.read().decode("utf-8"))["data"]
        print(f"[03 Options] Top CE movers: {len(og['ce_gainers'])}, Top PE movers: {len(og['pe_gainers'])}")
        assert len(og["ce_gainers"]) >= 3 and len(og["pe_gainers"]) >= 3

    # 04. Paper-Trading Proof
    with urllib.request.urlopen(f"{BASE_URL}/api/paper/ledger") as res:
        pl = json.loads(res.read().decode("utf-8"))["data"]
        summary = pl["closed_summary"]
        print(f"[04 Paper] Trades: {summary['total_trades']}, Win Rate: {summary['win_rate_pct']}%, Day P&L: INR {summary['day_pnl_inr']}")
        assert len(pl["open_trades"]) == 3
        assert summary["win_rate_pct"] > 60

    with urllib.request.urlopen(f"{BASE_URL}/api/paper/lifecycle") as res:
        lc = json.loads(res.read().decode("utf-8"))["data"]
        assert len(lc["lifecycle"]) == 5

    # 05. ML Prediction Validation
    with urllib.request.urlopen(f"{BASE_URL}/api/ml/forecast-vs-actual") as res:
        fa = json.loads(res.read().decode("utf-8"))["data"]
        print(f"[05 ML] Forecast vs Actual: {len(fa['comparisons'])} instruments checked")
        assert len(fa["comparisons"]) >= 3

    with urllib.request.urlopen(f"{BASE_URL}/api/ml/prediction-audit") as res:
        pa = json.loads(res.read().decode("utf-8"))["data"]
        print(f"[05 ML] Hit Rate: {pa['hit_rate_pct']}%, MAE: {pa['mae_pct']}%, Spearman Rho: {pa['spearman_rho']}")
        assert pa["hit_rate_pct"] > 70
        assert pa["spearman_rho"] >= 0.70

    with urllib.request.urlopen(f"{BASE_URL}/api/ml/benchmark") as res:
        bm = json.loads(res.read().decode("utf-8"))["data"]
        print(f"[05 ML] Strategy Return: {bm['strategy_return_pct']}%, Benchmark: {bm['nifty_return_pct']}%, Alpha: {bm['alpha_pct']}%")
        assert bm["alpha_pct"] > 0

    # 06. Dashboard and Operational Proof
    with urllib.request.urlopen(f"{BASE_URL}/ui") as res:
        html = res.read().decode("utf-8")
        assert res.status == 200
        assert "GENESIS SYSTEM3" in html
        assert "PRO TRADING COMMAND" in html
        assert "Sector Heatmap" in html
        assert "Options Intelligence" in html
        print(f"[06 UI] Verified /ui length: {len(html)} bytes")

    with urllib.request.urlopen(f"{BASE_URL}/api/routes") as res:
        r_data = json.loads(res.read().decode("utf-8"))
        print(f"[06 Routes] Total routes verified: {r_data['total']}")
        assert r_data["total"] >= 500

    print("\n>>> ALL 6 PILLARS VERIFIED 100% SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_six_pillars()
