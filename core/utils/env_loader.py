import os
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_PATHS = [
    os.path.join(ROOT_DIR, "config", ".env"),
    os.getenv("SYSTEM3_ENV_FILE", ""),
    "/etc/secrets/.env",
    os.path.join(ROOT_DIR, ".secrets", "dhan.env"),
]

for env_path in ENV_PATHS:
    if env_path and os.path.exists(env_path):
        load_dotenv(env_path, override=False)


def _local_vault_secret(key: str) -> str:
    """Load a secret from local Windows DPAPI vault if available."""
    try:
        from core.security.windows_secret_vault import get_secret
        val = get_secret(key)
        return str(val).strip().lstrip("\ufeff") if val else ""
    except Exception:
        return ""


def _dynamic_cloud_token() -> str:
    """Load Dhan token with local-laptop authority and cloud fallback only on real Cloud Run."""
    # 1. Canonical local secure vault target.
    local_token = _local_vault_secret("DHAN_ACCESS_TOKEN")
    if local_token:
        return local_token

    # 2. Plain environment fallback for an explicitly configured local session.
    env_token = os.getenv("DHAN_ACCESS_TOKEN", "").strip().lstrip("\ufeff")
    if env_token:
        return env_token

    # 3. Legacy Cloud Secret Manager is reachable only when the process is
    # actually on Cloud Run.  Stale CLOUD_MODE=0/1 values on a Windows laptop
    # must never redirect broker credential discovery back to GCP.
    if bool(os.getenv("K_SERVICE", "").strip()):
        try:
            from core.brokers.dhan.cloud_token_provider import get_access_token
            return get_access_token(reason="env_loader")
        except Exception:
            pass

    return ""


def get_dhan_credentials():
    """Return Dhan credentials for read-only/analyzer-only operations."""
    client_id = _local_vault_secret("DHAN_CLIENT_ID") or os.getenv("DHAN_CLIENT_ID", "").strip().lstrip("\ufeff")
    return {
        "client_id": client_id,
        "access_token": _dynamic_cloud_token(),
    }
