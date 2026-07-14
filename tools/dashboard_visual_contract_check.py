#!/usr/bin/env python3
"""Fail-closed static contract check for dashboard visual proof markers.

This tool reads repository source only. It does not call Render, brokers, market
feeds, scanners, paper engines, ML services, or order endpoints. It never reads
or prints secrets.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "dashboard_visual_contract_check"
PAPER = ROOT / "dashboard" / "frontend" / "src" / "components" / "PaperTrading.tsx"
PROOF = ROOT / "tools" / "dashboard_live_ui_proof.mjs"
SIDEBAR = ROOT / "dashboard" / "frontend" / "src" / "components" / "Sidebar.tsx"

PAPER_MARKERS = (
    "Paper Truth Provenance",
    "Fake/fixture rejected",
    "Order endpoints",
    "NOT CALLED",
)
PROOF_MARKERS = (
    "Paper Truth Provenance",
    "Fake\\/fixture rejected",
    "Order endpoints",
    "NOT CALLED|BLOCKED",
)
EXPECTED_TABS = (
    "Truth Control",
    "Genesis Brain",
    "E2E Proof",
    "Overview",
    "Option Chain",
    "Signals",
    "Paper Trades",
    "Positions",
    "Broker",
    "Performance",
    "ML Model",
    "Live Gate",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def main() -> int:
    paper_text = read_text(PAPER)
    proof_text = read_text(PROOF)
    sidebar_text = read_text(SIDEBAR)

    checks: list[dict[str, object]] = []
    blockers: list[str] = []

    for marker in PAPER_MARKERS:
        ok = marker in paper_text
        checks.append({"scope": "paper_source", "marker": marker, "ok": ok})
        if not ok:
            blockers.append(f"PAPER_SOURCE_MARKER_MISSING:{marker}")

    for marker in PROOF_MARKERS:
        ok = marker in proof_text
        checks.append({"scope": "proof_contract", "marker": marker, "ok": ok})
        if not ok:
            blockers.append(f"PROOF_CONTRACT_MARKER_MISSING:{marker}")

    for title in EXPECTED_TABS:
        source_ok = title in sidebar_text
        proof_ok = bool(re.search(rf"['\"]{re.escape(title)}['\"]", proof_text))
        checks.append({"scope": "tab_contract", "title": title, "source_ok": source_ok, "proof_ok": proof_ok})
        if not source_ok:
            blockers.append(f"SIDEBAR_TAB_MISSING:{title}")
        if not proof_ok:
            blockers.append(f"PROOF_TAB_MISSING:{title}")

    status = "PASS" if not blockers else "BLOCKED"
    result = {
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "purpose": "Distinguish repository visual-contract regressions from deployed/runtime proof failures.",
        "safety": {
            "analyze_mode": True,
            "live_trading_enabled": False,
            "system3_live_trading_allowed": False,
            "network_calls": False,
            "broker_order_endpoints_called": False,
            "secrets_read_or_written": False,
        },
        "paper_source_contract_complete": all(
            c.get("ok") is True for c in checks if c.get("scope") == "paper_source"
        ),
        "proof_marker_contract_complete": all(
            c.get("ok") is True for c in checks if c.get("scope") == "proof_contract"
        ),
        "tab_contract_complete": all(
            c.get("source_ok") is True and c.get("proof_ok") is True
            for c in checks
            if c.get("scope") == "tab_contract"
        ),
        "checks": checks,
        "blockers": blockers,
        "interpretation": (
            "If this report passes while live visual proof reports PAPER_TRUTH_NOT_VISIBLE, "
            "the remaining cause is deployed asset drift, tab navigation, or asynchronous runtime rendering—not missing source labels."
        ),
        "production_grade_claim_allowed": False,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (OUT / "summary.md").write_text(
        "\n".join(
            [
                "# Dashboard Visual Contract Check",
                "",
                f"- Status: **{status}**",
                f"- Paper source contract complete: `{result['paper_source_contract_complete']}`",
                f"- Proof marker contract complete: `{result['proof_marker_contract_complete']}`",
                f"- Tab contract complete: `{result['tab_contract_complete']}`",
                "- Analyzer mode: `ON`",
                "- Live trading: `OFF`",
                "- Network/order calls: `false`",
                "",
                "## Blockers",
                *(f"- {item}" for item in blockers),
                *( ["- none"] if not blockers else [] ),
                "",
                "A PASS here does not make the live dashboard PASS. It only proves the repository source and visual-proof marker contract agree.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"dashboard_visual_contract_check status={status} blockers={len(blockers)}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
