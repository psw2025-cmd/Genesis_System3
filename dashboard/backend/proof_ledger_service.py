"""Append-only SHA256 proof ledger + fail-closed autonomous intent ticks.

Infinite GitOps loop: agents continue routine work without waiting for the user.
LIVE enablement, order placement, gate dilution, and secret minting remain blocked.
Secret payloads are never stored in the ledger.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

_LOG = logging.getLogger(__name__)

LEDGER_SCHEMA = "system3_proof_ledger_v1"
INTENT_SCHEMA = "system3_autonomous_intent_v1"
PROOF_LEDGER_PUBLIC_ERROR = "PROOF_LEDGER_UNAVAILABLE"
LEDGER_REL = Path("reports") / "latest" / "proof_ledger" / "ledger.jsonl"
INTENT_REL = Path("reports") / "latest" / "autonomous_loop" / "intent_tick.json"

FORBIDDEN_LEDGER_KEYS = frozenset(
    {
        "access_token",
        "dhan_access_token",
        "dhan_token",
        "token",
        "secret",
        "client_secret",
        "pin",
        "dhan_pin",
        "totp",
        "totp_secret",
        "password",
        "private_key",
        "sa_key",
        "authorization",
        "bearer",
    }
)

DEFAULT_CONSTRAINTS = (
    "LIVE=false",
    "order_placement_allowed=false",
    "no_secret_mint_except_rotator",
    "never_weaken_proof_gates",
    "zero_synthetic_inventions",
    "gitops_only_no_hot_graph_rewrite",
)


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash_payload(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _assert_no_forbidden(obj: Any, path: str = "") -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            lowered = str(key).lower()
            if lowered in FORBIDDEN_LEDGER_KEYS or any(
                token in lowered for token in ("access_token", "private_key", "totp_secret")
            ):
                raise ValueError(f"forbidden ledger key: {path}{key}")
            _assert_no_forbidden(value, f"{path}{key}.")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _assert_no_forbidden(item, f"{path}{i}.")


def ledger_path(root: Path) -> Path:
    return root / LEDGER_REL


def intent_path(root: Path) -> Path:
    return root / INTENT_REL


def _read_entries(root: Path) -> List[Dict[str, Any]]:
    path = ledger_path(root)
    if not path.exists():
        return []
    entries: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict):
            entries.append(row)
    return entries


def ledger_tip(root: Path) -> Optional[Dict[str, Any]]:
    entries = _read_entries(root)
    return entries[-1] if entries else None


def verify_ledger_chain(root: Path) -> Dict[str, Any]:
    entries = _read_entries(root)
    prev = "GENESIS"
    for i, entry in enumerate(entries):
        stored = str(entry.get("entry_hash") or "")
        body = {k: v for k, v in entry.items() if k != "entry_hash"}
        expected = _hash_payload(body)
        if stored != expected:
            return {"ok": False, "entries": len(entries), "break_at": i, "reason": "hash_mismatch"}
        if str(entry.get("prev_hash") or "") != prev:
            return {"ok": False, "entries": len(entries), "break_at": i, "reason": "prev_hash_mismatch"}
        if entry.get("live_trading_enabled") is True or entry.get("order_placement_allowed") is True:
            return {"ok": False, "entries": len(entries), "break_at": i, "reason": "live_lock_broken"}
        if entry.get("secret_payloads_present") is True:
            return {"ok": False, "entries": len(entries), "break_at": i, "reason": "secret_payload_flag"}
        prev = stored
    return {"ok": True, "entries": len(entries), "tip_hash": prev if entries else "GENESIS"}


def proof_ledger_status(root: Path) -> Dict[str, Any]:
    """Read-only ledger + latest intent tick. Never appends. Never includes secrets."""
    chain = verify_ledger_chain(root)
    tip = ledger_tip(root)
    intent = None
    path = intent_path(root)
    if path.exists():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            _assert_no_forbidden(loaded)
            intent = loaded
    return {
        "schema": "system3_proof_ledger_status_v1",
        "chain": chain,
        "tip": tip,
        "intent_tick": intent,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "secret_payloads_present": False,
        "wait_for_user_routine": False,
    }


def proof_ledger_fail_closed_payload() -> Dict[str, Any]:
    """Stable public error body. Never includes exception text or secrets."""
    return {
        "schema": "system3_proof_ledger_status_v1",
        "status": "error",
        "error": PROOF_LEDGER_PUBLIC_ERROR,
        "chain": {"ok": False, "entries": 0},
        "tip": None,
        "intent_tick": None,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "secret_payloads_present": False,
    }


def read_proof_ledger_public(root: Path) -> Dict[str, Any]:
    """Public read path: fail closed without leaking exception contents."""
    try:
        return proof_ledger_status(root)
    except Exception:
        _LOG.exception("proof_ledger_status_failed")
        return proof_ledger_fail_closed_payload()


def build_intent_tick(
    *,
    next_id: str,
    defect: str = "",
    success_criteria: str = "",
    requested_live: bool = False,
) -> Dict[str, Any]:
    """Compile one autonomous tick. Routine work never waits; LIVE always does."""
    live_request = bool(requested_live) or str(next_id).upper() in {"LIVE", "ENABLE_LIVE", "GO_LIVE"}
    human_gate = "LIVE_ENABLEMENT" if live_request else None
    return {
        "schema": INTENT_SCHEMA,
        "compiled_at_utc": _utc(),
        "next_id": next_id,
        "defect": defect,
        "success_criteria": success_criteria,
        "constraints": list(DEFAULT_CONSTRAINTS),
        "wait_for_user": bool(live_request),
        "auto_continue": not live_request,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "human_gate_required": human_gate,
        "rejected_action": "enable_live_trading" if live_request else None,
        "strategy_mutation_allowed": "code_via_pr_and_evals_only",
        "proof_gate_thresholds_locked": True,
        "synthetic_metrics_allowed": False,
        "hot_graph_rewrite_allowed": False,
        "roles": {
            "schema_drift": "claude_sonnet",
            "signal_graph": "gemini",
            "governance_ledger": "copilot",
            "ast_consistency": "claude_code",
            "atomic_patches": "codex_cli",
            "backtests": "gemini_verification",
            "runtime_truth": "copilot_governance",
        },
    }


def write_intent_tick(root: Path, tick: Dict[str, Any]) -> Path:
    path = intent_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tick, indent=2), encoding="utf-8")
    return path


def append_ledger_entry(
    root: Path,
    *,
    git_sha: str = "",
    cloud_run_revision: str = "",
    broker_connected: Optional[bool] = None,
    gate_ids: Optional[Iterable[str]] = None,
    next_id: str = "",
    evidence_class: str = "HISTORICAL_STORED",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    extra = dict(extra or {})
    _assert_no_forbidden(extra)
    tick = build_intent_tick(
        next_id=next_id or extra.get("next_id") or "NONE",
        defect=str(extra.get("defect") or ""),
        success_criteria=str(extra.get("success_criteria") or ""),
        requested_live=bool(extra.get("requested_live")),
    )
    write_intent_tick(root, tick)

    entries = _read_entries(root)
    prev_hash = str(entries[-1]["entry_hash"]) if entries else "GENESIS"
    body: Dict[str, Any] = {
        "schema": LEDGER_SCHEMA,
        "captured_at_utc": _utc(),
        "prev_hash": prev_hash,
        "git_sha": git_sha,
        "cloud_run_revision": cloud_run_revision,
        "broker_connected": broker_connected,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "gate_ids": list(gate_ids or []),
        "next_id": tick["next_id"],
        "intent_wait_for_user": tick["wait_for_user"],
        "intent_auto_continue": tick["auto_continue"],
        "evidence_class": evidence_class,
        "secret_payloads_present": False,
        "human_gate_required": tick["human_gate_required"],
    }
    _assert_no_forbidden(body)
    body["entry_hash"] = _hash_payload(body)

    path = ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(body, sort_keys=True) + "\n")
    return body
