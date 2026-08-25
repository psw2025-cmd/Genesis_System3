#!/usr/bin/env python3
"""RETIRED — Render.com memory/OOM audit.

Memory work belongs on Cloud Run `genesis-system3-web` and worker Jobs.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools._render_hosting_retired import write_retired_report

OUT = ROOT / "reports" / "latest" / "render_memory_stabilization"


def main() -> int:
    return write_retired_report(OUT, extra={"tool": "render_memory_stabilization_audit"})


if __name__ == "__main__":
    raise SystemExit(main())
