#!/usr/bin/env python3
"""Read-only reproduction of the global workflow policy grep rules."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
RULES = {
    "write_permission": re.compile(r"contents:\s*write|actions:\s*write|packages:\s*write|pull-requests:\s*write|issues:\s*write", re.I),
    "auto_write": re.compile(r"git\s+push|gh\s+pr\s+merge|gh\s+release|create-pull-request|peter-evans/create-pull-request|--auto-fix|auto_fix|autofix", re.I),
    "cloud_deploy": re.compile(r"azure/webapps-deploy|aws-actions|google-github-actions/deploy|render deploy|flyctl deploy|railway up|vercel --prod|netlify deploy", re.I),
    "live_enabled": re.compile(r"LIVE_TRADING_ENABLED:\s*[\"']?(?:1|true|yes)[\"']?|SYSTEM3_LIVE_TRADING_ALLOWED:\s*[\"']?(?:1|true|yes)[\"']?", re.I),
}


def main() -> int:
    findings: list[dict[str, object]] = []
    files = sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")])
    for path in files:
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for rule, pattern in RULES.items():
                if pattern.search(line):
                    findings.append({
                        "rule": rule,
                        "file": path.relative_to(ROOT).as_posix(),
                        "line": number,
                        "text": line.strip()[:300],
                    })
    payload = {"workflow_files": len(files), "finding_count": len(findings), "findings": findings}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
