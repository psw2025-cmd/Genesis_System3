"""Fail-closed release guard for Genesis System3.

This tool is read-only. It never submits broker orders or changes cloud state.
Exit status 0 means the inspected candidate passed these guard checks; it is
not itself authorization to deploy or enable live trading.
"""

from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
GCP_PROJECT = "system3-openalgo-safe"
GATE_SOURCE = ROOT / "scripts" / "system3_gate_evaluator.py"
_UI_PROBE_JS = r"""
const { chromium } = require('playwright');
(async () => {
  let browser;
  try { browser = await chromium.launch({headless: true}); }
  catch (_) { browser = await chromium.launch({headless: true, channel: 'msedge'}); }
  try {
    const page = await browser.newPage();
    await page.goto(process.argv[1], {waitUntil: 'domcontentloaded', timeout: 30000});
    const deadline = Date.now() + 30000;
    let text = '';
    while (Date.now() < deadline) {
      text = await page.locator('body').innerText({timeout: 5000}).catch(() => '');
      if (/ML MODEL TRUTH/i.test(text) && (/\bLIVE\s+OFF\b/i.test(text) || /\bLIVE\s+ON\b/i.test(text))) break;
      await page.waitForTimeout(500);
    }
    process.stdout.write(JSON.stringify({title: await page.title(), text}));
  } finally { await browser.close(); }
})().catch((error) => {
  process.stderr.write(`UI_PROBE_FAILED:${error && error.name ? error.name : 'Error'}`);
  process.exitCode = 2;
});
"""


def _enabled(value: Any) -> bool:
    if value is True:
        return True
    return isinstance(value, str) and value.strip().lower() in {"1", "true", "yes", "on"}


def api_ui_truth(api_payload: Dict[str, Any], visible_text: str) -> Tuple[bool, str]:
    """Require the rendered UI to show PAPER/live-off truth from the API."""
    ready = api_payload.get("ready_for_live")
    if not isinstance(ready, bool):
        return False, "API_READY_FOR_LIVE_MISSING_OR_INVALID"
    for key in ("live_trading_enabled", "live_allowed", "order_placement_allowed", "real_broker_orders"):
        if _enabled(api_payload.get(key)):
            return False, f"API_SAFETY_FLAG_ENABLED:{key}"
    upper_text = visible_text.upper()
    if not re.search(r"\bLIVE\s+OFF\b", upper_text):
        return False, "UI_LIVE_OFF_LABEL_MISSING"
    if re.search(r"\bLIVE\s+ON\b", upper_text):
        return False, "UI_CLAIMS_LIVE_ON"
    if "ML MODEL TRUTH" not in upper_text:
        return False, "UI_ML_MODEL_PANEL_MISSING"
    expected_proof = "FORWARD PROOF: REPORTED PASS" if ready else "FORWARD PROOF: NOT PROVEN"
    if expected_proof not in upper_text:
        return False, "ML_UI_READINESS_DOES_NOT_MATCH_API"
    # `ready_for_live` is a readiness claim, never authorization to place orders.
    return True, "API_UI_PAPER_TRUTH_MATCH"


def latest_firestore_proof(rows: Iterable[Dict[str, Any]]) -> Tuple[bool, str]:
    """Require valid official NSE session proof on the most recent stored row."""
    materialized = [row for row in rows if isinstance(row, dict) and row.get("date")]
    if not materialized:
        return False, "FIRESTORE_VALIDATION_ROWS_MISSING"
    latest = max(materialized, key=lambda row: str(row.get("date", "")))
    day = str(latest.get("date") or "")
    proof = latest.get("exchange_session_proof")
    if not isinstance(proof, dict):
        return False, "LATEST_FIRESTORE_SESSION_PROOF_MISSING"
    try:
        session_day = datetime.strptime(str(proof.get("session_date") or ""), "%Y-%m-%d").date()
        previous_day = datetime.strptime(str(proof.get("previous_session_date") or ""), "%Y-%m-%d").date()
        source = urlsplit(str(proof.get("source_url") or ""))
        host = (source.hostname or "").lower()
    except (TypeError, ValueError):
        return False, "LATEST_FIRESTORE_SESSION_PROOF_INVALID"
    official = (
        source.scheme.lower() == "https"
        and (host == "nseindia.com" or host.endswith(".nseindia.com"))
        and source.username is None and source.password is None
        and not source.query and not source.fragment
    )
    valid = (
        proof.get("verified") is True
        and str(proof.get("exchange") or "").upper() == "NSE"
        and session_day.isoformat() == day
        and previous_day.isoformat() == str(proof.get("previous_session_date") or "")
        and previous_day < session_day
        and official
    )
    return (True, "LATEST_FIRESTORE_SESSION_PROOF_VERIFIED") if valid else (False, "LATEST_FIRESTORE_SESSION_PROOF_INVALID")


