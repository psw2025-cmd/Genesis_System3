import os
from dotenv import load_dotenv

# Project root: .../Genesis_System3
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_PATH = os.path.join(ROOT_DIR, "config", ".env")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)


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
