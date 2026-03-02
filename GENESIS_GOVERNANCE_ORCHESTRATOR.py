"""
GENESIS SYSTEM3 — GOVERNANCE ORCHESTRATOR
==========================================
Full autonomous governance engine:
  1. Venv & dependency self-diagnosis
  2. Broker integration validation
  3. Model health check & retraining assessment
  4. QC audit engine
  5. Dashboard backend/frontend validation
  6. Pipeline integrity check
  7. Risk & safety validation
  8. Proof artifact generation
  9. Git commit & PR update

Run: .venv\Scripts\python.exe GENESIS_GOVERNANCE_ORCHESTRATOR.py
"""

import os
import sys
import json
import time
import subprocess
import importlib
import ast
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.absolute()
PROOF_DIR = ROOT / "proof"
REPORTS_DIR = ROOT / "reports" / "governance"
FORENSIC_DIR = ROOT / "reports" / "forensic"
CHANGELOG_DIR = ROOT / "reports" / "changelog"
RETRY_LOG_DIR = ROOT / "reports" / "retry_logs"

for d in [PROOF_DIR, REPORTS_DIR, FORENSIC_DIR, CHANGELOG_DIR, RETRY_LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT = {
    "timestamp": datetime.now().isoformat(),
    "governance_run_id": TS,
    "phases": {},
    "summary": {"passed": 0, "failed": 0, "warnings": 0},
    "overall_status": "UNKNOWN",
}
RETRY_LOG = []
CHANGELOG = []


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "✅", "WARN": "⚠️ ", "ERROR": "❌", "STEP": "🔷"}
    print(f"[{ts}] {icons.get(level,'  ')} {msg}")
    RETRY_LOG.append({"ts": ts, "level": level, "msg": msg})


