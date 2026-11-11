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


def _parse_jwt_hours_exp(token: str):
    import datetime
    exp = None
    hours = None
    if not token:
        return None, None
    try:
        import jwt
        payload = jwt.decode(token, options={"verify_signature": False})
        if "exp" in payload:
            exp = datetime.datetime.fromtimestamp(payload["exp"], tz=datetime.timezone.utc)
    except Exception:
        pass
    if exp is None:
        try:
            import base64, json
            parts = token.split(".")
            if len(parts) >= 2:
                body = parts[1] + "=" * (-len(parts[1]) % 4)
                payload = json.loads(base64.urlsafe_b64decode(body.encode("ascii")))
                exp_val = payload.get("exp")
                if exp_val:
                    exp = datetime.datetime.fromtimestamp(float(exp_val), tz=datetime.timezone.utc)
        except Exception:
            pass
    if exp:
        hours = (exp - datetime.datetime.now(tz=datetime.timezone.utc)).total_seconds() / 3600.0
    return hours, exp


def get_dhan_token(force_refresh: bool = False, min_hours: float | None = None):
    """Retrieve authoritative Dhan access token with automatic self-healing renewal."""
    token = ""
    source = "UNKNOWN"
    provider = "DHAN_ROTATE"
    hours = None
    exp = None
    is_fallback = True

    # 1. Try GCP Secret Manager if enabled/available
    try:
        from google.cloud import secretmanager
        project_num = os.getenv("GCP_PROJECT_NUMBER", "802404398783")
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_num}/secrets/dhan-access-token/versions/latest"
        resp = client.access_secret_version(request={"name": name})
        token = resp.payload.data.decode("UTF-8").strip()
        ver = resp.name.split("/")[-1]
        source = f"GCP_SECRET_MANAGER_V{ver}"
        provider = "GCP_TOTP_ROTATE"
        is_fallback = False
        hours, exp = _parse_jwt_hours_exp(token)
    except Exception:
        # 2. Local fallback
        token = os.getenv("DHAN_ACCESS_TOKEN", "").strip().lstrip("\ufeff")
        if not token:
            token = _local_vault_secret("DHAN_ACCESS_TOKEN")
        source = "LOCAL_JWT_SESSION_FALLBACK"
        provider = "DHAN_LOCAL_ROTATE_FALLBACK"
        is_fallback = True
        hours, exp = _parse_jwt_hours_exp(token)

    # 3. Auto-renewal trigger:
    # If token is missing, expired (hours <= 0), near expiry (<= min_hours), or force_refresh requested:
    needs_renew = force_refresh or not token
    if hours is not None:
        if hours <= 0:
            needs_renew = True
        elif min_hours is not None and hours <= min_hours:
            needs_renew = True

    if needs_renew:
        try:
            from scripts.gcp_dhan_token_rotation_job import rotate_token
            rot = rotate_token(force=True)
            if rot.get("success"):
                new_tok = os.getenv("DHAN_ACCESS_TOKEN", "").strip().lstrip("\ufeff")
                if not new_tok:
                    new_tok = _local_vault_secret("DHAN_ACCESS_TOKEN")
                if new_tok:
                    token = new_tok
                    source = "ROTATED_AND_VERIFIED"
                    provider = "DHAN_CANONICAL_ROTATE"
                    hours, exp = _parse_jwt_hours_exp(token)
                    is_fallback = False
        except Exception:
            pass

    if hours is None:
        hours = 23.5 if token else 0.0

    return token, source, provider, hours, exp, is_fallback


def _dynamic_cloud_token() -> str:
    """Load Dhan token with GCP Secret Manager dynamic authority or local fallback."""
    token, _, _, hours, _, is_fallback = get_dhan_token()
    if token and hours is not None and hours > 0 and not is_fallback:
        return token

    # If expired or fallback, re-verify with auto-renewal
    if not token or (hours is not None and hours <= 0):
        token, _, _, _, _, _ = get_dhan_token(force_refresh=True)
        if token:
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
