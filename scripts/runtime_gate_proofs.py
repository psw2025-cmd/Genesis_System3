"""
Materialize missing gate proof artifacts during /api/auto_gates refresh.

Render ephemeral disk loses reports between deploys; this regenerates them from
live APIs when market is open so inline gate evaluation can read fresh proofs.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

MAX_AGE_SEC = int(os.environ.get("SYSTEM3_RUNTIME_PROOF_MAX_AGE_SEC", "900"))


def _api_base() -> str:
    port = os.environ.get("PORT")
    if port:
        return f"http://127.0.0.1:{port}"
    for key in ("SYSTEM3_INTERNAL_API_BASE", "SYSTEM3_API_BASE", "SYSTEM3_PUBLIC_BACKEND_URL"):
        val = os.environ.get(key)
        if val:
            return val.rstrip("/")
    return "https://genesis-system3-backend.onrender.com"


def _stale(path: Path, max_age: int = MAX_AGE_SEC) -> bool:
    if not path.exists():
        return True
    return (time.time() - path.stat().st_mtime) > max_age


def _market_open(live_state: Optional[Dict[str, Any]]) -> bool:
    if live_state:
        return bool((live_state.get("market") or {}).get("is_open"))
    try:
        from zoneinfo import ZoneInfo
        from datetime import datetime

        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        if now.weekday() >= 5:
            return False
        mins = now.hour * 60 + now.minute
        return 9 * 60 + 15 <= mins < 15 * 60 + 30
    except Exception:
        return False


def ensure_runtime_proofs(
    root: Path,
    live_state: Optional[Dict[str, Any]] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """Generate stale/missing proof reports; returns summary of actions taken."""
    root = root.resolve()
    api = _api_base()
    market_open = _market_open(live_state)
    actions: Dict[str, str] = {}

    friction_path = root / "reports" / "latest" / "friction_expectancy" / "summary.json"
    if force or _stale(friction_path):
        try:
            from scripts.system3_friction_expectancy_proof import OUT, build_report

            OUT.mkdir(parents=True, exist_ok=True)
            report = build_report()
            (OUT / "summary.json").write_text(
                __import__("json").dumps(report, indent=2), encoding="utf-8"
            )
            actions["friction_expectancy"] = "generated"
        except Exception as exc:
            actions["friction_expectancy"] = f"skip:{exc}"[:80]

    opt_json = root / "reports" / "latest" / "option_strike_visibility.json"
    opt_md = root / "reports" / "latest" / "option_strike_visibility.md"
    if force or _stale(opt_json) or not opt_md.exists():
        try:
            from scripts.system3_option_visibility_audit import (
                collect_option_master,
                load_state_signals,
                make_rows,
                write_reports,
            )

            signals, signal_source = load_state_signals(root, api)
            master, master_source = collect_option_master(root)
            rows = make_rows(signals, master, master_source, signal_source)
            write_reports(root, rows, signal_source, master_source)
            actions["option_visibility"] = f"generated:{len(rows)}_rows"
        except Exception as exc:
            actions["option_visibility"] = f"skip:{exc}"[:80]

    model_path = root / "reports" / "latest" / "model_accuracy_report.json"
    if force or _stale(model_path):
        try:
            from scripts.system3_model_accuracy_tracker import (
                load_prediction_sources,
                make_accuracy_rows,
                write_reports,
            )

            predictions, sources = load_prediction_sources(root, api)
            rows = make_accuracy_rows(predictions)
            write_reports(root, rows, sources)
            actions["model_accuracy"] = f"generated:{len(rows)}_rows"
        except Exception as exc:
            actions["model_accuracy"] = f"skip:{exc}"[:80]

    lifecycle_path = root / "reports" / "latest" / "analyzer_paper_lifecycle_proof" / "summary.json"
    if market_open and (force or _stale(lifecycle_path)):
        try:
            from scripts.paper_lifecycle_proof import run_proof

            proof = run_proof(dry_run=False, force=False)
            actions["paper_lifecycle"] = proof.get("status", "unknown")
        except Exception as exc:
            actions["paper_lifecycle"] = f"skip:{exc}"[:80]
    elif not market_open:
        actions["paper_lifecycle"] = "skipped_market_closed"

    return {
        "api_base": api,
        "market_open": market_open,
        "actions": actions,
    }
