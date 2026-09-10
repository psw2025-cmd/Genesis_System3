import os
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_PATHS = [
    os.path.join(ROOT_DIR, "config", ".env"),
    os.getenv("SYSTEM3_ENV_FILE", ""),
    os.path.join(ROOT_DIR, ".secrets", "dhan.env"),
]

for env_path in ENV_PATHS:
    if env_path and os.path.exists(env_path):
        load_dotenv(env_path, override=False)


def _local_vault_secret(key: str) -> str:
    """Load a secret from the approved local Windows secure vault."""
    try:
        from core.security.windows_secret_vault import get_secret

        val = get_secret(key)
        return str(val).strip().lstrip("\ufeff") if val else ""
    except Exception:
        return ""


def _local_access_token() -> str:
    token = _local_vault_secret("DHAN_ACCESS_TOKEN")
    if token:
        return token
    return os.getenv("DHAN_ACCESS_TOKEN", "").strip().lstrip("\ufeff")


def get_dhan_credentials():
    """Return local-only Dhan credentials for read-only/analyzer/PAPER operations."""
    client_id = _local_vault_secret("DHAN_CLIENT_ID") or os.getenv("DHAN_CLIENT_ID", "").strip().lstrip("\ufeff")
    return {"client_id": client_id, "access_token": _local_access_token()}
