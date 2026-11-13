import sys
from pathlib import Path

# Add project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from core.engine.dhan_full_market_scanner import SCANNER

def test_dhan_full_market_scanning_daemon():
    print("Executing Dhan Full-Market Scanning Daemon & Router Tests...")

    # 1. Full-Market Symbol Discovery (Auto-Find)
    disc = SCANNER.get_market_discovery(min_contracts=10)
    total_und = disc["total_underlyings_discovered"]
    liquid_und = disc["liquid_underlyings_filtered"]
    print(f"[1. Auto-Find] Discovered {total_und} underlyings ({liquid_und} liquid filtered)")
    assert total_und >= 180, f"Expected >= 180 F&O underlyings, got {total_und}"
    assert liquid_und >= 180, f"Expected >= 180 liquid underlyings, got {liquid_und}"
    
    # Verify major underlyings are present
    discovered_names = [u["underlying"] for u in disc["underlyings"]]
    for expected in ["NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE", "TCS", "INFY"]:
        assert expected in discovered_names, f"Expected underlying {expected} missing from discovery"

    # 2. Dynamic Chain Subscriptions (Auto-Work)
    prox = SCANNER.get_proximity_strikes("NIFTY", 25447.86, strikes_count=5)
    print(f"[2. Auto-Work] NIFTY Spot: {prox['spot_price']} -> ATM Strike: {prox['atm_strike']}")
    assert prox["atm_strike"] == 25450
    assert len(prox["ce_strikes"]) == 11
    assert len(prox["pe_strikes"]) == 11
    
    # Verify Dhan WebSocket Multiplexing Subscription Packet
    pkt = prox["websocket_subscription_packet"]
    assert pkt["RequestCode"] == 21
    assert pkt["InstrumentCount"] == 22
    assert len(pkt["InstrumentList"]) == 22
    assert pkt["InstrumentList"][0]["ExchangeSegment"] == "NSE_FNO"
    print(f"[2. Auto-Work] WebSocket subscription packet generated with {pkt['InstrumentCount']} dynamic strikes")

    # 3. Broker Execution Binding (Dhan API) with Paper Safety Interlock
    order_res = SCANNER.bind_order_execution(
        underlying="NIFTY",
        strike=25500.0,
        option_type="CE",
        transaction_type="BUY",
        order_type="LIMIT",
        price=164.50,
        quantity=50
    )
    print(f"[3. Broker Binding] Order Status: {order_res['status']} | Mode: {order_res['execution_mode']}")
    assert order_res["status"] == "EXECUTED_PAPER"
    assert order_res["execution_mode"] == "PAPER_SIMULATED"
    assert order_res["real_broker_dispatch"] is False
    assert "safety_gate" in order_res
    
    # Verify dynamic Dhan payload fields
    payload = order_res["dhan_payload"]
    assert payload["exchangeSegment"] == "NSE_FNO"
    assert payload["securityId"] == "DHAN-OPT-NIFTY-25500-CE"
    assert payload["transactionType"] == "BUY"
    assert payload["quantity"] == 50
    assert payload["price"] == 164.50
    print(f"[3. Broker Binding] Dhan payload mapped to securityId: {payload['securityId']}")

    # Verify paper fill report
    fill = order_res["fill_report"]
    assert fill["fill_price"] > 164.50  # Slippage accounted for
    assert fill["estimated_brokerage_inr"] == 20.0
    assert fill["estimated_stt_inr"] > 0
    print(f"[3. Broker Binding] Paper fill: Rs. {fill['fill_price']} (Slippage: {fill['slippage_pts']} pts, STT: Rs. {fill['estimated_stt_inr']})")

    print("\n>>> ALL DHAN FULL-MARKET SCANNER & ROUTER TESTS PASSED! <<<")

if __name__ == "__main__":
    test_dhan_full_market_scanning_daemon()
