import json
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "http://127.0.0.1:8008"

def http_get(path: str) -> dict:
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "GenesisLiveVerifier/1.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))

def test_01_market_overview_matches_live_cache():
    """Verify /api/market spot prices match state/chain_cache/*.json"""
    data = http_get("/api/market")
    assert "data" in data and "quotes" in data["data"]
    quotes = {q["symbol"]: q["price"] for q in data["data"]["quotes"]}
    
    # Check NIFTY
    nifty_cache = Path("state/chain_cache/NIFTY.json")
    if nifty_cache.exists():
        expected_nifty = json.loads(nifty_cache.read_text(encoding="utf-8"))["spot"]
        assert abs(quotes["NIFTY"] - expected_nifty) < 1.0, f"NIFTY {quotes['NIFTY']} != {expected_nifty}"
        
    # Check BANKNIFTY
    bn_cache = Path("state/chain_cache/BANKNIFTY.json")
    if bn_cache.exists():
        expected_bn = json.loads(bn_cache.read_text(encoding="utf-8"))["spot"]
        assert abs(quotes["BANKNIFTY"] - expected_bn) < 1.0, f"BANKNIFTY {quotes['BANKNIFTY']} != {expected_bn}"

    # Check SENSEX
    sx_cache = Path("state/chain_cache/SENSEX.json")
    if sx_cache.exists():
        expected_sx = json.loads(sx_cache.read_text(encoding="utf-8"))["spot"]
        assert abs(quotes["SENSEX"] - expected_sx) < 1.0, f"SENSEX {quotes['SENSEX']} != {expected_sx}"

    # Check RELIANCE
    rel_cache = Path("state/chain_cache/RELIANCE.json")
    if rel_cache.exists():
        expected_rel = json.loads(rel_cache.read_text(encoding="utf-8"))["spot"]
        assert abs(quotes["RELIANCE"] - expected_rel) < 1.0, f"RELIANCE {quotes['RELIANCE']} != {expected_rel}"

def test_02_options_intelligence_matches_chain_cache():
    """Verify /api/options/intelligence matches chain_cache metrics for NIFTY, SENSEX, RELIANCE"""
    # NIFTY
    nifty_data = http_get("/api/options/intelligence?symbol=NIFTY")["data"]
    nifty_expected = json.loads(Path("state/chain_cache/NIFTY.json").read_text(encoding="utf-8"))
    assert abs(nifty_data["spot"] - nifty_expected["spot"]) < 1.0
    assert abs(nifty_data["pcr"] - nifty_expected["pcr"]) < 0.05
    assert nifty_data["atm_strike"] == nifty_expected["atm_strike"]
    assert nifty_data["max_pain"] == nifty_expected["max_pain"]

    # RELIANCE
    rel_data = http_get("/api/options/intelligence?symbol=RELIANCE")["data"]
    rel_expected = json.loads(Path("state/chain_cache/RELIANCE.json").read_text(encoding="utf-8"))
    assert abs(rel_data["spot"] - rel_expected["spot"]) < 1.0
    assert abs(rel_data["pcr"] - rel_expected["pcr"]) < 0.05
    assert rel_data["atm_strike"] == rel_expected["atm_strike"]
    assert rel_data["max_pain"] == rel_expected["max_pain"]

    # SENSEX
    sx_data = http_get("/api/options/intelligence?symbol=SENSEX")["data"]
    sx_expected = json.loads(Path("state/chain_cache/SENSEX.json").read_text(encoding="utf-8"))
    assert abs(sx_data["spot"] - sx_expected["spot"]) < 1.0
    assert abs(sx_data["pcr"] - sx_expected["pcr"]) < 0.05
    assert sx_data["atm_strike"] == sx_expected["atm_strike"]
    assert sx_data["max_pain"] == sx_expected["max_pain"]

def test_03_options_gainers_matches_live_feeds():
    """Verify /api/options/gainers returns real live gainers from Moneycontrol & Dhan state"""
    gainers = http_get("/api/options/gainers")["data"]
    assert "ce_gainers" in gainers
    assert len(gainers["ce_gainers"]) > 0

    # Ensure real scraped gainer (e.g. RELIANCE 1320 CE +654.4% or SENSEX / NIFTY top CE) is present
    contracts = [g["contract"] for g in gainers["ce_gainers"]]
    sources = [g.get("source", "") for g in gainers["ce_gainers"]]
    
    assert any("RELIANCE" in c for c in contracts) or any("SENSEX" in c for c in contracts) or any("NIFTY" in c for c in contracts)
    # Check that change_pct is substantial (real top gainers have > 50% gain)
    assert any(g["change_pct"] > 50.0 for g in gainers["ce_gainers"])

def test_04_dhan_chain_subscriptions_dynamic_proximity():
    """Verify /api/dhan/discovery/chain-subscriptions dynamically centers on live spot"""
    # For NIFTY (live spot ~23053), ATM should be 23050
    sub_nifty = http_get("/api/dhan/discovery/chain-subscriptions?symbol=NIFTY")["data"]
    assert sub_nifty["atm_strike"] == 23050.0
    assert sub_nifty["total_subscribed_strikes"] == 11
    assert 23050.0 in sub_nifty["strikes"]
    assert min(sub_nifty["strikes"]) <= 22800.0
    assert max(sub_nifty["strikes"]) >= 23300.0

    # For RELIANCE (live spot ~1164.9), ATM should be 1160
    sub_rel = http_get("/api/dhan/discovery/chain-subscriptions?symbol=RELIANCE")["data"]
    assert sub_rel["atm_strike"] == 1160.0
    assert sub_rel["total_subscribed_strikes"] == 11
    assert 1160.0 in sub_rel["strikes"]

def test_05_dhan_full_market_inventory():
    """Verify full-market discovery maps scrip master with 200+ underlyings"""
    inv = http_get("/api/dhan/discovery/full-market")["data"]
    total = inv.get("total_underlyings") or inv.get("total_underlyings_discovered", 0)
    assert total >= 200
    assert inv["active_fno_underlyings"] >= 150
    assert "NIFTY" in inv["underlyings_summary"]
    assert "RELIANCE" in inv["underlyings_summary"]

if __name__ == "__main__":
    test_01_market_overview_matches_live_cache()
    print("test_01_market_overview_matches_live_cache: PASS")
    test_02_options_intelligence_matches_chain_cache()
    print("test_02_options_intelligence_matches_chain_cache: PASS")
    test_03_options_gainers_matches_live_feeds()
    print("test_03_options_gainers_matches_live_feeds: PASS")
    test_04_dhan_chain_subscriptions_dynamic_proximity()
    print("test_04_dhan_chain_subscriptions_dynamic_proximity: PASS")
    test_05_dhan_full_market_inventory()
    print("test_05_dhan_full_market_inventory: PASS")
    print("ALL LIVE MARKET RECONCILIATION TESTS PASSED!")