def reconciliation_negative_control() -> Tuple[bool, str]:
    """Prove that one mismatch concealed by a zero rate fails the real gate."""
    try:
        from scripts.system3_gate_evaluator import eval_trade_reconciliation_gate
    except ImportError as exc:
        return False, f"RECONCILIATION_GATE_IMPORT_FAILED:{type(exc).__name__}"
    with tempfile.TemporaryDirectory(prefix="genesis-guard-") as temp_dir:
        root = Path(temp_dir)
        path = root / "reports" / "latest" / "trade_reconciliation" / "summary.json"
        path.parent.mkdir(parents=True)
        evidence = {
            "completed_trades": 100, "mismatch_count": 1, "mismatch_rate": 0,
            "entry_price_verified": True, "exit_price_verified": True,
            "quantity_verified": True, "charges_verified": True, "pnl_verified": True,
            "broker_records_verified": True, "internal_records_verified": True,
            "ledger_readback_verified": True, "generator_id": "guard-builder",
            "independent_reviewer_id": "guard-reviewer",
            "evidence_sha256": {key: "a" * 64 for key in ("broker_records", "internal_ledger", "reconciliation")},
        }
        path.write_text(json.dumps({"status": "PASS", "pass": True, "evidence": evidence}), encoding="utf-8")
        result = eval_trade_reconciliation_gate(root)
        if result.get("pass") is False:
            return True, "MISMATCH_NEGATIVE_CONTROL_BLOCKED"
        return False, "MISMATCH_NEGATIVE_CONTROL_FALSE_PASSED"


def unconditional_gate_passes(source: Path = GATE_SOURCE) -> List[str]:
    """Find literal PASS returns in gate functions; computed outcomes are allowed."""
    try:
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    except (OSError, SyntaxError) as exc:
        return [f"GATE_SOURCE_UNREADABLE:{type(exc).__name__}"]
    violations: List[str] = []

    def is_literal_pass(node: ast.AST) -> bool:
        if isinstance(node, ast.Constant):
            return node.value is True or (isinstance(node.value, str) and node.value.upper() == "PASS")
        if isinstance(node, ast.Dict):
            return any(
                isinstance(key, ast.Constant) and key.value in {"pass", "status"}
                and isinstance(value, ast.Constant)
                and (value.value is True or (isinstance(value.value, str) and value.value.upper() == "PASS"))
                for key, value in zip(node.keys, node.values)
            )
        return False

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and "gate" in node.name.lower():
            for child in ast.walk(node):
                if isinstance(child, ast.Return) and child.value is not None and is_literal_pass(child.value):
                    violations.append(f"UNCONDITIONAL_LITERAL_PASS:{node.name}:{child.lineno}")
    return violations


def _fetch_api(api_url: str, timeout: int) -> Dict[str, Any]:
    request = Request(api_url, headers={"Accept": "application/json", "User-Agent": "Genesis-Guard/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise RuntimeError(f"API_HTTP_{response.status}")
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"API_HTTP_{exc.code}") from None
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"API_READ_FAILED:{type(exc).__name__}") from None
    if not isinstance(payload, dict):
        raise RuntimeError("API_PAYLOAD_NOT_OBJECT")
    return payload


