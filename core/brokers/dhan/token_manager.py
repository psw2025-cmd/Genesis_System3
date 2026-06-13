"""
Dhan Token Manager — Permanent Auto-Refresh Solution
=====================================================
Dhan access tokens expire every 24 hours. This module solves that permanently.

THREE STRATEGIES (tried in order):
  1. generate_token()  — Uses PIN + live TOTP (no browser, fully automated)
  2. renew_token()     — Uses existing token to extend it (fastest, fails if fully expired)
  3. oauth_manual()    — Prints consent URL for manual browser login (emergency fallback)

On success: writes new DHAN_ACCESS_TOKEN to .secrets/dhan.env automatically.
Schedule:   Run daily at 08:30 AM via dhan_token_auto_refresh.py daemon.

Required in .secrets/dhan.env:
  DHAN_CLIENT_ID=<your_client_id>        ← already set
  DHAN_APP_ID=<api_key>                  ← already set
  DHAN_APP_SECRET=<api_secret>           ← already set
  DHAN_ACCESS_TOKEN=<token>              ← auto-updated by this script
  DHAN_PIN=<your_4-6_digit_pin>          ← add once (run setup_dhan_automation.py)
  DHAN_TOTP_SECRET=<totp_base32_secret>  ← add once (run setup_dhan_automation.py)

One-time setup: python scripts/setup_dhan_automation.py
"""

import os
import re
import sys
import logging
from datetime import datetime
from pathlib import Path

try:
    import pyotp
    _PYOTP_OK = True
except ImportError:
    _PYOTP_OK = False

try:
    from dhanhq import DhanLogin
    _DHAN_SDK_OK = True
except ImportError:
    _DHAN_SDK_OK = False

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = ROOT_DIR / ".secrets" / "dhan.env"
LOG_FILE = ROOT_DIR / "logs" / "dhan_token_refresh.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [TokenManager] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("dhan_token_manager")


# ------------------------------------------------------------------ #
#  Env helpers                                                         #
# ------------------------------------------------------------------ #

def _load_env() -> dict:
    """Load all key=value pairs from .secrets/dhan.env."""
    env = {}
    if not ENV_FILE.exists():
        logger.error(f"Env file not found: {ENV_FILE}")
        return env
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def _write_token(new_token: str) -> None:
    """Update DHAN_ACCESS_TOKEN in .secrets/dhan.env in-place."""
    if not ENV_FILE.exists():
        logger.error("Cannot write token — env file missing")
        return

    content = ENV_FILE.read_text()
    if "DHAN_ACCESS_TOKEN" in content:
        content = re.sub(
            r"^DHAN_ACCESS_TOKEN=.*$",
            f"DHAN_ACCESS_TOKEN={new_token}",
            content,
            flags=re.MULTILINE,
        )
    else:
        content += f"\nDHAN_ACCESS_TOKEN={new_token}\n"

    ENV_FILE.write_text(content)
    os.environ["DHAN_ACCESS_TOKEN"] = new_token
    logger.info("DHAN_ACCESS_TOKEN updated in .secrets/dhan.env")

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} | token refreshed | len={len(new_token)}\n")


def _token_expiry(token: str) -> datetime | None:
    """Decode JWT expiry without PyJWT."""
    import base64, json
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        pad = parts[1] + "=" * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(pad))
        exp = payload.get("exp")
        return datetime.fromtimestamp(exp) if exp else None
    except Exception:
        return None


# ------------------------------------------------------------------ #
#  Strategy 1 (primary): generate_token via PIN + TOTP               #
# ------------------------------------------------------------------ #

