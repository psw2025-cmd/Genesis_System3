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


def _dynamic_cloud_token() -> str:
    """Load the newest GCP Secret Manager token without exposing it."""
    try:
        from core.brokers.dhan.cloud_token_provider import get_access_token

        return get_access_token(reason="env_loader")
    except Exception:
        return os.getenv("DHAN_ACCESS_TOKEN", "").strip().lstrip("\ufeff")


def get_dhan_credentials():
    """Return Dhan credentials for read-only/analyzer-only operations."""
    return {
        "client_id": os.getenv("DHAN_CLIENT_ID", "").strip().lstrip("\ufeff"),
        "access_token": _dynamic_cloud_token(),
    }
