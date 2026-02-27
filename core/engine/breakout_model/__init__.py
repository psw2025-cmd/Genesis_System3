"""
Breakout Model - H-L breakouts, CPR, ORB signals, support/resistance breaks
"""

from .breakout_detector import detect_breakouts, compute_cpr_levels, compute_orb_signals

__all__ = ["detect_breakouts", "compute_cpr_levels", "compute_orb_signals"]