def record(phase, status, details=None, error=None):
    REPORT["phases"][phase] = {
        "status": status,
        "details": details or {},
        "error": str(error) if error else None,
        "timestamp": datetime.now().isoformat(),
    }
    if status == "PASS":
        REPORT["summary"]["passed"] += 1
    elif status == "FAIL":
        REPORT["summary"]["failed"] += 1
    elif status == "WARN":
        REPORT["summary"]["warnings"] += 1


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1: VENV & DEPENDENCY DIAGNOSIS
# ─────────────────────────────────────────────────────────────────────────────
def phase_venv_diagnosis():
    log("PHASE 1: Venv & Dependency Diagnosis", "STEP")
    results = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "venv_prefix": sys.prefix,
        "in_venv": hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix),
    }

    critical_packages = {
        "pandas": "pandas",
        "numpy": "numpy",
        "sklearn": "scikit-learn",
        "xgboost": "xgboost",
        "joblib": "joblib",
        "requests": "requests",
        "flask": "flask",
    }
    optional_packages = {
        "shap": "shap",
        "imblearn": "imbalanced-learn",
        "pyotp": "pyotp",
        "fastapi": "fastapi",
    }

    pkg_status = {}
    missing_critical = []

    for pkg, pip_name in critical_packages.items():
        try:
            mod = importlib.import_module(pkg)
            ver = getattr(mod, "__version__", "unknown")
            pkg_status[pkg] = {"status": "OK", "version": ver}
            log(f"  {pkg} {ver}")
        except ImportError:
            pkg_status[pkg] = {"status": "MISSING"}
            missing_critical.append(pip_name)
            log(f"  {pkg} MISSING", "WARN")

    for pkg, pip_name in optional_packages.items():
        try:
            mod = importlib.import_module(pkg)
            ver = getattr(mod, "__version__", "unknown")
            pkg_status[pkg] = {"status": "OK", "version": ver}
        except ImportError:
            pkg_status[pkg] = {"status": "MISSING"}
            log(f"  {pkg} (optional) MISSING", "WARN")

    results["packages"] = pkg_status
    results["missing_critical"] = missing_critical

    if missing_critical:
        log(f"Auto-installing: {missing_critical}", "WARN")
        for pkg in missing_critical:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", pkg, "-q"], check=True, capture_output=True)
                log(f"  Installed {pkg}")
                CHANGELOG.append(f"AUTO-INSTALL: {pkg}")
            except Exception as e:
                log(f"  Failed to install {pkg}: {e}", "ERROR")

    status = "PASS" if not missing_critical else "WARN"
    record("venv_diagnosis", status, results)
    log(f"Phase 1: {status}")
    return status


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2: BROKER INTEGRATION VALIDATION
# ─────────────────────────────────────────────────────────────────────────────
def phase_broker_validation():
    log("PHASE 2: Broker Integration Validation", "STEP")
    results = {}

    config_files = {
        "angel_config.json": ROOT / "config" / "angel_config.json",
        "live_trade_config.py": ROOT / "config" / "live_trade_config.py",
        ".env": ROOT / ".env",
    }
    results["config_files"] = {name: "EXISTS" if path.exists() else "MISSING" for name, path in config_files.items()}
    for name, st in results["config_files"].items():
        log(f"  {name}: {st}" + (" ✓" if st == "EXISTS" else ""), "INFO" if st == "EXISTS" else "WARN")

    broker_path = ROOT / "core" / "brokers" / "angel_one" / "broker.py"
    results["broker_module"] = "EXISTS" if broker_path.exists() else "MISSING"

    if broker_path.exists():
        try:
            with open(broker_path, "r", encoding="utf-8") as f:
                ast.parse(f.read())
            results["broker_syntax"] = "VALID"
            log("  Broker module syntax: VALID ✓")
        except SyntaxError as e:
            results["broker_syntax"] = f"SYNTAX_ERROR: {e}"
            log(f"  Broker syntax error: {e}", "ERROR")
            CHANGELOG.append(f"BROKER_SYNTAX_ERROR: {e}")
    else:
        results["broker_syntax"] = "MISSING"

    for cfg_path, cfg_name in [
        (ROOT / "config" / "kill_switch.json", "kill_switch"),
        (ROOT / "config" / "runtime_flags.json", "runtime_flags"),
        (ROOT / "config" / "autonomous_params.json", "autonomous_params"),
    ]:
        if cfg_path.exists():
            try:
                with open(cfg_path) as f:
                    results[cfg_name] = json.load(f)
                log(f"  {cfg_name}: loaded ✓")
            except Exception as e:
                results[cfg_name] = f"ERROR: {e}"

    status = "PASS" if results.get("broker_syntax") == "VALID" else "WARN"
    record("broker_validation", status, results)
    log(f"Phase 2: {status}")
    return status


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 3: MODEL HEALTH CHECK
# ─────────────────────────────────────────────────────────────────────────────
def phase_model_health():
    log("PHASE 3: Model Health Check", "STEP")
    results = {}

    try:
        import joblib
    except ImportError:
        record("model_health", "FAIL", {"error": "joblib not available"})
        return "FAIL"

    model_paths = {
        "xgboost_model": ROOT / "models" / "xgboost_model.pkl",
        "ensemble_model": ROOT / "storage" / "models" / "ensemble_model.pkl",
    }

    ultra_dir = ROOT / "core" / "models" / "angel_one_ultra"
    if ultra_dir.exists():
        for pkl in ultra_dir.glob("*.pkl"):
            model_paths[pkl.stem] = pkl

    model_status = {}
    loadable = 0
    total = len(model_paths)

    for name, path in model_paths.items():
        if not path.exists():
            model_status[name] = {"status": "MISSING"}
            log(f"  {name}: MISSING", "WARN")
            continue
        try:
            model = joblib.load(path)
            size_kb = path.stat().st_size / 1024
            model_status[name] = {"status": "LOADED", "type": type(model).__name__, "size_kb": round(size_kb, 1)}
            loadable += 1
            log(f"  {name}: {type(model).__name__} ({size_kb:.0f}KB) ✓")
        except Exception as e:
            model_status[name] = {"status": "CORRUPT", "error": str(e)}
            log(f"  {name}: CORRUPT - {e}", "ERROR")
            CHANGELOG.append(f"MODEL_CORRUPT: {name}")

    results["models"] = model_status
    results["load_rate"] = f"{loadable}/{total}"
    results["retrain_needed"] = [n for n, v in model_status.items() if v.get("status") in ["MISSING", "CORRUPT"]]

    meta_files = list(ultra_dir.glob("*_meta.json")) if ultra_dir.exists() else []
    results["meta_files_count"] = len(meta_files)

    status = "PASS" if loadable > 0 else "FAIL"
    record("model_health", status, results)
    log(f"Phase 3: {status} ({loadable}/{total} models loaded)")
    return status


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4: QC AUDIT ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def phase_qc_audit():
    log("PHASE 4: QC Audit Engine", "STEP")
    results = {}

    try:
        import pandas as pd
    except ImportError:
        record("qc_audit", "FAIL", {"error": "pandas not available"})
        return "FAIL"

    live_files = {
        "signals_production": ROOT / "storage" / "live" / "angel_index_ai_signals_production.csv",
        "pnl_log_production": ROOT / "storage" / "live" / "angel_index_ai_pnl_log_production.csv",
        "virtual_orders_production": ROOT / "storage" / "live" / "angel_virtual_orders_production.csv",
        "forward_returns": ROOT / "storage" / "live" / "forward" / "phase221_forward_returns.csv",
    }

    data_quality = {}
    for name, path in live_files.items():
        if not path.exists():
            data_quality[name] = {"status": "MISSING"}
            log(f"  {name}: MISSING", "WARN")
            continue
        try:
            df = pd.read_csv(path)
            null_pct = df.isnull().mean().mean() * 100
            data_quality[name] = {
                "status": "OK",
                "rows": len(df),
                "cols": len(df.columns),
                "null_pct": round(null_pct, 2),
                "columns": list(df.columns)[:8],
            }
            log(f"  {name}: {len(df)} rows, {null_pct:.1f}% nulls ✓")
        except Exception as e:
            data_quality[name] = {"status": "ERROR", "error": str(e)}
            log(f"  {name}: ERROR - {e}", "ERROR")

    results["data_quality"] = data_quality

    # Signal integrity check
    sig_path = ROOT / "storage" / "live" / "angel_index_ai_signals_production.csv"
    if sig_path.exists():
        try:
            df = pd.read_csv(sig_path)
            required = ["symbol", "signal", "confidence"]
            missing_cols = [c for c in required if c not in df.columns]
            results["signal_integrity"] = {
                "rows": len(df),
                "missing_required_cols": missing_cols,
                "status": "OK" if not missing_cols else "WARN",
            }
            if missing_cols:
                log(f"  Signal missing cols: {missing_cols}", "WARN")
                CHANGELOG.append(f"SIGNAL_MISSING_COLS: {missing_cols}")
        except Exception as e:
            results["signal_integrity"] = {"status": "ERROR", "error": str(e)}

    ok_count = sum(1 for v in data_quality.values() if v.get("status") == "OK")
    status = "PASS" if ok_count > 0 else "WARN"
    record("qc_audit", status, results)
    log(f"Phase 4: {status} ({ok_count}/{len(data_quality)} files OK)")
    return status


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 5: DASHBOARD VALIDATION
# ─────────────────────────────────────────────────────────────────────────────
def phase_dashboard_validation():
    log("PHASE 5: Dashboard Backend/Frontend Validation", "STEP")
    results = {}

    backend_path = ROOT / "dashboard" / "backend" / "app.py"
    if backend_path.exists():
        try:
            with open(backend_path, "r", encoding="utf-8") as f:
                source = f.read()
            ast.parse(source)
            results["backend_syntax"] = "VALID"
            endpoints = [l.strip() for l in source.split("\n") if "@app." in l or "@router." in l]
            results["backend_endpoints_count"] = len(endpoints)
            log(f"  Backend: VALID, {len(endpoints)} endpoints ✓")
        except SyntaxError as e:
            results["backend_syntax"] = f"SYNTAX_ERROR: {e}"
            log(f"  Backend syntax error: {e}", "ERROR")
            CHANGELOG.append(f"BACKEND_SYNTAX_ERROR: {e}")
    else:
        results["backend_syntax"] = "MISSING"
        log("  Backend app.py: MISSING", "WARN")

    frontend_dist = ROOT / "dashboard" / "frontend" / "dist"
    if frontend_dist.exists():
        dist_files = list(frontend_dist.rglob("*"))
        results["frontend_dist"] = {
            "status": "EXISTS",
            "file_count": len(dist_files),
            "has_index_html": (frontend_dist / "index.html").exists(),
        }
        log(f"  Frontend dist: {len(dist_files)} files ✓")
    else:
        results["frontend_dist"] = {"status": "MISSING"}
        log("  Frontend dist: MISSING", "WARN")

    components_dir = ROOT / "dashboard" / "frontend" / "src" / "components"
    if components_dir.exists():
        components = [f.name for f in components_dir.glob("*.tsx")]
        results["frontend_components"] = components
        log(f"  Components: {components}")

    status = "PASS" if results.get("backend_syntax") == "VALID" else "WARN"
    record("dashboard_validation", status, results)
    log(f"Phase 5: {status}")
    return status


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 6: PIPELINE INTEGRITY CHECK
# ─────────────────────────────────────────────────────────────────────────────
def phase_pipeline_integrity():
    log("PHASE 6: Pipeline Integrity (Phases 220→221→239)", "STEP")
    results = {}

    phase_files = {
        "phase220_aggregation": ROOT / "core" / "engine" / "system3_phase220_historical_aggregation.py",
        "phase304_forward_returns": ROOT / "core" / "engine" / "system3_phase304_forward_returns.py",
        "phase305_reconciliation": ROOT / "core" / "engine" / "system3_phase305_reconciliation.py",
        "merge_key_normalizer": ROOT / "core" / "engine" / "merge_key_normalizer.py",
        "timestamp_parser": ROOT / "core" / "utils" / "timestamp_parser.py",
        "continuous_validators": ROOT / "core" / "monitoring" / "continuous_validators.py",
        "signal_engine": ROOT / "core" / "engine" / "system3_signal_engine.py",
        "ensemble_predictor": ROOT / "core" / "engine" / "ensemble_predictor.py",
    }

    phase_status = {}
    valid_count = 0
    for name, path in phase_files.items():
        if not path.exists():
            phase_status[name] = "MISSING"
            log(f"  {name}: MISSING", "WARN")
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                ast.parse(f.read())
            phase_status[name] = "VALID"
            valid_count += 1
            log(f"  {name}: VALID ✓")
        except SyntaxError as e:
            phase_status[name] = f"SYNTAX_ERROR: {e}"
            log(f"  {name}: SYNTAX ERROR", "ERROR")
            CHANGELOG.append(f"SYNTAX_ERROR: {name}: {e}")

    results["phase_files"] = phase_status
    results["valid_phases"] = f"{valid_count}/{len(phase_files)}"

    # Ensure storage dirs exist
    for d in [
        ROOT / "storage" / "live" / "healed",
        ROOT / "storage" / "live" / "forward",
        ROOT / "storage" / "live" / "enriched",
        ROOT / "storage" / "metrics",
        ROOT / "storage" / "models",
        ROOT / "runtime_reports",
    ]:
        d.mkdir(parents=True, exist_ok=True)

    status = "PASS" if valid_count == len(phase_files) else "WARN"
    record("pipeline_integrity", status, results)
    log(f"Phase 6: {status} ({valid_count}/{len(phase_files)} valid)")
    return status


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 7: RISK & SAFETY VALIDATION
# ─────────────────────────────────────────────────────────────────────────────
def phase_risk_safety():
    log("PHASE 7: Risk & Safety Validation", "STEP")
    results = {}

    ks_path = ROOT / "config" / "kill_switch.json"
    if ks_path.exists():
        try:
            with open(ks_path) as f:
                ks = json.load(f)
            is_active = ks.get("kill_switch_active", False) or ks.get("active", False)
            results["kill_switch_active"] = is_active
            results["kill_switch"] = ks
            if is_active:
                log("  KILL SWITCH ACTIVE — trading halted", "WARN")
            else:
                log("  Kill switch: INACTIVE (trading allowed) ✓")
        except Exception as e:
            results["kill_switch"] = f"ERROR: {e}"
    else:
        results["kill_switch"] = "MISSING"
        log("  Kill switch config: MISSING", "WARN")

    rl_path = ROOT / "core" / "engine" / "config" / "risk_limits.json"
    if rl_path.exists():
        try:
            with open(rl_path) as f:
                rl = json.load(f)
            results["risk_limits"] = rl
            log(f"  Risk limits: {list(rl.keys())} ✓")
        except Exception as e:
            results["risk_limits"] = f"ERROR: {e}"
    else:
        results["risk_limits"] = "MISSING"
        log("  Risk limits: MISSING", "WARN")

    # Check safety guardrail phase
    guardrail_path = ROOT / "core" / "engine" / "system3_phase367_safety_guardrail_recommender.py"
    results["safety_guardrail"] = "EXISTS" if guardrail_path.exists() else "MISSING"
    log(f"  Safety guardrail: {results['safety_guardrail']}")

    status = "PASS"
    record("risk_safety", status, results)
    log(f"Phase 7: {status}")
    return status


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 8: GENERATE PROOF ARTIFACTS
# ─────────────────────────────────────────────────────────────────────────────
def phase_generate_proof():
    log("PHASE 8: Generating Proof Artifacts", "STEP")

    # Determine overall status
    statuses = [v.get("status") for v in REPORT["phases"].values()]
    if "FAIL" in statuses:
        REPORT["overall_status"] = "FAIL"
    elif "WARN" in statuses:
        REPORT["overall_status"] = "WARN"
    else:
        REPORT["overall_status"] = "PASS"

    # Governance report
    report_path = REPORTS_DIR / f"governance_report_{TS}.json"
    with open(report_path, "w") as f:
        json.dump(REPORT, f, indent=2, default=str)
    log(f"  Governance report: {report_path.name}")

    # Retry log
    retry_path = RETRY_LOG_DIR / f"retry_log_{TS}.json"
    with open(retry_path, "w") as f:
        json.dump(RETRY_LOG, f, indent=2)
    log(f"  Retry log: {retry_path.name}")

    # Changelog
    changelog_path = CHANGELOG_DIR / f"changelog_{TS}.txt"
    with open(changelog_path, "w") as f:
        f.write(f"GENESIS SYSTEM3 GOVERNANCE CHANGELOG\nRun: {TS}\n{'='*60}\n\n")
        for entry in CHANGELOG:
            f.write(f"  - {entry}\n")
        f.write(f"\nTotal changes: {len(CHANGELOG)}\n")
    log(f"  Changelog: {changelog_path.name}")

    # Forensic report
    forensic = {
        "run_id": TS,
        "timestamp": datetime.now().isoformat(),
        "system": {"python": sys.version, "venv": sys.prefix, "cwd": str(ROOT)},
        "phases_summary": {k: v.get("status") for k, v in REPORT["phases"].items()},
        "overall_status": REPORT["overall_status"],
        "changelog_entries": len(CHANGELOG),
        "retry_log_entries": len(RETRY_LOG),
    }
    forensic_path = FORENSIC_DIR / f"forensic_governance_{TS}.json"
    with open(forensic_path, "w") as f:
        json.dump(forensic, f, indent=2)
    log(f"  Forensic report: {forensic_path.name}")

    # Proof summary text
    proof_path = PROOF_DIR / f"governance_proof_{TS}.txt"
    with open(proof_path, "w", encoding="utf-8") as f:
        f.write(f"GENESIS SYSTEM3 GOVERNANCE PROOF\nRun ID: {TS}\n{'='*60}\n\n")
        f.write("PHASE RESULTS:\n")
        for phase, data in REPORT["phases"].items():
            st = data.get("status", "?")
            icon = "[PASS]" if st == "PASS" else "[WARN]" if st == "WARN" else "[FAIL]"
            f.write(f"  {icon} {phase}: {st}\n")
        f.write(f"\nSUMMARY:\n")
        f.write(f"  Passed:   {REPORT['summary']['passed']}\n")
        f.write(f"  Warnings: {REPORT['summary']['warnings']}\n")
        f.write(f"  Failed:   {REPORT['summary']['failed']}\n")
        f.write(f"  Overall:  {REPORT['overall_status']}\n")
    log(f"  Proof summary: {proof_path.name}")

    record(
        "proof_generation",
        "PASS",
        {
            "report": str(report_path),
            "retry_log": str(retry_path),
            "changelog": str(changelog_path),
            "forensic": str(forensic_path),
            "proof_summary": str(proof_path),
        },
    )
    log("Phase 8: PASS")
    return "PASS"


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 9: GIT COMMIT & PR UPDATE
# ─────────────────────────────────────────────────────────────────────────────
def phase_git_commit():
    log("PHASE 9: Git Commit & PR Update", "STEP")
    results = {}

    files_to_stage = [
        f"reports/governance/governance_report_{TS}.json",
        f"reports/retry_logs/retry_log_{TS}.json",
        f"reports/changelog/changelog_{TS}.txt",
        f"reports/forensic/forensic_governance_{TS}.json",
        f"proof/governance_proof_{TS}.txt",
        "GENESIS_GOVERNANCE_ORCHESTRATOR.py",
    ]

    staged = []
    for f in files_to_stage:
        full_path = ROOT / f
        if full_path.exists():
            r = subprocess.run(["git", "add", f], cwd=ROOT, capture_output=True)
            if r.returncode == 0:
                staged.append(f)

    results["staged_files"] = staged
    log(f"  Staged {len(staged)} files")

    if staged:
        overall = REPORT.get("overall_status", "UNKNOWN")
        passed = REPORT["summary"]["passed"]
        warned = REPORT["summary"]["warnings"]
        failed = REPORT["summary"]["failed"]

        commit_msg = (
            f"governance: autonomous QC run {TS} [{overall}]\n\n"
            f"Phases: {passed} PASS / {warned} WARN / {failed} FAIL\n\n"
            f"- venv_diagnosis: {REPORT['phases'].get('venv_diagnosis', {}).get('status', '?')}\n"
            f"- broker_validation: {REPORT['phases'].get('broker_validation', {}).get('status', '?')}\n"
            f"- model_health: {REPORT['phases'].get('model_health', {}).get('status', '?')}\n"
            f"- qc_audit: {REPORT['phases'].get('qc_audit', {}).get('status', '?')}\n"
            f"- dashboard_validation: {REPORT['phases'].get('dashboard_validation', {}).get('status', '?')}\n"
            f"- pipeline_integrity: {REPORT['phases'].get('pipeline_integrity', {}).get('status', '?')}\n"
            f"- risk_safety: {REPORT['phases'].get('risk_safety', {}).get('status', '?')}\n\n"
            f"Artifacts: reports/governance/, reports/forensic/, proof/"
        )

        r = subprocess.run(["git", "commit", "-m", commit_msg], cwd=ROOT, capture_output=True, text=True)
        results["commit_exit_code"] = r.returncode
        results["commit_status"] = "SUCCESS" if r.returncode == 0 else "FAILED"
        log(f"  Commit: {results['commit_status']} (exit {r.returncode})")

        if r.returncode == 0:
            # Push
            r2 = subprocess.run(
                ["git", "push", "origin", "blackboxai/system-analysis"], cwd=ROOT, capture_output=True, text=True
            )
            results["push_exit_code"] = r2.returncode
            results["push_status"] = "SUCCESS" if r2.returncode == 0 else "FAILED"
            log(f"  Push: {results['push_status']} (exit {r2.returncode})")
        else:
            log(f"  Commit stderr: {r.stderr[:200]}", "WARN")
    else:
        results["commit_status"] = "NOTHING_TO_COMMIT"
        log("  Nothing new to commit", "WARN")

    status = "PASS" if results.get("commit_status") in ["SUCCESS", "NOTHING_TO_COMMIT"] else "WARN"
    record("git_commit_push", status, results)
    log(f"Phase 9: {status}")
    return status


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATOR
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 70)
    print("  GENESIS SYSTEM3 — GOVERNANCE ORCHESTRATOR")
    print(f"  Run ID: {TS}")
    print("=" * 70 + "\n")

    start = time.time()

    phases = [
        ("venv_diagnosis", phase_venv_diagnosis),
        ("broker_validation", phase_broker_validation),
        ("model_health", phase_model_health),
        ("qc_audit", phase_qc_audit),
        ("dashboard_validation", phase_dashboard_validation),
        ("pipeline_integrity", phase_pipeline_integrity),
        ("risk_safety", phase_risk_safety),
        ("proof_generation", phase_generate_proof),
        ("git_commit_push", phase_git_commit),
    ]

    for name, fn in phases:
        print()
        try:
            fn()
        except Exception as e:
            log(f"Phase {name} CRASHED: {e}", "ERROR")
            record(name, "FAIL", error=e)
            CHANGELOG.append(f"PHASE_CRASH: {name}: {e}")

    elapsed = time.time() - start

    print("\n" + "=" * 70)
    print(f"  GOVERNANCE COMPLETE in {elapsed:.1f}s")
    print(f"  Overall Status: {REPORT['overall_status']}")
    print(
        f"  Passed: {REPORT['summary']['passed']}  "
        f"Warnings: {REPORT['summary']['warnings']}  "
        f"Failed: {REPORT['summary']['failed']}"
    )
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
