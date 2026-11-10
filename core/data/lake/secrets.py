"""Container-ready credential loading: environment variable first, GCP Secret
Manager fallback. Mirrors the pattern in core/brokers/dhan/cloud_token_provider.py
so this module behaves the same way whether it runs on a laptop (env vars) or
in Cloud Run (Secret Manager, no plaintext secrets baked into the image).

Never logs or returns raw secret values except as the function's return value.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Callable

_CLIENT_FACTORY: Callable[[], object] | None = None


def _project_id() -> str:
    return (
        os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCP_PROJECT")
        or os.getenv("SYSTEM3_FIRESTORE_PROJECT")
        or "system3-openalgo-safe"
    )


def _secret_manager_client():
    if _CLIENT_FACTORY is not None:
        return _CLIENT_FACTORY()
    from google.cloud import secretmanager

    return secretmanager.SecretManagerServiceClient()


def set_client_factory(factory: Callable[[], object] | None) -> None:
    """Test-only hook to inject a fake Secret Manager client."""
    global _CLIENT_FACTORY
    _CLIENT_FACTORY = factory


class SecretNotFoundError(RuntimeError):
    pass


def load_secret(env_var: str, secret_id: str | None = None, *, version: str = "latest") -> str:
    """Return the secret value for `env_var`, preferring the environment.

    Resolution order:
    1. `os.environ[env_var]` if set and non-empty (local dev, CI, or an
       operator-provided override in any environment).
    2. GCP Secret Manager, project `_project_id()`, secret id `secret_id`
       (defaults to the lowercase, dash-cased form of `env_var`), version
       `version`.

    Raises SecretNotFoundError if neither source has a value - callers must
    fail closed, never substitute a placeholder credential.
    """
    env_val = os.getenv(env_var, "").strip()
    if env_val:
        return env_val

    resolved_secret_id = secret_id or env_var.lower().replace("_", "-")
    try:
        client = _secret_manager_client()
        name = f"projects/{_project_id()}/secrets/{resolved_secret_id}/versions/{version}"
        response = client.access_secret_version(request={"name": name})
        value = response.payload.data.decode("utf-8").strip()
    except Exception as exc:  # noqa: BLE001 - surfaced as SecretNotFoundError below
        raise SecretNotFoundError(
            f"{env_var} not set and Secret Manager lookup for '{resolved_secret_id}' failed: {exc}"
        ) from exc

    if not value:
        raise SecretNotFoundError(f"{env_var} not set and Secret Manager returned an empty value")
    return value


@lru_cache(maxsize=1)
def gcs_bucket_name() -> str:
    return os.getenv("MARKET_DATA_LAKE_BUCKET", "").strip() or f"{_project_id()}-market-data-lake"
