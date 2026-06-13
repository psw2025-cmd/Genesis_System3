"""
Dhan Automation Setup Wizard
============================
One-time setup to enable fully automated daily token refresh.

What this does:
  1. Tests your current token (may already be valid)
  2. Guides you to find your DHAN_PIN and TOTP secret
  3. Tests PIN+TOTP generation immediately
  4. Saves credentials to .secrets/dhan.env
  5. Verifies the daemon works

Run once:
  python scripts/setup_dhan_automation.py

After setup:
  python scripts/dhan_token_auto_refresh.py          # daemon (runs daily at 08:30)
  python scripts/dhan_token_auto_refresh.py --now    # refresh immediately
  python scripts/dhan_token_auto_refresh.py --verify # check current token
"""

import sys
import os
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ENV_FILE = ROOT / ".secrets" / "dhan.env"


def _load_env() -> dict:
    env = {}
    if not ENV_FILE.exists():
        return env
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def _write_key(key: str, value: str) -> None:
    content = ENV_FILE.read_text() if ENV_FILE.exists() else ""
    if re.search(rf"^{key}=", content, re.MULTILINE):
        content = re.sub(rf"^{key}=.*$", f"{key}={value}", content, flags=re.MULTILINE)
    else:
        content = content.rstrip("\n") + f"\n{key}={value}\n"
    ENV_FILE.write_text(content)
    os.environ[key] = value


def step_banner():
    print("\n" + "=" * 60)
    print("  DHAN AUTOMATION SETUP — Genesis System3")
    print("=" * 60)
    print("\nThis wizard configures fully automated daily token refresh.")
    print("You need: Dhan PIN + TOTP authenticator secret.\n")


def step_check_current():
    from core.brokers.dhan.token_manager import verify_token
    print("Step 1: Checking current token...")
    v = verify_token()
    if v.get("valid"):
        hrs = v.get("hours_remaining", "?")
        exp = v.get("expires_at", "")
        print(f"  ✅ Token is VALID — expires in {hrs}h ({exp})")
        return True
    else:
        reason = v.get("reason", "unknown")
        print(f"  ❌ Token INVALID: {reason}")
        return False


def step_get_pin():
    env = _load_env()
    existing = env.get("DHAN_PIN", "")
    if existing:
        print(f"\nStep 2: DHAN_PIN already set (****). Skip? [Y/n] ", end="")
        ans = input().strip().lower()
        if ans != "n":
            return existing

    print("\nStep 2: Enter your Dhan account PIN (4–6 digits)")
    print("  (This is the PIN you use to log into Dhan app/web)")
    pin = input("  PIN: ").strip()
    if not pin.isdigit() or len(pin) < 4:
        print("  Invalid PIN — must be 4–6 digits")
        return None
    _write_key("DHAN_PIN", pin)
    print("  ✅ Saved DHAN_PIN")
    return pin


def step_get_totp_secret():
    env = _load_env()
    existing = env.get("DHAN_TOTP_SECRET", "")
    if existing:
        print(f"\nStep 3: DHAN_TOTP_SECRET already set (len={len(existing)}). Skip? [Y/n] ", end="")
        ans = input().strip().lower()
        if ans != "n":
            return existing

    print("\nStep 3: Enter your TOTP base32 secret")
    print()
    print("  HOW TO FIND YOUR TOTP SECRET:")
    print("  ─────────────────────────────")
    print("  Option A — From your authenticator app:")
    print("    1. Open Google Authenticator / Authy")
    print("    2. Find the 'Dhan' or 'DhanHQ' entry")
    print("    3. Tap to view details → copy the secret key")
    print()
    print("  Option B — Set up fresh 2FA on Dhan:")
    print("    1. Login to Dhan web → Profile → Security → TOTP Setup")
    print("    2. When QR code shows, click 'Can't scan? Show key'")
    print("    3. Copy the BASE32 string (looks like: JBSWY3DPEHPK3PXP)")
    print()
    secret = input("  TOTP Secret (base32): ").strip().upper().replace(" ", "")
    if len(secret) < 16:
        print("  Too short — must be at least 16 characters")
        return None

    # Validate it generates a 6-digit OTP
    try:
        import pyotp
        totp = pyotp.TOTP(secret)
        otp = totp.now()
        print(f"  Generated OTP: {otp}")
        print(f"  Does this match your authenticator app? [y/N] ", end="")
        ans = input().strip().lower()
        if ans != "y":
            print("  OTP mismatch — please check the secret")
            return None
    except Exception as e:
        print(f"  TOTP validation failed: {e}")
        return None

    _write_key("DHAN_TOTP_SECRET", secret)
    print("  ✅ Saved DHAN_TOTP_SECRET")
    return secret


def step_test_generation():
    print("\nStep 4: Testing generate_token(pin, totp) now...")
    from core.brokers.dhan.token_manager import refresh_token
    result = refresh_token(force_generate=True)
    if result.get("success"):
        print(f"  ✅ Token generated successfully!")
        print(f"     Strategy : {result['strategy']}")
        print(f"     Token    : {result['token_preview']}")
        print(f"     Expires  : {result.get('expires_at', 'unknown')}")
        return True
    else:
        print(f"  ❌ Generation failed: {result['message']}")
        return False


def step_daemon_instructions():
    print("\nStep 5: Starting auto-refresh daemon...")
    print()
    print("  The daemon refreshes your token every day at 08:30 AM.")
    print()
    print("  START DAEMON (runs in background):")
    print("    python scripts/dhan_token_auto_refresh.py &")
    print()
    print("  OR add to system startup / cron:")
    print("    # crontab -e")
    print("    30 8 * * 1-5 cd /workspaces/Genesis_System3 && python scripts/dhan_token_auto_refresh.py --now")
    print()
    print("  MANUAL COMMANDS:")
    print("    python scripts/dhan_token_auto_refresh.py --verify   # check token status")
    print("    python scripts/dhan_token_auto_refresh.py --now      # refresh immediately")
    print("    python scripts/dhan_token_auto_refresh.py            # start daemon")
    print()
    print("=" * 60)
    print("  SETUP COMPLETE — fully automated token refresh active!")
    print("=" * 60 + "\n")


def main():
    step_banner()

    current_valid = step_check_current()
    if current_valid:
        env = _load_env()
        if env.get("DHAN_PIN") and env.get("DHAN_TOTP_SECRET"):
            print("\n✅ All credentials already configured! Nothing to set up.")
            print("   Run: python scripts/dhan_token_auto_refresh.py")
            return

    pin = step_get_pin()
    if not pin:
        print("\n⚠ Setup incomplete — PIN required for automation.")
        return

    secret = step_get_totp_secret()
    if not secret:
        print("\n⚠ Setup incomplete — TOTP secret required for automation.")
        return

    success = step_test_generation()
    if not success:
        print("\n⚠ Token generation failed. Check PIN and TOTP secret.")
        print("  You can still use: python scripts/dhan_token_auto_refresh.py --oauth")
        return

    step_daemon_instructions()


if __name__ == "__main__":
    main()
