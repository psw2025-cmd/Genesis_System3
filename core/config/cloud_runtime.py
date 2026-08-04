"""Canonical Google Cloud Run runtime defaults for Genesis System3."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_PATH = _ROOT / "config" / "cloud_runtime.json"

_DEFAULTS: Dict[str, Any] = {
    "deploy_target": "gcp-cloud-run",
    "cloud_provider": "google_cloud",
    "region": "asia-south1",
    "project_id": "system3-openalgo-safe",
    "service_name": "genesis-system3-web",
    "public_base_url": "https://genesis-system3-web-doq2wplepa-el.a.run.app",
    "ui_path": "/ui",
}


def load_cloud_runtime() -> Dict[str, Any]:
    data = dict(_DEFAULTS)
    try:
        if _CONFIG_PATH.exists():
            loaded = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data.update({k: v for k, v in loaded.items() if not str(k).startswith("_")})
    except Exception:
        pass
    return data


def public_base_url() -> str:
    env = (
        os.environ.get("SYSTEM3_PUBLIC_BACKEND_URL")
        or os.environ.get("SYSTEM3_API_BASE")
        or os.environ.get("DASHBOARD_BASE_URL")
        or ""
    ).strip().rstrip("/")
    if env:
        return env
    return str(load_cloud_runtime().get("public_base_url") or _DEFAULTS["public_base_url"]).rstrip("/")


def deploy_target() -> str:
    return (
        os.environ.get("SYSTEM3_DEPLOY_TARGET")
        or str(load_cloud_runtime().get("deploy_target") or "gcp-cloud-run")
    ).strip()
