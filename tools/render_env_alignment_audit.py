#!/usr/bin/env python3
"""Audit downloaded Render env files without printing secret values."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "render_env_alignment"
ENV_FILES = {
    "backend": Path(r"C:\System3\genesis-system3-backend.env"),
    "worker": Path(r"C:\System3\genesis-system3-worker.env"),
    "shared": Path(r"C:\System3\dhan-shared-credentials.env"),
}

SECRET_KEY_MARKERS = ("TOKEN", "SECRET", "PIN", "KEY", "CLIENT_ID", "APP_ID")
REQUIRED_COMMON = {
    "SYSTEM3_DEPLOY_TARGET",
    "RENDER",
    "SYSTEM3_MODE",
    "ANALYZE_MODE",
    "LIVE_TRADING_ENABLED",
    "SYSTEM3_LIVE_TRADING_ALLOWED",
    "CLOUD_PAPER_ENGINE",
    "DEFER_INSTRUMENT_WARMUP",
    "MEM_LIMIT_MB",
    "MEM_WARN_MB",
    "MEM_GC_MB",
}
REQUIRED_DHAN = {
    "DHAN_CLIENT_ID",
    "DHAN_ACCESS_TOKEN",
    "DHAN_APP_ID",
    "DHAN_APP_SECRET",
    "DHAN_PIN",
    "DHAN_TOTP_SECRET",
}
BACKEND_REQUIRED = REQUIRED_COMMON | REQUIRED_DHAN | {"API_KEY", "REQUIRE_API_KEY", "WORKER_PUSH_TOKEN"}
WORKER_REQUIRED = REQUIRED_COMMON | REQUIRED_DHAN | {"WORKER_PUSH_TOKEN", "WEB_SERVICE_URL", "CLOUD_WORKER"}
SAFE_EXPECTED = {
    "LIVE_TRADING_ENABLED": {"0", "false", "False", ""},
    "SYSTEM3_LIVE_TRADING_ALLOWED": {"0", "false", "False", ""},
    "SYSTEM3_MODE": {"analyzer", "paper", "PAPER", "ANALYZER"},
    "ANALYZE_MODE": {"1", "true", "True"},
    "REQUIRE_API_KEY": {"true", "True", "1"},
}


def parse_env(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def redacted_value(key: str, value: str) -> str | bool:
    if not value:
        return False
    if any(marker in key.upper() for marker in SECRET_KEY_MARKERS):
        return "<redacted>"
    if key in SAFE_EXPECTED or key in {"RENDER", "CLOUD_WORKER", "CLOUD_PAPER_ENGINE", "DEFER_INSTRUMENT_WARMUP"}:
        return value
    return "<set>"


def service_result(name: str, env: dict[str, str], required: set[str]) -> dict:
    missing = sorted(required - set(env))
    empty = sorted(k for k in required if k in env and env.get(k, "") == "")
    safe_flags = {}
    blockers = []
    warnings = []
    for key, allowed in SAFE_EXPECTED.items():
        if key not in env:
            if key in required:
                blockers.append(f"{key} missing")
            continue
        value = env.get(key, "")
        ok = value in allowed
        safe_flags[key] = {"ok": ok, "value": redacted_value(key, value)}
        if not ok:
            blockers.append(f"{key} has unsafe/unexpected value")
    for key in ("CLOUD_PAPER_ENGINE", "DEFER_INSTRUMENT_WARMUP"):
        if key in env and env[key] not in {"0", "1", "true", "false", "True", "False"}:
            warnings.append(f"{key} has non-boolean-looking value")
    if missing:
        blockers.append("missing required keys: " + ", ".join(missing))
    if empty:
        blockers.append("empty required keys: " + ", ".join(empty))
    return {
        "file": str(ENV_FILES[name]),
        "exists": bool(env),
        "keyCount": len(env),
        "requiredPresent": not missing,
        "requiredNonEmpty": not empty,
        "missing": missing,
        "empty": empty,
        "safeFlags": safe_flags,
        "keysRedacted": {k: redacted_value(k, v) for k, v in sorted(env.items())},
        "blockers": blockers,
        "warnings": warnings,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    envs = {name: parse_env(path) for name, path in ENV_FILES.items()}
    results = {
        "backend": service_result("backend", envs["backend"], BACKEND_REQUIRED),
        "worker": service_result("worker", envs["worker"], WORKER_REQUIRED),
        "shared": service_result("shared", envs["shared"], REQUIRED_DHAN),
    }

    cross_warnings = []
    for key in REQUIRED_DHAN:
        vals = {name: env.get(key, "") for name, env in envs.items() if key in env}
        non_empty_vals = {v for v in vals.values() if v}
        if len(non_empty_vals) > 1:
            cross_warnings.append(f"{key} differs across downloaded env files")
    backend_key = envs["backend"].get("API_KEY", "")
    if envs["backend"].get("REQUIRE_API_KEY", "").lower() == "true" and not backend_key:
        results["backend"]["blockers"].append("REQUIRE_API_KEY=true but API_KEY is empty")

    all_blockers = []
    all_warnings = cross_warnings[:]
    for name, result in results.items():
        all_blockers.extend([f"{name}: {b}" for b in result["blockers"]])
        all_warnings.extend([f"{name}: {w}" for w in result["warnings"]])

    payload = {
        "generatedUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "PASS" if not all_blockers else "FAIL",
        "files": {name: str(path) for name, path in ENV_FILES.items()},
        "results": results,
        "blockers": all_blockers,
        "warnings": all_warnings,
        "notes": [
            "Secret values are not printed; only presence and selected safe flag values are shown.",
            "Broker funds/holdings/positions should remain protected behind dashboard auth.",
            "LIVE_TRADING_ENABLED and SYSTEM3_LIVE_TRADING_ALLOWED must remain false/0.",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# Render Env Alignment Audit",
        "",
        f"Generated UTC: `{payload['generatedUtc']}`",
        f"Status: **{payload['status']}**",
        "",
        "## Files",
        *[f"- {name}: `{path}`" for name, path in payload["files"].items()],
        "",
        "## Service Summary",
        "",
        "| Service | Keys | Required Present | Required Non-Empty |",
        "|---|---:|---|---|",
    ]
    for name, result in results.items():
        lines.append(
            f"| {name} | {result['keyCount']} | {result['requiredPresent']} | {result['requiredNonEmpty']} |"
        )
    lines.extend(["", "## Blockers", *(f"- {b}" for b in all_blockers or ["None"])])
    lines.extend(["", "## Warnings", *(f"- {w}" for w in all_warnings or ["None"])])
    lines.extend(["", "## Required Next Step"])
    if payload["status"] == "PASS":
        lines.append("- Deploy current code to Render, then unlock `/ui` with the backend `API_KEY`.")
    else:
        lines.append("- Fix blockers in Render env before relying on broker read-only dashboard data.")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "summary": str(OUT / "summary.json")}, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
