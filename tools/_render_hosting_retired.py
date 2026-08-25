#!/usr/bin/env python3
"""Render.com hosting is retired. GCP Cloud Run is the only production host.

Shared fail-closed helper for leftover Render-named tools. Historical report
paths may still exist; they are not current deploy authority.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
GCP_UI = "https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/"
RETIRED_MSG = (
    "Render.com hosting is retired. Production is GCP Cloud Run only: "
    "project system3-openalgo-safe, service genesis-system3-web."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def render_yaml_exists() -> bool:
    return (ROOT / "render.yaml").exists()


def retired_payload(extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "generated_utc": utc_now(),
        "status": "FAIL" if render_yaml_exists() else "PASS",
        "retired": True,
        "hosting_authority": "gcp-cloud-run",
        "message": RETIRED_MSG,
        "production_ui": GCP_UI,
        "render_yaml_exists": render_yaml_exists(),
        "live_trading_enabled": False,
        "system3_live_trading_allowed": False,
        "order_routes_called": False,
        "secrets_printed": False,
        "todo": [],
        "todo_count": 0,
        "github_failed_count": 0,
        "render_failed_count": 0,
        "failed_workflows": [],
        "render_failures": [],
        "production_grade_claim_allowed": False,
        "report_only_no_self_failure_storm": True,
    }
    if extra:
        payload.update(extra)
    if render_yaml_exists():
        payload["status"] = "FAIL"
        payload["todo"] = ["render.yaml is present; delete it. Cloud Run is the only host."]
        payload["todo_count"] = 1
        payload["render_failed_count"] = 1
    return payload


def write_retired_report(out_dir: Path, extra: Dict[str, Any] | None = None) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = retired_payload(extra)
    (out_dir / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (out_dir / "summary.md").write_text(
        "# RETIRED — Render.com hosting\n\n"
        f"{RETIRED_MSG}\n\n"
        f"Status: **{payload['status']}**\n\n"
        f"Production UI: {GCP_UI}\n",
        encoding="utf-8",
    )
    return 2 if render_yaml_exists() else 0
