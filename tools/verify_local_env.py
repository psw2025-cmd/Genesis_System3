#!/usr/bin/env python3
"""Verify local laptop env vs Render — no secrets printed."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

KEYS = [
    "DHAN_CLIENT_ID",
    "DHAN_APP_ID",
    "DHAN_APP_SECRET",
    "DHAN_ACCESS_TOKEN",
    "DHAN_PIN",
    "DHAN_TOTP_SECRET",
]

ENV_PATHS = [
    ROOT / ".secrets" / "dhan.env",
    ROOT / "config" / ".env",
]


def _mask(v: str) -> str:
    if not v:
        return ""
    if len(v) <= 4:
        return "****"
    return f"...{v[-4:]}"


def main() -> int:
    print("=== Local env verification ===\n")

    for p in ENV_PATHS:
        print(f"  {p.relative_to(ROOT)}: {'FOUND' if p.exists() else 'MISSING'}")

    # Load like production
    try:
        from core.utils.env_loader import get_dhan_credentials

        get_dhan_credentials()
    except Exception as exc:
        print(f"\n  env_loader warning: {exc}")

    print("\n=== DHAN variables (after env_loader) ===")
    missing = []
    for k in KEYS:
        v = os.environ.get(k, "").strip()
        if v:
            print(f"  {k}: SET {_mask(v)}")
        else:
            print(f"  {k}: MISSING")
            missing.append(k)

    print("\n=== Diagnosis ===")
    if not (ROOT / ".secrets" / "dhan.env").exists():
        print("  .secrets/dhan.env not on laptop — Render/GitHub secrets do NOT sync here.")
        print("  Copy DHAN_* from Render dashboard -> Genesis_System3\\.secrets\\dhan.env")
        print("  Template: config\\.env.example")

    if missing:
        print(f"  Missing {len(missing)} key(s): {', '.join(missing)}")
        if "DHAN_PIN" in missing or "DHAN_TOTP_SECRET" in missing:
            print("  -> Startup log: 'DHAN_PIN/DHAN_TOTP_SECRET not set' (token auto-refresh skipped)")
        if "DHAN_ACCESS_TOKEN" in missing:
            print("  -> Broker will show OFFLINE until token is set")
    else:
        print("  All DHAN keys present locally.")

    print("\n=== Root URL note ===")
    print("  GET / shows Render URL by default (PUBLIC_BACKEND_URL).")
    print("  Local dashboard: http://127.0.0.1:8000/ui")

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
