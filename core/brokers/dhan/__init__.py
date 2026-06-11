# Dhan broker adapter — READ-ONLY / ANALYZER-ONLY
# No order placement. No live trading.
from core.brokers.dhan.dhan_readonly import DhanReadOnly

__all__ = ["DhanReadOnly"]
