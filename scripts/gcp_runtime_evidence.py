#!/usr/bin/env python3
"""Create sanitized, fail-closed Google Cloud runtime evidence for System3.

The authoritative web runtime is automated PAPER mode. `AUTO_EXECUTE_TRADES=1`
means simulated PaperExecutor fills only; it is accepted only when PAPER mode,
CLOUD_PAPER_ENGINE=1 and both independent LIVE locks are false.
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.getenv("GCP_REGION", "asia-south1")
SERVICE = os.getenv("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
EXPECTED_SHA = os.getenv("GITHUB_SHA", "").strip()
OUT = Path(os.getenv("SYSTEM3_GCP_EVIDENCE_DIR", "reports/latest/gcp_runtime_lock"))
SAFE_ENV_NAMES = {
    "SYSTEM3_MODE",
    "ANALYZE_MODE",
    "CLOUD_PAPER_ENGINE",
    "AUTO_EXECUTE_TRADES",
    "LIVE_TRADING_ENABLED",
    "SYSTEM3_LIVE_TRADING_ALLOWED",
    "REQUIRE_API_KEY",
    "SYSTEM3_STATE_BACKEND",
    "SYSTEM3_REAL_ONLY",
    "DEPLOY_GIT_SHA",
    "SYSTEM3_DEPLOY_TARGET",
}
SECRET_BACKED_ENV_NAMES = {"API_KEY", "WORKER_PUSH_TOKEN"}


def _is_on(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _is_off(value: Any) -> bool:
    return str(value or "").strip().lower() in {"0", "false", "no", "off"}


def _run_json(args: list[str]) -> tuple[Any, dict[str, Any]]:
    proc = subprocess.run(args, text=True, capture_output=True, check=False, timeout=90)
    meta = {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "command": " ".join(args[:4]) + (" ..." if len(args) > 4 else ""),
    }
    if proc.returncode:
        meta["error_type"] = "gcloud_nonzero"
        return None, meta
    try:
        return json.loads(proc.stdout or "null"), meta
    except json.JSONDecodeError:
        meta["ok"] = False
        meta["error_type"] = "invalid_json"
        return None, meta


def _container(service: dict[str, Any]) -> dict[str, Any]:
    rows = (((service.get("spec") or {}).get("template") or {}).get("spec") or {}).get("containers") or []
    if not rows:
        rows = (service.get("template") or {}).get("containers") or []
    return rows[0] if rows else {}


def _runtime_env(service: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    env: dict[str, Any] = {}
    secret_refs: list[str] = []
    plaintext_secret_names: list[str] = []
    for row in _container(service).get("env") or []:
        name = str(row.get("name") or "")
        if not name:
            continue
        if "valueFrom" in row:
            secret_refs.append(name)
        elif name in SAFE_ENV_NAMES:
            env[name] = row.get("value")
        elif name in SECRET_BACKED_ENV_NAMES:
            plaintext_secret_names.append(name)
    return env, sorted(secret_refs), sorted(plaintext_secret_names)


def evaluate_safety(
    env: dict[str, Any], secret_refs: list[str], plaintext_secret_names: list[str]
) -> dict[str, Any]:
    mode = str(env.get("SYSTEM3_MODE") or "").strip().upper()
    analyze_mode = _is_on(env.get("ANALYZE_MODE"))
    cloud_paper_engine = _is_on(env.get("CLOUD_PAPER_ENGINE"))
    auto_execute_trades = _is_on(env.get("AUTO_EXECUTE_TRADES"))
    live_trading_enabled = not _is_off(env.get("LIVE_TRADING_ENABLED"))
    system3_live_trading_allowed = not _is_off(env.get("SYSTEM3_LIVE_TRADING_ALLOWED"))
    api_key_required = not _is_off(env.get("REQUIRE_API_KEY"))
    api_key_mounted = "API_KEY" in secret_refs
    api_key_plaintext_exposed = "API_KEY" in plaintext_secret_names
    dashboard_public_readonly = not api_key_required and not api_key_mounted and not api_key_plaintext_exposed

    paper_mode = mode == "PAPER" and not analyze_mode
    automated_paper = paper_mode and cloud_paper_engine and auto_execute_trades
    live_locks_ok = not live_trading_enabled and not system3_live_trading_allowed
    auto_execute_is_paper_only = automated_paper and live_locks_ok

    return {
        "system3_mode": mode,
        "analyze_mode": analyze_mode,
        "paper_mode": paper_mode,
        "cloud_paper_engine": cloud_paper_engine,
        "auto_execute_trades": auto_execute_trades,
        "auto_execute_is_paper_only": auto_execute_is_paper_only,
        "live_trading_enabled": live_trading_enabled,
        "system3_live_trading_allowed": system3_live_trading_allowed,
        "live_locks_ok": live_locks_ok,
        "api_key_required": api_key_required,
        "api_key_mounted": api_key_mounted,
        "api_key_plaintext_exposed": api_key_plaintext_exposed,
        "dashboard_public_readonly": dashboard_public_readonly,
        "secret_payloads_exposed": False,
    }


def safety_passes(safety: dict[str, Any]) -> bool:
    return bool(
        safety.get("paper_mode")
        and safety.get("cloud_paper_engine")
        and safety.get("auto_execute_trades")
        and safety.get("auto_execute_is_paper_only")
        and safety.get("live_locks_ok")
        and safety.get("dashboard_public_readonly")
        and not safety.get("api_key_plaintext_exposed")
    )


def safety_blockers(safety: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not safety.get("paper_mode"):
        blockers.append("SYSTEM3_MODE=PAPER with ANALYZE_MODE=0 is not proven.")
    if not safety.get("cloud_paper_engine"):
        blockers.append("CLOUD_PAPER_ENGINE=1 is not proven.")
    if not safety.get("auto_execute_trades"):
        blockers.append("AUTO_EXECUTE_TRADES=1 is not proven for PAPER simulation.")
    if not safety.get("live_locks_ok"):
        blockers.append("One or both independent LIVE-trading locks are not OFF.")
    if safety.get("auto_execute_trades") and not safety.get("auto_execute_is_paper_only"):
        blockers.append("AUTO_EXECUTE_TRADES is enabled outside the fully locked PAPER contract.")
    if not safety.get("dashboard_public_readonly"):
        blockers.append("Public read-only dashboard contract is not proven.")
    return blockers


def _serving_revision(service: dict[str, Any]) -> tuple[str, int]:
    for row in ((service.get("status") or {}).get("traffic") or []):
        percent = int(row.get("percent") or 0)
        revision = str(row.get("revisionName") or "")
        if revision and percent == 100:
            return revision, percent
    return "", 0


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    service, service_meta = _run_json(
        [
            "gcloud", "run", "services", "describe", SERVICE,
            f"--project={PROJECT}", f"--region={REGION}", "--format=json",
        ]
    )
    if not isinstance(service, dict):
        report = {
            "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            "project": PROJECT,
            "region": REGION,
            "service": SERVICE,
            "lock_result": "FAIL_CLOSED",
            "source_matches_deployment": False,
            "secret_values_exposed": False,
            "safety": {},
            "blockers": ["Cloud Run service evidence unavailable."],
            "commands": {"service": service_meta},
        }
        (OUT / "gcp_runtime_lock.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print("GCP_RUNTIME_EVIDENCE FAIL_CLOSED service_unavailable")
        return 2

    env, secret_refs, plaintext_secret_names = _runtime_env(service)
    safety = evaluate_safety(env, secret_refs, plaintext_secret_names)
    serving_revision, traffic_percent = _serving_revision(service)
    deployed_sha = str(env.get("DEPLOY_GIT_SHA") or "").strip()
    source_matches = bool(EXPECTED_SHA and deployed_sha == EXPECTED_SHA)
    blockers = safety_blockers(safety)
    if traffic_percent != 100:
        blockers.append(f"No single immutable revision has 100% traffic: {serving_revision or 'unknown'}={traffic_percent}%")
    if not source_matches:
        blockers.append(
            f"Serving DEPLOY_GIT_SHA does not match workflow SHA: serving={deployed_sha or 'missing'} expected={EXPECTED_SHA or 'missing'}"
        )

    passed = safety_passes(safety) and traffic_percent == 100 and source_matches
    report = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "project": PROJECT,
        "region": REGION,
        "service": SERVICE,
        "serving_revision": serving_revision,
        "traffic_percent": traffic_percent,
        "expected_git_sha": EXPECTED_SHA,
        "deployed_git_sha": deployed_sha,
        "source_matches_deployment": source_matches,
        "runtime_env": env,
        "secret_env_refs": secret_refs,
        "plaintext_secret_names": plaintext_secret_names,
        "secret_values_exposed": False,
        "safety": safety,
        "blockers": blockers,
        "lock_result": "PASS" if passed else "FAIL_CLOSED",
        "commands": {"service": service_meta},
    }
    (OUT / "gcp_runtime_lock.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "GCP_RUNTIME_EVIDENCE",
        json.dumps(
            {
                "lock_result": report["lock_result"],
                "serving_revision": serving_revision,
                "source_matches_deployment": source_matches,
                "safety": safety,
                "blockers": blockers,
            },
            sort_keys=True,
        ),
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