def _try_generate(client_id: str, pin: str, totp_secret: str) -> str | None:
    """
    Generate a brand-new token using PIN + live TOTP.
    POST https://auth.dhan.co/app/generateAccessToken?dhanClientId=...&pin=...&totp=...
    Returns new token string on success, None on failure.
    """
    if not _DHAN_SDK_OK:
        logger.error("DhanHQ SDK not installed — run: pip install dhanhq")
        return None
    if not _PYOTP_OK:
        logger.error("pyotp not installed — run: pip install pyotp")
        return None
    if not pin:
        logger.warning("DHAN_PIN not set in .secrets/dhan.env — skipping generate_token")
        return None
    if not totp_secret:
        logger.warning("DHAN_TOTP_SECRET not set in .secrets/dhan.env — skipping generate_token")
        return None

    try:
        totp = pyotp.TOTP(totp_secret)
        current_otp = totp.now()
        seconds_left = 30 - (int(datetime.now().timestamp()) % 30)
        logger.info(f"Generated TOTP (valid {seconds_left}s more)")

        login = DhanLogin(client_id)
        resp = login.generate_token(pin, current_otp)
        logger.info(f"generate_token response keys: {list(resp.keys()) if isinstance(resp, dict) else type(resp)}")

        token = (
            resp.get("accessToken")
            or resp.get("access_token")
            or (resp.get("data") or {}).get("accessToken")
        )
        if token:
            return token
        logger.error(f"generate_token: no accessToken in response: {resp}")
        return None
    except Exception as e:
        logger.error(f"generate_token failed: {e}")
        return None


# ------------------------------------------------------------------ #
#  Strategy 2 (fallback): renew existing token                        #
# ------------------------------------------------------------------ #

def _try_renew(client_id: str, current_token: str) -> str | None:
    """
    Try to renew the current token using Dhan's RenewToken endpoint.
    GET https://api.dhan.co/v2/RenewToken (passes current token in header)
    Returns new token string on success, None on failure.
    """
    if not _DHAN_SDK_OK:
        return None
    if not current_token:
        return None
    try:
        login = DhanLogin(client_id)
        resp = login.renew_token(current_token)
        logger.info(f"renew_token response keys: {list(resp.keys()) if isinstance(resp, dict) else type(resp)}")
        token = (
            resp.get("accessToken")
            or resp.get("access_token")
            or (resp.get("data") or {}).get("accessToken")
        )
        return token if token else None
    except Exception as e:
        logger.warning(f"renew_token failed: {e}")
        return None


# ------------------------------------------------------------------ #
#  Strategy 3 (emergency): OAuth manual consent flow                  #
# ------------------------------------------------------------------ #

def _try_oauth_manual(client_id: str, app_id: str, app_secret: str) -> str | None:
    """
    Generate a consent URL and print it for manual browser login.
    Returns None always — this prints the URL and expects user action.
    User must call consume_oauth_token(token_id) after clicking the URL.
    """
    if not _DHAN_SDK_OK:
        return None
    if not app_id or not app_secret:
        logger.error("DHAN_APP_ID or DHAN_APP_SECRET missing")
        return None
    try:
        login = DhanLogin(client_id)
        import requests
        resp = requests.post(
            f"{login.AUTH_BASE_URL}/app/generate-consent",
            params={"client_id": client_id},
            headers={"app_id": app_id, "app_secret": app_secret},
        )
        data = resp.json()
        if data.get("status") == "success":
            consent_id = data["consentAppId"]
            url = f"{login.AUTH_BASE_URL}/login/consentApp-login?consentAppId={consent_id}"
            print("\n" + "=" * 60)
            print("ACTION REQUIRED: Open the URL below in your browser:")
            print(url)
            print("\nAfter login, copy the tokenId from the redirect URL:")
            print("  http://localhost/?tokenId=XXXX-XXXX")
            print("\nThen run:")
            print("  python scripts/dhan_token_auto_refresh.py --consume <tokenId>")
            print("=" * 60 + "\n")
            return None
        logger.error(f"OAuth consent failed: {data}")
        return None
    except Exception as e:
        logger.error(f"OAuth manual flow failed: {e}")
        return None


