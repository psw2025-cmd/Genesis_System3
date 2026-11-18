#!/usr/bin/env python3
"""Read-only structural inventory of lazy route imports and mount-time preloads.

This cannot prove a browser failure's root cause; correlate with Chrome traces.
"""
import argparse
import json
import re
from pathlib import Path

DEFAULT_SOURCE = Path(__file__).resolve().parents[1] / "dashboard/frontend/src/App.tsx"
IMPORT = re.compile(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
LAZY = re.compile(r"\blazy\s*\(\s*\(\s*\)\s*=>\s*import\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")


def inspect(source: str) -> dict:
    lazy_paths = LAZY.findall(source)
    effects = re.findall(r"\buseEffect\s*\(\s*\(\s*\)\s*=>\s*\{(.*?)\}\s*,\s*\[\s*\]\s*\)", source, re.S)
    if not lazy_paths or not effects:
        raise ValueError("Expected lazy routes and mount-only useEffect; source structure changed")
    background_paths = [path for effect in effects for path in IMPORT.findall(effect)]
    return {
        "lazy_route_count": len(lazy_paths),
        "mount_background_import_count": len(background_paths),
        "overlapping_lazy_background_paths": sorted(set(lazy_paths) & set(background_paths)),
        "background_fanout_present": len(background_paths) > 1,
        "interpretation": "structural diagnostic only; correlate with network and browser console traces",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()
    print(json.dumps(inspect(args.source.read_text(encoding="utf-8")), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
