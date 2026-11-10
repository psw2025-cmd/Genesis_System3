"""400 market-like PAPER execution stress scenarios; synthetic, not live evidence."""
from datetime import datetime, timedelta, timezone
import pytest
from dashboard.backend.paper_market_replay import MarketTick,replay_paper_buy

BASE=datetime(2026,11,7,4,0,tzinfo=timezone.utc)
def tick(second,bid=99.0,ask=100.0,available=10,**kwargs):
    return MarketTick((BASE+timedelta(seconds=second)).isoformat(),bid,ask,available,**kwargs)

@pytest.mark.parametrize("case",range(400))
def test_market_like_partial_fills_and_liquidity(case):
    qty=1+case%40
    chunk=1+case%11
    ticks=[tick(i,bid=89+case%20,ask=90+case%20,available=chunk) for i in range((qty+chunk-1)//chunk)]
    result=replay_paper_buy(ticks,qty)
    assert result["status"]=="PAPER_FILLED"
    assert result["filled_qty"]==qty
    assert sum(x["qty"] for x in result["fills"])==qty
    assert all(x["mode"]=="SYNTHETIC_PAPER_FILL_NOT_BROKER" for x in result["fills"])

def test_disconnect_after_partial_preserves_evidence():
    result=replay_paper_buy([tick(0,available=2),tick(1,available=8,connected=False)],10)
    assert result["status"]=="BLOCKED_DISCONNECTED_OR_UNTRUSTED"
    assert result["filled_qty"]==2 and result["remaining_qty"]==8

@pytest.mark.parametrize("ticks,expected",[
    ([tick(0,ask=0)],"BLOCKED_INVALID_QUOTE"),
    ([tick(0,bid=105,ask=100)],"BLOCKED_INVALID_QUOTE"),
    ([tick(0,ask=1000)],"BLOCKED_CAPITAL_LIMIT"),
    ([tick(0,available=0),tick(5)],"BLOCKED_STALE_OR_OUT_OF_ORDER"),
    ([tick(1,available=0),tick(0)],"BLOCKED_STALE_OR_OUT_OF_ORDER"),
    ([tick(0,connected=False)],"BLOCKED_DISCONNECTED_OR_UNTRUSTED"),
])
def test_replay_failure_modes(ticks,expected):
    assert replay_paper_buy(ticks,100)["status"]==expected

def test_no_ticks_never_claims_full_fill():
    assert replay_paper_buy([],10)["status"]=="PAPER_PARTIAL"
