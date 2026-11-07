"""Sell-side market replay: BID execution, inventory limits, no broker orders."""
import pytest
from dashboard.backend.paper_market_replay import MarketTick, replay_paper_sell
from dashboard.backend.synthetic_paper_lifecycle import virtual_paper_lifecycle

def tick(bid=99.5,ask=100,qty=25,connected=True):
    return MarketTick("2026-11-09T03:45:30+00:00",bid,ask,qty,connected=connected)

@pytest.mark.parametrize("bid,ask",[(1,1.5),(25,25.5),(99.5,100),(100,101),(250,260)])
@pytest.mark.parametrize("qty",range(1,26))
def test_sell_executes_at_bid_not_ask(bid,ask,qty):
    result=replay_paper_sell([tick(bid,ask,qty)],qty,qty)
    assert result["status"]=="PAPER_FILLED"
    assert result["fills"]==[{"timestamp":"2026-11-09T03:45:30+00:00","qty":qty,
                             "price":bid,"mode":"SYNTHETIC_PAPER_FILL_NOT_BROKER"}]

@pytest.mark.parametrize("qty,held",[(1,0),(25,24),(0,0),(-1,100),(2,1)])
def test_sell_cannot_exceed_held_inventory(qty,held):
    with pytest.raises(ValueError,match="INVALID_SELL_RISK"):
        replay_paper_sell([tick()],qty,held)

@pytest.mark.parametrize("bid,ask,available,connected,expected",[
    (0,100,25,True,"BLOCKED_INVALID_QUOTE"),
    (101,100,25,True,"BLOCKED_INVALID_QUOTE"),
    (99,100,-1,True,"BLOCKED_INVALID_QUOTE"),
    (99,100,25,False,"BLOCKED_DISCONNECTED_OR_UNTRUSTED"),
    (99,100,0,True,"PAPER_PARTIAL"),
])
def test_sell_fails_closed(bid,ask,available,connected,expected):
    assert replay_paper_sell([tick(bid,ask,available,connected)],25,25)["status"]==expected

@pytest.mark.parametrize("scenario",["trend","range","volatile"])
def test_lifecycle_sell_receipt_matches_bid(scenario):
    result=virtual_paper_lifecycle(scenario,30)
    assert len(result["fills"])==2
    entry,exit=result["fills"]
    assert entry["side"]=="BUY" and exit["side"]=="SELL"
    assert exit["price"]<virtual_paper_lifecycle(scenario,30)["closed_positions"][0]["gross_pnl"]/25+entry["price"]+0.01
    assert result["closed_positions"][0]["gross_pnl"]==round((exit["price"]-entry["price"])*25,2)
    assert result["closed_positions"][0]["net_pnl"] is None
