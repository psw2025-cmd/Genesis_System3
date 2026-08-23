#!/usr/bin/env python3
"""RETIRED — Render.com worker preflight.

Use Cloud Run worker Job env and `/api/scheduler/health` on the GCP service.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools._render_hosting_retired import write_retired_report

OUT = ROOT / "reports" / "latest" / "render_worker_preflight"


def main() -> int:
    return write_retired_report(OUT, extra={"tool": "system3_render_worker_preflight"})


if __name__ == "__main__":
    raise SystemExit(main())
