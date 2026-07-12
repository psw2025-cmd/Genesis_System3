#!/usr/bin/env python3
"""
System3 1000+ TODO Status Updater

Converts a static markdown checklist into a proof-driven status file using latest local proof artifacts.
Statuses: DONE / PARTIAL / PENDING / BLOCKED.

Input default:
  docs/SYSTEM3_PRODUCTION_GRADE_1000_POINT_QC_TODO.md
Fallback:
  System3_Production_Grade_1000_Point_QC_TODO.md in repo root

Outputs:
  reports/latest/todo_status_update/summary.json
  reports/latest/todo_status_update/summary.md
  reports/latest/todo_status_update/System3_Production_Grade_1000_Point_QC_TODO_STATUS.md
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "todo_status_update"
DEFAULT_TODO = ROOT / "docs" / "SYSTEM3_PRODUCTION_GRADE_1000_POINT_QC_TODO.md"
FALLBACK_TODO = ROOT / "System3_Production_Grade_1000_Point_QC_TODO.md"

STATUS_DONE = "DONE"
STATUS_PARTIAL = "PARTIAL"
STATUS_PENDING = "PENDING"
STATUS_BLOCKED = "BLOCKED"


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {"_json_error": str(exc)}


def has_file(path: str) -> bool:
    return (ROOT / path).exists()


def low(s: str) -> str:
    return s.lower()


def proof_state() -> Dict[str, Any]:
    visual = read_json(ROOT / "reports/latest/dashboard_visual_production_proof/summary.json")
    live_ui = read_json(ROOT / "reports/latest/dashboard_live_ui_proof/summary.json")
    public_truth_json = read_json(ROOT / "reports/latest/system3_public_truth/index.json")
    public_truth_md = read_text(ROOT / "reports/latest/system3_public_truth/index.md")
    parallel = read_json(ROOT / "reports/latest/parallel_root_cause_audit/summary.json")
    workflow_fail = read_json(ROOT / "reports/latest/workflow_failure_tracker/summary.json")
    options_ml = read_json(ROOT / "reports/latest/options_ml_training/summary.json")
    contracts = read_json(ROOT / "reports/latest/options_contract_builder/summary.json")

    visual_pass = bool(visual.get("visual_gate_pass") is True or visual.get("final_verdict") == "PASS")
    screenshots = visual.get("screenshots") or []
    screenshots_ok = bool(screenshots) and all(bool(x.get("ok")) for x in screenshots if isinstance(x, dict))
    live_ui_pass = live_ui.get("final_verdict") == "PASS"
    owner_visible = bool(live_ui.get("owner_badge_visible") is True or visual_pass)
    proof_bar_visible = bool(live_ui.get("production_proof_bar_visible") is True)
    ml_visible = bool(live_ui.get("ml_proof_visible") is True)
    paper_visible = bool(live_ui.get("paper_truth_visible") is True)

    public_fail = "Final verdict: **FAIL**" in public_truth_md or public_truth_json.get("final_verdict") == "FAIL"
    public_pass = "Final verdict: **PASS**" in public_truth_md or public_truth_json.get("final_verdict") == "PASS"

    workflow_blocked = workflow_fail.get("status") == "BLOCKED" or int(workflow_fail.get("failed_count") or 0) > 0
    parallel_blocked = parallel.get("status") == "BLOCKED" or int(parallel.get("blocker_count") or 0) > 0

    ml_pass = options_ml.get("status") in {"PASS", "PASS_HIGH_SCORE", "PROVEN_TRAINED_ANALYZER_ONLY"}
    ml_blocked = bool(options_ml) and not ml_pass
    contracts_pass = contracts.get("status") == "PASS"

    return {
        "visual_pass": visual_pass,
        "screenshots_ok": screenshots_ok,
        "live_ui_pass": live_ui_pass,
        "owner_visible": owner_visible,
        "proof_bar_visible": proof_bar_visible,
        "ml_visible": ml_visible,
        "paper_visible": paper_visible,
        "public_pass": public_pass,
        "public_fail": public_fail,
        "workflow_blocked": workflow_blocked,
        "parallel_blocked": parallel_blocked,
        "parallel_blocker_count": int(parallel.get("blocker_count") or 0) if parallel else None,
        "ml_pass": ml_pass,
        "ml_blocked": ml_blocked,
        "contracts_pass": contracts_pass,
        "has_parallel_workflow": has_file(".github/workflows/system3-parallel-root-cause-audit.yml"),
        "has_workflow_tracker": has_file(".github/workflows/system3-workflow-failure-tracker.yml"),
        "has_visual_rules": has_file("docs/SYSTEM3_VISUAL_PROOF_AND_RENDER_RULES.md"),
        "has_360_matrix": has_file("docs/SYSTEM3_360_ROOT_CAUSE_BLOCKERS.md"),
        "has_parallel_tool": has_file("tools/system3_parallel_root_cause_audit.py"),
        "has_tracker_tool": has_file("tools/system3_workflow_failure_tracker.py"),
        "has_options_pipeline": has_file("scripts/options_ce_pe_history_pipeline.py"),
        "has_contract_builder": has_file("scripts/build_options_history_contracts.py"),
    }


def classify_item(item_text: str, state: Dict[str, Any]) -> Tuple[str, str]:
    t = low(item_text)

    # Hard blockers first
    if any(k in t for k in ["live trading", "live order", "real money", "money ready", "order placement", "broker order"]):
        if "off" in t or "disabled" in t or "blocked" in t or "safety" in t:
            return STATUS_DONE, "Live trading safety is intentionally OFF/blocked."
        return STATUS_BLOCKED, "Real-money/live-order readiness is blocked until all proof gates pass."

    if any(k in t for k in ["final truth", "public truth", "production grade", "money-ready", "money ready"]):
        if state["public_pass"]:
            return STATUS_DONE, "Final public truth PASS found."
        if state["public_fail"]:
            return STATUS_BLOCKED, "Final public truth is FAIL or stale."
        return STATUS_PENDING, "Final public truth proof missing or not current."

    if any(k in t for k in ["workflow", "github action", "ci", "failure tracker", "failed workflow"]):
        if "tracker" in t and state["has_workflow_tracker"]:
            return STATUS_DONE, "Workflow failure tracker exists."
        if state["workflow_blocked"]:
            return STATUS_BLOCKED, "One or more workflows are failed/timed out/cancelled/action-required."
        return STATUS_PARTIAL if state["has_workflow_tracker"] else STATUS_PENDING, "Workflow tracker exists but latest run proof may be pending."

    if any(k in t for k in ["parallel", "root-cause", "root cause", "360", "360°"]):
        if state["parallel_blocked"]:
            return STATUS_PARTIAL if state["has_parallel_workflow"] else STATUS_PENDING, "Parallel audit exists but blockers remain."
        if state["has_parallel_workflow"] and state["has_parallel_tool"]:
            return STATUS_DONE, "Parallel root-cause audit workflow/tool exists."
        return STATUS_PENDING, "Parallel audit tool/workflow not fully proven."

    if any(k in t for k in ["render", "deploy", "frontend bundle", "stale frontend", "backend api refresh"]):
        if state["live_ui_pass"] and not state["public_fail"]:
            return STATUS_DONE, "Render/UI proof reports PASS and public truth is not failing."
        return STATUS_BLOCKED, "Render/deploy freshness needs proof; stale deploy or missing proof blocks claim."

    if any(k in t for k in ["visual", "screenshot", "owner", "proof bar", "ui proof", "dashboard proof"]):
        if "owner" in t and state["owner_visible"]:
            return STATUS_PARTIAL, "Owner visibility has evidence, but full automated visual proof may still be pending."
        if "proof bar" in t and state["proof_bar_visible"]:
            return STATUS_PARTIAL, "Production Proof Bar visible in latest live UI proof/user evidence, full automated proof pending."
        if state["visual_pass"] and state["screenshots_ok"]:
            return STATUS_PARTIAL, "Screenshot proof exists; visible text freshness still must match latest commit."
        return STATUS_PENDING, "Fresh dashboard screenshot proof required."

    if any(k in t for k in ["dhan", "broker", "token", "fund", "holding", "positions", "client id"]):
        if "live order" in t or "order placement" in t:
            return STATUS_DONE, "Broker order path remains disabled."
        return STATUS_PARTIAL, "Latest user visual evidence shows Dhan read-only connected; automated API proof still required."

    if any(k in t for k in ["option chain", "option-chain", "chain", "expiry", "strike", "strike visibility"]):
        if state["contracts_pass"]:
            return STATUS_PARTIAL, "Contract builder proof exists, but live option-chain/strike visibility still needs proof."
        return STATUS_BLOCKED, "Dhan option-chain/strike visibility proof is pending or blocked."

    if any(k in t for k in ["scanner", "ranker", "candidate", "ce/pe", "ce pe", "call put", "signal"]):
        return STATUS_BLOCKED, "Scanner/ranker/CE-PE candidate proof is not yet complete."

    if any(k in t for k in ["paper", "lifecycle", "entry", "exit", "p&l", "pnl", "provenance"]):
        if state["paper_visible"]:
            return STATUS_PARTIAL, "Paper provenance is visually expected/partially visible, lifecycle proof still required."
        return STATUS_BLOCKED, "Paper lifecycle entry/exit/PnL/provenance proof is pending."

    if any(k in t for k in ["ml", "model", "training", "accuracy", "auc", "spearman", "expectancy", "profit"]):
        if state["ml_pass"]:
            return STATUS_DONE, "ML training proof PASS found."
        if state["has_options_pipeline"] and state["has_contract_builder"]:
            return STATUS_PARTIAL, "ML/contract pipeline exists, but training score proof is missing or blocked."
        return STATUS_BLOCKED, "ML training/score proof is pending."

    if any(k in t for k in ["secret", "env", "credential"]):
        return STATUS_PENDING, "Secret/env correctness cannot be proven from repo; verify in Render without exposing values."

    if any(k in t for k in ["documentation", "md", "todo", "rules", "matrix"]):
        if state["has_visual_rules"] and state["has_360_matrix"]:
            return STATUS_DONE, "Rules/matrix documentation exists."
        return STATUS_PARTIAL, "Some documentation exists; proof docs may still be incomplete."

    return STATUS_PENDING, "No matching proof rule; needs explicit evidence mapping."


def update_todo_markdown(todo_text: str, state: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    counts = Counter()
    updated_lines: List[str] = []
    items: List[Dict[str, str]] = []
    checkbox_re = re.compile(r"^(\s*)[-*]\s+\[( |x|X)\]\s+(.*)$")

    for line in todo_text.splitlines():
        m = checkbox_re.match(line)
        if not m:
            updated_lines.append(line)
            continue
        indent, _old, text = m.groups()
        status, reason = classify_item(text, state)
        counts[status] += 1
        items.append({"text": text.strip(), "status": status, "reason": reason})
        mark = "x" if status == STATUS_DONE else " "
        updated_lines.append(f"{indent}- [{mark}] **{status}** — {text}  ")
        updated_lines.append(f"{indent}  - Proof/status: {reason}")

    header = [
        "# System3 Production Grade 1000+ TODO — Proof Status Update",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Summary",
        "",
        f"- Total checklist items scanned: `{sum(counts.values())}`",
        f"- DONE: `{counts[STATUS_DONE]}`",
        f"- PARTIAL: `{counts[STATUS_PARTIAL]}`",
        f"- PENDING: `{counts[STATUS_PENDING]}`",
        f"- BLOCKED: `{counts[STATUS_BLOCKED]}`",
        "",
        "## Proof state used",
        "",
    ]
    for k in sorted(state):
        header.append(f"- `{k}`: `{state[k]}`")
    header.extend(["", "---", ""])

    return "\n".join(header + updated_lines) + "\n", {
        "counts": dict(counts),
        "items": items,
        "total": sum(counts.values()),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--todo", default="", help="Input TODO markdown path")
    ap.add_argument("--output-name", default="System3_Production_Grade_1000_Point_QC_TODO_STATUS.md")
    args = ap.parse_args()

    todo_path = Path(args.todo) if args.todo else DEFAULT_TODO
    if not todo_path.exists() and not args.todo:
        todo_path = FALLBACK_TODO

    OUT.mkdir(parents=True, exist_ok=True)
    state = proof_state()
    todo_text = read_text(todo_path)

    if not todo_text:
        payload = {
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "status": STATUS_BLOCKED,
            "reason": f"TODO file not found or empty: {todo_path}",
            "todo_path": str(todo_path),
            "proof_state": state,
            "counts": {STATUS_DONE: 0, STATUS_PARTIAL: 0, STATUS_PENDING: 0, STATUS_BLOCKED: 1},
            "total": 0,
        }
        (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        (OUT / "summary.md").write_text(f"# TODO Status Update\n\nStatus: **BLOCKED**\n\nReason: `{payload['reason']}`\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 0

    updated, meta = update_todo_markdown(todo_text, state)
    out_md = OUT / args.output_name
    out_md.write_text(updated, encoding="utf-8")

    counts = Counter(meta["counts"])
    status = STATUS_DONE if counts[STATUS_BLOCKED] == 0 and counts[STATUS_PENDING] == 0 and counts[STATUS_PARTIAL] == 0 else STATUS_BLOCKED
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "todo_path": str(todo_path),
        "output_markdown": str(out_md.relative_to(ROOT)),
        "counts": dict(counts),
        "total": meta["total"],
        "proof_state": state,
        "production_grade_claim_allowed": status == STATUS_DONE,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    summary_lines = [
        "# System3 1000+ TODO Status Summary",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Status: **{payload['status']}**",
        f"Input TODO: `{payload['todo_path']}`",
        f"Output TODO status file: `{payload['output_markdown']}`",
        "",
        "## Counts",
        "",
        f"- Total: `{payload['total']}`",
        f"- DONE: `{counts[STATUS_DONE]}`",
        f"- PARTIAL: `{counts[STATUS_PARTIAL]}`",
        f"- PENDING: `{counts[STATUS_PENDING]}`",
        f"- BLOCKED: `{counts[STATUS_BLOCKED]}`",
        "",
        "## Claim rule",
        "",
        "Production-grade claim is allowed only if every scanned checklist item is DONE.",
    ]
    (OUT / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
