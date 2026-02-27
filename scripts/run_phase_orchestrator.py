#!/usr/bin/env python3
"""
Phase Orchestrator (201–310) – Strict + Guided

Runs System3 phases in numeric order using diagnostics mappings, in a
test/orchestration mode:

- For each phase:
  - Calls the corresponding `run_phaseXXX` function from diagnostics/engine.
  - Interprets its result dict (status: OK/WARN/SKIP/ERROR).
  - Records PASS / WARN / SKIP / FAIL.
- On FIRST FAIL (status ERROR/unknown or exception):
  - Stops immediately.
  - Writes `proof/archive/PHASE_ORCHESTRATOR_FAIL_YYYYMMDD_HHMMSS.json`
    with: failed_phase, reason, impact, next_actions.
  - Prints a human-readable summary.
  - Exits with code 1.
- On FULL PASS (no FAIL):
  - Writes `proof/archive/PHASE_ORCHESTRATOR_OK_YYYYMMDD_HHMMSS.json`
    with counts of OK/WARN/SKIP.
  - Exits with code 0.

Usage (from project root, with .venv activated):
  python scripts/run_phase_orchestrator.py
  python scripts/run_phase_orchestrator.py --start 201 --end 260

This script does **NOT** run live trading; it only calls phase diagnostic
functions that are already safe / DRY-RUN.
"""

import argparse
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parent.parent
PROOF_DIR = ROOT / "proof" / "archive"
PROOF_DIR.mkdir(parents=True, exist_ok=True)


def _import_phase_modules() -> Dict[int, Any]:
    """
    Build a mapping {phase_number: callable} using diagnostics modules:
      - system3_phase_201_230_diagnostics.PHASE_MODULES
      - system3_phase_231_260_diagnostics.PHASE_MODULES
      - system3_phase_261_300_diagnostics.PHASE_MODULES
      - system3_phases_301_310_diagnostics.PHASE_MODULES
    """
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    phase_funcs: Dict[int, Any] = {}

    def merge_phase_modules(mod_name: str) -> None:
        try:
            mod = __import__(mod_name, fromlist=["PHASE_MODULES"])
            modules = getattr(mod, "PHASE_MODULES", {})
            if isinstance(modules, dict):
                for phase, fn in modules.items():
                    if callable(fn):
                        phase_funcs[int(phase)] = fn
        except Exception:
            # Diagnostics modules are allowed to be missing; we don't fail import here.
            pass

    merge_phase_modules("system3_phase_201_230_diagnostics")
    merge_phase_modules("system3_phase_231_260_diagnostics")
    merge_phase_modules("system3_phase_261_300_diagnostics")
    merge_phase_modules("system3_phases_301_310_diagnostics")

    return phase_funcs


def _phase_impact(phase: int) -> str:
    """
    Return a coarse-grained impact string based on phase ranges.
    """
    if 201 <= phase <= 230:
        return (
            "Core research/data-quality & safety phases (features, labels, drift, "
            "overfit sentinel, etc.). Failures here mean upstream data/science "
            "pipeline is not trustworthy."
        )
    if 231 <= phase <= 240:
        return (
            "Virtual orders & trades pipeline (thresholds → virtual trades → summary). "
            "Failures mean virtual trade views are unreliable."
        )
    if 241 <= phase <= 247:
        return (
            "Virtual trades diagnostics, attribution, density and regimes. "
            "Failures affect analytics used to understand model/edge behavior."
        )
    if 249 <= phase <= 255:
        return (
            "LSTM/online-learning/production model phases (forward predictor, online "
            "learning manager, drift tracker, retraining scheduler, shadow/production "
            "switch, performance logger). Failures here impact ML model lifecycle "
            "and any dashboards depending on those metrics."
        )
    if 256 <= phase <= 260:
        return (
            "Reserved phases 256–260. A true ERROR here usually indicates a wiring "
            "or diagnostics bug; in normal runs these should be SKIP/NOT_IMPLEMENTED."
        )
    if 261 <= phase <= 300:
        return (
            "Later System3 pipeline phases (261–300). Failure affects higher-level "
            "orchestration and downstream analytics beyond core research/ML blocks."
        )
    if 301 <= phase <= 310:
        return (
            "Meta, safety, and monitoring phases (301–310). Failure here affects "
            "system monitoring, observability, or meta-behavior."
        )
    return "Unknown phase range; consult phase docs for impact."


def _phase_next_actions(phase: int) -> List[str]:
    """
    Return generic next-actions for a failed phase.
    """
    if 201 <= phase <= 230:
        return [
            "Open system3_phase_201_230_diagnostics.py and identify the failing phase entry.",
            "Inspect the corresponding engine module under core/engine/ for that phase.",
            "Fix data/feature/label or safety logic causing the failure.",
            "Re-run: python scripts/run_phase_orchestrator.py --start 201 --end 230",
        ]
    if 231 <= phase <= 247:
        return [
            "Open system3_phase_231_260_diagnostics.py and locate the failing phase.",
            "Inspect the core/engine module referenced for that phase (e.g. virtual orders/trades).",
            "Fix schema / calculations / file paths for that phase.",
            "Re-run: python scripts/run_phase_orchestrator.py --start 231 --end 260",
        ]
    if 249 <= phase <= 255:
        return [
            "Open system3_phase_231_260_diagnostics.py and the corresponding core/engine/system3_phaseXXX_*.py module.",
            "Inspect core/engine/system3_lstm_utils.py and related LSTM evaluation modules if relevant.",
            "Fix NaN/inf issues, file paths, or model loading/saving problems.",
            "Re-run: python scripts/run_phase_orchestrator.py --start 249 --end 255",
        ]
    if 261 <= phase <= 300:
        return [
            "Open system3_phase_261_300_diagnostics.py and find the failing phase.",
            "Inspect the referenced engine module under core/engine/ for that phase.",
            "Fix the underlying logic or dependencies.",
            "Re-run: python scripts/run_phase_orchestrator.py --start 261 --end 300",
        ]
    if 301 <= phase <= 310:
        return [
            "Open system3_phases_301_310_diagnostics.py and locate the failing phase.",
            "Inspect the corresponding engine/monitoring module.",
            "Fix monitoring/meta logic as needed.",
            "Re-run: python scripts/run_phase_orchestrator.py --start 301 --end 310",
        ]
    return [
        "Check diagnostics modules for this phase range.",
        "Inspect the associated core/engine module for the failing phase.",
        "Re-run: python scripts/run_phase_orchestrator.py with a narrow range around this phase.",
    ]


