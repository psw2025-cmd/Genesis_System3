import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Project roots
ROOT_DIR = Path(__file__).resolve().parent
APP_CONTENT_DIR = ROOT_DIR / "content" / "app"

# Load environment secrets
load_dotenv(ROOT_DIR / ".secrets" / "dhan.env")
load_dotenv(ROOT_DIR / ".env")

# Ensure content/app and root are in sys.path
for p in [str(APP_CONTENT_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Import the main FastAPI application
from content.app.app import app
