#!/usr/bin/env python3
"""Continuous closure orchestrator — scan → verify → watchdog → cards → auto-resume.

Usage:
  python scripts/system3_continuous_closure_orchestrator.py
  python scripts/system3_continuous_closure_orchestrator.py --offline
  python scripts/system3_continuous_closure_orchestrator.py --prod-base https://genesis-system3-web-doq2wplepa-el.a.run.app

Writes:
  reports/latest/continuous_closure/summary.json
  reports/latest/continuous_closure/resume_state.json
  reports/latest/proof_ledger/ledger.jsonl
  reports/latest/autonomous_loop/intent_tick.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.backend.continuous_closure_service import (  # noqa: E402
    DEFAULT_PROD,
    build_continuous_closure_report,
    write_closure_artifacts,
)
from dashboard.backend.proof_ledger_service import (  # noqa: E402
    append_ledger_entry,
    verify_ledger_chain,
)


def _git_sha() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return (proc.stdout or "").strip()
    except Exception:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="System3 continuous closure orchestrator")
    parser.add_argument("--prod-base", default=DEFAULT_PROD)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip live URL probes (repo/reports only)",
    )
    args = parser.parse_args()

    report = build_continuous_closure_report(
        ROOT,
        prod_base=args.prod_base,
        include_live=not args.offline,
    )
    summary_path, state_path = write_closure_artifacts(ROOT, report)
    nxt = (report.get("phases") or {}).get("auto_resume") or {}
    next_id = str(nxt.get("next_id") or "NONE")
    ledger_status: dict = {"ok": False, "error": "not_appended"}
    try:
        entry = append_ledger_entry(
            ROOT,
            git_sha=_git_sha(),
            next_id=next_id,
            evidence_class="HISTORICAL_STORED" if args.offline else "REQUEST_SCOPED_LIVE",
            extra={
                "defect": str(nxt.get("title") or nxt.get("defect") or ""),
                "success_criteria": "execute next OPEN card test-first; LIVE=false; no secret payloads",
            },
        )
        ledger_status = {
            "ok": True,
            "entry_hash": entry.get("entry_hash"),
            "chain": verify_ledger_chain(ROOT),
        }
    except Exception as exc:
        ledger_status = {"ok": False, "error": str(exc)[:200]}
    print(
        json.dumps(
            {
                "summary": report.get("summary"),
                "summary_path": str(summary_path),
                "resume_path": str(state_path),
                "proof_ledger": ledger_status,
            },
            indent=2,
        )
    )
    if nxt:
        print(f"AUTO_RESUME next={nxt.get('next_id')} state={nxt.get('state')}")
    else:
        print("AUTO_RESUME next=NONE (no open cards)")
    # Exit 0 always for observability runs; open cards are not a process failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
