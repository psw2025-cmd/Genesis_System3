#!/usr/bin/env python3
"""RETIRED fallback for the GitHub/Render.com tracker.

Render.com hosting is retired. Writes the same retired Cloud Run report.
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
    return write_retired_report(OUT, extra={"tracker": "write_github_render_tracker_fallback"})


if __name__ == "__main__":
    raise SystemExit(main())