def consume_oauth_token(token_id: str) -> dict:
    """
    Complete the OAuth flow after user provides tokenId from browser redirect.
    Called by: python scripts/dhan_token_auto_refresh.py --consume <tokenId>
    """
    env = _load_env()
    client_id  = env.get("DHAN_CLIENT_ID", "").strip()
    app_id     = env.get("DHAN_APP_ID", "").strip()
    app_secret = env.get("DHAN_APP_SECRET", "").strip()

    if not all([client_id, app_id, app_secret, token_id]):
        return {"success": False, "message": "Missing credentials or token_id"}

    if not _DHAN_SDK_OK:
        return {"success": False, "message": "DhanHQ SDK not installed"}
    try:
        login = DhanLogin(client_id)
        resp = login.consume_token_id(token_id, app_id, app_secret)
        token = (
            resp.get("accessToken")
            or resp.get("access_token")
            or (resp.get("data") or {}).get("accessToken")
        )
        if token:
            _write_token(token)
            return {
                "success": True,
                "strategy": "oauth_consume",
                "message": "Token obtained via OAuth consent flow",
                "token_preview": f"...{token[-8:]}",
                "token_length": len(token),
            }
        return {"success": False, "message": f"No token in response: {resp}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ------------------------------------------------------------------ #
#  Main refresh logic                                                  #
# ------------------------------------------------------------------ #

def refresh_token(force_generate: bool = False, force_oauth: bool = False) -> dict:
    """
    Refresh the Dhan access token using best available strategy.

    Strategy order:
      1. generate_token(pin, totp) — if DHAN_PIN + DHAN_TOTP_SECRET set
      2. renew_token(current)      — if token is still parseable
      3. oauth_manual()            — prints consent URL, returns False (user action needed)

    Args:
        force_generate: Skip renew and go straight to generate_token.
        force_oauth: Skip all and go to OAuth manual flow.

    Returns:
        dict with keys: success, strategy, message, token_preview
    """
    env = _load_env()
    client_id   = env.get("DHAN_CLIENT_ID", "").strip()
    cur_token   = env.get("DHAN_ACCESS_TOKEN", "").strip()
    pin         = env.get("DHAN_PIN", "").strip()
    totp_secret = env.get("DHAN_TOTP_SECRET", "").strip()
    app_id      = env.get("DHAN_APP_ID", "").strip()
    app_secret  = env.get("DHAN_APP_SECRET", "").strip()

    if not client_id:
        return {"success": False, "message": "DHAN_CLIENT_ID missing from .secrets/dhan.env"}

    logger.info(f"Starting token refresh for client_id=...{client_id[-4:]}")

    if force_oauth:
        _try_oauth_manual(client_id, app_id, app_secret)
        return {"success": False, "strategy": "oauth_manual", "message": "Browser action required — see console"}

    # Strategy 1: generate_token via PIN + TOTP (primary — fastest, fully automated)
    if not force_generate or (pin and totp_secret):
        if pin and totp_secret:
            logger.info("Trying Strategy 1: generate_token(pin, totp)")
            new_token = _try_generate(client_id, pin, totp_secret)
            if new_token:
                _write_token(new_token)
                exp = _token_expiry(new_token)
                return {
                    "success": True,
                    "strategy": "generate_token",
                    "message": "Token generated via PIN + TOTP (fully automated)",
                    "token_preview": f"...{new_token[-8:]}",
                    "token_length": len(new_token),
                    "expires_at": exp.isoformat() if exp else "unknown",
                }
            logger.warning("generate_token failed — falling back")

    # Strategy 2: renew existing token
    if not force_generate and cur_token:
        logger.info("Trying Strategy 2: renew_token(current_token)")
        new_token = _try_renew(client_id, cur_token)
        if new_token:
            _write_token(new_token)
            exp = _token_expiry(new_token)
            return {
                "success": True,
                "strategy": "renew_token",
                "message": "Token renewed (extended from current token)",
                "token_preview": f"...{new_token[-8:]}",
                "token_length": len(new_token),
                "expires_at": exp.isoformat() if exp else "unknown",
            }
        logger.warning("renew_token failed — falling back to OAuth manual")

    # Strategy 3: OAuth manual flow (requires browser action)
    logger.warning("Automated strategies failed — initiating OAuth manual flow")
    _try_oauth_manual(client_id, app_id, app_secret)

    missing = []
    if not pin:
        missing.append("DHAN_PIN")
    if not totp_secret:
        missing.append("DHAN_TOTP_SECRET")
    hint = (
        f"For full automation, add {', '.join(missing)} to .secrets/dhan.env "
        f"then run: python scripts/setup_dhan_automation.py"
        if missing else
        "All credentials present but both auto-strategies failed — check logs"
    )
    return {
        "success": False,
        "strategy": "oauth_manual",
        "message": hint,
    }


# ------------------------------------------------------------------ #
#  Token verification                                                  #
# ------------------------------------------------------------------ #

def verify_token() -> dict:
    """Quick check: is the current token valid? Returns expiry info."""
    env = _load_env()
    client_id = env.get("DHAN_CLIENT_ID", "")
    token = env.get("DHAN_ACCESS_TOKEN", "")
    if not client_id or not token:
        return {"valid": False, "reason": "credentials_missing"}

    exp = _token_expiry(token)
    if exp:
        now = datetime.now()
        hours_left = (exp - now).total_seconds() / 3600
        if hours_left < 0:
            return {"valid": False, "reason": f"expired {abs(hours_left):.1f}h ago", "expired_at": exp.isoformat()}

    if not _DHAN_SDK_OK:
        # Can't verify via API — check expiry only
        if exp and hours_left > 0:
            return {"valid": True, "reason": "jwt_expiry_ok", "expires_at": exp.isoformat(),
                    "hours_remaining": round(hours_left, 1)}
        return {"valid": False, "reason": "sdk_unavailable_and_no_expiry"}

    try:
        login = DhanLogin(client_id)
        profile = login.user_profile(token)
        if profile and not profile.get("errorCode"):
            cid = profile.get("dhanClientId") or profile.get("clientId")
            name = profile.get("clientName") or profile.get("name", "")
            return {
                "valid": True,
                "client_id": str(cid)[-4:] if cid else client_id[-4:],
                "name": name,
                "expires_at": exp.isoformat() if exp else "unknown",
                "hours_remaining": round(hours_left, 1) if exp else None,
            }
        return {"valid": False, "reason": str(profile)}
    except Exception as e:
        return {"valid": False, "reason": str(e)}


# ------------------------------------------------------------------ #
#  CLI                                                                 #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    import json
    import argparse

    parser = argparse.ArgumentParser(description="Dhan Token Manager")
    parser.add_argument("--verify",   action="store_true", help="Check if current token is valid")
    parser.add_argument("--refresh",  action="store_true", help="Refresh token (generate first, then renew)")
    parser.add_argument("--generate", action="store_true", help="Force generate new token via PIN+TOTP")
    parser.add_argument("--oauth",    action="store_true", help="Show OAuth consent URL for manual browser login")
    parser.add_argument("--consume",  metavar="TOKEN_ID",  help="Consume OAuth tokenId from browser redirect")
    args = parser.parse_args()

    if args.consume:
        result = consume_oauth_token(args.consume)
        print(json.dumps(result, indent=2))
    elif args.verify:
        result = verify_token()
        print(json.dumps(result, indent=2))
    elif args.refresh:
        result = refresh_token()
        print(json.dumps(result, indent=2))
    elif args.generate:
        result = refresh_token(force_generate=True)
        print(json.dumps(result, indent=2))
    elif args.oauth:
        result = refresh_token(force_oauth=True)
        print(json.dumps(result, indent=2))
    else:
        print("=== Dhan Token Manager ===")
        v = verify_token()
        print(f"Token valid: {v['valid']}")
        if v.get("name"):
            print(f"Account: {v['name']}")
        if v.get("hours_remaining") is not None:
            print(f"Expires in: {v['hours_remaining']:.1f}h  ({v.get('expires_at','')})")
        if not v["valid"]:
            print(f"\nReason: {v.get('reason')}")
            print("\nAttempting refresh...")
            r = refresh_token()
            print(json.dumps(r, indent=2))
