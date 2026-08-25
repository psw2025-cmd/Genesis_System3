#!/usr/bin/env python3
"""RETIRED — Render.com deploy-commit proof.

Use Cloud Run `/api/deploy/info` (`DEPLOY_GIT_SHA`, `K_SERVICE`) instead.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools._render_hosting_retired import write_retired_report

OUT = ROOT / "reports" / "latest" / "render_deploy_commit_proof"


def main() -> int:
    return write_retired_report(OUT, extra={"tool": "render_deploy_commit_proof"})


if __name__ == "__main__":
    raise SystemExit(main())
