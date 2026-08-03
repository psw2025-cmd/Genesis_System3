#!/usr/bin/env python3
"""Prepare gcloud auth materials from .secrets/gcp_user_token.json."""
from __future__ import annotations

import json
from pathlib import Path

from google.auth.transport.requests import AuthorizedSession, Request
from google.oauth2.credentials import Credentials

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ".secrets" / "gcp_user_token.json"
OUT_DIR = Path.home() / "AppData" / "Roaming" / "gcloud"


def main() -> int:
    d = json.loads(SRC.read_text(encoding="utf-8-sig"))
    creds = Credentials(
        token=d.get("token"),
        refresh_token=d["refresh_token"],
        token_uri=d.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=d["client_id"],
        client_secret=d["client_secret"],
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    if not creds.valid:
        creds.refresh(Request())

    sess = AuthorizedSession(creds)
    info = sess.get("https://www.googleapis.com/oauth2/v2/userinfo", timeout=30).json()
    email = (info.get("email") or d.get("account") or "").strip()
    print(f"email={email}")
    print(f"token_prefix={(creds.token or '')[:5]}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    adc = {
        "type": "authorized_user",
        "client_id": d["client_id"],
        "client_secret": d["client_secret"],
        "refresh_token": d["refresh_token"],
    }
    (OUT_DIR / "application_default_credentials.json").write_text(
        json.dumps(adc, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "genesis_authorized_user.json").write_text(
        json.dumps(adc, indent=2), encoding="utf-8"
    )
    secrets = ROOT / ".secrets"
    (secrets / "_gcloud_account.txt").write_text(email, encoding="utf-8")
    (secrets / "_gcloud_refresh.txt").write_text(d["refresh_token"], encoding="utf-8")
    return 0 if email else 1


if __name__ == "__main__":
    raise SystemExit(main())
