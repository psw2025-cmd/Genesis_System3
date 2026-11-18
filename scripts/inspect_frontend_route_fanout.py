#!/usr/bin/env python3
"""Read-only report of route lazy imports and mount-time background import fanout.

This is a structural diagnostic, not proof of a browser-rendering root cause.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dashboard/frontend/src/App.tsx"


def inspect(source: str) -> dict:
    lazy_paths = re.findall(r"\blazy\(\(\)\s*=>\s*import\(['\"]([^'\"]+)['\"]\)", source)
    mount_effect = re.search(r"export default function App\(\)\s*\{.*?useEffect\(\(\)\s*=>\s*\{(.*?)\},\s*\[\]\)", source, re.S)
    effect = mount_effect.group(1) if mount_effect else ""
    background_paths = re.findall(r"\bimport\(['\"]([^'\"]+)['\"]\)", effect)
    overlapping = sorted(set(lazy_paths) & set(background_paths))
    return {
        "lazy_route_count": len(lazy_paths),
        "mount_background_import_count": len(background_paths),
        "overlapping_lazy_background_paths": overlapping,
        "background_fanout_present": len(background_paths) > 1,
        "interpretation": "structural diagnostic only; correlate with network and browser console traces",
    }


def main() -> None:
    report = inspect(SOURCE.read_text(encoding="utf-8"))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
