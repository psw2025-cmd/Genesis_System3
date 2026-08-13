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


def _canonical_public_base_url() -> str:
    return str(load_cloud_runtime().get("public_base_url") or _DEFAULTS["public_base_url"]).rstrip("/")


def public_ui_path() -> str:
    path = str(load_cloud_runtime().get("ui_path") or _DEFAULTS["ui_path"] or "/ui").strip()
    if not path.startswith("/"):
        path = "/" + path
    return path.rstrip("/") or "/ui"


def _is_loopback_url(url: str) -> bool:
    lowered = (url or "").strip().lower()
    return "127.0.0.1" in lowered or "localhost" in lowered


def is_cloud_runtime() -> bool:
    """True only for this running process, not for the checked-in production target."""
    mode = os.environ.get("CLOUD_MODE", "").strip().lower()
    target = os.environ.get("SYSTEM3_DEPLOY_TARGET", "").strip().lower()
    return (
        mode in {"1", "true", "yes", "on"}
        or "cloud-run" in target
        or bool(os.environ.get("K_SERVICE", "").strip())
    )


def _cloud_permanent() -> bool:
    return is_cloud_runtime()


def public_cors_origins() -> list[str]:
    origins: list[str] = []
    seen: set[str] = set()
    cfg = load_cloud_runtime()
    candidates = [public_base_url(), *list(cfg.get("public_origin_aliases") or [])]
    for raw in candidates:
        origin = str(raw or "").strip().rstrip("/")
        if not origin or origin in seen or _is_loopback_url(origin):
            continue
        seen.add(origin)
        origins.append(origin)
    return origins


def public_base_url() -> str:
    env = (
        os.environ.get("PUBLIC_BACKEND_URL")
        or os.environ.get("SYSTEM3_PUBLIC_BACKEND_URL")
        or os.environ.get("SYSTEM3_API_BASE")
        or os.environ.get("DASHBOARD_BASE_URL")
        or ""
    ).strip().rstrip("/")
    if env and not (_is_loopback_url(env) and _cloud_permanent()):
        return env
    if _cloud_permanent() or not env:
        return _canonical_public_base_url()
    return env


def public_dashboard_url() -> str:
    env = (os.environ.get("PUBLIC_DASHBOARD_URL") or "").strip().rstrip("/")
    if env and not (_is_loopback_url(env) and _cloud_permanent()):
        return env
    return f"{public_base_url()}{public_ui_path()}"


def deploy_target() -> str:
    return (
        os.environ.get("SYSTEM3_DEPLOY_TARGET")
        or str(load_cloud_runtime().get("deploy_target") or "gcp-cloud-run")
    ).strip()