def _run_phases_in_range(
    start: int,
    end: int,
    phase_funcs: Dict[int, Any],
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Run phases [start, end] using phase_funcs mapping.
    Returns (all_passed, steps) where steps is a list of per-phase records.
    """
    steps: List[Dict[str, Any]] = []
    any_fail = False

    for phase in range(start, end + 1):
        fn = phase_funcs.get(phase)
        if fn is None:
            steps.append(
                {
                    "phase": phase,
                    "status": "SKIP",
                    "detail": "No function found in diagnostics PHASE_MODULES (reserved/not implemented).",
                }
            )
            continue

        print(f"\n[PHASE] {phase} ...")
        try:
            result = fn()
        except Exception as exc:
            tb = traceback.format_exc(limit=3)
            steps.append(
                {
                    "phase": phase,
                    "status": "FAIL",
                    "detail": f"Exception: {exc}",
                    "traceback": tb,
                }
            )
            any_fail = True
            break

        status_raw = str(result.get("status", "")).upper()
        detail = result.get("details") or result.get("detail") or ""

        if status_raw in ("OK", "SUCCESS"):
            status = "OK"
        elif status_raw in ("WARN", "WARNING", "SKIP"):
            status = "WARN" if status_raw != "SKIP" else "SKIP"
        else:
            status = "FAIL"

        steps.append(
            {
                "phase": phase,
                "status": status,
                "detail": detail or f"status={status_raw!r}",
            }
        )

        if status == "FAIL":
            any_fail = True
            break

    return (not any_fail, steps)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run System3 phases 201–310 in sequence (strict + guided).")
    parser.add_argument("--start", type=int, default=201, help="Start phase (inclusive, default 201)")
    parser.add_argument("--end", type=int, default=310, help="End phase (inclusive, default 310)")
    args = parser.parse_args()

    start = args.start
    end = args.end
    if start > end:
        print("[ERROR] --start must be <= --end")
        sys.exit(1)

    print("\n" + "=" * 70)
    print(f"  PHASE ORCHESTRATOR: {start}–{end}")
    print("=" * 70)
    print(f"Root: {ROOT}")

    phase_funcs = _import_phase_modules()
    if not phase_funcs:
        print("[ERROR] No phase functions found from diagnostics modules.")
        report = {
            "timestamp": datetime.now().isoformat(),
            "start_phase": start,
            "end_phase": end,
            "overall_status": "FAIL",
            "failed_phase": None,
            "reason": "No PHASE_MODULES found in diagnostics modules.",
            "impact": "Cannot run any phases; diagnostics modules missing or broken.",
            "next_actions": [
                "Ensure system3_phase_201_230_diagnostics.py and related diagnostics files exist and import correctly.",
                "Run diagnostics modules directly to see detailed errors.",
            ],
        }
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = PROOF_DIR / f"PHASE_ORCHESTRATOR_FAIL_{ts}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Report written: {path}")
        sys.exit(1)

    all_passed, steps = _run_phases_in_range(start, end, phase_funcs)
    failed_step = next((s for s in steps if s["status"] == "FAIL"), None)

    if not all_passed and failed_step is not None:
        phase = int(failed_step["phase"])
        reason = failed_step.get("detail", "Unknown failure.")
        impact = _phase_impact(phase)
        next_actions = _phase_next_actions(phase)

        report = {
            "timestamp": datetime.now().isoformat(),
            "start_phase": start,
            "end_phase": end,
            "overall_status": "FAIL",
            "failed_phase": phase,
            "reason": reason,
            "impact": impact,
            "next_actions": next_actions,
            "steps": steps,
        }
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = PROOF_DIR / f"PHASE_ORCHESTRATOR_FAIL_{ts}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print("\n" + "=" * 70)
        print("  PHASE ORCHESTRATOR FAILED")
        print("=" * 70)
        print(f"Failed phase: {phase}")
        print(f"Reason: {reason}")
        print(f"Impact: {impact}")
        print("Next actions (in order):")
        for idx, action in enumerate(next_actions, 1):
            print(f"  {idx}. {action}")
        print(f"\nFull report written: {path}")
        print("=" * 70 + "\n")
        sys.exit(1)

    ok_count = sum(1 for s in steps if s["status"] == "OK")
    warn_count = sum(1 for s in steps if s["status"] in ("WARN", "SKIP"))

    report = {
        "timestamp": datetime.now().isoformat(),
        "start_phase": start,
        "end_phase": end,
        "overall_status": "PASS",
        "ok": ok_count,
        "warn_or_skip": warn_count,
        "steps": steps,
    }
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = PROOF_DIR / f"PHASE_ORCHESTRATOR_OK_{ts}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 70)
    print("  PHASE ORCHESTRATOR COMPLETED (NO FAIL)")
    print("=" * 70)
    print(f"Phases {start}–{end}: OK={ok_count}, WARN/SKIP={warn_count}, FAIL=0")
    print(f"OK report written: {path}")
    print("=" * 70 + "\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
