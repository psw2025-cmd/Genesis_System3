#!/usr/bin/env python3
"""One-shot System3 Gmail thread pull for full cross-verify."""
from __future__ import annotations

import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = Path(
    r"C:\Pritam_CV_Tier1_EPC\Piping-E3D-Job-Intelligence\private-config\gmail_token.json"
)
OUT = Path(__file__).with_name("gmail_system3_threads.json")
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
]
QUERY = (
    "(System3 OR Genesis_System3 OR genesis-system3 OR RHUI OR "
    '"issue #188" OR "Cloud Run" OR "Workflow Priority Guard" OR '
    "psw2025-cmd) newer_than:14d"
)


def main() -> int:
    if not TOKEN.exists():
        OUT.write_text(
            json.dumps(
                {
                    "ok": False,
                    "blocked": True,
                    "reason": f"token missing: {TOKEN}",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print("BLOCKED token missing")
        return 2

    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    svc = build("gmail", "v1", credentials=creds, cache_discovery=False)
    res = svc.users().messages().list(userId="me", q=QUERY, maxResults=25).execute()
    msgs = res.get("messages") or []
    out = []
    for m in msgs:
        full = (
            svc.users()
            .messages()
            .get(
                userId="me",
                id=m["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            )
            .execute()
        )
        headers = {
            h["name"]: h["value"] for h in full.get("payload", {}).get("headers", [])
        }
        out.append(
            {
                "id": m["id"],
                "threadId": full.get("threadId"),
                "snippet": (full.get("snippet") or "")[:280],
                "from": headers.get("From"),
                "subject": headers.get("Subject"),
                "date": headers.get("Date"),
                "labelIds": full.get("labelIds"),
            }
        )
    payload = {"ok": True, "query": QUERY, "count": len(out), "messages": out}
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"OK count={len(out)} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
