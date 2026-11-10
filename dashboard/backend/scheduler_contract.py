"""Single source of truth for Cloud Scheduler + Cloud Run job control-plane contracts.

Coverage counts, identity, cadence grace, and expected job targets must all derive
from this module so Auto Deploy proofs and live health cannot drift apart when a
lane is added (validate-daily taught that lesson).
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Tuple

# name -> (state, target_job_when_enabled, schedule, time_zone, max_age_hours|None)
SchedulerContractRow = Tuple[str, Optional[str], str, str, Optional[float]]

EXPECTED_SCHEDULER_CONTRACT: Dict[str, SchedulerContractRow] = {
    "genesis-system3-forecast-daily": ("ENABLED", "genesis-system3-forecast", "0 4 * * MON-FRI", "UTC", 98),
    "genesis-system3-rank-daily": ("ENABLED", "genesis-system3-rank", "45 3 * * MON-FRI", "UTC", 98),
    "genesis-system3-validate-daily": ("ENABLED", "genesis-system3-validate", "5 10 * * MON-FRI", "UTC", 98),
    "genesis-system3-signals-daily": ("ENABLED", "genesis-system3-signals", "15 13 * * MON-FRI", "UTC", 98),
    # */5 is the live trigger/check cadence (Asia/Kolkata). Remint cooldown stays
    # independent of this Scheduler expression. Do not change live Scheduler here.
    "genesis-system3-dhan-token-rotate-daily": ("ENABLED", "genesis-system3-dhan-token-rotate", "*/5 * * * *", "Asia/Kolkata", 26),
    "genesis-system3-forecast-schedule": ("PAUSED", None, "0 4,5,6,7,8,9 * * 1-5", "UTC", None),
    "genesis-system3-rank-schedule": ("PAUSED", None, "50 3 * * 1-5", "UTC", None),
    "genesis-system3-signals-schedule": ("PAUSED", None, "0 10 * * 1-5", "UTC", None),
    "genesis-system3-scheduler-collector-every-minute": (
        "ENABLED",
        "genesis-system3-scheduler-collector",
        "* * * * *",
        "UTC",
        1,
    ),
}

COLLECTOR_SCHEDULER_NAME = "genesis-system3-scheduler-collector-every-minute"
BUSINESS_LANE_JOBS = ("rank", "forecast", "validate", "signals")


def expected_job_targets() -> list[str]:
    return sorted({target for state, target, *_ in EXPECTED_SCHEDULER_CONTRACT.values() if state == "ENABLED" and target})


def expected_scheduler_states() -> Dict[str, Tuple[str, Optional[str]]]:
    """Minimal (state, target) map used by the collector identity checks."""
    out: Dict[str, Tuple[str, Optional[str]]] = {}
    for name, (state, target, *_rest) in EXPECTED_SCHEDULER_CONTRACT.items():
        out[name] = (state, target if state == "ENABLED" else target)
    return out


def coverage_expectations() -> Dict[str, int]:
    expected_total = len(EXPECTED_SCHEDULER_CONTRACT)
    expected_enabled = sum(1 for row in EXPECTED_SCHEDULER_CONTRACT.values() if row[0] == "ENABLED")
    expected_paused = sum(1 for row in EXPECTED_SCHEDULER_CONTRACT.values() if row[0] == "PAUSED")
    expected_control = 1
    expected_workload = expected_total - expected_control
    return {
        "expected_total": expected_total,
        "expected_workload": expected_workload,
        "expected_control": expected_control,
        "expected_enabled": expected_enabled,
        "expected_paused": expected_paused,
    }


def coverage_snapshot(resources: list[Mapping[str, Any]]) -> Dict[str, Any]:
    """Derive actual + expected coverage from live resource facts + SSOT."""
    expected = coverage_expectations()
    enabled = [row for row in resources if row.get("state") == "ENABLED"]
    paused = [row for row in resources if row.get("state") == "PAUSED"]
    workload = [row for row in resources if row.get("name") != COLLECTOR_SCHEDULER_NAME]
    control = [row for row in resources if row.get("name") == COLLECTOR_SCHEDULER_NAME]
    actual = {
        "workload": len(workload),
        "control": len(control),
        "total": len(resources),
        "enabled": len(enabled),
        "paused": len(paused),
    }
    matched = (
        actual["total"] == expected["expected_total"]
        and actual["workload"] == expected["expected_workload"]
        and actual["control"] == expected["expected_control"]
        and actual["enabled"] == expected["expected_enabled"]
        and actual["paused"] == expected["expected_paused"]
    )
    return {**actual, **expected, "contract_matched": matched}
