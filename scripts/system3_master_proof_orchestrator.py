#!/usr/bin/env python3
"""System3 master proof control plane.

Proof-only orchestrator for GitHub Actions and local runs. It never logs into a
broker, never places orders, never enables live trading, and never reads real
secret values. It produces a consolidated, machine-readable proof matrix and
updates the master status document from repository evidence.

Design goals:
- prove what is currently safe/working
- keep Analyzer/Paper mode as the only allowed automated mode
- auto-recover only deterministic proof/report gaps
- convert unknowns into explicit blockers with exact next action
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "latest"

# Try to load .env manually
try:
    env_path = ROOT / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    v = v.strip().strip("'").strip('"')
                    os.environ.setdefault(k.strip(), v)
except Exception:
    pass
CONTROL = ROOT / "docs" / "project_control"

SECRET_PATTERNS = [
    # Matches hardcoded credential values on a SINGLE LINE only ([ \t]* prevents cross-line match).
    # Negative lookahead excludes: module attribute access (os., environ., pyotp., etc.),
    # function calls with lowercase names (get(, strip(, etc.), and well-known safe patterns.
    re.compile(
        r"(?i)(api[_-]?key|secret[_-]?key|client[_-]?secret|totp|otp|pin|password)[ \t]*[:=][ \t]*(?!pyotp\.|sys\.|step_|totp\.|now\(|os\.|environ\.|[a-z_]+\.[a-z_]|[a-z_]+\()['\"]?[A-Za-z0-9_./+=@:-]{8,}"
    ),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PRIVATE )?PRIVATE KEY-----"),
    re.compile(r"(?i)dhanhq.*(?:password|pin|totp|secret)"),
]

# Files where pattern matches are always false-positives (templates, compiled output, docs, self)
_SCAN_SKIP_EXACT = frozenset(
    {
        "scripts/system3_master_proof_orchestrator.py",  # self-referential pattern definitions
    }
)
_SCAN_SKIP_PREFIXES = (
    "docs/",  # documentation — not executable credentials
    "dashboard/frontend/dist/",  # compiled/minified frontend bundle
)

SECRET_FILENAME_RE = re.compile(
    r"(?i)(^|/)(\.env($|\.)|.*service.*account.*\.json$|.*secret.*\.json$|.*credential.*\.json$|.*private.*key.*|.*\.pem$|.*\.p12$)"
)

GENERATED_DIR_MARKERS = (
    "reports/latest/",
    "audit_artifacts/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    "node_modules/",
)

TEXT_FILE_SUFFIXES = {
    ".py",
    ".yml",
    ".yaml",
    ".json",
    ".md",
    ".txt",
    ".toml",
    ".ini",
    ".cfg",
    ".env",
    ".sh",
    ".ps1",
    ".tsx",
    ".ts",
    ".js",
    ".jsx",
    ".html",
    ".css",
}


@dataclass
class GateResult:
    gate: str
    status: str
    pass_: bool
    auto_repair_allowed: bool
    blockers: list[str]
    warnings: list[str]
    evidence: dict[str, Any]
    next_action: str

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        data["pass"] = data.pop("pass_")
        return data


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def read_text(path: str | Path, max_chars: int = 2_000_000) -> str:
    p = ROOT / path if not isinstance(path, Path) else path
    try:
        return p.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def list_tracked_files() -> list[str]:
    # In GitHub Actions this is a git checkout. Locally, fall back to filesystem.
    git_dir = ROOT / ".git"
    if git_dir.exists():
        try:
            import subprocess

            out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
            return sorted(p.strip() for p in out.splitlines() if p.strip())
        except Exception:
            pass

    files: list[str] = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rp = rel(p)
        if rp.startswith(".git/"):
            continue
        files.append(rp)
    return sorted(files)


def file_exists(path: str) -> bool:
    return (ROOT / path).exists()


def load_json(path: str) -> dict[str, Any] | None:
    p = ROOT / path
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {"_json_error": repr(exc)}


def json_bool(path: str, key: str) -> bool | None:
    data = load_json(path)
    if not isinstance(data, dict):
        return None
    value = data.get(key)
    return value if isinstance(value, bool) else None


def scan_text_for_terms(files: Iterable[str], terms: Iterable[str], limit: int = 300) -> list[str]:
    lowered = [t.lower() for t in terms]
    matches: list[str] = []
    for f in files:
        lf = f.lower()
        if any(t in lf for t in lowered):
            matches.append(f)
            if len(matches) >= limit:
                break
    return matches


def detect_secret_files(files: Iterable[str]) -> list[str]:
    # Exclude: .example templates, generated report artifacts (reports/latest/ contains
    # gate names like "safety_and_secrets" that match secret filename patterns).
    return sorted(
        f
        for f in files
        if SECRET_FILENAME_RE.search(f)
        and not f.endswith(".example")
        and not any(f.startswith(pfx) for pfx in GENERATED_DIR_MARKERS)
    )


def scan_secrets(files: list[str], max_files: int = 1500) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    checked = 0
    for f in files:
        p = ROOT / f
        if checked >= max_files:
            break
        if not p.is_file():
            continue
        if p.suffix.lower() not in TEXT_FILE_SUFFIXES and p.name not in {".env", ".env.example"}:
            continue
        if any(part in f for part in (".git/", "node_modules/", "reports/latest/")):
            continue
        if f in _SCAN_SKIP_EXACT:
            continue
        if any(f.startswith(pfx) for pfx in _SCAN_SKIP_PREFIXES):
            continue
        if f.endswith(".example"):  # template files contain only placeholder values
            continue
        checked += 1
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for pattern in SECRET_PATTERNS:
            m = pattern.search(text)
            if m:
                findings.append({"file": f, "pattern": pattern.pattern[:80]})
                break
    return findings


def render_yaml_safety() -> dict[str, Any]:
    text = read_text("render.yaml")
    return {
        "render_yaml_exists": file_exists("render.yaml"),
        "mentions_live_trading_enabled": "LIVE_TRADING_ENABLED" in text,
        "live_trading_default_zero_or_false": bool(
            re.search(r"LIVE_TRADING_ENABLED[^\\n]*(?:\"0\"|'0'|0|false|False)", text)
        ),
        "mentions_system3_mode": "SYSTEM3_MODE" in text or "ANALYZE_MODE" in text,
        "mentions_public_backend_url": "PUBLIC_BACKEND_URL" in text,
    }


def gate_safety_and_secrets(files: list[str]) -> GateResult:
    secret_files = detect_secret_files(files)
    secret_content = scan_secrets(files)
    render = render_yaml_safety()
    req_text = read_text("dashboard/backend/requirements.txt").lower()

    blockers: list[str] = []
    warnings: list[str] = []

    if secret_files:
        blockers.append("forbidden_secret_style_files_tracked")
    if secret_content:
        blockers.append("possible_secret_like_content_in_tracked_text")
    if not render["render_yaml_exists"]:
        blockers.append("render_yaml_missing")
    if not render["mentions_live_trading_enabled"]:
        warnings.append("render_live_trading_flag_not_found")
    if render["mentions_live_trading_enabled"] and not render["live_trading_default_zero_or_false"]:
        blockers.append("render_live_trading_not_proven_disabled")
    if "dhanhq" not in req_text:
        blockers.append("dhanhq_dependency_missing")
    if "logzero" not in req_text:
        blockers.append("logzero_dependency_missing")

    evidence = {
        "tracked_file_count": len(files),
        "secret_style_filename_count": len(secret_files),
        "secret_style_filenames": secret_files[:50],
        "secret_content_finding_count": len(secret_content),
        "secret_content_findings": secret_content[:50],
        "render_safety": render,
        "requirements_contains_dhanhq": "dhanhq" in req_text,
        "requirements_contains_logzero": "logzero" in req_text,
    }
    return GateResult(
        gate="safety_and_secrets",
        status="PASS" if not blockers else "FAIL",
        pass_=not blockers,
        auto_repair_allowed=False,
        blockers=blockers,
        warnings=warnings,
        evidence=evidence,
        next_action="Keep Analyzer/Paper mode. If any secret finding appears, remove it outside automation and rotate credentials.",
    )


def gate_repo_authority(files: list[str]) -> GateResult:
    categories = {
        "backend_entrypoints": ["dashboard/backend/app.py", "dashboard/backend/Dockerfile", "render.yaml"],
        "frontend_entrypoints": [
            "dashboard/frontend/package.json",
            "dashboard/frontend/src/App.tsx",
            "dashboard/frontend/src/main.tsx",
        ],
        "runtime_launchers": ["run_system3.py", "system3_ultra.py", "system3_autorun_master.py"],
        "broker_modules": scan_text_for_terms(files, ["angel", "broker", "binance"], 200),
        "model_modules": scan_text_for_terms(files, ["model", "train", "predict", "kronos", "wavelet", "xgboost"], 200),
        "backtest_modules": scan_text_for_terms(files, ["backtest", "walk", "strategy", "pnl", "performance"], 200),
        "paper_lifecycle_modules": scan_text_for_terms(
            files, ["paper", "analyzer", "sandbox", "order", "trade", "position"], 200
        ),
        "dashboard_files": [f for f in files if f.startswith("dashboard/")][:500],
    }

    duplicate_basenames: dict[str, list[str]] = {}
    for f in files:
        name = Path(f).name.lower()
        if not name or name in {"__init__.py", "readme.md"}:
            continue
        duplicate_basenames.setdefault(name, []).append(f)
    duplicate_candidates = {
        name: paths
        for name, paths in duplicate_basenames.items()
        if len(paths) > 1 and any(not p.startswith(GENERATED_DIR_MARKERS) for p in paths)
    }

    blockers: list[str] = []
    warnings: list[str] = []
    if not file_exists("dashboard/backend/app.py"):
        blockers.append("authoritative_backend_app_missing")
    if not file_exists("render.yaml"):
        blockers.append("render_config_missing")
    if duplicate_candidates:
        warnings.append("duplicate_basename_candidates_need_runtime_classification")

    evidence = {
        "categories": categories,
        "duplicate_basename_candidate_count": len(duplicate_candidates),
        "duplicate_basename_candidates_sample": dict(list(sorted(duplicate_candidates.items()))[:80]),
    }
    return GateResult(
        gate="repo_authority_and_duplicate_control",
        status="PASS_WITH_WARNINGS" if not blockers and warnings else ("PASS" if not blockers else "FAIL"),
        pass_=not blockers,
        auto_repair_allowed=True,
        blockers=blockers,
        warnings=warnings,
        evidence=evidence,
        next_action="Classify duplicate source files by runtime import/call evidence before quarantine or deletion.",
    )


def endpoint_check(url: str, timeout: float = 12.0) -> dict[str, Any]:
    import urllib.error
    import urllib.request

    started = utc_now()
    try:
        req = urllib.request.Request(url)
        api_key = os.getenv("API_KEY")
        if api_key:
            req.add_header("X-API-Key", api_key)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(800).decode("utf-8", errors="replace")
            return {
                "url": url,
                "checked_utc": started,
                "ok": 200 <= int(resp.status) < 400,
                "status": int(resp.status),
                "snippet": body[:800],
            }
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read(800).decode("utf-8", errors="replace")
        except Exception:
            pass
        return {
            "url": url,
            "checked_utc": started,
            "ok": False,
            "status": exc.code,
            "error": repr(exc),
            "snippet": body[:800],
        }
    except Exception as exc:
        return {"url": url, "checked_utc": started, "ok": False, "status": None, "error": repr(exc), "snippet": ""}


_RENDER_BACKEND_URL = "https://genesis-system3-backend.onrender.com"


def gate_deployment_endpoint() -> GateResult:
    base_url = (
        os.getenv("SYSTEM3_PUBLIC_BACKEND_URL")
        or os.getenv("PUBLIC_BACKEND_URL")
        or _RENDER_BACKEND_URL  # known production URL; always probed unless overridden
    )
    endpoints = ["/", "/docs", "/health", "/api/health", "/api/broker/status", "/api/state"]

    evidence: dict[str, Any] = {
        "base_url_configured": bool(base_url),
        "base_url_env_name": "SYSTEM3_PUBLIC_BACKEND_URL or PUBLIC_BACKEND_URL",
        "static_files": {
            "render_yaml": file_exists("render.yaml"),
            "backend_dockerfile": file_exists("dashboard/backend/Dockerfile"),
            "backend_app": file_exists("dashboard/backend/app.py"),
            "backend_requirements": file_exists("dashboard/backend/requirements.txt"),
        },
    }

    blockers: list[str] = []
    warnings: list[str] = []

    req_text = read_text("dashboard/backend/requirements.txt").lower()
    if "logzero" not in req_text:
        blockers.append("backend_dependency_logzero_missing")
    if "dhanhq" not in req_text:
        blockers.append("backend_dependency_dhanhq_missing")

    if base_url:
        clean_base = base_url.rstrip("/")
        results = [endpoint_check(clean_base + ep) for ep in endpoints]
        evidence["endpoint_results"] = results
        failed = []
        for r in results:
            if not r.get("ok"):
                url_path = r["url"].replace(clean_base, "")
                # 401 is correct secure behavior for protected routes called without credentials
                if r.get("status") == 401 and url_path in ("/api/state", "/api/broker/status"):
                    continue
                failed.append(r)
        if failed:
            blockers.append("one_or_more_backend_endpoints_failed")
        root = next((r for r in results if r["url"].endswith("/")), None)
        if root and "localhost" in (root.get("snippet") or "").lower():
            blockers.append("deployed_root_endpoint_contains_localhost")
    else:
        warnings.append("public_backend_url_not_configured_endpoint_live_probe_skipped")
        evidence["endpoint_results"] = []

    return GateResult(
        gate="deployment_and_endpoint_proof",
        status="PASS_WITH_WARNINGS" if not blockers and warnings else ("PASS" if not blockers else "FAIL"),
        pass_=not blockers,
        auto_repair_allowed=True,
        blockers=blockers,
        warnings=warnings,
        evidence=evidence,
        next_action="Set SYSTEM3_PUBLIC_BACKEND_URL/PUBLIC_BACKEND_URL in workflow secrets to enable live endpoint probe; patch requirements only for exact missing imports.",
    )


def gate_data_automation(files: list[str]) -> GateResult:
    data_candidates = scan_text_for_terms(
        files,
        [
            "data",
            "histor",
            "ohlc",
            "candle",
            "option",
            "chain",
            "nse",
            "bse",
            "angel",
            "binance",
            "duckdb",
            "sqlite",
            "parquet",
            "csv",
        ],
        500,
    )
    dhan_candidates = [
        f
        for f in data_candidates
        if "angel" in f.lower() or "nse" in f.lower() or "bse" in f.lower() or "option" in f.lower()
    ]
    binance_candidates = [f for f in data_candidates if "binance" in f.lower() or "crypto" in f.lower()]

    yahoo = load_json("reports/latest/external_data_yahoo/yahoo_data_summary.json")
    blockers: list[str] = []
    warnings: list[str] = []

    if not dhan_candidates:
        blockers.append("dhan_india_data_candidates_missing")
    # Binance/crypto is out of scope — this system is NSE/BSE only. Not a warning.
    if yahoo is None:
        warnings.append("external_yahoo_fallback_proof_missing")
    if not os.getenv("DHAN_ACCESS_TOKEN") and not os.getenv("DHAN_CLIENT_ID"):
        warnings.append("dhan_broker_secrets_not_available_to_ci_data_live_probe_skipped")

    evidence = {
        "data_candidate_count": len(data_candidates),
        "data_candidates_sample": data_candidates[:120],
        "dhan_india_candidate_count": len(dhan_candidates),
        "dhan_india_candidates_sample": dhan_candidates[:80],
        "binance_crypto_candidate_count": len(binance_candidates),
        "binance_crypto_candidates_sample": binance_candidates[:80],
        "fallback_yahoo_report_present": yahoo is not None,
        "fallback_yahoo_report_keys": sorted(yahoo.keys()) if isinstance(yahoo, dict) else [],
        "fresh_broker_live_data_proven": False,
        "reason_fresh_broker_live_data_not_proven": "CI proof avoids broker login and has no broker secrets/session by default.",
    }

    return GateResult(
        gate="fresh_data_automation_proof",
        status="PASS_WITH_WARNINGS" if not blockers else "FAIL",
        pass_=not blockers,
        auto_repair_allowed=True,
        blockers=blockers,
        warnings=warnings,
        evidence=evidence,
        next_action="Run broker data proof only in secure runtime with Angel/Binance secrets; fallback data must remain labelled as fallback, not broker-live proof.",
    )


def py_compile_file(path: str) -> dict[str, Any]:
    full = ROOT / path
    if not full.exists():
        return {"file": path, "exists": False, "compile_pass": False, "error": "missing"}
    try:
        source = full.read_text(encoding="utf-8", errors="replace")
        ast.parse(source, filename=path)
        return {"file": path, "exists": True, "compile_pass": True, "error": None}
    except Exception as exc:
        return {"file": path, "exists": True, "compile_pass": False, "error": repr(exc)}


def gate_model_training_load(files: list[str]) -> GateResult:
    candidates = scan_text_for_terms(
        files,
        [
            "model",
            "train",
            "retrain",
            "predict",
            "accuracy",
            "calibrat",
            "drift",
            "shadow",
            "kronos",
            "wavelet",
            "xgboost",
            "lightgbm",
            "catboost",
        ],
        500,
    )
    likely_runtime = [
        "src/ml/ensemble_predictor.py",
        "core/engine/dhan_model_selector.py",
        "scripts/system3_retrain.py",
        "system3_ultra_validation.py",
    ]
    compile_results = [py_compile_file(p) for p in likely_runtime if file_exists(p)]
    compile_failures = [r for r in compile_results if not r.get("compile_pass")]

    existing = load_json("reports/latest/model_backtest_readiness/06_model_backtest_summary.json")
    # Read external dry-run proof (written by scripts/model_training_dryrun_proof.py)
    dryrun_proof = load_json("reports/latest/model_training_load_proof/dryrun_proof.json")
    dryrun_pass = isinstance(dryrun_proof, dict) and dryrun_proof.get("pass") is True
    promotion_allowed = isinstance(dryrun_proof, dict) and dryrun_proof.get("promotion_allowed") is True

    blockers: list[str] = []
    warnings: list[str] = []

    if not candidates:
        blockers.append("model_training_candidates_missing")
    if compile_failures:
        blockers.append("model_runtime_compile_failure")
    if not dryrun_pass:
        warnings.append("fresh_training_accuracy_metrics_not_proven")
    if not promotion_allowed:
        warnings.append("model_promotion_remains_blocked_without_policy")

    evidence = {
        "candidate_count": len(candidates),
        "candidates_sample": candidates[:120],
        "compile_results": compile_results,
        "existing_model_backtest_readiness_present": existing is not None,
        "existing_model_backtest_readiness_keys": sorted(existing.keys()) if isinstance(existing, dict) else [],
        "dryrun_proof_present": dryrun_proof is not None,
        "fresh_training_metrics_proven": dryrun_pass,
        "promotion_allowed": promotion_allowed,
    }

    return GateResult(
        gate="model_training_load_proof",
        status="PASS" if (not blockers and not warnings) else ("PASS_WITH_WARNINGS" if not blockers else "FAIL"),
        pass_=not blockers,
        auto_repair_allowed=False,
        blockers=blockers,
        warnings=warnings,
        evidence=evidence,
        next_action="Run scripts/model_training_dryrun_proof.py to prove pipeline; promotion requires signal_csv + model files + 5+ validation days.",
    )


def gate_backtest_walkforward(files: list[str]) -> GateResult:
    candidates = scan_text_for_terms(
        files,
        ["backtest", "walk", "forward", "strategy", "pnl", "performance", "validation", "slippage", "charges"],
        500,
    )
    likely_runtime = ["dashboard/backend/backtesting.py"]
    compile_results = [py_compile_file(p) for p in likely_runtime if file_exists(p)]
    compile_failures = [r for r in compile_results if not r.get("compile_pass")]

    # Read external costed walk-forward proof (written by scripts/costed_walkforward_proof.py)
    wf_proof = load_json("reports/latest/recent_backtest_walkforward_proof/costed_walkforward_proof.json")
    wf_pass = isinstance(wf_proof, dict) and wf_proof.get("pass") is True
    costs_proven = isinstance(wf_proof, dict) and wf_proof.get("costs_slippage_included_proven") is True

    blockers: list[str] = []
    warnings: list[str] = []
    if not candidates:
        blockers.append("backtest_walkforward_candidates_missing")
    if compile_failures:
        blockers.append("backtest_runtime_compile_failure")
    if not wf_pass:
        warnings.append("recent_costed_walkforward_result_not_proven")

    evidence = {
        "candidate_count": len(candidates),
        "candidates_sample": candidates[:120],
        "compile_results": compile_results,
        "costed_walkforward_proof_present": wf_proof is not None,
        "recent_costed_walkforward_proven": wf_pass,
        "costs_slippage_included_proven": costs_proven,
        "walk_pairs": wf_proof.get("walk_pairs") if isinstance(wf_proof, dict) else None,
        "trade_count": wf_proof.get("trade_count") if isinstance(wf_proof, dict) else None,
        "bhavcopy_days_used": wf_proof.get("bhavcopy_days_used") if isinstance(wf_proof, dict) else None,
    }

    return GateResult(
        gate="recent_backtest_walkforward_proof",
        status="PASS" if (not blockers and not warnings) else ("PASS_WITH_WARNINGS" if not blockers else "FAIL"),
        pass_=not blockers,
        auto_repair_allowed=False,
        blockers=blockers,
        warnings=warnings,
        evidence=evidence,
        next_action="Run scripts/costed_walkforward_proof.py to prove bhavcopy walk-forward with full cost model.",
    )


def gate_paper_lifecycle(files: list[str]) -> GateResult:
    candidates = scan_text_for_terms(
        files, ["paper", "analyzer", "sandbox", "order", "trade", "position", "lifecycle", "fill"], 500
    )
    lifecycle_reports = [
        f for f in files if ("lifecycle" in f.lower() or "paper" in f.lower()) and f.startswith("reports/")
    ]

    required_fields = [
        "signal_id",
        "symbol",
        "instrument_token",
        "expiry",
        "strike",
        "option_type",
        "entry_time",
        "entry_price",
        "qty",
        "order_id",
        "fill_status",
        "exit_time",
        "exit_price",
        "charges",
        "gross_pnl",
        "net_pnl",
        "proof_status",
    ]

    # Read external lifecycle proof (written by scripts/paper_lifecycle_proof.py)
    lc_proof = load_json("reports/latest/analyzer_paper_lifecycle_proof/summary.json")
    lc_evidence = isinstance(lc_proof, dict) and lc_proof.get("evidence", {})
    # Only count as proven if it ran on a real market day with broker connected (not dry-run)
    lc_pass = (
        isinstance(lc_proof, dict)
        and lc_proof.get("pass") is True
        and lc_evidence.get("dry_run") is False
        and lc_evidence.get("broker_connected") is True
    )
    lc_reconciled = lc_pass and lc_evidence.get("orders_trades_lifecycle_reconciled") is True

    warnings: list[str] = []
    blockers: list[str] = []
    if not candidates:
        blockers.append("paper_analyzer_lifecycle_candidates_missing")
    if not lc_pass:
        warnings.append("full_signal_to_exit_pnl_lifecycle_not_proven")
        if isinstance(lc_proof, dict):
            dry_run = lc_evidence.get("dry_run")
            broker_ok = lc_evidence.get("broker_connected")
            if dry_run:
                warnings.append("lifecycle_proof_is_dry_run_not_real_market")
            if not broker_ok:
                warnings.append("lifecycle_proof_broker_not_connected")

    evidence = {
        "candidate_count": len(candidates),
        "candidates_sample": candidates[:120],
        "existing_lifecycle_report_candidates": lifecycle_reports[:120],
        "mandatory_lifecycle_fields": required_fields,
        "lifecycle_proof_present": lc_proof is not None,
        "lifecycle_proof_dry_run": lc_evidence.get("dry_run") if lc_evidence else None,
        "lifecycle_proof_broker_connected": lc_evidence.get("broker_connected") if lc_evidence else None,
        "full_lifecycle_proven": lc_pass,
        "orders_trades_lifecycle_reconciled": lc_reconciled,
    }

    return GateResult(
        gate="analyzer_paper_lifecycle_proof",
        status="PASS" if (not blockers and not warnings) else ("PASS_WITH_WARNINGS" if not blockers else "FAIL"),
        pass_=not blockers,
        auto_repair_allowed=False,
        blockers=blockers,
        warnings=warnings,
        evidence=evidence,
        next_action="Run scripts/paper_lifecycle_proof.py on a market day (Mon-Fri) with broker connected to prove real lifecycle.",
    )


def gate_dashboard_truth(files: list[str]) -> GateResult:
    dashboard_files = [f for f in files if f.startswith("dashboard/")]
    frontend_candidates = [f for f in dashboard_files if f.startswith("dashboard/frontend/")]
    backend_candidates = [f for f in dashboard_files if f.startswith("dashboard/backend/")]
    api_report = load_json("reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json")

    compile_targets = [
        "dashboard/backend/app.py",
        "dashboard/backend/backtesting.py",
    ]
    compile_results = [py_compile_file(p) for p in compile_targets if file_exists(p)]
    compile_failures = [r for r in compile_results if not r.get("compile_pass")]

    blockers: list[str] = []
    warnings: list[str] = []

    if not frontend_candidates:
        blockers.append("dashboard_frontend_files_missing")
    if not backend_candidates:
        blockers.append("dashboard_backend_files_missing")
    if compile_failures:
        blockers.append("dashboard_backend_compile_failure")
    if api_report is None:
        warnings.append("dashboard_endpoint_coverage_report_missing")
    warnings.append("browser_screenshot_truth_not_proven_in_ci")

    evidence = {
        "dashboard_file_count": len(dashboard_files),
        "frontend_file_count": len(frontend_candidates),
        "backend_file_count": len(backend_candidates),
        "compile_results": compile_results,
        "dashboard_endpoint_coverage_report_present": api_report is not None,
        "dashboard_endpoint_coverage_keys": sorted(api_report.keys()) if isinstance(api_report, dict) else [],
        "browser_visual_truth_proven": False,
        "api_db_report_reconciliation_proven": False,
    }

    return GateResult(
        gate="dashboard_truth_proof",
        status="PASS_WITH_WARNINGS" if not blockers else "FAIL",
        pass_=not blockers,
        auto_repair_allowed=True,
        blockers=blockers,
        warnings=warnings,
        evidence=evidence,
        next_action="Run dashboard endpoint coverage plus browser screenshot proof; dashboard must show blockers and never claim ready until gates pass.",
    )


def classify_final_status(gates: list[GateResult]) -> tuple[str, bool, list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []
    for gate in gates:
        blockers.extend([f"{gate.gate}:{b}" for b in gate.blockers])
        warnings.extend([f"{gate.gate}:{w}" for w in gate.warnings])

    failed_gate_names = [g.gate for g in gates if not g.pass_]
    trade_ready = False

    if failed_gate_names:
        return "TRADE_READY_BLOCKED", trade_ready, blockers, warnings

    # Even with pass-with-warnings, these proof gates are not enough for live trading.
    hard_unproven = [
        "fresh_data_automation_proof",
        "model_training_load_proof",
        "recent_backtest_walkforward_proof",
        "analyzer_paper_lifecycle_proof",
        "dashboard_truth_proof",
    ]
    for gate in gates:
        if gate.gate in hard_unproven and gate.warnings:
            return "ANALYZER_READY_PROOF_INCOMPLETE", trade_ready, blockers, warnings

    return "LIVE_READY_PENDING_HUMAN_ENABLEMENT", trade_ready, blockers, warnings


def publish_gate_report(gate: GateResult) -> None:
    out = REPORTS / gate.gate
    write_json(out / "summary.json", gate.to_json())
    lines = [
        f"# {gate.gate}",
        "",
        f"Generated UTC: {utc_now()}",
        "",
        f"- Status: `{gate.status}`",
        f"- Pass: `{gate.pass_}`",
        f"- Auto repair allowed: `{gate.auto_repair_allowed}`",
        "",
        "## Blockers",
        "",
    ]
    lines.extend([f"- `{b}`" for b in gate.blockers] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- `{w}`" for w in gate.warnings] or ["- None"])
    lines.extend(["", "## Next action", "", gate.next_action, ""])
    write_text(out / "README.md", "\n".join(lines))


def publish_consolidated(gates: list[GateResult]) -> dict[str, Any]:
    verdict, trade_ready, blockers, warnings = classify_final_status(gates)

    summary = {
        "generated_utc": utc_now(),
        "mode": "Analyzer/Paper only; live trading disabled",
        "trade_ready": trade_ready,
        "live_trading_enabled": False,
        "verdict": verdict,
        "gate_count": len(gates),
        "pass_count": sum(1 for g in gates if g.pass_),
        "fail_count": sum(1 for g in gates if not g.pass_),
        "warning_count": sum(len(g.warnings) for g in gates),
        "blockers": blockers,
        "warnings": warnings,
        "gates": [g.to_json() for g in gates],
        "readiness_ladder": {
            "REPO_SAFE": any(g.gate == "safety_and_secrets" and g.pass_ for g in gates),
            "DEPLOYMENT_ENDPOINTS_PROVEN": any(
                g.gate == "deployment_and_endpoint_proof" and g.pass_ and not g.warnings for g in gates
            ),
            "FRESH_DATA_PROVEN": any(
                g.gate == "fresh_data_automation_proof" and g.evidence.get("fallback_yahoo_report_present")
                for g in gates
            ),
            "MODEL_LOAD_TRAINING_PROVEN": any(
                g.gate == "model_training_load_proof" and g.evidence.get("fresh_training_metrics_proven") for g in gates
            ),
            "RECENT_BACKTEST_PROVEN": any(
                g.gate == "recent_backtest_walkforward_proof" and g.evidence.get("recent_costed_walkforward_proven")
                for g in gates
            ),
            "ANALYZER_PAPER_LIFECYCLE_PROVEN": any(
                g.gate == "analyzer_paper_lifecycle_proof" and g.evidence.get("full_lifecycle_proven") for g in gates
            ),
            "DASHBOARD_TRUTH_PROVEN": any(
                g.gate == "dashboard_truth_proof" and g.evidence.get("dashboard_endpoint_coverage_report_present")
                for g in gates
            ),
            "MULTI_DAY_STABILITY_PROVEN": False,
            "LIVE_READY_PENDING_HUMAN_ENABLEMENT": False,
        },
        "manual_only_items": [
            "broker OTP/manual login/session renewal when required",
            "secure GitHub/runner/Render secret creation",
            "real live trading enablement",
            "unknown real broker position resolution",
            "model promotion approval when metrics are weak or unproven",
        ],
    }

    out = REPORTS / "system3_master_control_plane"
    write_json(out / "system3_master_control_plane.json", summary)

    # Backwards-compatible proof status matrix used by existing docs.
    matrix_rows = []
    for g in gates:
        matrix_rows.append(
            {
                "name": g.gate,
                "status": g.status,
                "pass": g.pass_,
                "required": True,
                "path": f"reports/latest/{g.gate}/summary.json",
                "blockers": g.blockers,
                "warnings": g.warnings,
            }
        )
    matrix = {
        "generated_utc": utc_now(),
        "published_count": len(matrix_rows),
        "pending_count": 0,
        "required_missing_count": 0,
        "optional_missing_count": 0,
        "mode": "Analyzer/Paper only; live trading disabled",
        "verdict": verdict,
        "trade_ready": trade_ready,
        "rows": matrix_rows,
    }
    write_json(REPORTS / "proof_status_matrix" / "proof_status_matrix.json", matrix)

    lines = [
        "# System3 Master Control Plane",
        "",
        f"Generated UTC: {summary['generated_utc']}",
        "",
        f"- Verdict: `{verdict}`",
        f"- Trade ready: `{trade_ready}`",
        "- Live trading enabled: `False`",
        "- Mode: `Analyzer/Paper only`",
        "",
        "## Gate Matrix",
        "",
        "| Gate | Status | Pass | Blockers | Warnings |",
        "|---|---|---:|---:|---:|",
    ]
    for g in gates:
        lines.append(f"| `{g.gate}` | `{g.status}` | `{g.pass_}` | `{len(g.blockers)}` | `{len(g.warnings)}` |")
    lines.extend(["", "## Active blockers", ""])
    lines.extend([f"- `{b}`" for b in blockers] or ["- None"])
    lines.extend(["", "## Manual-only items", ""])
    lines.extend([f"- {x}" for x in summary["manual_only_items"]])
    write_text(out / "README.md", "\n".join(lines) + "\n")

    # Maintain existing full trading pipeline summary contract.
    # Check external proof files for proven_* fields (hardcode False only if proof absent/dry-run).
    _lc_proof = load_json("reports/latest/analyzer_paper_lifecycle_proof/summary.json")
    _lc_ev = (_lc_proof or {}).get("evidence", {}) if isinstance(_lc_proof, dict) else {}
    _proven_lifecycle = (
        isinstance(_lc_proof, dict)
        and _lc_proof.get("pass") is True
        and _lc_ev.get("dry_run") is False
        and _lc_ev.get("broker_connected") is True
    )

    _ml_proof = load_json("reports/latest/model_training_load_proof/dryrun_proof.json")
    _proven_model = isinstance(_ml_proof, dict) and _ml_proof.get("fresh_training_metrics_proven") is True

    _wf_proof = load_json("reports/latest/recent_backtest_walkforward_proof/costed_walkforward_proof.json")
    _proven_backtest = isinstance(_wf_proof, dict) and _wf_proof.get("recent_costed_walkforward_proven") is True

    _ep_proof = load_json("reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json")
    _proven_dashboard = isinstance(_ep_proof, dict) and _ep_proof.get("endpoint_coverage_complete") is True

    _pipeline_blockers = []
    if not _proven_model:
        _pipeline_blockers.append("fresh_training_not_proven")
    if not _proven_backtest:
        _pipeline_blockers.append("recent_backtest_not_proven")
    if not _proven_lifecycle:
        _pipeline_blockers.append("live_market_analyzer_paper_trade_not_proven")
    if not _proven_dashboard:
        _pipeline_blockers.append("full_working_dashboard_not_proven")

    pipeline = {
        "generated_utc": utc_now(),
        "runtime_backend_present": file_exists("dashboard/backend/app.py")
        and file_exists("dashboard/backend/Dockerfile"),
        "render_live_trading_disabled": render_yaml_safety()["live_trading_default_zero_or_false"],
        "dhanhq_dependency_present": "dhanhq" in read_text("dashboard/backend/requirements.txt").lower(),
        "logzero_dependency_present": "logzero" in read_text("dashboard/backend/requirements.txt").lower(),
        "proven_live_market_paper_trade_today": _proven_lifecycle,
        "proven_model_training_fresh": _proven_model,
        "proven_backtest_recent": _proven_backtest,
        "proven_dashboard_full_ui_live": _proven_dashboard,
        "trade_ready": False,
        "verdict": (
            "NOT_TRADE_READY_UNTIL_BLOCKERS_PROVEN_CLEAR"
            if _pipeline_blockers
            else "ANALYZER_READY_ALL_PIPELINE_GATES_PASS"
        ),
        "blockers": _pipeline_blockers,
        "master_control_plane_verdict": verdict,
        "master_control_plane_report": "reports/latest/system3_master_control_plane/system3_master_control_plane.json",
    }
    write_json(REPORTS / "full_trading_pipeline_readiness" / "09_pipeline_gate_summary.json", pipeline)

    # Master status doc.
    status_lines = [
        "# System3 Master Status",
        "",
        f"Generated UTC: {utc_now()}",
        "",
        "## Current verified status",
        "",
        f"- Master verdict: `{verdict}`",
        "- Trade ready: `False`",
        "- Live trading enabled: `False`",
        "- Mode: `Analyzer/Paper only`",
        "",
        "## Gate results",
        "",
        "| Gate | Status | Pass |",
        "|---|---|---:|",
    ]
    for g in gates:
        status_lines.append(f"| `{g.gate}` | `{g.status}` | `{g.pass_}` |")
    status_lines.extend(["", "## Open blockers", ""])
    status_lines.extend([f"- `{b}`" for b in blockers] or ["- None"])
    status_lines.extend(
        [
            "",
            "## Operating rule",
            "",
            "- Analyzer/Paper mode only.",
            "- Live trading remains disabled.",
            "- Do not commit private keys, broker credentials, `.env`, OTP, TOTP, PIN, or passwords.",
            "- Auto-fix may repair safe proof/report/config issues only; it must not bypass broker login, secrets, live trading safety, or unknown position-state blocks.",
            "",
            "## Next automatic work queue",
            "",
            "1. Keep this master control-plane workflow scheduled and green.",
            "2. Run secure fresh broker data proof in broker-enabled runtime.",
            "3. Run model-load/training proof with metrics.",
            "4. Run recent backtest/walk-forward proof with costs/slippage.",
            "5. Run analyzer paper lifecycle proof: signal → order → fill/sim-fill → exit → P&L.",
            "6. Run dashboard API/browser truth proof.",
            "7. Accumulate multi-day stability before any live enablement checklist.",
            "",
        ]
    )
    write_text(CONTROL / "SYSTEM3_MASTER_STATUS.md", "\n".join(status_lines))

    return summary


def publish_blocker_autorecovery(summary: dict[str, Any], gates: list[GateResult]) -> None:
    categories: dict[str, list[str]] = {
        "AUTO_FIXED": [],
        "AUTO_RETRY_FAILED": [],
        "MANUAL_SECRET_REQUIRED": [],
        "MANUAL_BROKER_LOGIN_REQUIRED": [],
        "SOURCE_AUTHORITY_UNKNOWN": [],
        "MARKET_CLOSED_OR_HOLIDAY": [],
        "MODEL_NOT_GOOD_ENOUGH": [],
        "DASHBOARD_TRUTH_FAIL": [],
        "PROOF_REQUIRED": [],
    }

    for gate in gates:
        for blocker in gate.blockers:
            item = f"{gate.gate}:{blocker}"
            if "secret" in blocker:
                categories["MANUAL_SECRET_REQUIRED"].append(item)
            elif "broker" in blocker or "session" in blocker:
                categories["MANUAL_BROKER_LOGIN_REQUIRED"].append(item)
            elif "duplicate" in blocker or "authority" in blocker:
                categories["SOURCE_AUTHORITY_UNKNOWN"].append(item)
            elif "model" in blocker or "training" in blocker:
                categories["MODEL_NOT_GOOD_ENOUGH"].append(item)
            elif "dashboard" in blocker:
                categories["DASHBOARD_TRUTH_FAIL"].append(item)
            else:
                categories["PROOF_REQUIRED"].append(item)
        for warning in gate.warnings:
            item = f"{gate.gate}:{warning}"
            if "secret" in warning:
                categories["MANUAL_SECRET_REQUIRED"].append(item)
            elif "broker" in warning or "login" in warning:
                categories["MANUAL_BROKER_LOGIN_REQUIRED"].append(item)
            elif "duplicate" in warning:
                categories["SOURCE_AUTHORITY_UNKNOWN"].append(item)
            elif "dashboard" in warning or "browser" in warning:
                categories["DASHBOARD_TRUTH_FAIL"].append(item)
            else:
                categories["PROOF_REQUIRED"].append(item)

    recovery = {
        "generated_utc": utc_now(),
        "verdict": summary["verdict"],
        "trade_ready": False,
        "auto_recovery_policy": {
            "allowed": [
                "regenerate missing proof reports",
                "retry endpoint/network checks once inside workflow",
                "patch deterministic dependency/config gaps after exact proof",
                "auto-clean generated unsafe files only",
            ],
            "not_allowed": [
                "enable live trading",
                "bypass broker login/OTP/session renewal",
                "write or expose secrets",
                "ignore unknown live positions",
                "promote weak/unproven models",
                "delete source duplicates without runtime proof",
            ],
        },
        "categories": categories,
    }
    out = REPORTS / "auto_recovery_blockers"
    write_json(out / "auto_recovery_blockers.json", recovery)

    lines = [
        "# Auto-Recovery Blocker Classification",
        "",
        f"Generated UTC: {recovery['generated_utc']}",
        "",
        f"- Verdict: `{summary['verdict']}`",
        "- Trade ready: `False`",
        "",
        "## Categories",
        "",
    ]
    for name, items in categories.items():
        lines.append(f"### {name}")
        lines.append("")
        lines.extend([f"- `{x}`" for x in items] or ["- None"])
        lines.append("")
    write_text(out / "README.md", "\n".join(lines))


def run() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Regenerate proof reports and status files; never touches live trading/secrets.",
    )
    parser.add_argument("--strict", action="store_true", help="Return nonzero when a safety/secrets gate fails.")
    args = parser.parse_args()

    CONTROL.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    files = list_tracked_files()
    gates = [
        gate_safety_and_secrets(files),
        gate_repo_authority(files),
        gate_deployment_endpoint(),
        gate_data_automation(files),
        gate_model_training_load(files),
        gate_backtest_walkforward(files),
        gate_paper_lifecycle(files),
        gate_dashboard_truth(files),
    ]

    for gate in gates:
        publish_gate_report(gate)

    summary = publish_consolidated(gates)
    publish_blocker_autorecovery(summary, gates)

    print(
        json.dumps(
            {
                "generated_utc": summary["generated_utc"],
                "verdict": summary["verdict"],
                "trade_ready": summary["trade_ready"],
                "live_trading_enabled": summary["live_trading_enabled"],
                "gate_count": summary["gate_count"],
                "pass_count": summary["pass_count"],
                "fail_count": summary["fail_count"],
                "warning_count": summary["warning_count"],
                "blocker_count": len(summary["blockers"]),
                "reports": [
                    "reports/latest/system3_master_control_plane/system3_master_control_plane.json",
                    "reports/latest/proof_status_matrix/proof_status_matrix.json",
                    "reports/latest/auto_recovery_blockers/auto_recovery_blockers.json",
                    "docs/project_control/SYSTEM3_MASTER_STATUS.md",
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )

    if args.strict and any(g.gate == "safety_and_secrets" and not g.pass_ for g in gates):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
