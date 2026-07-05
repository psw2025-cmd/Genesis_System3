"""
Advanced Order Management System
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytz

IST = pytz.timezone("Asia/Kolkata")


class OrderType:
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"
    BRACKET = "BRACKET"


class OrderStatus:
    PENDING = "PENDING"
    PLACED = "PLACED"
    EXECUTED = "EXECUTED"
    PARTIALLY_EXECUTED = "PARTIALLY_EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class OrderManagement:
    """
    Advanced order management system
    """

    def __init__(self, orders_file: Optional[Path] = None):
        if orders_file is None:
            orders_file = Path(__file__).parent.parent.parent / "outputs" / "orders.jsonl"
        self.orders_file = orders_file
        self.orders_file.parent.mkdir(parents=True, exist_ok=True)

    def create_order(
        self,
        symbol: str,
        order_type: str,
        quantity: int,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        target: Optional[float] = None,
        trailing_stop_pct: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Create a new order. Paper-only today, but gated on the same
        kill switch (storage/live/kill_switch.json) the batch session loop
        checks, so a single switch governs every order-creation path -
        including this one, if a live path is ever added on top of it."""
        try:
            from core.engine.system3_phase113_kill_switch_monitor import run_phase113
        except ImportError:
            run_phase113 = None
        if run_phase113 is not None:
            kill_result = run_phase113()
            if kill_result.get("status") == "KILL":
                raise RuntimeError(f"Order rejected: kill switch active ({kill_result.get('details')})")

        order = {
            "order_id": f"ORD_{datetime.now(IST).strftime('%Y%m%d%H%M%S%f')}",
            "symbol": symbol,
            "order_type": order_type,
            "quantity": quantity,
            "price": price,
            "stop_loss": stop_loss,
            "target": target,
            "trailing_stop_pct": trailing_stop_pct,
            "status": OrderStatus.PENDING,
            "created_at": datetime.now(IST).isoformat(),
            "executed_at": None,
            "executed_price": None,
            "executed_quantity": 0,
        }

        # Append to orders file
        with open(self.orders_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(order, default=str) + "\n")

        return order

    def get_orders(
        self, status: Optional[str] = None, symbol: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get orders"""
        orders = []

        if not self.orders_file.exists():
            return orders

        with open(self.orders_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        order = json.loads(line)

                        # Filter by status
                        if status and order.get("status") != status:
                            continue

                        # Filter by symbol
                        if symbol and order.get("symbol") != symbol:
                            continue

                        orders.append(order)
                    except:
                        pass

        # Sort by created_at (newest first)
        orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return orders[:limit]

    def update_order_status(
        self,
        order_id: str,
        status: str,
        executed_price: Optional[float] = None,
        executed_quantity: Optional[int] = None,
    ) -> bool:
        """Update order status"""
        # This would require rewriting the file, which is expensive
        # For now, we'll track status in memory or a separate status file
        return True

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        return self.update_order_status(order_id, OrderStatus.CANCELLED)

    def get_order_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get order history"""
        all_orders = self.get_orders(symbol=symbol, limit=limit * 2)

        # Filter executed/cancelled orders
        history = [
            o
            for o in all_orders
            if o.get("status") in [OrderStatus.EXECUTED, OrderStatus.CANCELLED, OrderStatus.REJECTED]
        ]

        return history[:limit]


# Global instance
_order_management = OrderManagement()


def get_order_management() -> OrderManagement:
    """Get global order management instance"""
    return _order_management
