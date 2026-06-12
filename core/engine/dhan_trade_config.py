from dataclasses import dataclass


@dataclass
class TradeThresholds:
    # Minimum model confidence to even consider a trade
    min_confidence: float = 0.80

    # Minimum |score| (expected short-term move) to consider a trade
    # (this is your "edge" strength)
    min_abs_score: float = 0.30

    # Max % distance from ATM allowed (e.g. ±1% of spot)
    max_atm_dist_pct: float = 1.0

    # Risk parameters (these are per-trade default values, in % of option premium)
    target_pct: float = 10.0  # target move in option premium
    stoploss_pct: float = 5.0  # stoploss in option premium


# Global default thresholds object
DEFAULT_THRESHOLDS = TradeThresholds()
