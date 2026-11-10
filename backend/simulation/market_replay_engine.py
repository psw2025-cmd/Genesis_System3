from __future__ import annotations
import time
import uuid
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Any


@dataclass(frozen=True)
class TickEvent:
    symbol: str
    ltp: float
    volume: int
    timestamp_ns: int
    bid: float
    ask: float
    is_market_open: bool = True


@dataclass
class SimulatedOrder:
    order_id: str
    symbol: str
    side: str
    order_type: str
    quantity: int
    price: float
    status: str = "PENDING"
    filled_price: Optional[float] = None
    filled_at_ns: Optional[int] = None
    rejection_reason: Optional[str] = None


class DeterministicMarketSimulator:
    def __init__(self, stale_threshold_sec: float = 15.0) -> None:
        self.stale_threshold_sec = stale_threshold_sec
        self._last_ticks: Dict[str, TickEvent] = {}
        self._orders: Dict[str, SimulatedOrder] = {}
        self._subscribers: List[Callable[[Dict[str, Any]], None]] = []
        self._market_status: str = "CLOSED"
        self._rate_limit_forced: bool = False
        self._heartbeat_ts: float = 0.0

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        self._subscribers.append(callback)

    def force_rate_limit(self, active: bool) -> None:
        self._rate_limit_forced = active

    def ingest_tick(self, tick: TickEvent, current_clock_sec: Optional[float] = None) -> Dict[str, Any]:
        if not isinstance(tick.ltp, (int, float)) or tick.ltp <= 0:
            raise ValueError(f"FAIL_CLOSED_GATE_INVALID_LTP: {tick.ltp}")

        self._last_ticks[tick.symbol] = tick
        self._heartbeat_ts = current_clock_sec if current_clock_sec is not None else time.time()
        self._market_status = "OPEN" if tick.is_market_open else "CLOSED"

        self._match_open_orders(tick)

        payload = self.get_ui_snapshot(tick.symbol, current_clock_sec=self._heartbeat_ts)
        for sub in self._subscribers:
            sub(payload)
        return payload

    def get_ui_snapshot(self, symbol: str, current_clock_sec: Optional[float] = None) -> Dict[str, Any]:
        if symbol not in self._last_ticks:
            raise KeyError(f"FAIL_CLOSED_NO_LTP_RECORDED: {symbol}")

        last_tick = self._last_ticks[symbol]
        now = current_clock_sec if current_clock_sec is not None else time.time()
        age_sec = max(0.0, now - self._heartbeat_ts)
        is_stale = (self._market_status == "OPEN") and (age_sec > self.stale_threshold_sec)

        return {
            "symbol": symbol,
            "market_status": self._market_status,
            "display_banner": "Market Closed" if self._market_status == "CLOSED" else "Market Live",
            "ltp": last_tick.ltp,
            "bid": last_tick.bid,
            "ask": last_tick.ask,
            "volume": last_tick.volume,
            "timestamp_ns": last_tick.timestamp_ns,
            "feed_stale": is_stale,
            "healthy_gate_pass": not is_stale,
        }

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: int,
        price: float = 0.0,
        current_clock_sec: Optional[float] = None,
    ) -> SimulatedOrder:
        if self._rate_limit_forced:
            order = SimulatedOrder(
                order_id=f"sim-{uuid.uuid4().hex[:8]}",
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                status="REJECTED",
                rejection_reason="HTTP_429_RATE_LIMIT",
            )
            self._orders[order.order_id] = order
            return order

        if symbol not in self._last_ticks:
            raise RuntimeError(f"FAIL_CLOSED_GATE_MISSING_QUOTE: {symbol}")

        snapshot = self.get_ui_snapshot(symbol, current_clock_sec=current_clock_sec)
        if not snapshot["healthy_gate_pass"]:
            order = SimulatedOrder(
                order_id=f"sim-{uuid.uuid4().hex[:8]}",
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                status="REJECTED",
                rejection_reason="FAIL_CLOSED_STALE_FEED",
            )
            self._orders[order.order_id] = order
            return order

        order = SimulatedOrder(
            order_id=f"sim-{uuid.uuid4().hex[:8]}",
            symbol=symbol,
            side=side.upper(),
            order_type=order_type.upper(),
            quantity=quantity,
            price=price,
        )
        self._orders[order.order_id] = order
        self._match_open_orders(self._last_ticks[symbol])
        return self._orders[order.order_id]

    def _match_open_orders(self, tick: TickEvent) -> None:
        if not tick.is_market_open:
            return
        for order in self._orders.values():
            if order.status != "PENDING" or order.symbol != tick.symbol:
                continue
            if order.order_type == "MARKET":
                order.status = "FILLED"
                order.filled_price = tick.ask if order.side == "BUY" else tick.bid
                order.filled_at_ns = tick.timestamp_ns
            elif order.order_type == "LIMIT":
                if order.side == "BUY" and tick.ask <= order.price:
                    order.status = "FILLED"
                    order.filled_price = min(order.price, tick.ask)
                    order.filled_at_ns = tick.timestamp_ns
                elif order.side == "SELL" and tick.bid >= order.price:
                    order.status = "FILLED"
                    order.filled_price = max(order.price, tick.bid)
                    order.filled_at_ns = tick.timestamp_ns
            elif order.order_type == "STOP":
                if order.side == "BUY" and tick.ltp >= order.price:
                    order.status = "FILLED"
                    order.filled_price = tick.ask
                    order.filled_at_ns = tick.timestamp_ns
                elif order.side == "SELL" and tick.ltp <= order.price:
                    order.status = "FILLED"
                    order.filled_price = tick.bid
                    order.filled_at_ns = tick.timestamp_ns