def _fetch_ui_text(ui_url: str, timeout: int) -> str:
    if not (ROOT / "node_modules" / "playwright").exists():
        raise RuntimeError("PLAYWRIGHT_NOT_INSTALLED")
    try:
        parsed = urlsplit(ui_url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query["tab"] = "ml"
        ml_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))
        result = subprocess.run(
            ["node", "-e", _UI_PROBE_JS, ml_url], cwd=ROOT, capture_output=True,
            text=True, timeout=timeout + 35, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"UI_BROWSER_PROBE_FAILED:{type(exc).__name__}") from None
    if result.returncode != 0:
        kind = "PLAYWRIGHT_BROWSER_PROBE_FAILED"
        match = re.search(r"UI_PROBE_FAILED:([A-Za-z0-9_]+)", result.stderr or "")
        if match:
            kind = f"UI_BROWSER_PROBE_FAILED:{match.group(1)}"
        raise RuntimeError(kind)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError("UI_BROWSER_PROBE_INVALID_OUTPUT") from None
    text = payload.get("text")
    if not isinstance(text, str):
        raise RuntimeError("UI_BROWSER_TEXT_MISSING")
    return text


def _firestore_rows() -> List[Dict[str, Any]]:
    try:
        from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend
        return FirestoreSchedulerEvidenceBackend(project=GCP_PROJECT).list_validation_days()
    except Exception as exc:
        raise RuntimeError(f"FIRESTORE_READ_FAILED:{type(exc).__name__}") from None


def _append_log(path: Path, checks: List[Tuple[str, bool, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        for name, passed, reason in checks:
            safe_reason = re.sub(r"[^A-Z0-9_:.-]", "_", reason.upper())[:180]
            stream.write(f"{timestamp} guard={name} result={'PASS' if passed else 'FAIL'} reason={safe_reason}\n")


def run_guard(api_url: str, ui_url: str, log_path: Path, timeout: int = 10) -> int:
    checks: List[Tuple[str, bool, str]] = []
    checks.append(("reconciliation_negative_control", *reconciliation_negative_control()))
    static_errors = unconditional_gate_passes()
    checks.append(("no_literal_gate_pass", not static_errors, ";".join(static_errors) if static_errors else "NO_LITERAL_GATE_PASS"))
    try:
        proof_ok, proof_reason = latest_firestore_proof(_firestore_rows())
    except RuntimeError as exc:
        proof_ok, proof_reason = False, str(exc)
    checks.append(("firestore_latest_proof", proof_ok, proof_reason))
    try:
        api_payload = _fetch_api(api_url, timeout)
        visible_text = _fetch_ui_text(ui_url, timeout)
        truth_ok, truth_reason = api_ui_truth(api_payload, visible_text)
    except RuntimeError as exc:
        truth_ok, truth_reason = False, str(exc)
    checks.append(("api_ui_paper_truth", truth_ok, truth_reason))
    _append_log(log_path, checks)
    for name, passed, reason in checks:
        print(f"{'PASS' if passed else 'FAIL'} {name}: {reason}")
    if not all(passed for _, passed, _ in checks):
        print("DEPLOY_BLOCKED: guard has one or more failed checks")
        return 1
    print("GUARD_PASS: candidate passed; deploy approval and PAPER locks remain separate")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", help="read-only /api/ml/performance URL")
    parser.add_argument("--ui-url", help="UI URL to inspect with headless Playwright")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--log-path", type=Path, default=ROOT / "logs" / "guard.log")
    args = parser.parse_args(argv)
    if not args.api_url or not args.ui_url:
        parser.error("--api-url and --ui-url are required; missing evidence must not default to PASS")
    try:
        split = urlsplit(args.api_url)
        if split.scheme != "https" or not split.hostname or split.username or split.password or split.query:
            parser.error("--api-url must be credential-free HTTPS without query parameters")
        ui_split = urlsplit(args.ui_url)
        if ui_split.scheme != "https" or not ui_split.hostname or ui_split.username or ui_split.password:
            parser.error("--ui-url must be credential-free HTTPS")
    except ValueError:
        parser.error("invalid URL")
    if args.timeout < 1 or args.timeout > 60:
        parser.error("--timeout must be 1..60 seconds")
    return run_guard(args.api_url, args.ui_url, args.log_path, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
