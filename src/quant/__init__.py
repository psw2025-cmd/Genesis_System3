"""Fail-closed quantitative research evaluation for Genesis System3."""

from .alpha_truth import AlphaTargets, evaluate_alpha_evidence
from .factor_decay import DecayPolicy, evaluate_decay

__all__ = ["AlphaTargets", "DecayPolicy", "evaluate_alpha_evidence", "evaluate_decay"]
