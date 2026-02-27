"""
System3 GENI Ultra Master Agent

GENI (Genesis Intelligence) - High-level orchestration and validation layer
for System3 Ultra operations.

All operations are SAFE MODE - no real trades, no auto-promotion, read-only orchestration.
"""

from pathlib import Path

__version__ = "1.0.0"
__all__ = [
    "geni_config",
    "geni_state",
    "geni_tasks",
    "geni_validator",
    "geni_orchestrator",
]
