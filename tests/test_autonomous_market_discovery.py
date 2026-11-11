import json
import os
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "http://127.0.0.1:8008"

def test_autonomous_market_discovery():
    print(f"Connecting to live server at {BASE_URL}...")

    # 1. Full-Market Discovery Verification
    discovery_url = f"{BASE_URL}/api/dhan/discovery/full-market?min_contracts=10"
    req1 = urllib.request.Request(discovery_url, headers={"User-Agent": "GenesisScripDiscovery/1.0"})
    with urllib.request.urlopen(req1, timeout=25) as res1:
        data1 = json.loads(res1.read().decode("utf-8"))["data"]
    
    total_und = data1.get("total_underlyings") or data1.get("total_underlyings_discovered", 0)
    liquid_und = data1.get("liquid_underlyings_filtered", 0)
    print(f"[1. Auto-Find] Discovered: {total_und} F&O underlyings ({liquid_und} liquid filtered)")
    assert total_und >= 180, f"Expected >= 180 underlyings, got {total_und}"
    assert liquid_und >= 180, f"Expected >= 180 liquid underlyings, got {liquid_und}"
    
    underlying_names = [u["underlying"] for u in data1["underlyings"]]
    for key_asset in ["NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE", "TCS", "INFY"]:
        assert key_asset in underlying_names, f"Asset {key_asset} missing from discovery"

    # 2. Dynamic Chain Subscriptions across Multiple Underlyings
    test_cases = [
        {"symbol": "NIFTY", "spot": 25447.86, "expected_atm": 25450, "step": 50},
        {"symbol": "BANKNIFTY", "spot": 57815.19, "expected_atm": 57800, "step": 100},
        {"symbol": "RELIANCE", "spot": 1307.77, "expected_atm": 1300, "step": 20},
        {"symbol": "TCS", "spot": 3355.00, "expected_atm": 3350, "step": 50}
    ]

    for tc in test_cases:
        sym = tc["symbol"]
        spot = tc["spot"]
        chain_url = f"{BASE_URL}/api/dhan/discovery/chain-subscriptions?symbol={sym}&spot={spot}&strikes=5"
        req2 = urllib.request.Request(chain_url, headers={"User-Agent": "GenesisScripDiscovery/1.0"})
        with urllib.request.urlopen(req2, timeout=25) as res2:
            data2 = json.loads(res2.read().decode("utf-8"))["data"]

        atm = data2["atm_strike"]
        ce_count = len(data2["ce_strikes"])
        pe_count = len(data2["pe_strikes"])
        pkt = data2["websocket_subscription_packet"]
        
        print(f"[2. Auto-Work] {sym}: Spot {spot} -> ATM {atm} | CE Strikes: {ce_count}, PE Strikes: {pe_count} | WS Packet: {pkt['InstrumentCount']} items")
        assert atm == tc["expected_atm"]
        assert ce_count == 11
        assert pe_count == 11
        assert pkt["RequestCode"] == 21
        assert pkt["InstrumentCount"] == 22

    # 3. Dynamic Order Routing & Safety Rules Verification
    order_cases = [
        {"symbol": "NIFTY", "strike": 25500.0, "opt": "CE", "side": "BUY", "price": 164.50, "qty": 50},
        {"symbol": "BANKNIFTY", "strike": 57500.0, "opt": "PE", "side": "BUY", "price": 195.40, "qty": 30},
        {"symbol": "RELIANCE", "strike": 1320.0, "opt": "CE", "side": "BUY", "price": 24.30, "qty": 250}
    ]

    for oc in order_cases:
        order_url = f"{BASE_URL}/api/dhan/orders/dynamic-bind?symbol={oc['symbol']}&strike={oc['strike']}&option_type={oc['opt']}&side={oc['side']}&price={oc['price']}&qty={oc['qty']}"
        req3 = urllib.request.Request(order_url, headers={"User-Agent": "GenesisScripDiscovery/1.0"})
        with urllib.request.urlopen(req3, timeout=15) as res3:
            order_data = json.loads(res3.read().decode("utf-8"))["data"]

        print(f"[3. Order Execution Binding] {oc['symbol']} {oc['strike']} {oc['opt']} -> Mode: {order_data.get('execution_mode')} | ID: {order_data.get('order_id')}")
        assert "PAPER" in order_data.get("execution_mode", "")
        assert order_data.get("status") in ("SUCCESS", "TRANSIT_SIMULATED", "EXECUTED_PAPER")
        assert order_data.get("dhan_payload", {}).get("exchangeSegment") == "NSE_FNO"

    print("ALL AUTONOMOUS MARKET DISCOVERY & ROUTING CHECKS PASSED!")

if __name__ == "__main__":
    test_autonomous_market_discovery()
