#!/usr/bin/env python3
"""Read-only nested dependency inventory; supports offline fixture verification."""
import argparse
import json
from pathlib import Path

DEFAULT_LOCK = Path(__file__).resolve().parents[1] / "dashboard/frontend/package-lock.json"
WATCH = {"picomatch", "fdir", "tinyglobby", "vite"}


def inspect(lockfile: Path) -> dict:
    data = json.loads(lockfile.read_text(encoding="utf-8"))
    packages = data.get("packages")
    if not isinstance(packages, dict):
        raise ValueError("Invalid npm lockfile: packages mapping missing")
    found = []
    for path, meta in sorted(packages.items()):
        if not isinstance(meta, dict) or "node_modules/" not in path:
            continue
        name = path.rsplit("node_modules/", 1)[-1]
        if name in WATCH:
            found.append({"path": path, "name": name, "version": meta.get("version"),
                          "dependencies": meta.get("dependencies", {})})
    missing = sorted(WATCH - {item["name"] for item in found})
    return {"lockfile": str(lockfile), "packages": found, "missing": missing}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lockfile", type=Path, default=DEFAULT_LOCK,
                        help="Alternate lockfile for offline regression fixtures")
    args = parser.parse_args()
    result = inspect(args.lockfile)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["missing"]:
        raise SystemExit("Missing expected dependency records: " + ", ".join(result["missing"]))


if __name__ == "__main__":
    main()
