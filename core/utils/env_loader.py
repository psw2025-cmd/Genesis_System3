import os

from dotenv import load_dotenv

# Project root: .../Genesis_System3
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_PATHS = [
    os.path.join(ROOT_DIR, "config", ".env"),
    os.getenv("SYSTEM3_ENV_FILE", ""),
    "/etc/secrets/.env",
    # Dhan-specific local secret file (git-excluded)
    os.path.join(ROOT_DIR, ".secrets", "dhan.env"),
]

for env_path in ENV_PATHS:
    if env_path and os.path.exists(env_path):
        load_dotenv(env_path, override=False)


def get_dhan_credentials():
    """
    Returns Dhan credentials (read-only / analyzer-only).
    Access token only — no API key or password needed for read ops.
    Never logs or returns the raw token in user-facing output.
    """
    return {
        "client_id": os.getenv("DHAN_CLIENT_ID", "").strip(),
        "access_token": os.getenv("DHAN_ACCESS_TOKEN", "").strip(),
    }
