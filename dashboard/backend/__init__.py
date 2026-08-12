"""Genesis System3 backend package boundary.

The dashboard is permanently public/read-only. Retired browser/dashboard
credential settings are removed before *any* backend submodule can import them,
including direct imports of the large legacy app module. Mutation authority is
separate and remains fail-closed.
"""
from __future__ import annotations

import os


RETIRED_DASHBOARD_ENV = (
    "REQUIRE_" + "API_KEY",
    "API_" + "KEY",
    "DASHBOARD_" + "API_KEY",
    "ENABLE_DASHBOARD_" + "AUTH",
    "DASHBOARD_SESSION_" + "MAX_AGE",
)


def scrub_retired_dashboard_auth_environment() -> tuple[str, ...]:
    """Remove obsolete dashboard credential/session inputs from this process."""
    removed = []
    for name in RETIRED_DASHBOARD_ENV:
        if name in os.environ:
            os.environ.pop(name, None)
            removed.append(name)
    return tuple(removed)


# Execute before dashboard.backend.app or any sibling module is imported.
scrub_retired_dashboard_auth_environment()
