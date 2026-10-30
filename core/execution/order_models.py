"""
System3 Phase 233 - Virtual Order Models

Define structured Python models for planned orders and risk decisions.
"""

from dataclasses import dataclass


@dataclass
class PlannedOrder:
    """Model for a planned virtual order."""

    ts: str
    underlying: str
    strike: float
    option_type: str  # "CE" or "PE"
    side: str  # "BUY" or "SELL"
    expiry: str
    ltp: float
    final_score: float
    ai_score: float
    lots: int
    reason: str
    snapshot_id: int | None = None


@dataclass
class RiskDecision:
    """Model for risk check decision."""

    approved: bool
    adjusted_lots: int
    reason: str
    risk_flags: dict[str, str]
