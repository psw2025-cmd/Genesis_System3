#!/usr/bin/env python3
"""
Maximum safe production proof probe for Genesis System3.

This script is proof-only. It does not log in to brokers, does not place orders,
does not modify runtime state, and does not enable live trading.
"""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "maximum_safe_production_probe"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: str, max_chars: int = 1_000_000) -> str:
    p = ROOT / path
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")[:max_chars]


def read_json(path: str) -> Any:
    p = ROOT / path
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {"_json_error": repr(exc)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def tracked_files() -> list[str]:
    try:
        out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
        return sorted(x for x in out.splitlines() if x.strip())
    except Exception:
        return sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in ROOT.rglob("*") if p.is_file())


def py_compile(path: str) -> dict[str, Any]:
    p = ROOT / path
    result = {"file": path, "exists": p.exists(), "compile_pass": False, "error": None}
    if not p.exists():
        result["error"] = "missing"
        return result
    try:
        ast.parse(p.read_text(encoding="utf-8", errors="replace"), filename=path)
        result["compile_pass"] = True
    except Exception as exc:
        result["error"] = repr(exc)
    return result


def safety_scan(files: list[str]) -> dict[str, Any]:
    render = read_text("render.yaml")
    req = read_text("dashboard/backend/requirements.txt").lower()
    tracked_secret_names = [
        f for f in files
        if re.search(r"(^|/)(\.env($|\.)|.*secret.*\.json$|.*credential.*\.json$|.*private.*key.*|.*\.pem$)", f, re.I)
    ]
    return {
        "render_yaml_exists": (ROOT / "render.yaml").exists(),
        "live_trading_disabled_in_render": "LIVE_TRADING_ENABLED" in render and re.search(r"LIVE_TRADING_ENABLED[^\n]*(\"0\"|'0'|0|false|False)", render) is not None,
        "analyze_mode_enabled_in_render": "ANALYZE_MODE" in render and re.search(r"ANALYZE_MODE[^\n]*(\"1\"|'1'|1|true|True)", render) is not None,
        "dhanhq_dependency_present": "dhanhq" in req,
        "tracked_secret_style_file_count": len(tracked_secret_names),
        "tracked_secret_style_files": tracked_secret_names[:50],
    }


def model_metadata(files: list[str]) -> dict[str, Any]:
    model_files = [f for f in files if re.search(r"core/models/.*\.(pkl|pth|joblib|json)$", f, re.I)]
    meta_files = [f for f in model_files if f.endswith("_meta.json") or f.endswith("meta.json")]
    meta_samples = []
    metric_keys = {"accuracy", "precision", "recall", "f1", "auc", "win_rate", "sharpe", "trained_at", "training_date", "dataset", "samples"}
    metric_hits = []
    for f in meta_files[:80]:
        data = read_json(f)
        if isinstance(data, dict):
            keys = sorted(data.keys())
            meta_samples.append({"file": f, "keys": keys[:40]})
            hits = sorted(k for k in keys if k.lower() in metric_keys or any(m in k.lower() for m in ["accuracy", "score", "metric", "date", "sample"]))
            if hits:
                metric_hits.append({"file": f, "metric_like_keys": hits[:20]})
    return {
        "model_artifact_count": len(model_files),
        "model_meta_count": len(meta_files),
        "model_meta_samples": meta_samples[:20],
        "model_metric_key_hits": metric_hits[:30],
        "fresh_training_execution_proven": False,
        "fresh_training_accuracy_metric_proven": False,
        "reason": "metadata inventory only; no fresh training executed by this safe probe",
    }


def backtest_probe(files: list[str]) -> dict[str, Any]:
    candidates = [f for f in files if re.search(r"(backtest|walk.?forward|slippage|charges|pnl|strategy|validation).*\.py$", f, re.I)]
    compile_targets = []
    for f in ["dashboard/backend/backtesting.py", "system3_ultra_validation.py", "run_system3.py"]:
        if (ROOT / f).exists():
            compile_targets.append(f)
    compile_targets += candidates[:60]
    compile_results = [py_compile(f) for f in sorted(set(compile_targets))]
    return {
        "candidate_count": len(candidates),
        "candidate_sample": candidates[:80],
        "compile_pass_count": sum(1 for r in compile_results if r["compile_pass"]),
        "compile_fail_count": sum(1 for r in compile_results if not r["compile_pass"]),
        "compile_results": compile_results,
        "recent_costed_backtest_proven": False,
        "walk_forward_cost_slippage_proven": False,
        "reason": "compile/inventory only; no authoritative costed backtest entrypoint executed",
    }


