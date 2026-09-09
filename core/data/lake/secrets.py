"""Local-only secret loading for the authorized System3 laptop runtime.

Values are read from the process environment after approved local environment
files/vault mapping have been loaded. Missing values fail closed. This module
never logs credential values.
"""
from __future__ import annotations

import os
from pathlib import Path


class SecretNotFoundError(RuntimeError):
    pass


def load_secret(env_var: str, secret_id: str | None = None, *, version: str = "latest") -> str:
    del secret_id, version
    value = os.getenv(env_var, "").strip().lstrip("\ufeff")
    if not value:
        raise SecretNotFoundError(f"{env_var} is not configured in the approved local runtime")
    return value


def data_lake_root() -> Path:
    configured = os.getenv("SYSTEM3_DATA_LAKE_ROOT", "").strip()
    return Path(configured) if configured else Path("storage") / "market_data_lake"
