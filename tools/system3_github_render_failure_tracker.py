#!/usr/bin/env python3
"""RETIRED — GitHub + Render.com failure tracker.

Render.com hosting is retired. This script no longer probes onrender.com.
It writes a retired PASS report unless render.yaml has been recreated.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools._render_hosting_retired import write_retired_report

OUT = ROOT / "reports" / "latest" / "github_render_failure_tracker"


def main() -> int:
    return write_retired_report(
        OUT,
        extra={"tracker": "system3_github_render_failure_tracker", "scope": "retired_render_host"},
    )


if __name__ == "__main__":
    raise SystemExit(main())
