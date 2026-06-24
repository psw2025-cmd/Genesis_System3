"""
Entry/Exit Engine - Entry rules, dynamic SL/Target, trailing SL
"""

from .entry_exit_rules import (
    compute_dynamic_sl_tp,
    compute_entry_signals,
    compute_exit_signals,
)

__all__ = ["compute_entry_signals", "compute_exit_signals", "compute_dynamic_sl_tp"]
