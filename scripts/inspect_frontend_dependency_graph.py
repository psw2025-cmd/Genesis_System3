#!/usr/bin/env python3
"""Read-only inventory of nested frontend dependencies for security triage."""
import json
from pathlib import Path

LOCK = Path(__file__).resolve().parents[1] / "dashboard/frontend/package-lock.json"
WATCH = {"picomatch", "fdir", "tinyglobby", "vite"}
def main():
    packages = json.loads(LOCK.read_text(encoding="utf-8"))["packages"]
    found = []
    for path, meta in sorted(packages.items()):
        name = path.rsplit("node_modules/", 1)[-1]
        if name in WATCH:
            found.append({"path": path, "name": name, "version": meta.get("version"),
                          "dependencies": meta.get("dependencies", {})})
    print(json.dumps({"lockfile": str(LOCK), "packages": found}, indent=2, sort_keys=True))
    missing = WATCH - {item["name"] for item in found}
    if missing:
        raise SystemExit("Missing expected dependency records: " + ", ".join(sorted(missing)))
if __name__ == "__main__":
    main()
