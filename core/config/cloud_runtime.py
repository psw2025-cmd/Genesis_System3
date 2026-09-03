"""Canonical runtime defaults for Genesis System3."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_PATH = _ROOT / "config" / "cloud_runtime.json"

_DEFAULTS: Dict[str, Any] = {
    "deploy_target": "local-laptop",
    "cloud_provider": "local",
    "region": "",
    "project_id": "",
    "service_name": "local-laptop",
    "public_base_url": "http://127.0.0.1:8000",
    "ui_path": "/ui",
}
_CLOUD_DEFAULT_PUBLIC_BASE_URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app"


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
    """True only when the process is actually running on Cloud Run."""
    return bool(os.environ.get("K_SERVICE", "").strip())


def _cloud_permanent() -> bool:
    """Runtime truth must come from the actual process location, not stale env/config."""
    return is_cloud_runtime()


def _first_loopback_env(*names: str) -> str:
    """Return the first explicitly configured loopback URL, ignoring stale remote URLs."""
    for name in names:
        value = (os.environ.get(name) or "").strip().rstrip("/")
        if value and _is_loopback_url(value):
            return value
    return ""


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
    """Return truthful public metadata for the current runtime.

    Local-laptop mode is authoritative whenever this process is not actually on
    Cloud Run.  Stale machine/user environment variables left over from the GCP
    era must therefore never make a localhost process advertise a Cloud Run URL.
    """
    if not is_cloud_runtime():
        local_env = _first_loopback_env(
            "SYSTEM3_API_BASE",
            "DASHBOARD_BASE_URL",
            "SYSTEM3_PUBLIC_BACKEND_URL",
            "PUBLIC_BACKEND_URL",
        )
        if local_env:
            return local_env
        canonical = _canonical_public_base_url()
        return canonical if _is_loopback_url(canonical) else str(_DEFAULTS["public_base_url"])

    env = (
        os.environ.get("PUBLIC_BACKEND_URL")
        or os.environ.get("SYSTEM3_PUBLIC_BACKEND_URL")
        or os.environ.get("SYSTEM3_API_BASE")
        or os.environ.get("DASHBOARD_BASE_URL")
        or ""
    ).strip().rstrip("/")
    if env and not _is_loopback_url(env):
        return env
    canonical = _canonical_public_base_url()
    if canonical and not _is_loopback_url(canonical):
        return canonical
    return _CLOUD_DEFAULT_PUBLIC_BASE_URL


def public_dashboard_url() -> str:
    env = (os.environ.get("PUBLIC_DASHBOARD_URL") or "").strip().rstrip("/")
    if is_cloud_runtime() and env and not _is_loopback_url(env):
        return env
    if not is_cloud_runtime() and env and _is_loopback_url(env):
        return env
    return f"{public_base_url()}{public_ui_path()}"


def deploy_target() -> str:
    if not is_cloud_runtime():
        return "local-laptop"
    return (
        os.environ.get("SYSTEM3_DEPLOY_TARGET")
        or str(load_cloud_runtime().get("deploy_target") or "local-laptop")
    ).strip()
