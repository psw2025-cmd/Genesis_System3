"""
Market Result Validator (src/ranking) — shim to canonical src/validation version.

The canonical implementation lives at src/validation/market_result_validator.py.
This shim re-exports everything from there so any callers of src/ranking/
continue to work without change.

Field name note: canonical uses 'rank_correlation_spearman';
older JSON files on disk may use 'spearman_correlation' — both mean the same thing.
"""

from src.validation.market_result_validator import MarketResultValidator  # noqa: F401

__all__ = ["MarketResultValidator"]