def paper_lifecycle_probe(files: list[str]) -> dict[str, Any]:
    reports = [f for f in files if f.startswith("reports/") and re.search(r"(paper|lifecycle|trade|position|pnl)", f, re.I)]
    modules = [f for f in files if re.search(r"(paper|analyzer|sandbox|order|trade|position|broker).*\.py$", f, re.I)]
    return {
        "paper_module_count": len(modules),
        "paper_module_sample": modules[:100],
        "existing_report_count": len(reports),
        "existing_report_sample": reports[:100],
        "mandatory_fields": [
            "signal_id", "symbol", "instrument_token", "expiry", "strike", "option_type",
            "entry_time", "entry_price", "qty", "order_id", "fill_status",
            "exit_time", "exit_price", "gross_pnl", "charges", "net_pnl", "proof_status",
        ],
        "full_signal_to_exit_pnl_lifecycle_proven": False,
        "reason": "no fresh analyzer session executed by this safe CI probe",
    }


def dashboard_probe() -> dict[str, Any]:
    ultra = read_json("reports/latest/dashboard_ultra_readiness/dashboard_ultra_readiness_summary.json")
    tabs = read_json("reports/latest/ultra_dashboard_tabs_proof/summary.json")
    endpoint = read_json("reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json")
    return {
        "ultra_readiness_present": ultra is not None,
        "ultra_readiness_verdict": ultra.get("verdict") if isinstance(ultra, dict) else None,
        "all_tabs_proof_present": tabs is not None,
        "all_tabs_visual_proof": tabs.get("all_tabs_visual_proof") if isinstance(tabs, dict) else None,
        "all_tabs_verdict": tabs.get("verdict") if isinstance(tabs, dict) else None,
        "endpoint_coverage_present": endpoint is not None,
        "endpoint_core_ok": endpoint.get("core_ok") if isinstance(endpoint, dict) else None,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    files = tracked_files()
    compile_targets = [
        "dashboard/backend/app.py",
        "scripts/verify_dhan_readonly.py",
        "core/brokers/dhan/dhan_readonly.py",
        "scripts/system3_master_proof_orchestrator.py",
        "scripts/system3_maximum_safe_production_probe.py",
    ]
    compile_results = [py_compile(f) for f in compile_targets]

    safety = safety_scan(files)
    model = model_metadata(files)
    backtest = backtest_probe(files)
    paper = paper_lifecycle_probe(files)
    dashboard = dashboard_probe()

    blockers = []
    warnings = []
    if not safety["live_trading_disabled_in_render"]:
        blockers.append("live_trading_not_proven_disabled_in_render")
    if safety["tracked_secret_style_file_count"]:
        blockers.append("tracked_secret_style_files_present")
    if not safety["dhanhq_dependency_present"]:
        blockers.append("dhanhq_dependency_missing")
    if any(not r["compile_pass"] for r in compile_results):
        blockers.append("critical_compile_failure")
    if not dashboard.get("all_tabs_visual_proof"):
        warnings.append("all_tabs_visual_proof_not_present_or_not_passed")
    warnings.extend([
        "fresh_training_execution_not_proven",
        "fresh_training_accuracy_metric_not_proven",
        "recent_costed_backtest_not_proven",
        "walk_forward_cost_slippage_not_proven",
        "full_analyzer_paper_lifecycle_not_proven",
    ])

    summary = {
        "generated_utc": utc_now(),
        "mode": "Analyzer/Paper only; live trading disabled",
        "trade_ready": False,
        "production_grade_ready": False,
        "verdict": "MAXIMUM_SAFE_PROBE_COMPLETE_NOT_PRODUCTION_READY" if not blockers else "MAXIMUM_SAFE_PROBE_BLOCKED",
        "blockers": blockers,
        "warnings": warnings,
        "safety": safety,
        "critical_compile": compile_results,
        "model": model,
        "backtest": backtest,
        "paper_lifecycle": paper,
        "dashboard": dashboard,
        "next_required": [
            "re-run all-tabs screenshot proof after Agent tab patch",
            "prove Dhan connected across /api/broker/status, /api/health, MODE_GATE",
            "identify and run authoritative fresh training/load proof with metrics",
            "identify and run recent backtest/walk-forward with costs/slippage",
            "run analyzer paper lifecycle proof: signal to entry to fill to exit to net PnL",
        ],
    }

    write_json(OUT / "summary.json", summary)
    lines = [
        "# Maximum Safe Production Probe",
        "",
        f"Generated UTC: {summary['generated_utc']}",
        "",
        f"Verdict: `{summary['verdict']}`",
        f"Production-grade ready: `{summary['production_grade_ready']}`",
        f"Trade ready: `{summary['trade_ready']}`",
        "",
        "## Blockers",
        "",
    ]
    lines.extend([f"- `{b}`" for b in blockers] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- `{w}`" for w in warnings] or ["- None"])
    lines.extend(["", "## Next required", ""])
    lines.extend([f"{i}. {x}" for i, x in enumerate(summary["next_required"], 1)])
    write_text(OUT / "README.md", "\n".join(lines) + "\n")
    print(json.dumps({"verdict": summary["verdict"], "blockers": blockers, "warning_count": len(warnings)}, indent=2))
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
