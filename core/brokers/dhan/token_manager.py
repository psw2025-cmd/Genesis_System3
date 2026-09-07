"""Dhan token manager — 100% LOCAL MODE.
No GCP, No Cloud Run. Only this laptop is authority.
Token source:.secrets/dhan.env and outputs/dhan_token.json
"""
from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRETS_FILE = ROOT / ".secrets" / "dhan.env"
TOKEN_JSON = ROOT / "outputs" / "dhan_token.json"

def _read_env_file():
    data = {}
    if SECRETS_FILE.exists():
        for line in SECRETS_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k,v = line.split("=",1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data

def _current_token() -> str:
    token = (os.getenv("DHAN_ACCESS_TOKEN") or "").strip().lstrip("\ufeff")
    if token:
        return token
    env_data = _read_env_file()
    token = env_data.get("DHAN_ACCESS_TOKEN") or env_data.get("access_token") or ""
    if token:
        return token.strip()
    if TOKEN_JSON.exists():
        try:
            j = json.loads(TOKEN_JSON.read_text(encoding="utf-8", errors="ignore"))
            return str(j.get("access_token") or j.get("token") or "").strip()
        except:
            pass
    try:
        from core.utils.env_loader import get_dhan_credentials
        return str(get_dhan_credentials().get("access_token") or "").strip().lstrip("\ufeff")
    except Exception:
        return ""

def _expiry(token: str) -> datetime | None:
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        body = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(body.encode("ascii")))
        exp = payload.get("exp")
        return datetime.fromtimestamp(float(exp), tz=timezone.utc) if exp else None
    except Exception:
        return None

def verify_token() -> dict:
    token = _current_token()
    if not token:
        return {"valid": False, "reason": "credentials_missing", "source": "local_file", "raw_token_exposed": False}
    exp = _expiry(token)
    if exp is None:
        return {"valid": True, "reason": "jwt_expiry_unavailable_but_token_present", "source": "local_file", "raw_token_exposed": False, "mode": "LOCAL"}
    now = datetime.now(timezone.utc)
    hours = (exp - now).total_seconds() / 3600.0
    return {
        "valid": hours > 0,
        "reason": "jwt_expiry_ok" if hours > 0 else "jwt_expired",
        "expires_at": exp.isoformat(),
        "hours_remaining": round(hours, 2),
        "source": "local_file",
        "raw_token_exposed": False,
        "mode": "LOCAL"
    }

def get_token_status() -> dict:
    return verify_token()

def refresh_token(*args, **kwargs) -> dict:
    """LOCAL refresh - just validates current token from.secrets/dhan.env"""
    status = verify_token()
    if status.get("valid"):
        return {
            "success": True,
            "strategy": "LOCAL_FILE",
            "message": "Local mode active - token loaded from.secrets/dhan.env",
            "mutation_attempted": False,
            "raw_token_exposed": False,
            "token_status": status,
            "mode": "LOCAL"
        }
    else:
        return {
            "success": False,
            "strategy": "LOCAL_FILE",
            "message": f"Local token invalid or missing. Put token in {SECRETS_FILE}",
            "mutation_attempted": False,
            "raw_token_exposed": False,
            "token_status": status,
            "mode": "LOCAL"
        }

def consume_oauth_token(*args, **kwargs) -> dict:
    return refresh_token(*args, **kwargs)

if __name__ == "__main__":
    print(json.dumps(verify_token(), indent=2))