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


def get_dhan_token():
    try:
        from google.cloud import secretmanager
        import jwt
        import datetime

        client = secretmanager.SecretManagerServiceClient()
        name = "projects/802404398783/secrets/dhan-access-token/versions/latest"
        resp = client.access_secret_version(request={"name": name})
        token = resp.payload.data.decode("UTF-8").strip()
        ver = resp.name.split("/")[-1]  # 335
        # Decode expiry from JWT
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = datetime.datetime.fromtimestamp(payload["exp"], tz=datetime.timezone.utc)
        hours = (exp - datetime.datetime.now(tz=datetime.timezone.utc)).total_seconds() / 3600
        return token, f"GCP_SECRET_MANAGER_V{ver}", "GCP_TOTP_ROTATE", hours, exp, False
    except Exception as e:
        # fallback local
        local_token = os.getenv("DHAN_ACCESS_TOKEN", "").strip().lstrip("\ufeff")
        if not local_token:
            local_token = _local_vault_secret("DHAN_ACCESS_TOKEN")
        hours = 0.0
        exp = None
        if local_token:
            try:
                import jwt
                import datetime

                payload = jwt.decode(local_token, options={"verify_signature": False})
                exp = datetime.datetime.fromtimestamp(payload["exp"], tz=datetime.timezone.utc)
                hours = (exp - datetime.datetime.now(tz=datetime.timezone.utc)).total_seconds() / 3600
            except Exception:
                pass
        return local_token, "LOCAL_JWT_SESSION_FALLBACK", "DHAN_LOCAL_ROTATE_FALLBACK", hours, exp, True


def _dynamic_cloud_token() -> str:
    """Load Dhan token with GCP Secret Manager dynamic authority or local fallback."""
    token, _, _, _, _, is_fallback = get_dhan_token()
    if token and not is_fallback:
        return token

    # 1. Canonical local secure vault target.
    local_token = _local_vault_secret("DHAN_ACCESS_TOKEN")
    if local_token:
        return local_token

    # 2. Plain environment fallback for an explicitly configured local session.
    env_token = os.getenv("DHAN_ACCESS_TOKEN", "").strip().lstrip("\ufeff")
    if env_token:
        return env_token

    return token or ""


def get_dhan_credentials():
    """Return Dhan credentials for read-only/analyzer-only operations."""
    client_id = _local_vault_secret("DHAN_CLIENT_ID") or os.getenv("DHAN_CLIENT_ID", "").strip().lstrip("\ufeff")
    return {
        "client_id": client_id,
        "access_token": _dynamic_cloud_token(),
    }
