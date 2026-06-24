"""Cross-platform subprocess command helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def resolve_npx() -> str:
    npx = shutil.which("npx")
    if npx:
        return npx
    raise FileNotFoundError("npx not found in PATH — install Node.js")


def playwright_test_cmd() -> list[str]:
    return [
        resolve_npx(),
        "--prefix",
        "tools/playwright-setup",
        "playwright",
        "test",
        "--config",
        str(ROOT / "playwright.config.ts"),
    ]
