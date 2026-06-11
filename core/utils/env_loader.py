import os
from dotenv import load_dotenv

# Project root: .../Genesis_System3
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_PATHS = [
    os.path.join(ROOT_DIR, "config", ".env"),
    os.getenv("SYSTEM3_ENV_FILE", ""),
    "/etc/secrets/.env",
]

for env_path in ENV_PATHS:
    if env_path and os.path.exists(env_path):
        load_dotenv(env_path, override=False)


def get_angelone_credentials():
    """
    Returns Angel One credentials from config/.env
    """
    return {
        "api_key": os.getenv("ANGELONE_API_KEY", "").strip(),
        "client_id": os.getenv("ANGELONE_CLIENT_ID", "").strip(),
        "pin": os.getenv("ANGELONE_PIN", "").strip(),
        "password": os.getenv("ANGELONE_PASSWORD", "").strip(),
        "totp_secret": os.getenv("ANGELONE_TOTP", "").strip(),
    }
