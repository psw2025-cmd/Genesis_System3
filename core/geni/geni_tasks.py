"""
System3 GENI - Task Registry

Defines high-level tasks that GENI can orchestrate.
Tasks reference existing scripts and validators.
"""

from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path

from .geni_config import (
    PROJECT_ROOT,
    ULTRA_DAILY_RUNNER,
    ULTRA_VALIDATION,
    FULL_VERIFICATION,
    SYSTEM3_ULTRA_ENTRY,
)


@dataclass
class GeniTask:
    """Task descriptor."""

    name: str
    description: str
    command_line: List[str]
    expected_logs: List[str]
    estimated_runtime_sec: int


# Task registry
_TASKS: dict[str, GeniTask] = {
    "full_validation": GeniTask(
        name="full_validation",
        description="Run full System3 validation suite",
        command_line=["python", str(FULL_VERIFICATION)],
        expected_logs=[],
        estimated_runtime_sec=120,
    ),
    "quick_validation": GeniTask(
        name="quick_validation",
        description="Run quick System3 Ultra validation",
        command_line=["python", str(ULTRA_VALIDATION)],
        expected_logs=[],
        estimated_runtime_sec=30,
    ),
    "run_daily_ultra": GeniTask(
        name="run_daily_ultra",
        description="Run daily Ultra automation cycle (DRY-RUN)",
        command_line=["python", str(ULTRA_DAILY_RUNNER)],
        expected_logs=[],
        estimated_runtime_sec=60,
    ),
    "run_ultra_all_logged": GeniTask(
        name="run_ultra_all_logged",
        description="Run all Ultra operations with logging",
        command_line=["python", str(SYSTEM3_ULTRA_ENTRY)],
        expected_logs=[],
        estimated_runtime_sec=300,
    ),
    "run_status_check": GeniTask(
        name="run_status_check",
        description="Check System3 status and health",
        command_line=["python", str(SYSTEM3_ULTRA_ENTRY)],
        expected_logs=[],
        estimated_runtime_sec=10,
    ),
    "run_ultra_panel_test": GeniTask(
        name="run_ultra_panel_test",
        description="Run Ultra control panel test suite",
        command_line=["python", str(ULTRA_VALIDATION)],
        expected_logs=[],
        estimated_runtime_sec=60,
    ),
}


def get_all_tasks() -> dict[str, GeniTask]:
    """
    Get all registered tasks.

    Returns:
        Dictionary mapping task names to GeniTask objects
    """
    return _TASKS.copy()


def get_task(name: str) -> Optional[GeniTask]:
    """
    Get a specific task by name.

    Args:
        name: Task name

    Returns:
        GeniTask if found, None otherwise
    """
    return _TASKS.get(name)
