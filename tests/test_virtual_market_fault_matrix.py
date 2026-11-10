"""Deterministic cloud-only virtual market fault injection; no broker connection."""
from datetime import datetime, timedelta, timezone
import pytest
from dashboard.backend.paper_market_replay import MarketTick, replay_paper_buy, replay_paper_sell
from dashboard.backend.synthetic_paper_lifecycle import virtual_paper_lifecycle

T=datetime(2026,11,9,3,45,tzinfo=timezone.utc)
def tick(n=0,**kwargs):
    args=dict(timestamp=(T+timedelta(seconds=n)).isoformat(),bid=99.5,ask=100.0,
              available_qty=25,source="DHAN_REPLAY_SYNTHETIC",connected=True)
    args.update(kwargs)
    return MarketTick(**args)

@pytest.mark.parametrize("scenario",["trend","range","volatile"])
@pytest.mark.parametrize("step,orders,fills,opens,closes",[
    (0,0,0,0,0),(4,0,0,0,0),(5,1,1,1,0),(29,1,1,1,0),
    (30,2,2,0,1),(3600,2,2,0,1)])
def test_full_lifecycle_matrix(scenario,step,orders,fills,opens,closes):
    a=virtual_paper_lifecycle(scenario,step)
    b=virtual_paper_lifecycle(scenario,step)
    assert a==b
    assert (a["order_count"],a["fill_count"],len(a["positions"]),len(a["closed_positions"]))==(orders,fills,opens,closes)
    assert a["broker_orders"] is False
    assert a["net_pnl_verified"] is False
    assert a["realized_net_pnl"] is None

@pytest.mark.parametrize("overrides,status",[
    ({"connected":False},"BLOCKED_DISCONNECTED_OR_UNTRUSTED"),
    ({"source":"REAL_BROKER"},"BLOCKED_DISCONNECTED_OR_UNTRUSTED"),
    ({"bid":0},"BLOCKED_INVALID_QUOTE"),
    ({"bid":101},"BLOCKED_INVALID_QUOTE"),
    ({"available_qty":-1},"BLOCKED_INVALID_QUOTE"),
    ({"available_qty":0},"PAPER_PARTIAL"),
])
@pytest.mark.parametrize("side",["BUY","SELL"])
def test_quote_faults_block_or_remain_partial(side,overrides,status):
    q=tick(**overrides)
    result=replay_paper_buy([q],25) if side=="BUY" else replay_paper_sell([q],25,held_qty=25)
    assert result["status"]==status
    assert result["filled_qty"]==0

@pytest.mark.parametrize("side",["BUY","SELL"])
def test_out_of_order_and_stale_ticks_fail_closed(side):
    runner=lambda ticks: replay_paper_buy(ticks,25) if side=="BUY" else replay_paper_sell(ticks,25,held_qty=25)
    for ticks in ([tick(0,available_qty=5),tick(-1)], [tick(0,available_qty=5),tick(4)]):
        result=runner(ticks)
        assert result["status"]=="BLOCKED_STALE_OR_OUT_OF_ORDER"
        assert result["filled_qty"]==5
        assert result["remaining_qty"]==20

@pytest.mark.parametrize("side",["BUY","SELL"])
def test_partial_liquidity_and_bid_ask_execution(side):
    runner=lambda ticks: replay_paper_buy(ticks,25) if side=="BUY" else replay_paper_sell(ticks,25,held_qty=25)
    result=runner([tick(0,available_qty=10),tick(1,available_qty=15)])
    assert result["status"]=="PAPER_FILLED"
    assert [f["qty"] for f in result["fills"]]==[10,15]
    assert all(f["price"]==(100.0 if side=="BUY" else 99.5) for f in result["fills"])

def test_capital_limit_and_no_naked_sell():
    assert replay_paper_buy([tick()],25,capital_limit=1000)["status"]=="BLOCKED_CAPITAL_LIMIT"
    with pytest.raises(ValueError,match="PAPER_REPLAY_INVALID_SELL_RISK"):
        replay_paper_sell([tick()],25,held_qty=24)

@pytest.mark.parametrize("scenario,step",[
    ("invalid",0),("trend",-1),("range",3601),("volatile",True)])
def test_invalid_scenario_and_steps(scenario,step):
    with pytest.raises(ValueError,match="INVALID_SYNTHETIC_REPLAY_INPUT"):
        virtual_paper_lifecycle(scenario,step)
