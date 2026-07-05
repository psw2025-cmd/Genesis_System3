"""
Breakout Model - H-L breakouts, CPR, ORB signals, support/resistance breaks
"""

from .breakout_detector import compute_cpr_levels, compute_orb_signals, detect_breakouts

__all__ = ["detect_breakouts", "compute_cpr_levels", "compute_orb_signals"]
