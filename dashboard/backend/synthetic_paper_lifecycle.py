"""Deterministic, isolated PAPER market lifecycle demonstration.

Never reads broker credentials, writes real ledgers, or claims realized broker P&L.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from dashboard.backend.paper_market_replay import MarketTick, replay_paper_buy, replay_paper_sell

START = datetime(2026, 11, 9, 3, 45, tzinfo=timezone.utc)
CAPITAL_LIMIT = 50000.0
DAILY_LOSS_LIMIT = 5000.0

def virtual_paper_lifecycle(scenario: str, step: int) -> dict[str, Any]:
    if scenario not in ("trend", "range", "volatile") or type(step) is not int or not 0 <= step <= 3600:
        raise ValueError("INVALID_SYNTHETIC_REPLAY_INPUT")
    factor = {"trend": 0.3, "range": 0.0, "volatile": -0.25}[scenario]
    qty = 25
    def price(at: int) -> float:
        variation = ((at % 9) - 4) * {"trend": .2, "range": 1.2, "volatile": 2.2}[scenario]
        return round(max(1.0, 100 + factor * at + variation), 2)
    def stamp(at: int) -> str:
        return (START + timedelta(seconds=at)).isoformat()
    def fill(at: int, side: str) -> dict[str, Any]:
        px=price(at)
        tick=MarketTick(timestamp=stamp(at), bid=max(.01,px-.5), ask=px, available_qty=qty)
        result=(replay_paper_buy([tick], qty, CAPITAL_LIMIT) if side == "BUY" else
                replay_paper_sell([tick], qty, held_qty=qty))
        return {"fill_id":f"SYN-{scenario}-{side}-{at}", "side":side, "qty":result["filled_qty"],
                "price":result["fills"][0]["price"] if result["fills"] else None, "timestamp_utc":stamp(at),
                "source":"SYNTHETIC_PAPER_FILL_NOT_BROKER", "status":result["status"]}
    orders=[]
    fills=[]
    positions=[]
    closed=[]
    if step >= 5:
        entry=fill(5,"BUY")
        orders.append({"order_id":f"SYN-{scenario}-ENTRY", "side":"BUY", "qty":qty,
                       "status":entry["status"], "timestamp_utc":stamp(5)})
        if entry["status"]=="PAPER_FILLED":
            fills.append(entry)
            if step < 30:
                positions.append({"position_id":f"SYN-{scenario}-POS", "symbol":"NIFTY CE SYNTHETIC",
                                  "qty":qty,"entry_price":entry["price"],"mark_price":price(step),
                                  "unrealized_pnl_illustrative":round((price(step)-entry["price"])*qty,2),
                                  "status":"OPEN","source":"SYNTHETIC"})
            else:
                exit_fill=fill(30,"SELL")
                orders.append({"order_id":f"SYN-{scenario}-EXIT", "side":"SELL", "qty":qty,
                               "status":exit_fill["status"],"timestamp_utc":stamp(30)})
                if exit_fill["status"]=="PAPER_FILLED":
                    fills.append(exit_fill)
                    gross=round((exit_fill["price"]-entry["price"])*qty,2)
                    closed.append({"position_id":f"SYN-{scenario}-POS","entry_fill_id":entry["fill_id"],
                                   "exit_fill_id":exit_fill["fill_id"],"qty":qty,"gross_pnl":gross,
                                   "charges":None,"net_pnl":None,"verification_status":"NOT_VERIFIED",
                                   "reason":"Synthetic fill model; charges not independently verified"})
    return {"mode":"SYNTHETIC_PAPER_ONLY","scenario":scenario,"step":step,
            "source":"DETERMINISTIC_SYNTHETIC_MARKET","broker_orders":False,
            "capital_limit_inr":CAPITAL_LIMIT,"daily_loss_limit_inr":DAILY_LOSS_LIMIT,
            "orders":orders,"fills":fills,"positions":positions,"closed_positions":closed,
            "order_count":len(orders),"fill_count":len(fills),
            "net_pnl_verified":False,"realized_net_pnl":None,
            "trade_verification_status":"NOT_VERIFIED",
            "generated_market_timestamp_utc":stamp(step)}
